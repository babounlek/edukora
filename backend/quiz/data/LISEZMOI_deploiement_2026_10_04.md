# Correctifs de contenu du Mode Quiz, 2026-10-03/04 : déploiement

Le contenu du Mode Quiz vit **en base**, pas dans git. Ces correctifs ont été faits sur la base
locale ; ce dossier permet de les rejouer sur n'importe quelle autre base (production comprise),
de façon sûre et répétable.

## Ce qui est rejoué

| Quoi | Combien | Détail |
|---|---|---|
| Figures ajoutées aux corrigés | 284 items | courbes, constructions, circuits, optique, schémas... (modèle `CompetenceItemFigure`) |
| Énoncés réécrits | 19 items | renvois orphelins (« le montage précédent »...), résultats inchangés |
| Remplacements de texte | 2 | `$24 million` (anglais probatoire E 2004) et `\nu_0` du cours de l'effet photoélectrique |
| Commandes LaTeX restaurées (`\ne`, `\times`...) | ~160 lignes | commande séparée : `reparer_caracteres_controle_maths` |

Les items sont retrouvés par `external_id` (jamais par id). Un item déjà corrigé est ignoré ; un
item modifié à la main depuis est signalé et laissé intact ; un item absent de la base est ignoré
(relancer la commande plus tard s'il arrive après).

## Marche à suivre

À faire depuis le dépôt sur le serveur (`/srv/edukora` sur le Droplet), dans cet ordre.

0. **Sauvegarde** de la base (dump Postgres ou `docker/backup/backup.sh`). Il n'y a pas de commande
   d'annulation : la sauvegarde est le retour arrière.
1. `git pull` : amène le code, le paquet de correctifs (`backend/quiz/data/`) et les 284 images
   WebP (`media/figures/cm/quiz/`).
2. Reconstruire et relancer le backend, puis migrer :
   ```bash
   docker compose build backend && docker compose up -d backend
   docker compose exec backend python manage.py migrate
   ```
   (la migration `quiz.0018_competenceitemfigure` crée la table des figures).
3. **Commandes LaTeX** : simulation puis écriture.
   ```bash
   docker compose exec backend python manage.py reparer_caracteres_controle_maths
   docker compose exec backend python manage.py reparer_caracteres_controle_maths --apply
   ```
4. **Correctifs du quiz** : simulation, lire les compteurs, puis écriture.
   ```bash
   docker compose exec backend python manage.py appliquer_correctifs_quiz_2026_10_04
   docker compose exec backend python manage.py appliquer_correctifs_quiz_2026_10_04 --apply
   ```
5. **Vérification** : relancer les deux simulations, tout doit être « déjà faites » / « 0 ligne ».

L'ordre 3 puis 4 est conseillé mais pas obligatoire : les comparaisons passent par la même
réparation des commandes LaTeX.

## Images en production

Les images sont dans le dépôt (`media/figures/cm/quiz/`). Si le stockage par défaut du serveur est
Spaces (S3), la commande les **téléverse** depuis le dossier du dépôt quand elles manquent dans le
stockage. Par défaut elle lit `MEDIA_ROOT/figures/cm/quiz` ; si ce dossier n'est pas monté dans le
conteneur, indiquer le bon chemin avec `--images-dir`.

## Ce qui a été vérifié

Rejeu complet sur une restauration de la sauvegarde du 2026-10-02 (avant tous ces changements) :
migrations, réparation LaTeX (155 lignes), correctifs (19 réécritures, 251 figures ; 33 items
absents de cette sauvegarde, plus récents, ignorés), puis seconde simulation : tout « déjà fait ».
Comparaison avec la base locale : les 6 453 items de quiz de la sauvegarde sont identiques
(dont les 270 items concernés), 251 figures identiques, 0 différence sur les exercices et les
questions. Les différences restantes sur des cours et des leçons viennent de modifications faites
par ailleurs depuis la sauvegarde (399 cours et 154 leçons modifiés depuis), pas de ces commandes.

## Après coup

- Un item que la figure ou la réécriture ne convient plus : le corrigé d'origine est dans
  `corrige_avant` du paquet (`correctifs_2026_10_04.json`).
- Les sources de génération (scripts matplotlib, PNG, specs) sont dans
  `backend/ingest/_audit/figures_quiz/`, dossier ignoré par git, uniquement sur la machine de
  développement.
