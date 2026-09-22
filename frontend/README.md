# EduKamer — Frontend

Interface web et application progressive (PWA) d'**EduKamer**, une plateforme de préparation aux examens du secondaire. Elle donne accès à des annales corrigées, des cours, des fiches de révision, des quiz et des épreuves inédites.

Le frontend est une SPA React reliée à l'API Django présente dans le dossier [`../backend`](../backend). Il est conçu pour rester utile sur une connexion instable : les contenus déjà consultés peuvent être relus hors connexion.

## Fonctionnalités

- Catalogue d'annales, cours et fiches, organisés par pays, niveau, série et matière.
- Lecteur de corrigés avec prise en charge du Markdown et des formules mathématiques KaTeX.
- Quiz, suivi de progression, abonnement et espace personnel.
- Connexion par identifiants ou Google lorsque cette option est configurée.
- Installation comme application sur mobile ou ordinateur grâce à la PWA.
- Cache hors ligne des contenus et figures déjà ouverts.

## Technologies

- React 19 et TypeScript
- Vite 8
- React Router et TanStack Query
- Tailwind CSS 4 et Radix UI
- Vitest et Testing Library
- Vite PWA / Workbox

## Prérequis

- Node.js 20 ou une version plus récente
- npm 10 ou une version plus récente
- Une API EduKamer en cours d'exécution (voir [`../backend`](../backend))

## Démarrage rapide

Depuis ce dossier :

```bash
npm ci
npm run dev
```

Vite affiche ensuite l'adresse locale de l'application, généralement `http://localhost:5173`.

Par défaut, le frontend appelle l'API sur `http://localhost:8001`. Lancez le backend dans un autre terminal :

```bash
cd ../backend
python manage.py runserver 8001
```

## Configuration

Créez un fichier `frontend/.env.local` pour les variables propres à votre poste :

```dotenv
# Adresse de l'API Django utilisée en développement
VITE_API_BASE_URL=http://localhost:8001

# Optionnelles
VITE_SITE_NAME=EduKamer
VITE_SITE_URL=http://localhost:5173
VITE_GOOGLE_CLIENT_ID=
VITE_SENTRY_DSN=
```

Les variables commençant par `VITE_` sont intégrées au bundle au moment de la compilation : n'y placez jamais de secret. La configuration complète de l'environnement, notamment celle du backend et de Docker, est documentée dans [`../.env.example`](../.env.example).

Si le frontend et le backend ne sont pas servis depuis la même origine, ajoutez l'URL du frontend à `CORS_ALLOWED_ORIGINS` côté backend.

## Scripts disponibles

| Commande | Rôle |
| --- | --- |
| `npm run dev` | Lance le serveur de développement avec rechargement à chaud. |
| `npm run build` | Vérifie TypeScript puis génère le bundle de production dans `dist/`. |
| `npm run preview` | Sert localement le dernier bundle de production. |
| `npm run lint` | Analyse le code avec Oxlint. |
| `npm test` | Lance la suite de tests Vitest. |

## Développement avec Docker

Pour démarrer l'ensemble de la plateforme (PostgreSQL, API, frontend et proxy Caddy), exécutez depuis la racine du dépôt :

```bash
docker compose up --build
```

Copiez d'abord `.env.example` vers `.env` et renseignez les valeurs nécessaires. Les étapes de déploiement sur DigitalOcean sont détaillées dans [`../deploy/README.md`](../deploy/README.md).

## Structure du code

```text
src/
├── api/          # Client HTTP, types et points d'entrée de l'API
├── components/   # Composants réutilisables de l'interface
├── lib/          # Utilitaires, configuration et logique partagée
├── pages/        # Pages associées aux routes de l'application
├── test/         # Configuration et utilitaires de test
├── App.tsx       # Routes et structure principale
└── main.tsx      # Point d'entrée et initialisation de la PWA
```

## Qualité et contribution

Avant de proposer une modification, vérifiez au minimum :

```bash
npm run lint
npm test
npm run build
```

Gardez les interfaces accessibles, testez les parcours importants sur mobile et évitez d'introduire des secrets dans les fichiers suivis par Git.

## Ressources associées

- [Backend Django](../backend)
- [Configuration d'environnement](../.env.example)
- [Guide de déploiement](../deploy/README.md)
