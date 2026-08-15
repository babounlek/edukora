import path from "path"
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Le nom affiché doit rester le même que celui résolu à l'exécution par
  // lib/site.ts (VITE_SITE_NAME) - un manifest PWA figé sur "EduKamer" en dur
  // désynchroniserait le nom de l'icône installée du nom affiché partout ailleurs
  // dans l'app dès que VITE_SITE_NAME change. loadEnv (pas import.meta.env,
  // indisponible ici : ce fichier tourne côté Node, pas dans le bundle Vite) lit le
  // même .env que le reste du build.
  const env = loadEnv(mode, process.cwd(), "VITE_")
  const siteName = env.VITE_SITE_NAME || "EduKamer"

  return {
    plugins: [
      react(),
      tailwindcss(),
      VitePWA({
        registerType: "autoUpdate",
        // Injection du <script> d'enregistrement désactivée : enregistré à la main
        // dans main.tsx (voir virtual:pwa-register), pour rester cohérent avec le
        // reste du bootstrap de l'app qui est déjà explicite plutôt qu'auto-injecté
        // (voir main.tsx, captureReferralCode()).
        injectRegister: false,
        manifest: {
          lang: "fr",
          name: `${siteName} - Corrigés, cours et quiz`,
          short_name: siteName,
          description:
            "Corrigés d'annales, sujets et cours pour le BEPC, le Probatoire et le BAC, rédigés par des enseignants.",
          // Même teinte que <meta name="theme-color"> dans index.html et --primary
          // dans index.css (mode clair) - la couleur de la barre de statut/de
          // l'écran de démarrage doit correspondre à l'identité visuelle déjà en
          // place, pas une valeur PWA à part.
          theme_color: "#0a6e4e",
          background_color: "#0a6e4e",
          display: "standalone",
          start_url: "/",
          icons: [
            { src: "/pwa-192.png", sizes: "192x192", type: "image/png" },
            { src: "/pwa-512.png", sizes: "512x512", type: "image/png" },
            { src: "/pwa-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
          ],
        },
        workbox: {
          // Fallback SPA hors ligne : une navigation vers une route jamais visitée
          // pendant que l'appareil est hors ligne charge quand même la coquille de
          // l'app (déjà précachée par Workbox) plutôt que l'écran "Sans connexion"
          // natif du navigateur - React Router prend ensuite le relais, la page se
          // rend avec les données déjà en cache si elles y sont (voir
          // runtimeCaching ci-dessous), sinon avec ses propres états de chargement.
          navigateFallback: "/index.html",
          // Bug réel constaté en prod après rebuild : sans exclusion, Workbox
          // applique navigateFallback à TOUTE navigation dans le scope du service
          // worker (tout le domaine, voir manifest.scope="/") - y compris /admin/
          // (Django) et un PDF de sujet ouvert en navigation directe
          // (/media/sujets_pdf/...), tous deux servis index.html au lieu du contenu
          // réel. Cette liste doit rester le miroir exact de ce que le Caddyfile
          // route déjà vers autre chose que le frontend (voir docker/caddy/Caddyfile :
          // le matcher @backend pour /admin, /auth, /catalog, /subscriptions,
          // /payments, /access, /quiz/sessions, /sitemap*, plus /static/* et
          // /media/* servis directement par Caddy) - si un nouveau préfixe backend
          // est ajouté côté Caddyfile, il doit être ajouté ici aussi.
          navigateFallbackDenylist: [
            /^\/admin/,
            /^\/auth/,
            /^\/catalog/,
            /^\/subscriptions/,
            /^\/payments/,
            /^\/access/,
            /^\/quiz\/sessions/,
            /^\/sitemap/,
            /^\/static/,
            /^\/media/,
          ],
          runtimeCaching: [
            {
              // Contenu déjà lu (corrigé/cours) : StaleWhileRevalidate - sert
              // instantanément depuis le cache (fonctionne hors ligne) tout en
              // revalidant en arrière-plan si la connexion est là. C'est le cas
              // d'usage central de cette PWA pour ce public précis (réviser dans le
              // bus/en zone peu couverte) : un contenu ouvert une fois en ligne
              // reste consultable ensuite sans connexion.
              urlPattern: ({ url }) =>
                url.pathname.startsWith("/access/read/") || url.pathname.startsWith("/access/cours/read/"),
              handler: "StaleWhileRevalidate",
              options: {
                cacheName: "edukamer-content",
                expiration: { maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 * 30 },
              },
            },
            {
              // Catalogue/fiches/sujets publics (jamais réservé aux abonnés) : même
              // stratégie, pour que la navigation dans le catalogue reste fluide sur
              // une connexion instable plutôt que de dépendre de sa qualité du moment.
              urlPattern: ({ url }) =>
                url.pathname.startsWith("/catalog/") || url.pathname.startsWith("/access/preview/"),
              handler: "StaleWhileRevalidate",
              options: {
                cacheName: "edukamer-catalogue",
                expiration: { maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 * 7 },
              },
            },
            {
              // Figures (graphiques, schémas, tableaux scannés) : CacheFirst - une
              // fois uploadée, une figure ne change jamais (voir catalog.ingestion,
              // aucune mise à jour en place), donc revalider en arrière-plan n'a
              // aucune valeur ici, contrairement au texte du corrigé.
              urlPattern: ({ url }) => url.pathname.startsWith("/media/figures/"),
              handler: "CacheFirst",
              options: {
                cacheName: "edukamer-figures",
                expiration: { maxEntries: 300, maxAgeSeconds: 60 * 60 * 24 * 90 },
              },
            },
          ],
        },
        devOptions: {
          // Utile pour vérifier le SW en `npm run dev` sans passer par un build de
          // prod à chaque fois - Workbox reste en mode "dev" (pas de precache réel).
          enabled: true,
        },
      }),
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
  }
})
