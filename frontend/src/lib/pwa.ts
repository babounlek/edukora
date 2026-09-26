import { useSyncExternalStore } from "react"
import { toast } from "sonner"

import { API_BASE_URL } from "@/api/client"
import { getCours, getEpreuve, readCours, readEpreuve } from "@/api/endpoints"

/** Cache Workbox des réponses d'API de lecture - même nom que dans vite.config.ts. */
export const CACHE_LECTURE = "lecture-hors-ligne"

export type TypeContenu = "epreuve" | "cours"

/** Chemins d'API qu'un lecteur charge pour afficher ce contenu (voir EpreuveReaderPage et
 * CoursReaderPage) : c'est très exactement ce qu'il faut avoir en cache pour le relire. */
function cheminsDeLecture(type: TypeContenu, slug: string): string[] {
  return type === "epreuve"
    ? [`/catalog/lessons/${slug}/`, `/access/read/${slug}/`]
    : [`/catalog/cours/${slug}/`, `/access/cours/read/${slug}/`]
}

/**
 * Le service worker est un plus, jamais un prérequis : sans lui (navigateur ancien,
 * mode économie de données, interrupteur VITE_DISABLE_PWA=1 au build, serveur de dev),
 * l'app se comporte exactement comme avant. Dans ces cas on désinstalle ce qui traîne :
 * un ancien worker resterait sinon actif indéfiniment sans qu'aucune nouvelle version
 * puisse le remplacer (incident qui avait fait retirer la PWA une première fois).
 */
function nettoyerLesAnciensWorkers() {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    registrations.forEach((registration) => registration.unregister())
  })
  caches?.keys().then((keys) => keys.forEach((key) => caches.delete(key)))
}

export function initialiserPwa() {
  if (!("serviceWorker" in navigator)) return
  const connexion = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection
  if (import.meta.env.DEV || import.meta.env.VITE_DISABLE_PWA === "1" || connexion?.saveData) {
    nettoyerLesAnciensWorkers()
    return
  }

  // Après le chargement complet : les ~2 Mo de précache ne doivent jamais concurrencer le
  // premier affichage sur une connexion lente.
  window.addEventListener("load", async () => {
    const { registerSW } = await import("virtual:pwa-register")
    const mettreAJour = registerSW({
      onNeedRefresh() {
        // Une action, pas un rechargement automatique : la mise à jour ne doit jamais
        // couper un examen chronométré ou une lecture en cours.
        toast("Nouvelle version disponible", {
          id: "maj-app",
          description: "Mets à jour quand tu n'es pas en pleine épreuve.",
          duration: Infinity,
          action: { label: "Mettre à jour", onClick: () => mettreAJour(true) },
        })
      },
      onOfflineReady() {
        toast.success("Prêt pour la lecture hors connexion", {
          id: "hors-ligne-pret",
          description: "Les épreuves et cours que tu as lus restent disponibles sans réseau.",
        })
      },
    })
  })
}

function abonnerEnLigne(rappel: () => void) {
  window.addEventListener("online", rappel)
  window.addEventListener("offline", rappel)
  return () => {
    window.removeEventListener("online", rappel)
    window.removeEventListener("offline", rappel)
  }
}

export function useEnLigne(): boolean {
  return useSyncExternalStore(abonnerEnLigne, () => navigator.onLine, () => true)
}

/** À appeler à la déconnexion : sur un téléphone partagé, un corrigé lu hors connexion ne
 * doit pas rester lisible pour le compte suivant. */
export async function viderCacheHorsLigne() {
  try {
    await caches?.delete(CACHE_LECTURE)
  } catch {
    // Cache API absente ou refusée : rien à vider.
  }
}

/** Ce contenu est-il déjà lisible sans réseau ? */
export async function estDisponibleHorsLigne(type: TypeContenu, slug: string): Promise<boolean> {
  try {
    if (!("caches" in window)) return false
    const cache = await caches.open(CACHE_LECTURE)
    const trouves = await Promise.all(
      cheminsDeLecture(type, slug).map((chemin) => cache.match(`${API_BASE_URL}${chemin}`)),
    )
    return trouves.every(Boolean)
  } catch {
    return false
  }
}

/** Charge maintenant ce que le lecteur demandera : le service worker garde chaque réponse
 * au passage. Lecture = téléchargement ; ce geste sert à préparer un trajet sans réseau
 * sans avoir à ouvrir chaque document. */
export async function telechargerPourLireHorsLigne(type: TypeContenu, slug: string) {
  if (type === "epreuve") await Promise.all([getEpreuve(slug), readEpreuve(slug)])
  else await Promise.all([getCours(slug), readCours(slug)])
}
