# Prompt : purge sécurisée des données de test avant le lancement (1er décembre 2026)

> Version améliorée. Elle s'appuie sur ce qui existe déjà dans le dépôt (vérifié le 2026-10-27) et sépare
> l'analyse, la décision, puis le code, pour qu'aucune suppression ne soit écrite avant que tu aies tranché.
> Les points marqués **[À VÉRIFIER]** sont des faits tirés de mes notes ou de ma lecture rapide : à confirmer dans le code avant de s'appuyer dessus.

---

## Contexte

EduKora est un projet Django + PostgreSQL déployé par Docker Compose sur un Droplet DigitalOcean (utilisateur `deploy`, **pas de sudo sans mot de passe** : toute opération root passe par la console DO). Le lancement public est prévu le **1er décembre 2026**. Avant cette date, des testeurs et des recettes ont écrit dans la base de production ; je veux une procédure fiable pour retirer ces données de test **sans toucher à un vrai utilisateur ni à un contenu pédagogique**.

Tu ne lances aucune suppression et ne modifies aucune donnée de production pendant les phases 1 et 2.

## Ce qui existe déjà : à réutiliser, pas à réinventer

- `backend/users/management/commands/seed_donnees_test.py` : crée des comptes de recette avec un **marqueur strict** (adresse `local+edukora-test-<rôle>@domaine` ET nom commençant par `[TEST] `), et a déjà un mode `--purge` (liste) / `--purge --oui` (supprime) et une garde d'environnement `ALLOW_TEST_DATA=1`. Lis-le en entier : la nouvelle commande doit l'étendre ou s'y appuyer, pas le dupliquer.
- `deploy/sync-lot.sh sauvegarde <id>` : `pg_dump --format=custom`, refus d'un dump trop petit, copie hors site (marqueur `.hors-site`, bucket `edukora-backups`), et `deploy/sync-lot.sh test-restauration <fichier.dump>` : restauration dans une base jetable avec comparaison de compteurs. C'est le contrôle d'intégrité attendu ; réutilise-le au lieu d'écrire une autre sauvegarde.
- `backend/synchro/` (chaîne de lots par archive, `sync_contenu`) et `scripts/edukora.ps1` (orchestration SSH depuis Windows, clé `edukora_lots_ed25519`, `edukora_known_hosts`, sous-commande `doctor -Distant`) : modèle à suivre pour le script PowerShell.
- Commandes de nettoyage existantes à lire avant d'en créer une : `purge_otp_codes`, `purger_telechargements`, `clean_duplicate_question_text`.
- Une purge locale a déjà été faite le 2026-10-12 (13 comptes de test, abonnements, paiements, progression, quiz utilisateur, analytics, OTP, sessions, journal d'admin). Elle est faite à la main, sans commande réutilisable : c'est la liste de catégories de départ, pas une preuve de ce qu'il y a en prod.
- Faits d'infrastructure **[À VÉRIFIER]** : fichiers stockés sur **DigitalOcean Spaces** (bucket `edukora-media`, pas de volume local pour les médias) ; noms de fichiers adressés par contenu ; `CAMPAY_ENVIRONMENT=DEV` en prod à la dernière vérification (les paiements CamPay actuels sont donc des paiements de test) ; le backend n'a pas de bind mount (`docker cp` ou image reconstruite pour y mettre du code) ; l'override `docker-compose.prod.yml` exige `IMAGE_TAG` même pour `exec` (voir `.deploy/current_tag` et comment `sync-lot.sh` l'exporte).

## Contraintes dures

