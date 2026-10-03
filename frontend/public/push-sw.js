// Notifications push : chargé par le service worker généré (voir importScripts dans
// vite.config.ts), qui garde la mise en cache hors connexion. Ce fichier ne fait que deux choses -
// afficher le message reçu et ouvrir l'application au bon endroit au clic.

self.addEventListener("push", (event) => {
  let donnees = {}
  try {
    donnees = event.data ? event.data.json() : {}
  } catch {
    donnees = { body: event.data ? event.data.text() : "" }
  }
  event.waitUntil(
    self.registration.showNotification(donnees.title || "EduKora", {
      body: donnees.body || "",
      icon: "/pwa-192.png",
      badge: "/pwa-192.png",
      // Même tag : un rappel qui arrive remplace celui d'hier resté dans le tiroir au lieu de
      // s'empiler.
      tag: donnees.tag || "edukora",
      data: { url: donnees.url || "/" },
    }),
  )
})

self.addEventListener("notificationclick", (event) => {
  event.notification.close()
  // Jamais une adresse hors du site : le message est signé par notre serveur, mais l'ouverture
  // d'une URL reste la partie qu'on veut impossible à détourner.
  let cible = new URL("/", self.location.origin)
  try {
    const demandee = new URL((event.notification.data && event.notification.data.url) || "/", self.location.origin)
    if (demandee.origin === self.location.origin) cible = demandee
  } catch {
    // URL illisible : l'accueil.
  }
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((fenetres) => {
      for (const fenetre of fenetres) {
        if (fenetre.url.startsWith(self.location.origin) && "focus" in fenetre) {
          return fenetre.focus().then((f) => (f && "navigate" in f ? f.navigate(cible.href) : undefined))
        }
      }
      return self.clients.openWindow(cible.href)
    }),
  )
})
