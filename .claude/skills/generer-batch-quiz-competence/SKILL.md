---
name: generer-batch-quiz-competence
description: Génère et ingère un lot de contenu CompetenceItem pour le Mode Quiz d'edukora, à partir des épreuves déjà corrigées par correction-experte. Tâche déclenchée à la demande (pas de planification cron). À utiliser quand l'utilisateur demande de lancer/générer un batch de quiz, de peupler le quiz pour un pays donné, ou référence explicitement cette tâche ("lance le batch quiz pour cm", "génère un lot de quiz", "peuple le quiz à partir des épreuves déjà corrigées").
---

# Génération d'un batch de quiz par compétence

Orchestration en 4 étapes. Traite jusqu'à 5 compétences sous-couvertes par exécution
(volume choisi délibérément prudent - voir NFR) : à relancer plusieurs fois pour
converger vers une couverture complète, jamais en une seule passe géante.

## Prérequis

- **Code déployé** : ce pipeline (`quiz.CompetenceItem`, `quiz.ingestion`,
  `select_quiz_batch`, `ingest_quiz_content`) doit être présent sur l'image du
  conteneur `edukora-backend-1` en cours d'exécution - le code n'est PAS bind-monté
  (voir `docker/backend/Dockerfile`), donc un simple `git pull` sur l'hôte ne suffit
  pas. Déploiement : push sur la branche cible, puis déclenchement manuel du workflow
  GitHub Actions "Deploy" (`.github/workflows/deploy.yml`, jamais automatique -
  CamPay traite de vrais paiements en production sur cette même machine). Si une
  commande ci-dessous échoue avec "Unknown command", c'est probablement que ce
  déploiement n'a pas encore eu lieu.
- **Skill `concepteur-quiz-competence` installé** (voir son fichier `.skill`/`.md` -
  bouton "Save skill").

## Étape 1 - Sélection des compétences sous-couvertes (déterministe, pas de LLM)

```bash
docker exec edukora-backend-1 python manage.py select_quiz_batch --pays cm --limit 5 --floor 6 --output /app/ingest/_quiz/_batch_cm.json
```

Produit un tableau JSON de jusqu'à 5 requêtes de génération (une par compétence sous
le plancher de couverture), chacune avec son matériel de référence déjà réuni depuis
les `Question` déjà validées de ce pays (voir `quiz.management.commands.select_quiz_batch`
- pure requête DB, aucun jugement éditorial à ce stade).

Si le tableau est vide (avertissement stderr), tout est déjà couvert pour ce pays au
plancher demandé - rien à faire, s'arrêter ici.

## Étape 2 - Génération (skill concepteur-quiz-competence)

Lire le fichier produit à l'étape 1 (`backend/ingest/_quiz/_batch_cm.json` côté
hôte). Pour CHAQUE requête du tableau, suivre le skill `concepteur-quiz-competence`
pour produire son propre tableau JSON de `CompetenceItem`. Écrire le résultat de
chaque requête dans son propre fichier :

```
backend/ingest/_quiz/<pays>/<competence_slug>.json
```

(`competence_slug` dérivé du champ `competence` de la requête : minuscules, accents
supprimés, espaces remplacés par des tirets - même convention que `external_id` dans
le skill).

Traiter les requêtes une par une, jamais toutes en un seul message au skill : chaque
génération applique une vérification rigoureuse par item (résolution indépendante ou
contrôle structurel/factuel selon la matière - voir la section "Rigueur" du skill),
pas un traitement en lot superficiel qui la court-circuiterait.

## Étape 3 - Ingestion

```bash
docker exec edukora-backend-1 python manage.py ingest_quiz_content /app/ingest/_quiz/cm
```

Les items entrent `statut=VALIDE` et sont immédiatement servables en Quiz (voir
`quiz.ingestion.ingest_competence_item`) - aucune étape de relecture humaine
supplémentaire dans ce pipeline.

## Étape 4 - Rapport

Résumer pour l'utilisateur : compétences traitées, items créés, erreurs éventuelles
(fichier + détail). Ne jamais passer sous silence une erreur d'ingestion, même si le
reste du lot a réussi.

## NFR à respecter

- **Accès DB uniquement via `docker exec` dans `edukora-backend-1`** - jamais depuis
  un venv hôte nu (`DB_HOST=db` injoignable depuis l'hôte, le port Postgres n'est pas
  publié).
- **Portée bornée** : jamais plus de `--limit 5` compétences par exécution (coût/temps
  maîtrisés - un lot de 4 items vérifiés sérieusement a déjà pris ~270s/~72k tokens
  lors des tests du skill).
- **Aucune relecture humaine avant publication** (`statut=VALIDE` immédiat, décision
  explicite de l'utilisateur) : la rigueur du skill est la seule garantie avant qu'un
  élève ne voie ce contenu - ne jamais sauter son étape de vérification finale pour
  aller plus vite.
- **Environnement de production réelle** (edukora.africa, paiements CamPay réels) -
  pas de bac à sable distinct identifié dans ce projet, chaque exécution touche les
  données réelles.
- **Déclenchement à la demande uniquement** - pas de planification cron pour cette
  tâche (choix explicite de l'utilisateur, 2026-08-02).