1. **Aucune détection par ancienneté, nom ou e-mail seuls.** Le marqueur `[TEST]` + `+edukora-test-` combine deux signaux explicites posés par le seed : c'est acceptable, mais dis-moi s'il couvre aussi les comptes de testeurs créés autrement (par exemple par le skill `eleve`, qui crée « une origine par testeur », ou à la main). Pour tout compte non couvert, **n'invente pas de règle** : propose un mécanisme d'identification explicite (liste d'identifiants validée par moi, ou champ/marqueur à poser) et une liste de validation.
2. **Les vrais utilisateurs inscrits entre-temps sont protégés par défaut.** La commande est de type liste blanche : elle ne supprime que ce qui est explicitement ciblé, jamais « tout sauf ».
3. **Rien de sensible ou ambigu n'est supprimé sans catégorie explicitement activée.** Par défaut, sont protégés : matières, chapitres, cours, leçons, épreuves officielles BEPC/Probatoire/BAC et GCE, corrigés, items de quiz, épreuves inédites et leurs fichiers, figures et images pédagogiques, plans, index de recherche, paramètres de production, migrations, comptes administrateurs réels, et, pour les vrais utilisateurs, abonnements, paiements, Mobile Money, journaux d'audit.
4. **Cas à trancher, pas à deviner** : les paiements, transactions et abonnements **rattachés à un compte de test** (la protection des données de paiement vaut-elle aussi pour eux ? `CAMPAY_ENVIRONMENT=DEV` plaide pour qu'ils soient purgeables, mais le journal comptable est peut-être à conserver). Présente-le comme une décision pour moi.
5. **Code livré sans reconstruction d'image.** La commande vit dans le backend ; explique comment elle arrive dans le conteneur sans `build` (par exemple la méthode `docker cp` déjà utilisée, ou le pipeline Release/Deploy si c'est lui qui doit la livrer) et comment on vérifie que le conteneur a bien la bonne version du fichier avant de lancer quoi que ce soit.
6. **Fichiers sur Spaces.** Une suppression d'objet S3 est définitive (pas de corbeille). Ne supprime un objet que si tu as prouvé qu'aucune ligne conservée ne le référence (cherche dans **tous** les champs fichier/image/URL, y compris JSON et Markdown). Dans le doute : le lister dans le rapport, ne pas le supprimer.
7. **Aucune action externe.** La purge ne doit déclencher ni SMS, ni e-mail, ni appel CamPay, ni notification push, ni signal qui écrit ailleurs (vérifie les `post_delete`/`pre_delete`).

## Phase 1 — Analyse en lecture seule (livrable : rapport, pas de code)

Inspecte le code réel (n'invente aucun modèle, champ ou commande) :

1. Tous les modèles et leurs `ForeignKey`/`OneToOne`/`ManyToMany`, avec le `on_delete` de chacun (`CASCADE`, `PROTECT`, `SET_NULL`…). Produis le graphe des dépendances à partir de `User` et `Profil` : qu'est-ce qui disparaît en cascade, qu'est-ce qui bloque (`PROTECT`), qu'est-ce qui est laissé orphelin ?
2. Les données générées par l'usage : tentatives et réponses de quiz, historique, instantanés, progression/maîtrise, XP, séries, objectifs, analytics, OTP, sessions, abonnements, paiements, téléchargements et quotas PDF, notifications push, témoignages, journal d'admin, historiques de recherche, appareils/profils, PIN.
3. Les données pédagogiques et leurs fichiers (champs fichier/image, PDF générés, figures), et où vivent les fichiers (Spaces, caches, volumes).
4. Pour chaque catégorie : *test* / *opérationnel* / *pédagogique*, le critère d'identification **fiable** disponible aujourd'hui, ou « aucun ».
5. **Compte réel sur la prod**, en lecture seule (`SELECT`/`count` uniquement, via le shell Django ou `psql` en `-c` lecture) : combien de comptes, combien portent le marqueur strict, lesquels ne le portent pas, combien sont staff/superuser. Me donner la liste des comptes non classables pour validation.
6. Les signaux Django et tâches liées à la suppression d'utilisateurs.

**Livrable de la phase 1** : tableau modèle → catégorie → critère d'identification → effet de suppression → décision proposée (supprimer / conserver / à valider), plus la liste des questions ouvertes. **Arrête-toi là et attends mon accord** avant la phase 2.

## Phase 2 — Conception (livrable : plan, pas de code)

Propose, en suivant les conventions des commandes existantes, une commande `purge_test_data` (ou un nom plus cohérent avec le dépôt) :

- **Simulation par défaut**, sans aucune écriture ; la simulation s'exécute dans une transaction annulée ou en lecture pure, et elle doit échouer bruyamment si elle ne peut pas garantir qu'elle n'écrit pas.
- **Exécution explicite** : option dédiée (`--execute`), puis confirmation par saisie ou jeton imprimé par la simulation (le jeton encode le périmètre : il devient invalide si les données ont changé entre-temps).
- **Garde production** : confirmation supplémentaire, variable d'environnement passée à la commande (`docker compose exec -e …`) et non écrite dans le `.env`, refus si un seul enregistrement du périmètre est ambigu.
- **Catégories activables une à une** (`--categories comptes,quiz,…`), la liste par défaut étant vide ou minimale.
- **Rapport** : par catégorie, nombre ciblé / supprimé / conservé / ignoré, identifiants, erreurs ; sortie lisible et JSON optionnel ; code de sortie 0 (terminé), 1 (échec), 2 (garde refusée / ambiguïté).
- **Transaction unique pour la base** (`transaction.atomic`), fichiers supprimés **après** commit seulement et uniquement s'ils sont exclusifs ; échec ou interruption pendant la suppression de fichiers : la base reste cohérente, les fichiers restants sont listés pour un second passage idempotent.
- **Verrou** contre deux exécutions simultanées, et vérification qu'aucun lot de synchro (`synchro`) n'est en cours.
- **Prérequis de sauvegarde exigés par la commande elle-même** : refuse de s'exécuter sans une sauvegarde `.dump` récente, avec marqueur `.hors-site`, **et** un `test-restauration` réussi sur ce même dump (pas seulement un fichier qui existe).
- Script PowerShell dans le style de `scripts/edukora.ps1` (nouvelle sous-commande plutôt qu'un script isolé) : `purge-simuler`, `purge-sauvegarder`, `purge-executer` (demande une confirmation tapée, jamais de suppression automatique), `purge-verifier`.

**Livrable de la phase 2** : la spec ci-dessus complétée, les fichiers à créer/modifier, la liste des décisions qui me reviennent. **Arrête-toi et attends mon accord** avant la phase 3.

## Phase 3 — Implémentation et tests (seulement après accord)

Tests automatisés dans le style des tests existants (Django `TestCase`, base de test PostgreSQL du conteneur) :

- la simulation ne modifie rien (compare des empreintes de table avant/après, y compris `django_session`) ;
- un compte de test marqué est supprimé avec ses profils et ses données d'usage ; un compte quasi identique mais non marqué (un seul des deux marqueurs) est conservé ;
- les administrateurs et les vrais utilisateurs sont intacts ; les contenus pédagogiques (matières, cours, épreuves, quiz, inédites) sont strictement inchangés (compteurs + empreintes) ;
- un fichier référencé par un contenu conservé n'est pas supprimé, un fichier exclusif l'est, un fichier dans le doute est seulement listé ;
- une erreur injectée au milieu (par exemple un `PROTECT` ou une exception forcée) annule tout : zéro purge partielle ;
- une seconde exécution ne supprime rien de plus (idempotence) ;
- le jeton de confirmation devient invalide si le périmètre change ;
- la commande tourne dans l'image Docker de prod avec la config du dépôt (`docker compose exec`), pas seulement en local.

Exécute la suite complète du backend et dis-moi quels échecs préexistaient (la base de référence connaît des échecs d'environnement : `payments`, `vapid`).

## Livrables finaux

1. Rapport d'analyse (phase 1) tel que validé.
2. Fichiers créés/modifiés, contenu complet, y compris la doc dans `deploy/` (pas de modification de `.env.example`, qui contient de vrais secrets et ne doit jamais être committé).
3. Commandes exactes, dans cet ordre : simuler → sauvegarder → tester la restauration → exécuter → vérifier (compteurs avant/après, contrôle que les contenus et les vrais comptes sont intacts, re-simulation à zéro).
4. Procédure de restauration, testée au moins une fois sur une base jetable avec le résultat réel.
5. Résultats des tests, bruts.
6. Risques résiduels et décisions pour moi, en liste courte.

**Ne committe rien** : montre-moi le diff et attends mon accord. Si tu dois choisir entre « plus sûr » et « plus complet », choisis plus sûr et dis-le.
