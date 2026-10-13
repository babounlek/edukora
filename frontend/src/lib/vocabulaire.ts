/**
 * Une épreuve inédite se note question par question, une annale officielle exercice par
 * exercice (voir simulations.cadre côté backend). La même page sert aux deux : ce que compte
 * une « unité » change, et avec lui les mots - « traitée » pour une question, « traité » pour un
 * exercice. Tout le vocabulaire qui en dépend vit ici, jamais éparpillé en ternaires.
 */
import { t, tn, type CleAvecPluriel, type CleI18n } from "@/lib/i18n"

export type Unite = "question" | "exercice"

/** Les mots d'une unité dans la langue courante (« question » / « exercise », « traitée » / « completed »).
 * `mots()` ci-dessous reste le vocabulaire français, avec ses accords, pour les écrans pas encore traduits. */
export function libellesUnite(unite: Unite) {
  const exercice = unite === "exercice"
  return {
    singulier: t(exercice ? "vo.exercice" : "vo.question"),
    pluriel: t(exercice ? "vo.exercices" : "vo.questions"),
    traite: t(exercice ? "vo.exercice_traite" : "vo.question_traite"),
  }
}

type Variables = Record<string, string | number>

/** Clé de texte propre à l'unité : `tu("bn.suivante", "exercice")` lit `bn.suivante_exercice`. Le français
 * accorde (« traitée » / « traité »), l'anglais n'en a pas besoin : chaque phrase est donc écrite en entier. */
export function tu(base: string, unite: Unite, variables?: Variables): string {
  return t(`${base}_${unite}` as CleI18n, variables)
}

/** Pareil pour un pluriel : `tnu("rp.repondues", "question", 3)` lit `rp.repondues_question_other`. */
export function tnu(base: string, unite: Unite, n: number, variables?: Variables): string {
  return tn(`${base}_${unite}` as CleAvecPluriel, n, variables)
}

/** « 1 exercice », « 3 questions » dans la langue courante. */
export function compteUnite(unite: Unite, n: number): string {
  return unite === "exercice" ? tn("ep.exercices", n) : tn("quiz.n_questions", n)
}

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
