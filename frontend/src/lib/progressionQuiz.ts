import { t, tn } from "@/lib/i18n"

/** Ce que le serveur dit de l'avancement d'un profil dans un périmètre de quiz (une matière, un thème). */
export interface AvancementQuiz {
  total: number
  /** Questions vues dans le tour en cours : repart à zéro dès que la dernière manquante est répondue. */
  vues: number
  /** Tours complets déjà terminés. */
  tours: number
}

/**
 * Le compteur « vues/total » et son explication au survol, ou null tant que rien n'a été fait (on n'affiche alors
 * que ce que la liste affichait déjà). Un tour qui vient de se terminer montre « 0/30 » : le tour suivant commence.
 */
export function libelleAvancement({ total, vues, tours }: AvancementQuiz): { texte: string; titre: string } | null {
  if (total <= 0 || (vues <= 0 && tours <= 0)) return null
  const vuesBornees = Math.min(vues, total)
  const base = vuesBornees > 0 ? t("qd.vues_sur", { vues: vuesBornees, total }) : t("qd.tour_termine")
  return {
    texte: `${vuesBornees}/${total}`,
    titre: tours > 0 ? `${base} · ${tn("qd.tours_faits", tours)}` : base,
  }
}
