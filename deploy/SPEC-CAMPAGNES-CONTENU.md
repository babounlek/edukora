# Cahier des charges : campagnes de contenu (quiz, cours) par la chaîne de lots

Date : 2026-10-26. Statut : **proposition, rien n'est codé.** Complète [SPEC-SYNC-CONTENU.md](SPEC-SYNC-CONTENU.md) ;
ne la remplace pas.

## 0. Correction de ce que j'ai dit plus tôt

J'avais annoncé qu'il fallait « ajouter une opération de mise à jour gardée » et « vérifier le retrait de cours ».
**Après lecture du code, c'est déjà fait** :

| Besoin des campagnes | Déjà dans la chaîne | Où |
|---|---|---|
| Mettre à jour sur place un item de quiz (QCM, choix, corrigé) | oui, `mettre_a_jour_item`, ne touche ni `statut` ni `est_vitrine` | `quiz/ingestion.py`, `QuizAdaptateur` |
| Garde « le contenu en prod est bien celui que je crois » | oui, `empreinte_etat` + `adoption_a_confirmer` + `empreinte_etat_prod_vue` | SPEC §2 et §6 |
| Retirer un cours (REJETE), par clé naturelle, même jamais journalisé | oui, opération `retirer` + `--confirme-retraits` | `_traiter_statut`, `CoursAdaptateur` |
| Réindexer la recherche et les fréquences après un lot | oui, `post_traiter` | `moteur.py` |
| Aucune suppression physique | oui, test T6 | SPEC §6 |

Donc **mes deux scripts de cette semaine étaient redondants avec la chaîne**, sauf sur les points du §2 ci-dessous. Et
l'inquiétude sur les collisions d'`external_id` est sans objet côté chaîne : la base impose déjà l'unicité globale
(`unique_competenceitem_external_id_when_set`). Le piège est en amont, dans la génération des identifiants (`cqc-<thème>-<difficulté>-<n>`).

## 1. Principe directeur

**Une campagne est un producteur de fichiers d'ingestion, pas un script qui écrit en base.** La chaîne part des JSON de
`backend/ingest/` : tout ce qui n'y figure pas ne peut pas être livré. Mes scripts de la semaine ont écrit en base locale
sans toucher aux JSON ; le lot aurait donc été vide.

Conséquence : chaque campagne suit toujours les mêmes six étapes.

1. **Produire** : le générateur écrit ou corrige les JSON d'ingestion (items de quiz, cours), jamais la base.
2. **Contrôler** (automatique, local) : forme, rendu KaTeX avec le vrai moteur, recalculs numériques.
3. **Relire** (indépendant) : rapport du relecteur aveugle, versé au lot.
4. **Ingérer en local** et passer le tunnel de validation existant.
5. **Préparer un lot** (`edukora.ps1 prepare`), l'approuver (`-Approuver`), simuler côté serveur.
6. **Appliquer**, puis vérifier les compteurs attendus.

L'humain décide aux étapes 3 (seuil de relecture), 5 (approbation) et 6 (`-Appliquer`). Rien d'autre n'est manuel.

## 2. Ce qui manque réellement (par priorité)

