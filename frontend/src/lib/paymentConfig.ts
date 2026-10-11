import { useQuery } from "@tanstack/react-query"

import { getPaymentConfig } from "@/api/endpoints"

export const PAYMENT_CONFIG_KEY = ["payment-config"] as const

/**
 * Le paiement automatique Campay est-il ouvert ? (backend : CAMPAY_ACTIVE, lu à
 * l'exécution - une bascule ne demande donc aucun rebuild du frontend).
 *
 * `pret` est faux tant que la réponse n'est pas arrivée : les écrans qui changent de
 * forme selon l'état attendent ce signal plutôt que d'afficher Campay une demi-seconde
 * avant de le retirer. En cas d'erreur réseau on retombe sur « actif » (comportement
 * historique) - le backend refuse de toute façon une demande Campay quand il est coupé.
 */
export function usePaymentConfig(): { campayActif: boolean; pret: boolean } {
  const { data, isPending } = useQuery({
    queryKey: PAYMENT_CONFIG_KEY,
    queryFn: getPaymentConfig,
    staleTime: 60_000,
    retry: false,
  })
  return { campayActif: data?.campay_active ?? true, pret: !isPending }
}
