import type { MesTentatives } from "@/api/types"
import { formatNote } from "./notation"

/** Ce que le clic sur une carte d'épreuve inédite fait pour CETTE personne : reprendre sa copie,
 * la refaire une fois rendue, ou la composer pour la première fois. */
export type ActionInedite = "reprendre" | "refaire" | "composer"

export function actionInedite(mes: MesTentatives | null | undefined): ActionInedite {
  if (mes?.en_cours) return "reprendre"
  if (mes && mes.nb_terminees > 0) return "refaire"
  return "composer"
}

export const LIBELLE_ACTION: Record<ActionInedite, string> = {
  reprendre: "Reprendre l'épreuve",
  refaire: "Refaire l'épreuve",
  composer: "Composer l'épreuve",
}

/** « Faite · 12 / 20 » (meilleure copie), ou « Faite » quand aucune note n'existe encore. Null
 * pour une épreuve qu'aucune copie rendue ne couvre. */
export function libelleFaite(mes: MesTentatives | null | undefined): string | null {
  if (!mes || mes.nb_terminees === 0) return null
  return mes.meilleure_note !== null && mes.bareme !== null
    ? `Faite · ${formatNote(mes.meilleure_note, mes.bareme)}`
    : "Faite"
}
