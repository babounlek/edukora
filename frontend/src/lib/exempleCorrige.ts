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

  const secondeSousQuestion = exercice.enonce_markdown.split("\n\n")[1]
  if (!secondeSousQuestion) return { exercice, corrigeMarkdown: exercice.corrige_markdown }
  const coupure = exercice.corrige_markdown.indexOf(secondeSousQuestion)
  return {
    exercice,
    corrigeMarkdown: coupure > 0 ? exercice.corrige_markdown.slice(0, coupure).trim() : exercice.corrige_markdown,
  }
}
