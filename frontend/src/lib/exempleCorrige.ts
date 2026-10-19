import type { EpreuveContent, EpreuveExercise } from "@/api/types"
import type { Langue } from "@/lib/i18n"

/**
 * L'exemple de « corrigé pas à pas » de l'accueil : un vrai extrait d'une épreuve gratuite (jamais un mock), choisi
 * PAR LANGUE - une interface anglaise qui montrait un corrigé de BEPC en français ne prouvait rien à son lecteur.
 *
 * - `slug` : l'épreuve gratuite ;
 * - `exercice` : le `numero_exercice` retenu (le premier si absent) ;
 * - `question1Seule` : ne montrer que le corrigé de la première sous-question (l'exercice entier serait trop long) ;
 *   sinon l'exercice entier, quand il est court et se suffit à lui-même.
 *
 * Un seul pays ouvert au lancement : le jour où un deuxième a du contenu, ce choix devra aussi se faire par pays.
 */
export interface ExempleCorrige {
  slug: string
  exercice?: string
  question1Seule: boolean
  /**
   * Avec `question1Seule` : coupe juste avant le DEUXIÈME repère de sous-question du corrigé (« **1.** », « **I.1.** »,
   * « **2)** »...) au lieu de retrouver l'énoncé de la question 2 mot pour mot. Les corrigés de BAC reprennent le repère
   * mais pas l'énoncé complet, donc la recherche par énoncé échoue et l'exercice entier (6 000 caractères) s'affichait.
   */
  coupeParRepere?: boolean
}

export const EXEMPLES_CORRIGE: Record<Langue, ExempleCorrige> = {
  fr: { slug: "mathematiques-bepc-2026", question1Seule: true },
  // Exercice 2 de Mathematics GCE O Level 2019, Paper 2 (facture d'électricité à deux tarifs, deux parties résolues) :
  // court, complet, et un SEUL rappel de méthode avant la première question - la même structure que l'exemple
  // français. Écartés : l'exercice 1 (un calcul BODMAS en une ligne) et l'exercice 3 (deux rappels empilés avant la
  // première ligne de résolution, dont celui de l'élimination qui sert la question b : voir ajouter_rappels_gce).
  en: { slug: "mathematics-gce-ordinary-level-2019-paper-2", exercice: "2", question1Seule: false },
}

/**
 * L'exemple de l'accueil adapté à l'examen déclaré (voir useCursusAccueil), en français : un élève de BAC C n'a que faire d'un
 * corrigé de BEPC. Clé : « EXAMEN » ou « EXAMEN:SÉRIE » (code de série du cursus).
 *
 * Seules les épreuves de mathématiques GRATUITES comptent : BEPC et BAC C, D, E. Le BAC A et le BAC C et E (épreuves
 * blanches ou à corrigé sans repères de sous-question) donneraient un exemple trop long ou mal découpé ; le Probatoire
 * et le BAC TI n'ont pas de mathématiques gratuites. Ces cursus gardent l'exemple par défaut de la langue.
 * Exercices retenus (mesurés le 2026-10-19) : un énoncé d'introduction court et une première question d'environ 800 caractères
 * qui se suffit à elle-même (BAC C : exercice 3, équation en entiers ; BAC D : exercice 2, suite numérique).
 */
const BAC_C: ExempleCorrige = { slug: "mathematiques-bac-c-2026", exercice: "3", question1Seule: true, coupeParRepere: true }
const EXEMPLES_FR_PAR_CURSUS: Record<string, ExempleCorrige> = {
  "BAC:C": BAC_C,
  // La Série E passe la même épreuve de mathématiques que la C (voir « Mathématiques BAC C et E 2026 »).
  "BAC:E": BAC_C,
  "BAC:D": { slug: "mathematiques-bac-d-2026", exercice: "2", question1Seule: true, coupeParRepere: true },
}

/**
 * Idem en anglais, par examen seulement : la branche technique d'un niveau (série « GCE_TECHNICAL ») n'a pas
 * d'épreuve de mathématiques gratuite propre et prépare le même niveau, elle montre donc l'exemple du niveau.
 *
 * - O Level : l'exemple par défaut de la langue (Mathematics 2019, Paper 2).
 * - A Level : l'exercice 4 de « Pure Mathematics with Mechanics 2023, Paper 2 » (dérivée d'un produit puis intégrale par
 *   changement de variable) : deux questions courtes, un corrigé complet de 1 600 caractères. Écartés : les exercices à
 *   cinq parties ou à preuve par récurrence, trop longs pour une page d'accueil.
 */
const EXEMPLES_EN_PAR_EXAMEN: Record<string, ExempleCorrige> = {
  GCE_AL: { slug: "pure-mathematics-with-mechanics-gce-a-level-2023-paper-2", exercice: "4", question1Seule: false },
}

export function exempleDuCursus(
  langue: Langue,
  cursus: { examen: string; series: { code: string } | null } | null | undefined,
): ExempleCorrige {
  if (langue === "fr" && cursus) {
    const cle = cursus.series ? `${cursus.examen}:${cursus.series.code}` : cursus.examen
    return EXEMPLES_FR_PAR_CURSUS[cle] ?? EXEMPLES_CORRIGE.fr
  }
  if (langue === "en" && cursus) return EXEMPLES_EN_PAR_EXAMEN[cursus.examen] ?? EXEMPLES_CORRIGE.en
  return EXEMPLES_CORRIGE[langue]
}

const REPERE_SOUS_QUESTION = /^\*\*(?:[IVX]+[.)]?\s*)?\d+[.)]\*\*/gm

/**
 * L'exercice retenu et le corrigé à montrer, ou null si l'épreuve ne contient pas cet exercice.
 *
 * `corrige_markdown` concatène toutes les sous-questions sans séparateur explicite et commence déjà par l'énoncé de la
 * première : pas d'« Énoncé » à part qui le répéterait. Pour `question1Seule`, on coupe juste avant l'énoncé de la
 * question 2, retrouvé tel quel dans le corrigé (même correspondance par chaîne exacte que
 * catalog.rendering.annotate_cours_links côté backend) ; repli sur le corrigé entier si l'exercice n'a qu'une
 * question, ou si ce texte ne s'y retrouve pas.
 */
export function extraireExempleCorrige(
  epreuve: Pick<EpreuveContent, "exercises"> | undefined,
  exemple: ExempleCorrige,
): { exercice: EpreuveExercise; corrigeMarkdown: string } | null {
  const exercices = epreuve?.exercises ?? []
  const exercice = exemple.exercice
    ? exercices.find((e) => String(e.numero_exercice) === exemple.exercice)
    : exercices[0]
  if (!exercice) return null
  if (!exemple.question1Seule) return { exercice, corrigeMarkdown: exercice.corrige_markdown }
  if (exemple.coupeParRepere) {
    const reperes = [...exercice.corrige_markdown.matchAll(REPERE_SOUS_QUESTION)]
    const coupure = reperes[1]?.index ?? -1
    return {
      exercice,
      corrigeMarkdown: coupure > 0 ? exercice.corrige_markdown.slice(0, coupure).trim() : exercice.corrige_markdown,
    }
  }

  const secondeSousQuestion = exercice.enonce_markdown.split("\n\n")[1]
  if (!secondeSousQuestion) return { exercice, corrigeMarkdown: exercice.corrige_markdown }
  const coupure = exercice.corrige_markdown.indexOf(secondeSousQuestion)
  return {
    exercice,
    corrigeMarkdown: coupure > 0 ? exercice.corrige_markdown.slice(0, coupure).trim() : exercice.corrige_markdown,
  }
}
