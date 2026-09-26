// Bouchon de « virtual:pwa-register » pour Vitest : ce module virtuel n'existe que dans la
// config de build (VitePWA, voir vite.config.ts), pas dans celle des tests.
export function registerSW() {
  return () => Promise.resolve()
}
