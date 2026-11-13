import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"

import { refaireErreurs } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { t } from "@/lib/i18n"

/** La clé de cache de la banque d'erreurs d'un cursus (page « Mes erreurs », carte de Ma progression). */
export const cleErreurs = (cursusId: number | null | undefined) => ["erreurs", cursusId] as const

export interface EchecRefaire {
  message: string
  /** Le serveur a répondu « abonnement requis » : l'écran propose alors les prix, pas un nouvel essai. */
  abonnement: boolean
}

/**
 * « Refaire mes erreurs » : ouvre un quiz fait des erreurs les plus anciennes (voir quiz.erreurs côté
 * serveur) et y conduit. Un seul lancement à la fois : `enCours` vaut "tout", ou l'identifiant de la
 * matière visée, pour que seul le bouton touché montre « Préparation… ».
 *
 * Partagé par la page, la ligne de l'accueil et la carte de Ma progression : le même geste, la même
 * erreur dite de la même façon.
 */
export function useRefaireErreurs(cursusId: number | null | undefined) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [enCours, setEnCours] = useState<number | "tout" | null>(null)
  const [echec, setEchec] = useState<EchecRefaire | null>(null)

  async function lancer(subjectId?: number) {
    if (enCours !== null || !cursusId) return
    setEnCours(subjectId ?? "tout")
    setEchec(null)
    try {
      const session = await refaireErreurs({ cursus: cursusId, ...(subjectId !== undefined && { subject: subjectId }) })
      // La banque va changer au fil des réponses : la relire au retour, pas la servir du cache.
      queryClient.invalidateQueries({ queryKey: ["erreurs"] })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      const api = err instanceof ApiError ? err : null
      setEchec({ message: api?.message ?? t("erreurs.err_lancer"), abonnement: api?.status === 403 })
      setEnCours(null)
    }
  }

  return { lancer, enCours, echec }
}
