import { useQuery } from "@tanstack/react-query"

import { listQuizEnCours } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { useEssaiSansCompte } from "@/lib/useEssaiSansCompte"

// Les quiz commencés et pas terminés viennent du SERVEUR (voir quiz.historique.en_cours côté backend) :
// la progression y est enregistrée à chaque réponse, donc la reprise marche depuis n'importe quel
// appareil et ne dépend plus d'un pointeur gardé dans le navigateur. Ce module ne retient sur CET
// appareil qu'une chose : les quiz que l'élève a demandé à ne plus se voir proposer.
const PREFIXE = "edukora:quiz-ignores:"

/** Clé propre à l'élève actif : un appareil partagé entre frères et sœurs ne doit pas mélanger. Un visiteur qui joue avec un
 * compte invité (voir lib/invite.ts) a la sienne : ses quiz se reprennent aussi. */
export function useCleQuizEnCours(): string | null {
  const { user } = useAuth()
  const invite = useEssaiSansCompte()
  if (!user) return invite ? `${PREFIXE}invite` : null
  return `${PREFIXE}${user.id}:${user.profil_actif?.id ?? 0}`
}

/**
 * Sur l'accueil, la liste des quiz en cours arrive dans la réponse de l'accueil (voir AccueilEleve) : pendant ce
 * délai, la carte « Quiz en cours » et le bouton « Quiz express » s'en contentent au lieu de la redemander.
 */
export const FRAICHEUR_ACCUEIL_MS = 30_000

/** Clé de cache des quiz en cours d'un profil : la même pour la route seule et pour l'accueil, qui la remplit. */
export function cleQuizEnCours(profilId: number | "invite" | null) {
  return ["quiz-en-cours", profilId] as const
}

/**
 * Les tentatives interrompues du profil actif (ou de l'invité), la dernière réponse en tête.
 *
 * `fraicheurMs` : l'accueil d'un abonné reçoit cette liste dans sa propre réponse et la dépose dans ce cache (voir
 * AccueilEleve). Il passe quelques secondes ici pour que la carte s'en serve sans refaire la requête ; partout
 * ailleurs la liste est relue à chaque montage, comme avant.
 */
export function useQuizEnCours({ fraicheurMs = 0 }: { fraicheurMs?: number } = {}) {
  const { user } = useAuth()
  const invite = useEssaiSansCompte()
  return useQuery({
    queryKey: cleQuizEnCours(user?.profil_actif?.id ?? (invite ? "invite" : null)),
    queryFn: ({ signal }) => listQuizEnCours(signal),
    enabled: Boolean(user) || invite,
    // Une séance finie dans un autre onglet ne doit plus être proposée.
    staleTime: fraicheurMs,
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
