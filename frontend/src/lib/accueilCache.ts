import type { Accueil } from "@/api/types"

/**
 * La dernière version connue de l'accueil, gardée dans le navigateur pour que la page
 * s'affiche AVANT la réponse du serveur - et hors connexion.
 *
 * Sur un téléphone d'entrée de gamme en 3G, l'appel unique (voir getAccueil) prend
 * une à trois secondes : sans ce cache, l'élève regarde un squelette à chaque
 * ouverture. Avec, il voit sa page d'hier tout de suite, et elle se met à jour
 * silencieusement quand la réponse arrive (TanStack Query : initialData +
 * initialDataUpdatedAt, la donnée est aussitôt jugée périmée et refetchée).
 *
 * Par élève ET par cursus : un compte partagé entre deux frères ne doit jamais montrer
 * l'accueil de l'autre. Et jamais plus vieux que quelques jours : un accueil de la
 * semaine dernière dirait des choses fausses ("Séance faite") le temps du chargement.
 */
const CLE = "edukora:accueil:v1"
const AGE_MAX_MS = 3 * 24 * 3600 * 1000

interface Entree {
  userId: number
  cursusId: number
  date: number
  data: Accueil
}

export function lireAccueilEnCache(userId: number, cursusId: number): { data: Accueil; date: number } | null {
  try {
    const brut = localStorage.getItem(CLE)
    if (!brut) return null
    const entree = JSON.parse(brut) as Entree
    if (entree.userId !== userId || entree.cursusId !== cursusId) return null
    if (Date.now() - entree.date > AGE_MAX_MS) return null
    if (!entree.data || typeof entree.data !== "object" || !("plan" in entree.data)) return null
    return { data: entree.data, date: entree.date }
  } catch {
    return null
  }
}

export function ecrireAccueilEnCache(userId: number, cursusId: number, data: Accueil) {
  try {
    const entree: Entree = { userId, cursusId, date: Date.now(), data }
    localStorage.setItem(CLE, JSON.stringify(entree))
  } catch {
    // Stockage plein ou navigation privée : la page marche sans, juste moins vite.
  }
}

export function oublierAccueilEnCache() {
  try {
    localStorage.removeItem(CLE)
  } catch {
    // Rien à faire.
  }
}
