import { useQuery } from "@tanstack/react-query"

import { listCours, listEpreuves } from "@/api/endpoints"
import type { Langue } from "@/lib/i18n"

/**
 * Totaux annoncés par les puces des pages d'accueil, des épreuves et des cours : UN seul périmètre
 * (pays + langue, publié seulement), le même que celui des listes vers lesquelles elles mènent. Une puce « N cours »
 * doit mener à une liste qui affiche N : la compter ailleurs (autre langue, autre pays) la rend fausse dès le clic.
 *
 * `langue` : celle que la page envoie à sa propre liste (voir discipline.langueDeListe) ; `undefined` = toutes.
 * Les deux hooks partagent leur clé de cache avec les trois pages, donc un aller-retour ne repaie pas la requête.
 */

/** Paramètres de l'API pour le total d'épreuves du pays (annales et inédites fusionnées). */
export function paramsTotalEpreuves(country: string | undefined, langue: Langue | undefined) {
  return { country, langue }
}

/** Paramètres de l'API pour le total de cours du pays. */
export function paramsTotalCours(country: string | undefined, langue: Langue | undefined) {
  return { country, langue }
}

export function useTotalEpreuves(country: string | undefined, langue: Langue | undefined, enabled = true) {
  return useQuery({
    queryKey: ["epreuves-total", country, langue ?? "toutes"],
    queryFn: ({ signal }) => listEpreuves(paramsTotalEpreuves(country, langue), signal),
    enabled: Boolean(country) && enabled,
  })
}

export function useTotalCours(country: string | undefined, langue: Langue | undefined, enabled = true) {
  return useQuery({
    queryKey: ["cours-total", country, langue ?? "toutes"],
    queryFn: ({ signal }) => listCours(paramsTotalCours(country, langue), signal),
    enabled: Boolean(country) && enabled,
  })
}
