import { useQuery } from "@tanstack/react-query"

import { getPaymentConfig } from "@/api/endpoints"
import type { PaymentConfig } from "@/api/types"

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
export function usePaymentConfig(): {
  campayActif: boolean
  /** Le paiement manuel est-il proposé ? (backend : MANUAL_PAYMENT_ACTIVE ; actif par défaut). */
  manuelActif: boolean
  pret: boolean
  /** À qui part un transfert manuel (nom et opérateur). Vide si le serveur ne le dit pas. */
  beneficiaires: NonNullable<PaymentConfig["beneficiaires"]>
  /** Un code peut partir par SMS. Faux sans réponse : on ne met jamais en avant une méthode qui ne marcherait pas. */
  smsActif: boolean
} {
  const { data, isPending } = useQuery({
    queryKey: PAYMENT_CONFIG_KEY,
    queryFn: getPaymentConfig,
    staleTime: 60_000,
    retry: false,
  })
  return {
    campayActif: data?.campay_active ?? true,
    manuelActif: data?.manual_active ?? true,
    pret: !isPending,
    beneficiaires: data?.beneficiaires ?? [],
    smsActif: data?.sms_active ?? false,
  }
}
