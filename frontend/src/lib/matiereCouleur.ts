/**
 * Une couleur par matière : avec l'icône (voir subjectIcon), c'est ce qui permet de
 * reconnaître "les maths" ou "la SVT" d'un coup d'œil, sur la séance, les barres de
 * progression et les priorités, sans lire.
 *
 * Les classes sont écrites EN ENTIER (jamais assemblées à partir d'un nom de couleur) :
 * Tailwind ne génère que les classes qu'il voit littéralement dans le source.
 *
 * Les couleurs sont des repères d'identité, jamais un signal de réussite : le vert et le
 * rouge de "juste/faux" restent réservés au retour de quiz. La SVT prend donc le lime et
 * non l'émeraude, trop proche du vert de marque.
 */
export interface CouleurMatiere {
  /** Fond doux + texte : la pastille d'icône. */
  puce: string
  /** Aplat plein : la barre ou le filet. */
  barre: string
}

const SKY = { puce: "bg-sky-500/15 text-sky-700 dark:text-sky-300", barre: "bg-sky-500" }
const ORANGE = { puce: "bg-orange-500/15 text-orange-700 dark:text-orange-300", barre: "bg-orange-500" }
const TEAL = { puce: "bg-teal-500/15 text-teal-700 dark:text-teal-300", barre: "bg-teal-500" }
const LIME = { puce: "bg-lime-500/20 text-lime-800 dark:text-lime-300", barre: "bg-lime-500" }
const ROSE = { puce: "bg-rose-500/15 text-rose-700 dark:text-rose-300", barre: "bg-rose-500" }
const VIOLET = { puce: "bg-violet-500/15 text-violet-700 dark:text-violet-300", barre: "bg-violet-500" }
const AMBER = { puce: "bg-amber-500/20 text-amber-800 dark:text-amber-300", barre: "bg-amber-500" }
const CYAN = { puce: "bg-cyan-500/15 text-cyan-700 dark:text-cyan-300", barre: "bg-cyan-500" }
const FUCHSIA = { puce: "bg-fuchsia-500/15 text-fuchsia-700 dark:text-fuchsia-300", barre: "bg-fuchsia-500" }
const INDIGO = { puce: "bg-indigo-500/15 text-indigo-700 dark:text-indigo-300", barre: "bg-indigo-500" }
const NEUTRE: CouleurMatiere = { puce: "bg-primary/10 text-primary", barre: "bg-primary" }

const COULEURS: Record<string, CouleurMatiere> = {
  MATHS: SKY,
  PHYSIQUE: ORANGE,
  PHYSIQUE_CHIMIE: ORANGE,
  PHYSIQUE_CHIMIE_TECH: ORANGE,
  CHIMIE: TEAL,
  SVT: LIME,
  FRANCAIS: ROSE,
  LITTERATURE: ROSE,
  PHILOSOPHIE: VIOLET,
  HISTOIRE: AMBER,
  HISTOIRE_GEO: AMBER,
  GEOGRAPHIE: CYAN,
  ANGLAIS: FUCHSIA,
  ESPAGNOL: FUCHSIA,
  ALLEMAND: FUCHSIA,
  ECONOMIE: INDIGO,
  DROIT: INDIGO,
  EDUCATION_CIVIQUE: INDIGO,
  INFORMATIQUE: INDIGO,
  PROGRAMMATION: INDIGO,
  SYSTEMES_INFORMATION: INDIGO,
  RESEAUX_SECURITE: INDIGO,
}

/** Couleur d'une matière par son code ; la couleur de marque pour un code inconnu. */
export function couleurMatiere(code: string | null | undefined): CouleurMatiere {
  return (code && COULEURS[code]) || NEUTRE
}
