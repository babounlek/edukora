import { useQuery } from "@tanstack/react-query"

import { listQuizEnCours } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"

// Les quiz commencés et pas terminés viennent du SERVEUR (voir quiz.historique.en_cours côté backend) :
// la progression y est enregistrée à chaque réponse, donc la reprise marche depuis n'importe quel
// appareil et ne dépend plus d'un pointeur gardé dans le navigateur. Ce module ne retient sur CET
// appareil qu'une chose : les quiz que l'élève a demandé à ne plus se voir proposer.
const PREFIXE = "edukora:quiz-ignores:"

/** Clé propre à l'élève actif : un appareil partagé entre frères et sœurs ne doit pas mélanger. */
export function useCleQuizEnCours(): string | null {
  const { user } = useAuth()
  if (!user) return null
  return `${PREFIXE}${user.id}:${user.profil_actif?.id ?? 0}`
}

/** Les tentatives interrompues du profil actif, la dernière réponse en tête. */
export function useQuizEnCours() {
  const { user } = useAuth()
  return useQuery({
    queryKey: ["quiz-en-cours", user?.profil_actif?.id ?? null],
    queryFn: ({ signal }) => listQuizEnCours(signal),
    enabled: Boolean(user),
    // Une séance finie dans un autre onglet ne doit plus être proposée.
    staleTime: 0,
    retry: false,
  })
}

export function lireQuizIgnores(cle: string): number[] {
  try {
    const brut = JSON.parse(localStorage.getItem(cle) ?? "[]")
    return Array.isArray(brut) ? brut.filter((id): id is number => typeof id === "number") : []
  } catch {
    return []
  }
}

export function ignorerQuiz(cle: string, id: number) {
  try {
    // Les 50 derniers suffisent : une séance plus ancienne n'est de toute façon plus proposée.
    localStorage.setItem(cle, JSON.stringify([...lireQuizIgnores(cle).filter((i) => i !== id), id].slice(-50)))
  } catch {
    // Stockage indisponible (navigation privée...) : le quiz sera reproposé, rien de grave.
  }
}
