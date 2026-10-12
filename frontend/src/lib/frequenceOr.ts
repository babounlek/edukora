// Repère « tombe souvent à l'examen » du Parcours par fréquence : une étoile dorée sur les thèmes
// du quart supérieur. Fonctions pures, testables sans rendre quoi que ce soit.

/**
 * Seuil de fréquence à partir duquel un thème est « doré » (il tombe souvent à l'examen) : le
 * quart supérieur des thèmes de la liste, jamais en dessous de PLANCHER_OR % des épreuves. Sans
 * quart (moins de quatre fréquences connues) ou sans fréquence du tout (programme classique),
 * rien n'est doré : un repère rare reste un repère, et on ne dore pas au hasard.
 */
export const PLANCHER_OR = 30

export function seuilOr(frequences: (number | null | undefined)[]): number | null {
  const valeurs = frequences.filter((v): v is number => typeof v === "number")
  if (valeurs.length < 4) return null
  const tri = [...valeurs].sort((a, b) => b - a)
  return Math.max(tri[Math.ceil(valeurs.length / 4) - 1], PLANCHER_OR)
}

export function estDore(frequence: number | null | undefined, seuil: number | null): boolean {
  return seuil !== null && typeof frequence === "number" && frequence >= seuil
}
