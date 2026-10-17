# Mise en ligne du GCE - déroulé

Complète [README-TUNNEL.md](README-TUNNEL.md) (les deux canaux **Deploy** et **Contenu**). Ce document
ne remplace pas ce manuel : il dit **quoi lancer, dans quel ordre**, pour le lot GCE poussé le
2026-10-17 (`origin/main` = `523c56bf`), et ce qu'aucun canal automatique ne fait.

## 0. Avant de commencer

- [ ] **Release** vert sur `523c56bf` (tests + 3 images). Le push l'a déclenché ; rien ne part en prod tout seul.
- [ ] Le clone du Droplet est propre (aucun fichier suivi modifié), voir le manuel.
- [ ] `deploy/diagnostic-serveur.sh` lancé : dit si le contenu GCE existe déjà en prod
      (détermine l'étape 2 : `auto` ou chargement de départ).
- [ ] Décision de vente, **à toi** : les plans GCE sont créés **inactifs** par les migrations
      (`subscriptions 0019`/`0021`). Les activer ouvre une vente réelle (CamPay). Voir l'étape 4.

## 1. Application (Actions > Deploy)

Run workflow, branche `main`, `sha` vide, approuver. `deploy.sh` sauvegarde Postgres, tire les images,
**applique les migrations**, bascule, puis exige que `/healthz` renvoie le SHA déployé (sinon retour
arrière automatique des images).

Migrations qui partent avec ce lot (toutes additives, rétro-compatibles) :

| App | Migration | Effet |
|---|---|---|
| catalog | 0066, 0067 | libellés O/A Level ; 5 matières, `codes_officiels` du Board |
| subscriptions | 0019, 0020, 0021 | plans GCE O Level et A Level, **inactifs** |
| users | 0016, 0017 | `User.langue` ; `Profil.matieres_passees` |
| simulations | 0003 | simulation à la question (Paper 1) : `sous_question`, `reponse_choisie`, marquage |

La route Caddy `/quiz/matieres*` est dans l'image caddy de ce SHA : rien à faire à la main, mais sans ce
déploiement « Mes matières » ne marche pas en ligne.

## 2. Contenu (Actions > Contenu)

1. **Simulation cochée** : relire le plan (dossiers, fichiers) et la liste des fichiers *modifiés*.
2. Simulation décochée. Ordre imposé : programme → corrections → inédites → quiz →
   `valider_ingestion --since` → `indexer_recherche`.
3. Si `diagnostic-serveur.sh` dit que la prod n'a **aucun** contenu GCE : `auto --tout` ou le chargement
   de départ du manuel, pas `auto`.

Ce que le canal **ne fait pas** (et qui n'est pas dans git) :

- Les **416 JSON de quiz** francophones sous `backend/ingest/_quiz/cm/` (suffixes `-fr15`, `-fr23`...)
  sont **non versionnés** : ils n'arriveront jamais en prod tant qu'ils ne sont pas committés. Hors GCE.
- Les ~15 fichiers d'épreuves/cours **modifiés** après ingestion : l'ingestion ignore ce qui existe, un
  JSON modifié n'a aucun effet (le rapport les signale). Hors GCE.
- Les figures sous `media/figures/cm/` nouvelles et non suivies : vérifier qu'elles voyagent par le
  canal média (Spaces) avant de juger une figure manquante.

## 3. Commandes à lancer à la main (SSH, dans le conteneur backend)

À faire **après** l'étape 2 (elles supposent que les épreuves, les cours et les quiz existent). Chacune
est idempotente ; sans `--appliquer`, elle simule.

```bash
# depuis la racine du clone sur le Droplet (le dossier qui contient docker-compose.prod.yml)
# (si COMPOSE_FILE n'est pas posé : docker compose -f docker-compose.yml -f docker-compose.prod.yml exec backend ...)
docker compose exec backend python manage.py definir_papers_vitrine            # simulation : 15 papers attendus
docker compose exec backend python manage.py definir_papers_vitrine --appliquer
docker compose exec backend python manage.py definir_quiz_vitrine --appliquer
docker compose exec backend python manage.py ajouter_rappels_gce               # simulation
docker compose exec backend python manage.py ajouter_rappels_gce --appliquer
docker compose exec backend python manage.py indexer_recherche
```

- `definir_papers_vitrine` : la sélection couvre maintenant les **15** papers gratuits GCE (11 A Level,
  4 O Level). Avant ce lot, seuls 4 existaient dans la commande, les 11 autres n'avaient été posés qu'à la
  main en base locale.
- `definir_quiz_vitrine --appliquer` **aligne** : il décoche aussi ce qui n'est pas dans sa sélection
  (un thème gratuit par matière et par cursus). Relire la simulation avant.
- `ajouter_rappels_gce` se rejoue après toute nouvelle ingestion de cours ou d'épreuves GCE.

## 4. Décisions qui te reviennent

- **Activer les plans GCE** (`GCE O Level - Jusqu'à l'Examen`, `GCE A Level - Jusqu'à l'Examen`, 15 000
  FCFA / 30 j) : admin > Plans, ou
  `docker compose exec backend python manage.py shell -c "from subscriptions.models import Plan; Plan.objects.filter(cursus__examen__in=['GCE_OL','GCE_AL']).update(is_active=True)"`.
  Avant : relire la page Tarifs (elle promet inédites, cours, quiz et thèmes fréquents que le GCE n'a pas
  tous) et le libellé « jours avant ton examen » (le compte va jusqu'à la date de fin).
- **Barème estimé** sur les épreuves dont certains exercices n'ont pas de points lisibles (≈ 430 exercices
  de Paper 2 et 3) : la simulation donne alors le même poids à chaque exercice. Sujet de la suite.

## 5. Vérifier depuis l'extérieur

1. `https://<domaine>/healthz` renvoie le SHA `523c56bf…`.
2. Anonyme : une épreuve gratuite GCE (ex. Physics O Level 2023 - Paper 1) s'ouvre ; un quiz gratuit GCE joue.
3. Connecté (compte de test, voir README-TUNNEL « Données de test ») : onboarding GCE général → étape
   « Quelles matières passes-tu ? » → Passer ; page Mon inscription (`/quiz/matieres/` répond 200, pas 405).
4. Simulation d'un Paper 1 : 50 questions, une réponse part en `POST /simulations/<id>/questions/<id>/repondre/` (200),
   le résultat s'affiche `x / 50` **sans** note sur 20.
5. Simulation d'une épreuve à règle « parmi » (ex. Economics A Level 2023 - Paper 2) : bandeau « traite 2
   exercices parmi 4 », badge « Non compté » au résultat.
6. Recherche : une requête GCE renvoie des résultats (l'index a été reconstruit à l'étape 2).

## Si ça tourne mal

| Symptôme | Action |
|---|---|
| `/healthz` ne répond pas le bon SHA | retour arrière automatique ; lire `docker compose logs backend caddy` |
| Migration en échec | l'application ne bascule pas ; la sauvegarde d'avant déploiement est dans Spaces |
| `definir_papers_vitrine` : « sélection périmée » | un titre n'existe pas ou n'est pas VALIDE en prod : l'étape 2 est incomplète |
| `/quiz/matieres/` répond 405 ou renvoie la SPA | l'image caddy déployée n'est pas celle de ce SHA |
| Simulation d'un Paper 1 en 500 | la migration `simulations 0003` n'est pas appliquée |
