# Candidature des revendeurs — cahier des charges

État : projet, rien n'est codé. Rédigé le 2026-10-27. Remplace la création manuelle des fiches revendeur dans l'admin par un circuit de candidature validé par l'équipe. Suppose que la charte (`CHARTE-REVENDEUR.md`) est relue et figée : sans texte à accepter, la candidature n'a pas de valeur.

## 1. Décisions

- Les futurs revendeurs **candidatent eux-mêmes** ; l'équipe étudie et valide.
- Aucun code ni lien tant que la candidature n'est pas acceptée.
- Le numéro de versement est **vérifié par un code SMS** avant que la candidature soit envoyée.
- Une candidature en cours par compte.
- La candidature est **ouverte** à tout compte connecté (l'équipe trie), avec la possibilité de la restreindre plus tard à des invités. À confirmer : voir § 8.

## 2. Parcours du candidat

1. Il se connecte (ou crée son compte Edukora ordinaire), puis ouvre « Devenir revendeur ».
2. Il remplit : type (commercial, répétiteur, école ou centre), nom affiché, ville, courte présentation (comment il compte trouver des clients), numéro Mobile Money et opérateur de versement. Pour une école ou un centre : nom de l'établissement et fonction du candidat.
3. Il reçoit un code SMS sur le numéro de versement et le saisit.
4. Il lit la charte, coche l'acceptation et envoie.
5. Il suit sa candidature sur une page « Ma candidature » : envoyée, à compléter, acceptée ou refusée, avec le motif.
6. À l'acceptation, il reçoit un SMS ; son espace revendeur apparaît dans « Mon compte ».

## 3. Données

**CandidatureRevendeur**
- `user` (FK), `type`, `nom_affiche`, `ville`, `presentation`, `etablissement` et `fonction` (écoles et centres)
- `operateur_versement`, `numero_versement`, `numero_verifie_le`
- `charte_version`, `charte_acceptee_le`
- `statut` : SOUMISE, A_COMPLETER, ACCEPTEE, REFUSEE, RETIREE
- `motif` (refus ou complément demandé, montré au candidat), `notes_internes`
- `etudiee_par`, `etudiee_le`, `revendeur` (fiche créée à l'acceptation)
- dates de création et de mise à jour

Contrainte : au plus une candidature SOUMISE ou A_COMPLETER par compte. Un refus peut être rouvert par l'équipe, ou par une nouvelle candidature après [30] jours.

**Revendeur** : ajout de `charte_version` à côté de `contrat_accepte_le` (déjà présent), repris de la candidature.

## 4. Règles

- **Code SMS de vérification** : limité en essais et en durée, sur le modèle des codes OTP existants. Une candidature sans numéro vérifié ne peut pas être envoyée.
- **Acceptation par l'équipe** : crée la fiche `Revendeur` (statut ACTIF, code saisi par l'équipe, taux de base 14 %, palier de commercial à la création, numéro de versement repris de la candidature), reprend la version de charte et la date d'acceptation, passe la candidature à ACCEPTEE et envoie le SMS. Le code est unique et ne doit pas être égal à un code de parrainage (règle existante).
- **Refus** : motif obligatoire, montré au candidat, SMS envoyé.
- **Complément demandé** : le candidat voit la question, corrige et renvoie.
- **Un compte déjà revendeur** ne peut pas candidater à nouveau.
- Un candidat ne peut pas se rattacher lui-même à un revendeur par sa candidature, ni utiliser un code avant acceptation.
- **Anti-abus** : un numéro de versement déjà utilisé par un autre revendeur ou une autre candidature est signalé à l'équipe (pas refusé automatiquement) ; plafond de candidatures par compte et par jour.

## 5. Interfaces

- **Site** : page « Devenir revendeur » (formulaire + vérification SMS + charte), page « Ma candidature » (état, motif, bouton « compléter » ou « retirer »). Lien depuis la page de compte et depuis une page publique de présentation du programme [texte à écrire].
- **Admin** : liste des candidatures avec filtres par statut et type, vue détail, actions « Accepter », « Refuser » (motif), « Demander un complément » (motif). Compte des candidatures en attente visible depuis l'accueil de l'admin.
- **SMS** : candidature reçue, complément demandé, acceptée, refusée. Les textes passent par le système de SMS existant, en français et en anglais selon la langue du compte.

## 6. API (aperçu)

- `GET/POST /revendeurs/candidature/` : lire la sienne, la créer ou la mettre à jour (tant qu'elle est ouverte).
- `POST /revendeurs/candidature/verifier-numero/` et `.../envoyer-code/` : code SMS du numéro de versement.
- `POST /revendeurs/candidature/retirer/`.
- Pas d'endpoint d'acceptation : la décision se prend dans l'admin.

## 7. Tests à écrire

Parcours complet (envoi du code, vérification, soumission, acceptation → fiche créée et SMS) ; numéro non vérifié refusé ; une seule candidature ouverte ; refus avec motif ; complément puis renvoi ; compte déjà revendeur ; code de revendeur égal à un code de parrainage refusé ; numéro de versement déjà utilisé signalé ; plafond de candidatures ; un candidat ne voit que sa candidature ; textes SMS FR/EN.

## 8. Phasage et points ouverts

| Phase | Contenu | Taille |
|---|---|---|
| 0 (sans code) | Charte et contrat relus par un juriste, texte de la page de présentation | S |
| 1 | Modèle, vérification du numéro, soumission, admin (accepter, refuser, compléter), SMS | M |
| 2 | Pages du site (formulaire, « Ma candidature », lien depuis le compte), FR/EN | M |
| 3 | Restriction éventuelle aux invités, relances automatiques des dossiers en attente | S |

Points ouverts :
1. **Candidature ouverte ou sur invitation ?** Ouverte amène plus de candidats mais plus de dossiers à trier. Recommandation : ouverte au début, avec un plafond de candidatures par jour.
2. **Pièces justificatives** (pièce d'identité, justificatif d'établissement pour une école) : à demander ou non, ce qui implique de stocker des documents personnels. Recommandation : ne rien stocker au début et vérifier par appel téléphonique.
3. **Délai de réponse annoncé** au candidat.
4. **Qui étudie** : une personne de l'équipe, avec quelles consignes de décision (grille de critères à écrire).

## 9. Réalisation (2026-10-27)

**Fait, non committé.** Modèle `CandidatureRevendeur` (migration `revendeurs/0003_candidatures`, plus `Revendeur.charte_version`), services dans `backend/revendeurs/candidatures.py`, API `/revendeurs/candidature/` (+ `envoyer-code/`, `verifier-numero/`, `soumettre/`, `retirer/`), admin « Candidatures de revendeur » (actions Accepter, Refuser, Demander un complément), page `/devenir-revendeur` (en anglais `/en/become-a-reseller`) avec le texte de la charte en FR/EN, carte « Devenir revendeur » dans « Mon compte » pour qui n'est pas revendeur.

**Choix d'implémentation.** Le brouillon est enregistré côté serveur (statut BROUILLON) : la vérification du numéro et l'envoi portent sur ce qui est enregistré. Le code SMS réutilise le service de connexion (délai entre deux envois, plafond par IP, plafond global, 5 essais). Le code revendeur est proposé à l'envoi (lettres du nom + 2 chiffres) et modifiable par l'équipe avant l'acceptation. Refuser ou demander un complément : saisir le motif dans la fiche, enregistrer, puis lancer l'action depuis la liste. Un candidat refusé peut redéposer après 30 jours.

**Écarts avec le § 4.** Pas de plafond de candidatures par jour : une seule candidature ouverte par compte et 30 jours après un refus suffisent, et l'envoi du code a déjà ses plafonds. La charte affichée est un résumé en dix rubriques (version 0.1) ; le contrat signé prévaut. **Quand `CHARTE_VERSION` change, le texte du front (`charte.*`) doit être relu.**
