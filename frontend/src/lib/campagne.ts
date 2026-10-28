import { useQuery } from "@tanstack/react-query"

import { getCampagneEnCours } from "@/api/endpoints"
import type { CampagneEnCours } from "@/api/types"
import { localeCourante, t, tn } from "@/lib/i18n"

export const CAMPAGNE_KEY = ["campagne-en-cours"] as const

/**
 * La campagne promotionnelle ouverte (voir subscriptions.models.Campagne), ou null. Sert aux
 * écrans qui affichent un prix sans avoir chargé de plan (accueil, accès refusé, bandeau de
 * /tarifs) ; là où un plan est chargé, `plan.campagne` / `plan.prix_reference` suffisent.
 *
 * Une erreur réseau donne null : sans campagne affichée on montre le prix normal, jamais un
 * prix promotionnel dont on ne serait pas sûr. Le serveur reste seul juge du montant facturé.
 * Une campagne dont la date limite est passée sur l'horloge de l'appareil n'est plus montrée
 * (page restée ouverte), sans attendre le prochain rafraîchissement.
 */
export function useCampagne(): CampagneEnCours | null {
  const { data } = useQuery({
    queryKey: CAMPAGNE_KEY,
    queryFn: () => getCampagneEnCours(),
    staleTime: 60_000,
    retry: false,
  })
  if (!data || new Date(data.fin).getTime() <= Date.now()) return null
  return data
}

/** « 11 novembre » dans la langue courante. */
export function dateLimiteCampagne(fin: string): string {
  return new Date(fin).toLocaleDateString(localeCourante(), { day: "numeric", month: "long" })
}

/**
 * Urgence honnête, seulement quand elle est vraie : « Plus que 3 jours » dans la dernière semaine,
 * « Dernier jour » le dernier. Rien avant - un compte à rebours permanent n'inciterait à rien.
 */
export function urgenceCampagne(fin: string, maintenant = Date.now()): string | null {
  const restant = new Date(fin).getTime() - maintenant
  if (restant <= 0) return null
  const jours = Math.ceil(restant / 86_400_000)
  if (jours > 7) return null
  return jours <= 1 ? t("camp.dernier_jour") : tn("camp.jours_restants", jours)
}
