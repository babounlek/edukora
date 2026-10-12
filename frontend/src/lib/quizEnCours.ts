import { useAuth } from "@/context/AuthContext"

// Le quiz en cours, retenu sur CET appareil : l'API ne liste pas les séances commencées, et un
// quiz abandonné (onglet fermé, appel reçu, batterie vide) n'était retrouvable depuis nulle part.
// Ce n'est qu'un pointeur : la progression elle-même est enregistrée côté serveur à chaque réponse.
const PREFIXE = "edukora:quiz-en-cours:"
// Au-delà, on suppose la séance abandonnée pour de bon : la proposer encore serait du bruit.
const VALIDITE_MS = 3 * 24 * 60 * 60 * 1000

interface Memo {
  id: number
  date: number
}

/** Clé propre à l'élève actif : un appareil partagé entre frères et sœurs ne doit pas mélanger. */
export function useCleQuizEnCours(): string | null {
  const { user } = useAuth()
  if (!user) return null
  return `${PREFIXE}${user.id}:${user.profil_actif?.id ?? 0}`
}

export function memoriserQuizEnCours(cle: string, id: number) {
  try {
    localStorage.setItem(cle, JSON.stringify({ id, date: Date.now() } satisfies Memo))
  } catch {
    // Stockage indisponible (navigation privée...) : le quiz marche, seule la reprise manque.
  }
}

export function lireQuizEnCours(cle: string): number | null {
  try {
    const brut = localStorage.getItem(cle)
    if (!brut) return null
    const memo = JSON.parse(brut) as Partial<Memo>
    if (typeof memo.id !== "number" || typeof memo.date !== "number" || Date.now() - memo.date > VALIDITE_MS) {
      localStorage.removeItem(cle)
      return null
    }
    return memo.id
  } catch {
    return null
  }
}

/** Sans `id`, oublie quoi qu'il y ait ; avec, seulement si c'est cette séance (un autre onglet a pu en commencer une plus récente). */
export function oublierQuizEnCours(cle: string, id?: number) {
  try {
    if (id !== undefined && lireQuizEnCours(cle) !== id) return
    localStorage.removeItem(cle)
  } catch {
    // rien à faire
  }
}