### E1. Relecture aveugle comme pièce du lot, condition d'approbation
`validation.relecture_humaine` existe dans le manifeste mais `outil_lot.py` l'écrit toujours à `non_requise`
(lignes 411 et 425). À faire :
- un fichier `relecture-<campagne>.json` par campagne : pour chaque contenu, `verdict` (`accord` | `desaccord`), `relecteur`, `date`, `empreinte_source` relue ;
- `prepare` met `relecture_humaine: faite` si le verdict existe **pour l'empreinte exacte** du fichier ; `a_faire` sinon ; `desaccord` bloque ;
- un contenu modifié après relecture repasse en `a_faire` (l'empreinte ne correspond plus) ;
- seuil par campagne, dans le manifeste de campagne : relecture de **100 %** pour une campagne neuve, échantillon réduit seulement après deux campagnes sans désaccord.

Pourquoi en premier : sur mes 26 premiers QCM, le relecteur a trouvé 3 défauts réels. Sans cette condition, l'automatisation industrialise les erreurs.

### E2. Écrire les corrections dans les JSON, pas seulement en base
Le générateur de campagne (aujourd'hui `genere_qcm.py` + `appliquer_qcm.py`) doit :
- partir du JSON d'ingestion existant de l'item (retrouvé par `external_id`) ;
- le réécrire (type, choix, clé, corrigé) en conservant tous les autres champs ;
- consigner l'empreinte de l'**original** dans `originaux.json` (déjà fait par `appliquer_qcm.py`), ce qui devient `version_reference` du lot.

`appliquer_qcm.py` devient un outil de diagnostic local, plus un outil de livraison.

### E3. Garde « élèves en cours » avant retrait ou changement de type
La chaîne n'avertit pas quand un cours à retirer a des lectures en cours (`LectureProgress`) ni quand un item a des
`QuizQuestion` en session non terminée. À faire dans `planifier` (pas dans `appliquer`) :
- champ `donnees_eleves` dans le détail de l'opération : nombre de lectures en cours, de sessions de quiz non terminées, de `GainXP` rattachés ;
- **avertissement** (pas un blocage) dans le rapport de simulation ; blocage seulement si la campagne le demande (`bloquer_si_eleves_en_cours`).

Le retrait par REJETE ne détruit rien ; il faut seulement que l'humain voie l'impact avant d'approuver.

### E4. Vérifications d'après, déclarées par la campagne
`post_traiter` réindexe mais ne vérifie rien. Le manifeste de campagne déclare des **attendus** :
`{"qcm_apres": 25, "cours_rejetes": 6, "inchanges": 0}` ; `appliquer` les compare au résultat réel et passe en
`reussi_avec_avertissements` si l'écart est non nul, avec la liste des contenus « ignorés » et leur raison
(empreinte divergente, conflit, objet absent). C'est ce qui rend lisible le fait qu'un tiers du corpus historique diverge.

### E5. Manifeste de campagne (nouveau fichier, petit)
`campagnes/<nom>.json`, versionné :

```json
{
  "nom": "b1-qcm-maths-bepc-lot2",
  "type": "conversion_qcm | creation_quiz | creation_cours | retrait_cours",
  "perimetre": {"pays": "cm", "matiere": "mathematiques", "cursus": "bepc", "themes": ["..."]},
  "generateur": {"skill": "concepteur-quiz-competence", "version": "..."},
  "relecture": {"taux": 1.0, "rapport": "relecture-b1-lot2.json"},
  "attendus": {"qcm_apres": 25},
  "bloquer_si_eleves_en_cours": false
}
```

Il sert à `prepare` (E1), à `appliquer` (E4) et à garder une trace de ce qui a été fait, pourquoi, par qui.

### E6. Commande unique `edukora.ps1 campagne <nom>`
Enchaîne les étapes 2 à 5 et **s'arrête** avant l'application. Affiche le rapport de simulation en clair (créations, mises à jour,
sans effet, ignorés + raisons, élèves concernés). L'application reste `publish -Appliquer`. Pas de planification automatique
de l'application, jamais.

## 3. Ce qu'on n'automatise pas

- **L'application en production** : toujours un geste explicite. Un QCM à clé fausse punit un élève qui a raison.
- **La génération planifiée** (cron) : possible plus tard pour le brouillon seul, pas tant que le coût en jetons (~5 000 par question) n'est pas arbitré par budget de campagne.
- **La suppression** : interdite par la chaîne, le reste.

## 4. Prérequis avant la première vraie campagne par la chaîne

Rien de ce qui précède n'a tourné contre le vrai serveur. Dans l'ordre :

1. Installer la clé SSH dédiée `edukora_lots_ed25519` côté serveur et créer les dossiers de lots.
2. Mettre le serveur au niveau de `main` (aujourd'hui `7c4234fb`, la chaîne `synchro` n'y existe peut-être pas : à vérifier avec `diagnostic-serveur.sh`).
3. Régler la sauvegarde hors site (Spaces en 403) : l'état d'avant est aujourd'hui la seule protection.
4. Faire passer la CI au vert, ou documenter pourquoi elle est rouge.
5. **Lot d'épreuve de la chaîne** : rejouer les 25 QCM déjà en prod. Résultat attendu : 25 `noop`. Ça prouve l'idempotence et la lecture de l'état réel sans rien risquer.
6. Lot réel minuscule : retrait des 6 cours dupliqués (déjà prêt, `docs-relecture/b6-retrait/retraits.json` à convertir au format `retraits` de la chaîne). Ça prouve `retirer` + `--confirme-retraits` + réindexation.

## 5. Ordre de réalisation proposé et taille

| # | Travail | Taille | Dépend de |
|---|---|---|---|
| 1 | E5 manifeste de campagne + E1 relecture comme condition | moyenne | rien |
| 2 | E3 garde élèves en cours + E4 attendus | petite à moyenne | 1 |
| 3 | E2 réécriture des JSON (générateur de conversion) | moyenne | 1 |
| 4 | E6 commande `campagne` | petite | 1-3 |
| 5 | Prérequis §4 (étapes 1-4), puis lots d'épreuve 5 et 6 | côté serveur, votre main | rien, à lancer en parallèle |

Tests d'acceptation à ajouter (même style que SPEC §12) :
- C1 : relecture manquante, périmée ou en désaccord ⇒ `prepare` refuse l'archive.
- C2 : lot identique rejoué ⇒ 100 % `noop`.
- C3 : retrait d'un cours avec lecture en cours ⇒ avertissement dans la simulation, aucun effacement.
- C4 : attendus non atteints ⇒ `reussi_avec_avertissements` avec la liste des ignorés.
- C5 : la campagne n'écrit aucun fichier hors `backend/ingest/` et `campagnes/`.

## 6. Décisions à prendre

1. Valider le principe du §1 (les campagnes produisent des JSON, la chaîne seule livre).
2. Seuil de relecture : 100 % pour toute campagne neuve (recommandé).
3. Les campagnes ont-elles le droit de **bloquer** sur élèves en cours, ou seulement avertir (recommandé : avertir).
4. Quelle campagne sert de premier cas réel après les lots d'épreuve : extension B1 (maths BEPC) ou retrait des cours dupliqués (déjà prêt).

## 7. Réalisé (2026-10-26)

| Point | État | Où |
|---|---|---|
| E1 relecture obligatoire (`prepare -Campagne`) | fait, commité a2f6cb9c | `outil_lot.py`, `test_outil_lot.py` (CampagneTests) |
| E3 données d'élèves dans la simulation (`donnees_eleves` : lectures d'un cours, sessions de quiz) ; blocage optionnel `bloquer_si_eleves_en_cours`, décidé **avant** toute écriture | fait | `moteur.py` (`donnees_eleves`, `_traiter`), `test_moteur.py` (CampagneMoteurTests) |
| E4 attendus : `campagne.attendus` = `{résultat: nombre}` (ex. `{"mis_a_jour": 25}`), écarts ⇒ `reussi_avec_avertissements`, liste des contenus non appliqués avec raison dans `rapport.attendus` | fait | `moteur.py` (`_bilan_attendus`) |
| E2 réécriture des JSON : `outil_lot.py reecrire-quiz` (simulation par défaut, `--appliquer`), garde par empreinte (énoncé + corrigé) des versions relues, idempotent | fait ; **essayé en simulation sur les 25 propositions B1 et les JSON réels : 25/25 correspondent** | `outil_lot.py` (`cmd_reecrire_quiz`), `test_outil_lot.py` (ReecritureQuizTests) |
| E5 manifeste de campagne | champs lus : `nom`, `type`, `relecture{taux,rapport}`, `attendus`, `bloquer_si_eleves_en_cours`, `conversion{propositions,originaux}` | `campagnes/<nom>.json` (aucun fichier de campagne créé pour l'instant) |
| E6 `edukora.ps1 campagne -Campagne … [-Reecrire]` | fait pour `conversion_qcm` ; **syntaxe vérifiée, non exécuté** (pas de Python sur le poste Windows) ; s'arrête avant toute préparation de lot | `scripts/edukora.ps1` |

Limites connues :
- `reecrire-quiz` réécrit tout le fichier JSON touché avec une indentation de 2 : le diff git contient des changements d'espaces (l'empreinte de la chaîne est canonique, donc sans effet sur le lot).
- La commande `campagne` ne gère pas encore les types `creation_quiz`, `creation_cours`, `retrait_cours` (ces derniers passent par `prepare -Retraits`).
- Les `LectureProgress` comptent les profils ayant **ouvert** un cours, pas des lectures « en cours » : le chiffre est un ordre de grandeur de l'impact, pas un blocage utile par défaut.
