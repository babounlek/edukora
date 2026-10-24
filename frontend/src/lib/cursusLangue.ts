import { useEffect, useRef } from "react"
import { useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"

import { listCursus } from "@/api/endpoints"
import type { Cursus } from "@/api/types"
import { PARAM_TOUTES_LANGUES } from "@/lib/discipline"
import { langueCourante, type Langue } from "@/lib/i18n"

/**
 * Les examens proposés suivent la langue de l'interface, comme les matières, les épreuves et les cours : en anglais
 * le GCE seul, en français BEPC, Probatoire et BAC. Sans cela, un élève en anglais cliquait « BAC » et tombait sur une
 * liste entièrement française (un examen choisi prime sur la langue des listes).
 *
 * Deux exceptions, pour ne jamais retirer à l'élève l'examen qu'il a choisi :
 *  - l'examen déjà sélectionné (lien partagé `?cursus=12`, pastille cliquée) reste proposé, et les pastilles prennent
 *    alors SA langue (jamais BEPC et GCE ensemble : voir langueDuChoix) ;
 *  - « Toutes les langues » (`langue` indéfinie) lève le filtre.
 * L'examen déclaré sur le compte, lui, ne reste pas proposé hors de sa langue : il polluait les pastilles de l'autre
 * langue (un « Probatoire C » parmi celles du GCE). Il ne pré-filtre pas non plus (voir useFiltreCursusParDefaut).
 * Les pages de paiement et de compte ne passent pas par ici : un élève francophone doit pouvoir s'abonner au BAC
 * quelle que soit la langue de son interface.
 */

type IdCursus = number | string | null | undefined

/** Examens de `langue` ; `langue` indéfinie = tous. Les ids de `garder` sont conservés quelle que soit leur langue. */
export function cursusDeLangue(liste: Cursus[], langue: Langue | undefined, garder: IdCursus[] = []): Cursus[] {
  if (!langue) return liste
  const gardes = new Set(garder.filter((id) => id != null && id !== "").map(String))
  return liste.filter((c) => estDeLangue(c, langue) || gardes.has(String(c.id)))
}

/** L'examen est-il de cette langue ? Sans information de langue (ancienne réponse en cache), on le garde. */
export function estDeLangue(cursus: Pick<Cursus, "langue"> | null | undefined, langue: Langue | undefined): boolean {
  return !langue || !cursus?.langue || cursus.langue === langue
}

/**
 * La liste des examens du pays, déjà réduite à la langue demandée. Même clé de cache que partout (`["cursus", pays]`) :
 * la réduction se fait côté client, sur douze lignes, car les exceptions ci-dessus demandent la liste complète.
 * `tous` : la liste complète, pour retrouver un examen hors langue (examen déclaré, lien partagé).
 */
export function useCursusListe(
  country: string | undefined,
  options: { langue: Langue | undefined; garder?: IdCursus[]; enabled?: boolean },
) {
  const requete = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
    enabled: Boolean(country) && (options.enabled ?? true),
  })
  const tous = requete.data ?? []
  return { ...requete, data: cursusDeLangue(tous, langueDuChoix(tous, options.langue, options.garder), options.garder), tous }
}

/**
 * La langue des pastilles d'examen. Un examen choisi dans l'autre langue que l'interface fixe la langue de la liste
 * (comme il fixe celle des matières et des épreuves) : sans cela, « BEPC » restait proposé au milieu des « GCE » et
 * l'élève voyait les deux univers mélangés. Pour changer d'univers, « Tous » retire le choix et ramène la langue de
 * l'interface.
 */
export function langueDuChoix(liste: Cursus[], langue: Langue | undefined, choisis: IdCursus[] = []): Langue | undefined {
  if (!langue) return undefined
  const ids = new Set(choisis.filter((id) => id != null && id !== "").map(String))
  const choisi = liste.find((c) => ids.has(String(c.id)) && c.langue)
  return (choisi?.langue as Langue | undefined) ?? langue
}

/**
 * Au CHANGEMENT de langue, abandonne l'examen de l'URL s'il est de l'autre langue : sinon la page resterait sur une
 * liste de l'autre langue sous une interface traduite. Jamais à l'arrivée : un lien partagé `?cursus=12` ouvert dans
 * l'autre langue doit continuer à fonctionner. `cursus` seul est retiré (sans `tout=1`) : si l'examen déclaré est de
 * la nouvelle langue, le pré-filtrage par défaut le remet, ce qui est voulu (voir useFiltreCursusParDefaut).
 * « Toutes les langues » désactive ce retrait.
 */
export function useAbandonCursusHorsLangue(country: string | undefined) {
  const [params, setParams] = useSearchParams()
  const { tous } = useCursusListe(country, { langue: undefined })
  const langue = langueCourante()
  const precedente = useRef(langue)
  const aVerifier = useRef(false)
  const cursusDansUrl = params.get("cursus")
  const toutesLangues = params.get(PARAM_TOUTES_LANGUES) === "toutes"

  useEffect(() => {
    if (precedente.current !== langue) {
      precedente.current = langue
      aVerifier.current = true
    }
    if (!aVerifier.current || tous.length === 0) return
    aVerifier.current = false
    if (!cursusDansUrl || toutesLangues) return
    const cursus = tous.find((c) => String(c.id) === cursusDansUrl)
    if (!cursus || estDeLangue(cursus, langue)) return
    setParams(
      (prev) => {
        const suivant = new URLSearchParams(prev)
        suivant.delete("cursus")
        return suivant
      },
      { replace: true },
    )
  }, [langue, tous, cursusDansUrl, toutesLangues, setParams])
}
