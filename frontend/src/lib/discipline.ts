import { langueCourante, type Langue } from "@/lib/i18n"

/**
 * Matières jumelles du GCE (affichage seulement) : « Mathematics » prend l'icône et la couleur de « Mathématiques »,
 * « Physics » celles de « Physique », etc. Ce n'est PAS une équivalence de programme : le GCE garde ses propres
 * thèmes, quiz et programmes. Copie de backend `catalog.models.EQUIVALENTS_GCE` (Subject.equivalent_code) - à tenir
 * identique ; lib/discipline.test.ts en garde la forme.
 */
export const EQUIVALENTS_GCE: Record<string, string> = {
  GCE_MATHS: "MATHS", GCE_ADD_MATHS: "MATHS", GCE_PM_MECHANICS: "MATHS", GCE_PM_STATISTICS: "MATHS",
  GCE_FURTHER_MATHS: "MATHS",
  GCE_PHYSICS: "PHYSIQUE", GCE_CHEMISTRY: "CHIMIE", GCE_BIOLOGY: "SVT", GCE_HUMAN_BIOLOGY: "SVT",
  GCE_GEOLOGY: "SVT",
  GCE_HISTORY: "HISTOIRE", GCE_GEOGRAPHY: "GEOGRAPHIE", GCE_ECONOMICS: "ECONOMIE",
  GCE_PHILOSOPHY: "PHILOSOPHIE", GCE_LOGIC: "PHILOSOPHIE", GCE_LITERATURE: "LITTERATURE",
  GCE_ENGLISH: "ANGLAIS", GCE_FRENCH: "FRANCAIS", GCE_SBE_FRENCH: "FRANCAIS",
  GCE_COMPUTER_SCI: "INFORMATIQUE", GCE_ICT: "INFORMATIQUE",
  GCE_CITIZENSHIP: "EDUCATION_CIVIQUE", GCE_ACCOUNTING: "ECONOMIE", GCE_COMMERCE: "ECONOMIE",
  GCE_TECH_DRAWING: "DESSIN", GCE_CINEMATIC_ART: "DESSIN",
}

/** Code à utiliser pour retrouver icône et couleur : celui de la jumelle francophone s'il y en a une, sinon le code lui-même. */
export function codeVisuel(code: string): string {
  return EQUIVALENTS_GCE[code] ?? code
}

/** Paramètre `?langues=toutes` : l'élève veut voir les matières de toutes les langues. */
export const PARAM_TOUTES_LANGUES = "langues"

/**
 * Langue à envoyer à l'API pour une liste de matières, d'épreuves ou de cours : celle de l'interface, sauf quand un
 * examen est choisi (son cursus fixe déjà la langue) ou que l'élève a demandé toutes les langues. `undefined` = pas de filtre.
 */
export function langueDeListe(cursusFilter: string, toutesLangues: boolean): Langue | undefined {
  if (cursusFilter || toutesLangues) return undefined
  return langueCourante()
}
