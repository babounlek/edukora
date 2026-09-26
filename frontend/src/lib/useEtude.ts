import { useCallback, useMemo } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { getMarquesEtude, saveMarqueEtude } from "@/api/endpoints"
import type { CibleEtude, MarqueEtude } from "@/api/types"

type Patch = Partial<Pick<MarqueEtude, "compris" | "signet" | "note">>

/**
 * Les marques d'étude (compris / signet / note) de l'élève sur UN document, avec une
 * mise à jour optimiste : cocher "j'ai compris" doit répondre sur-le-champ, pas après un
 * aller-retour réseau. En cas d'échec, on revient à l'état d'avant plutôt que de laisser
 * croire à un enregistrement (même règle que ValiderResolution dans EpreuveReaderPage).
 *
 * `actif` faux (visiteur anonyme sur un contenu vitrine) : aucune requête, aucune marque
 * - le lecteur n'affiche alors simplement pas la barre d'outils d'étude.
 */
export function useEtude(cible: CibleEtude | null, actif: boolean) {
  const queryClient = useQueryClient()
  const cle = useMemo(() => ["etude", cible?.type, cible?.slug], [cible?.type, cible?.slug])

  const { data } = useQuery({
    queryKey: cle,
    queryFn: ({ signal }) => getMarquesEtude(cible as CibleEtude, signal),
    enabled: actif && cible !== null,
    retry: false,
  })

  const mutation = useMutation({
    mutationFn: ({ section, patch }: { section: string; patch: Patch }) =>
      saveMarqueEtude(cible as CibleEtude, section, patch),
    onMutate: async ({ section, patch }) => {
      await queryClient.cancelQueries({ queryKey: cle })
      const avant = queryClient.getQueryData<MarqueEtude[]>(cle) ?? []
      const existante = avant.find((m) => m.cle === section)
      const fusionnee: MarqueEtude = {
        cle: section, compris: false, signet: false, note: "", updated_at: null, ...existante, ...patch,
      }
      const vide = !fusionnee.compris && !fusionnee.signet && !fusionnee.note.trim()
      queryClient.setQueryData<MarqueEtude[]>(
        cle,
        vide ? avant.filter((m) => m.cle !== section) : [...avant.filter((m) => m.cle !== section), fusionnee],
      )
      return { avant }
    },
    onError: (_erreur, _variables, contexte) => {
      if (contexte) queryClient.setQueryData(cle, contexte.avant)
    },
    onSettled: () => {
      // Le carnet dépend de ces marques : la prochaine visite doit le retrouver à jour.
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
    },
  })

  const marques = useMemo(() => {
    const parCle: Record<string, MarqueEtude> = {}
    for (const marque of data ?? []) parCle[marque.cle] = marque
    return parCle
  }, [data])

  const maj = useCallback(
    (section: string, patch: Patch) => mutation.mutate({ section, patch }),
    // `mutate` est stable ; dépendre de l'objet `mutation` entier recréerait `maj` à
    // chaque rendu et relancerait les effets des composants qui l'observent.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [mutation.mutate],
  )

  return {
    disponible: actif && cible !== null,
    marques,
    maj,
    nbComprises: Object.values(marques).filter((m) => m.compris).length,
  }
}

export type Etude = ReturnType<typeof useEtude>
