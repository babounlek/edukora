import { useQuery } from "@tanstack/react-query"

import { listEpreuves } from "@/api/endpoints"
import { langueCourante } from "@/lib/i18n"
import { ineditesNouvelles, useIneditesVues } from "@/lib/ineditesVues"

/**
 * Y a-t-il une épreuve inédite plus récente que la dernière que cette personne a regardée ? Partagé par le point or du menu
 * (Header) et la carte « Épreuves » de la page Réviser, qui doivent s'allumer et s'éteindre ensemble.
 *
 * Même clé de cache que CataloguePage ("epreuves-inedites-recente") : un visiteur qui atterrit sur le catalogue puis navigue
 * ailleurs ne repaie pas cette requête dans la fenêtre de staleTime (60 s, voir main.tsx). Seuls le nombre et l'id servent.
 */
export function useNouvellesInedites(country: string) {
  const { data } = useQuery({
    queryKey: ["epreuves-inedites-recente", country, langueCourante()],
    queryFn: ({ signal }) => listEpreuves({ country, origine: "INEDITE", ordering: "recent", langue: langueCourante() }, signal),
    enabled: Boolean(country),
  })
  const vues = useIneditesVues()
  const derniereId = data?.results[0]?.id
  const nouvelles = Boolean(data && data.count > 0) && ineditesNouvelles(derniereId, vues)
  return { derniereId, nouvelles }
}
