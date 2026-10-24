import { useEffect } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"

import { getAccessToken } from "@/api/client"
import { getQuotaPdf } from "@/api/endpoints"
import { EVENEMENT_QUOTA_PDF } from "@/lib/quotaPdf"

const CLE = "quota-pdf"
// Au plus un jour : après, le quota est de toute façon remis à zéro et la page est rechargée par l'élève.
const ATTENTE_MAX_MS = 24 * 3600 * 1000

/**
 * Le quota de téléchargements PDF du moment, lu sur le serveur (jamais calculé ici) : visiteur anonyme compris.
 * `doc` : le document de la page (`cours:<slug>`, `lesson:<id>`, `inedit:<id>`, `quiz:<id>:sujet`, `fiche:<id>:corrige`)
 * pour savoir s'il est déjà téléchargé aujourd'hui, donc gratuit à nouveau.
 *
 * Se met à jour tout seul : après chaque téléchargement (signalerChangementQuota), au retour sur l'onglet, et à
 * l'heure de remise à zéro. En cas d'erreur réseau, `data` reste vide : les boutons restent utilisables, le serveur
 * décide - on n'affiche jamais un faux compteur.
 */
export function useQuotaPdf(doc?: string) {
  const queryClient = useQueryClient()
  const connecte = Boolean(getAccessToken())
  const requete = useQuery({
    queryKey: [CLE, doc ?? "", connecte],
    // Un compteur introuvable (réseau coupé, serveur lent) n'est pas une erreur à montrer : on n'affiche rien.
    queryFn: async ({ signal }) => {
      try {
        return await getQuotaPdf(doc ? [doc] : [], signal)
      } catch {
        return null
      }
    },
    staleTime: 30_000,
    refetchOnWindowFocus: true,
    retry: false,
  })

  useEffect(() => {
    const rafraichir = () => void queryClient.invalidateQueries({ queryKey: [CLE] })
    window.addEventListener(EVENEMENT_QUOTA_PDF, rafraichir)
    return () => window.removeEventListener(EVENEMENT_QUOTA_PDF, rafraichir)
  }, [queryClient])

  const reinitialisation = requete.data?.reinitialisation
  useEffect(() => {
    if (!reinitialisation) return
    const attente = new Date(reinitialisation).getTime() - Date.now()
    if (!(attente > 0)) return
    const minuteur = window.setTimeout(
      () => void queryClient.invalidateQueries({ queryKey: [CLE] }),
      Math.min(attente + 1000, ATTENTE_MAX_MS),
    )
    return () => window.clearTimeout(minuteur)
  }, [reinitialisation, queryClient])

  return requete.data && requete.data.actif ? requete.data : null
}
