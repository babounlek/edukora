import path from "path"
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "")
  const apiBaseUrl = env.VITE_API_BASE_URL ?? "http://localhost:8001"
  const siteName = env.VITE_SITE_NAME ?? "EduKamer"

  return {
    plugins: [
      react(),
      tailwindcss(),
      VitePWA({
        registerType: "autoUpdate",
        devOptions: { enabled: true, type: "module" },
        manifest: {
          name: siteName,
          short_name: siteName,
          description: "Corrigés d'annales, sujets et cours pour le BEPC, le Probatoire et le BAC au Cameroun.",
          lang: "fr",
          theme_color: "#0a6e4e",
          background_color: "#0c5f3a",
          display: "standalone",
          start_url: "/",
          icons: [
            { src: "/pwa-192.png", sizes: "192x192", type: "image/png" },
            { src: "/pwa-512.png", sizes: "512x512", type: "image/png" },
            { src: "/pwa-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
          ],
        },
        workbox: {
          // Une leçon/cours déjà consulté (lecture ou aperçu) reste disponible hors
          // connexion : NetworkFirst privilégie la version à jour quand le réseau
          // répond, et retombe sur le cache seulement si l'élève n'a plus de données -
          // le vrai frein identifié pour l'usage au Cameroun, pas une synchronisation
          // complète hors-ligne (hors de proportion pour cette taille d'app).
          runtimeCaching: [
            {
              urlPattern: new RegExp(
                `^${escapeRegExp(apiBaseUrl)}/(access/(read|preview|cours/read|cours/preview)/|catalog/(lessons|cours)/)`,
              ),
              handler: "NetworkFirst",
              options: {
                cacheName: "edukamer-content",
                expiration: { maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 * 30 },
                cacheableResponse: { statuses: [0, 200] },
              },
            },
          ],
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
