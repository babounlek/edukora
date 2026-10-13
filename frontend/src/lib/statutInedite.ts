import type { MesTentatives } from "@/api/types"
import { formatNote } from "./notation"
import { t } from "@/lib/i18n"

/** Ce que le clic sur une carte d'épreuve inédite fait pour CETTE personne : reprendre sa copie,
 * la refaire une fois rendue, ou la composer pour la première fois. */
export type ActionInedite = "reprendre" | "refaire" | "composer"

export function actionInedite(mes: MesTentatives | null | undefined): ActionInedite {
  if (mes?.en_cours) return "reprendre"
  if (mes && mes.nb_terminees > 0) return "refaire"
  return "composer"
}

/** Le libellé du bouton d'une inédite, dans la langue courante. */
export function libelleAction(action: ActionInedite): string {
  if (action === "reprendre") return t("inedite.reprendre")
  if (action === "refaire") return t("inedite.refaire")
  return t("inedite.composer")
}

/** « Faite · 12 / 20 » (meilleure copie), ou « Faite » quand aucune note n'existe encore. Null
 * pour une épreuve qu'aucune copie rendue ne couvre. */
export function libelleFaite(mes: MesTentatives | null | undefined): string | null {
  if (!mes || mes.nb_terminees === 0) return null
  return mes.meilleure_note !== null && mes.bareme !== null
    ? t("inedite.faite_note", { note: formatNote(mes.meilleure_note, mes.bareme) })
    : t("inedite.faite")
}
