import type { TentativeInediteQuestion } from "@/api/types"

const nombre = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 2 })

/** « 12,5 », « 4 », « 1,25 » : virgule française, jamais de zéros inutiles. */
export function formatPoints(valeur: number | null | undefined): string {
  return valeur === null || valeur === undefined ? "—" : nombre.format(valeur)
}

/** « 12,5 / 20 » - la note sur son barème réel. */
export function formatNote(note: number | null, bareme: number | null): string {
  if (note === null || bareme === null) return "—"
  return `${formatPoints(note)} / ${formatPoints(bareme)}`
}

/** « 1 point », « 2,5 points » - le pluriel français commence à 2 (1,5 reste singulier). */
export function libellePoints(valeur: number): string {
  return `${formatPoints(valeur)} ${valeur >= 2 ? "points" : "point"}`
}

/** Arrondit au quart de point : les sauts des boutons +/- restent des valeurs lisibles. */
export function arrondiQuart(valeur: number): number {
  return Math.round(valeur * 4) / 4
}

/** Points d'une question ouverte notée sans grille, déduits d'un niveau rapide. */
export function pointsDuNiveau(niveau: "echec" | "partiel" | "reussi", points: number): number {
  if (niveau === "echec") return 0
  if (niveau === "reussi") return points
  return arrondiQuart(points / 2)
}

/** Question ouverte traitée dont les points n'ont pas encore été attribués. */
export function estANoter(question: TentativeInediteQuestion): boolean {
  return question.type_reponse !== "QCM" && question.traitee && !question.reponse?.notee
}

/** Points effectivement obtenus par une question (0 tant qu'elle n'est pas traitée/notée). */
export function pointsObtenus(question: TentativeInediteQuestion): number {
  if (question.type_reponse === "QCM") {
    return question.reponse?.est_correcte ? question.points : 0
  }
  return question.reponse?.points_obtenus ?? 0
}
