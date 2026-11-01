/**
 * Ce que Kora (la mascotte) retient de l'élève : le résultat du dernier quiz et le jour où elle l'a vu. Gardé dans le
 * navigateur seulement (aucun appel réseau, rien côté serveur) : « content de te revoir », « mieux que la dernière fois ».
 * Par appareil et non par compte : sur un appareil partagé, elle peut parler du quiz d'un autre - sans conséquence, la
 * phrase ne cite jamais de nom ni de matière. Un stockage indisponible (navigation privée) la rend simplement sans mémoire.
 */

const CLE_MEMOIRE = "edukora:mascotte-memoire"
const CLE_PRESENTEE = "edukora:mascotte-presentee"

const JOUR_MS = 24 * 3600 * 1000

export interface SouvenirMascotte {
  /** Résultat du dernier quiz vu, en pourcentage. */
  pourcentage: number
  /** Jours écoulés depuis (0 = aujourd'hui). */
  jours: number
}

export function lireSouvenir(maintenant = Date.now()): SouvenirMascotte | null {
  try {
    const brut = localStorage.getItem(CLE_MEMOIRE)
    if (!brut) return null
    const { pourcentage, date } = JSON.parse(brut) as { pourcentage?: unknown; date?: unknown }
    if (typeof pourcentage !== "number" || typeof date !== "number") return null
    return { pourcentage, jours: Math.max(0, Math.floor((maintenant - date) / JOUR_MS)) }
  } catch {
    return null
  }
}

export function memoriserSouvenir(pourcentage: number, maintenant = Date.now()): void {
  try {
    localStorage.setItem(CLE_MEMOIRE, JSON.stringify({ pourcentage, date: maintenant }))
  } catch {
    /* stockage indisponible : elle ne se souviendra pas, le quiz marche */
  }
}

/** Vrai tant que Kora ne s'est pas encore présentée à ce navigateur (une seule fois). */
export function pasEncorePresentee(): boolean {
  try {
    return localStorage.getItem(CLE_PRESENTEE) === null
  } catch {
    return false
  }
}

export function memoriserPresentee(): void {
  try {
    localStorage.setItem(CLE_PRESENTEE, "1")
  } catch {
    /* stockage indisponible : pas de présentation répétée à chaque fois, voir pasEncorePresentee */
  }
}
