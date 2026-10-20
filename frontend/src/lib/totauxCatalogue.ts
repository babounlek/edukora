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

/**
 * `cursus` : seulement pour un élève abonné qui regarde son propre examen (voir useCursusAbonne). Sa liste est réduite à
 * son examen ET à ses matières par le serveur : annoncer le total de la langue (512 épreuves) à côté d'une liste de 96 et de
 * « tes 6 matières » était faux (test élève Gogo, GCE O Level). Un visiteur garde le total du pays dans la langue : c'est
 * ce qui lui montre l'étendue du catalogue.
 */

/** Paramètres de l'API pour le total d'épreuves du pays (annales et inédites fusionnées). */
export function paramsTotalEpreuves(country: string | undefined, langue: Langue | undefined, cursus?: number | null) {
  return cursus ? { country, langue, cursus } : { country, langue }
}

/** Paramètres de l'API pour le total de cours du pays. */
export function paramsTotalCours(country: string | undefined, langue: Langue | undefined, cursus?: number | null) {
  return cursus ? { country, langue, cursus } : { country, langue }
}

/** L'examen à compter : celui de l'élève abonné quand c'est bien celui qu'il regarde, sinon aucun (total du pays). */
export function cursusDesTotaux(cursusAbonne: number | null, cursusRegarde: number | undefined): number | null {
  return cursusAbonne !== null && cursusRegarde === cursusAbonne ? cursusAbonne : null
}

export function useTotalEpreuves(country: string | undefined, langue: Langue | undefined, enabled = true, cursus?: number | null) {
  return useQuery({
    queryKey: cursus ? ["epreuves-total", country, langue ?? "toutes", cursus] : ["epreuves-total", country, langue ?? "toutes"],
    queryFn: ({ signal }) => listEpreuves(paramsTotalEpreuves(country, langue, cursus), signal),
    enabled: Boolean(country) && enabled,
  })
}

export function useTotalCours(country: string | undefined, langue: Langue | undefined, enabled = true, cursus?: number | null) {
  return useQuery({
    queryKey: cursus ? ["cours-total", country, langue ?? "toutes", cursus] : ["cours-total", country, langue ?? "toutes"],
    queryFn: ({ signal }) => listCours(paramsTotalCours(country, langue, cursus), signal),
    enabled: Boolean(country) && enabled,
  })
}
