/**
 * Une épreuve inédite se note question par question, une annale officielle exercice par
 * exercice (voir simulations.cadre côté backend). La même page sert aux deux : ce que compte
 * une « unité » change, et avec lui les mots - « traitée » pour une question, « traité » pour un
 * exercice. Tout le vocabulaire qui en dépend vit ici, jamais éparpillé en ternaires.
 */
export type Unite = "question" | "exercice"

export function mots(unite: Unite) {
  const exercice = unite === "exercice"
  return {
    singulier: exercice ? "exercice" : "question",
    pluriel: exercice ? "exercices" : "questions",
    traite: exercice ? "traité" : "traitée",
    traites: exercice ? "traités" : "traitées",
    cet: exercice ? "cet" : "cette",
    Ce: exercice ? "Cet" : "Cette",
    nonTraite: exercice ? "non traité" : "non traitée",
    nonTraites: exercice ? "non traités" : "non traitées",
    marque: exercice ? "marqué" : "marquée",
    marques: exercice ? "marqués" : "marquées",
    ceLui: exercice ? "il" : "elle",
    /** « 1 exercice », « 3 questions » */
    compte(n: number) {
      return `${n} ${n > 1 ? this.pluriel : this.singulier}`
    },
  }
}

export function uniteDe(granularite: string | undefined): Unite {
  return granularite === "exercice" ? "exercice" : "question"
}
