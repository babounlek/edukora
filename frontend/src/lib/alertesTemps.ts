/**
 * Repères de temps d'une épreuve chronométrée : mi-parcours, 15 minutes, 5 minutes,
 * dernière minute. Chaque repère n'est annoncé qu'UNE fois, et un élève qui revient sur une
 * épreuve déjà avancée n'est jamais bombardé des repères qu'il a déjà passés : seul le plus
 * urgent est dit, les autres sont considérés comme annoncés.
 */
export type CleAlerte = "mi-parcours" | "quinze-minutes" | "cinq-minutes" | "une-minute"

interface Repere {
  cle: CleAlerte
  // Seuil en secondes restantes, calculé sur la durée totale.
  seuil: (dureeSecondes: number) => number
  // Sur une épreuve courte, certains repères n'ont pas de sens (15 min sur une épreuve de 30).
  applicable: (dureeSecondes: number) => boolean
}

const REPERES: Repere[] = [
  { cle: "mi-parcours", seuil: (d) => d / 2, applicable: (d) => d >= 20 * 60 },
  { cle: "quinze-minutes", seuil: () => 15 * 60, applicable: (d) => d >= 45 * 60 },
  { cle: "cinq-minutes", seuil: () => 5 * 60, applicable: (d) => d >= 15 * 60 },
  { cle: "une-minute", seuil: () => 60, applicable: (d) => d >= 10 * 60 },
]

/** Repères franchis et pas encore annoncés, du plus ancien au plus récent. */
export function reperesFranchis(restantSecondes: number, dureeSecondes: number, annonces: ReadonlySet<CleAlerte>): CleAlerte[] {
  return REPERES.filter(
    (repere) => repere.applicable(dureeSecondes) && restantSecondes <= repere.seuil(dureeSecondes) && !annonces.has(repere.cle),
  ).map((repere) => repere.cle)
}

export interface ContexteAlerte {
  traitees: number
  total: number
  unite?: "question" | "exercice"
}

export function messageAlerte(cle: CleAlerte, { traitees, total, unite = "question" }: ContexteAlerte): string {
  const exercice = unite === "exercice"
  switch (cle) {
    case "mi-parcours":
      return `Mi-parcours : ${traitees} ${exercice ? "exercice" : "question"}${traitees > 1 ? "s" : ""} ${exercice ? "traité" : "traitée"}${traitees > 1 ? "s" : ""} sur ${total}.`
    case "quinze-minutes":
      return "Il reste 15 minutes."
    case "cinq-minutes":
      return exercice
        ? "Il reste 5 minutes : pense à cocher les exercices que tu as traités."
        : "Il reste 5 minutes : pense à cocher les questions que tu as traitées."
    case "une-minute":
      return "Dernière minute."
  }
}
