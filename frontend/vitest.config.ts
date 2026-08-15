import path from "path"
import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"

// Config Vitest séparée de vite.config.ts plutôt que fusionnée : ce dernier embarque
// VitePWA (génération de service worker/manifest à la construction), qui n'a rien à
// faire tourner dans un environnement de test jsdom - seuls le plugin React (JSX) et
// l'alias @ sont réellement nécessaires ici.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    globals: true,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
