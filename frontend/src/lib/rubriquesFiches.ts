import type { FicheEdukora } from "@/api/types"

/** L'ordre des rubriques de maths ; une rubrique inconnue vient après, par ordre alphabétique. */
const ORDRE = ["Calcul", "Géométrie", "Repère", "Statistiques"]

function rang(rubrique: string): number {
  const i = ORDRE.indexOf(rubrique)
  return i === -1 ? ORDRE.length : i
}

export interface GroupeDeFiches {
  /** "" pour les fiches sans rubrique (les définitions d'éducation civique, par exemple). */
  rubrique: string
  fiches: FicheEdukora[]
}

/** Les fiches rangées par rubrique. L'ordre reçu du serveur (les plus souvent tombées d'abord) est gardé dans chacune. */
export function grouperParRubrique(fiches: FicheEdukora[]): GroupeDeFiches[] {
  const groupes = new Map<string, FicheEdukora[]>()
  for (const fiche of fiches) {
    const cle = fiche.rubrique ?? ""
    const liste = groupes.get(cle)
    if (liste) liste.push(fiche)
    else groupes.set(cle, [fiche])
  }
  return [...groupes.entries()]
    .map(([rubrique, liste]) => ({ rubrique, fiches: liste }))
    .sort((a, b) => {
      // Les fiches sans rubrique ferment la marche.
      if (!a.rubrique || !b.rubrique) return a.rubrique ? -1 : b.rubrique ? 1 : 0
      return rang(a.rubrique) - rang(b.rubrique) || a.rubrique.localeCompare(b.rubrique, "fr")
    })
}
