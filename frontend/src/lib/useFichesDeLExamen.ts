import { useQuery } from "@tanstack/react-query"

import { getFichesMatieres } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"

/**
 * Les Fiches EduKora publiées pour un examen, matière par matière. Les textes de l'offre et les liens vers les fiches
 * partent de ce compte : un examen sans fiches (le GCE aujourd'hui) ne doit jamais se les voir promettre, et la
 * couverture change à chaque publication, donc rien n'est écrit en dur. Même clé de cache que la page des fiches.
 */
export function useFichesDeLExamen(cursusId: number | null | undefined) {
  const { isAuthenticated } = useAuth()
  const { data } = useQuery({
    queryKey: ["fiches-edukora", "matieres", cursusId ?? null, isAuthenticated],
    queryFn: ({ signal }) => getFichesMatieres(cursusId as number, signal),
    enabled: Boolean(cursusId),
    staleTime: 5 * 60 * 1000,
  })
  const matieres = data?.matieres ?? []
  return {
    matieres,
    total: matieres.reduce((somme, m) => somme + m.total, 0),
    noms: matieres.map((m) => m.matiere).join(", "),
  }
}
