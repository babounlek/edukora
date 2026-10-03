import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'
import { CONTENU_DE_LECTURE } from './src/lib/contenuDeLecture.ts'

// https://vite.dev/config/
export default defineConfig(() => {
  return {
    plugins: [
      react(),
      tailwindcss(),
      // VITE_DISABLE_PWA=1 : interrupteur d'urgence. Le plugin reste déclaré (le module
      // virtuel doit exister) mais ne produit aucun service worker ; lib/pwa.ts désinstalle
      // alors ceux déjà en place chez les visiteurs.
      ...[
            VitePWA({
              disable: process.env.VITE_DISABLE_PWA === "1",
              // « prompt » et non « autoUpdate » : autoUpdate recharge la page dès qu'une
              // nouvelle version est prête, en plein examen chronométré ou au milieu d'un
              // corrigé. Ici l'élève choisit le moment (voir lib/pwa.ts).
              registerType: 'prompt',
              injectRegister: false,
              devOptions: { enabled: false },
              manifest: {
                name: 'EduKora',
                short_name: 'EduKora',
                description: "Révise le BEPC, le Probatoire et le BAC : corrigés d'annales, quiz et séance du jour.",
                lang: 'fr',
                start_url: '/',
                scope: '/',
                display: 'standalone',
                background_color: '#fbfaf8',
                theme_color: '#0a6e4e',
                icons: [
                  { src: '/pwa-192.png', sizes: '192x192', type: 'image/png' },
                  { src: '/pwa-512.png', sizes: '512x512', type: 'image/png' },
                  { src: '/pwa-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
                ],
              },
              workbox: {
                cleanupOutdatedCaches: true,
                // Notifications push : le gestionnaire vit dans public/push-sw.js, importé par le
                // worker généré - on garde ainsi toutes les règles de cache ci-dessous sans
                // passer en worker écrit à la main.
                importScripts: ['/push-sw.js'],
                // Précache : le code de l'app et les polices nécessaires au rendu d'un
                // corrigé (KaTeX, latin). Pas les ~270 drapeaux ni les sous-ensembles de
                // langues étrangères des polices : ils se chargent (et se mettent en cache)
                // à l'usage.
                globPatterns: ['assets/*.{js,css}', 'assets/KaTeX_*.woff2', 'assets/*-latin-*.woff2'],
                // JAMAIS de navigateFallback : il servirait un index.html précaché, donc
                // potentiellement périmé, à un visiteur en ligne. Les navigations passent par
                // le réseau d'abord (règle ci-dessous), le cache ne sert qu'hors connexion.
                navigateFallback: null,
                runtimeCaching: [
                  {
                    urlPattern: ({ request }: { request: Request }) => request.mode === 'navigate',
                    handler: 'NetworkFirst',
                    options: {
                      cacheName: 'coquille-app',
                      networkTimeoutSeconds: 4,
                      // Toutes les routes de l'app partagent le même index.html : hors connexion,
                      // n'importe quelle URL de l'app doit ouvrir la coquille.
                      plugins: [{ cacheKeyWillBeUsed: async () => '/index.html' }],
                    },
                  },
                  {
                    urlPattern: ({ url }: { url: URL }) => CONTENU_DE_LECTURE.test(url.pathname),
                    handler: 'NetworkFirst',
                    options: {
                      cacheName: 'lecture-hors-ligne',
                      networkTimeoutSeconds: 5,
                      expiration: { maxEntries: 120, maxAgeSeconds: 60 * 60 * 24 * 30, purgeOnQuotaError: true },
                      cacheableResponse: { statuses: [200] },
                    },
                  },
                  {
                    urlPattern: ({ url }: { url: URL }) => url.pathname.startsWith('/assets/'),
                    handler: 'CacheFirst',
                    options: {
                      cacheName: 'ressources-app',
                      expiration: { maxEntries: 200, purgeOnQuotaError: true },
                      cacheableResponse: { statuses: [200] },
                    },
                  },
                ],
              },
            }),
          ],
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    build: {
      // Les ~270 drapeaux de flag-icons (chacun sous le seuil d'inlining de 4 Ko de Vite)
      // étaient injectés en base64 DANS la feuille de style : 564 Ko de CSS, bloquants
      // pour le premier rendu de toutes les pages, alors qu'un visiteur n'en affiche
      // qu'un ou deux. Gardés en fichiers, ils ne sont téléchargés qu'à l'affichage.
      assetsInlineLimit: (file: string) => (file.includes("flag-icons") ? false : undefined),
    },
  }
})
