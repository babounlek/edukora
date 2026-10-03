// Géométrie du parcours en chemin : les thèmes sont des nœuds posés sur un fil qui serpente
// (gauche, centre, droite), un nœud par ligne. Fonctions pures, pour pouvoir les tester sans
// rendre quoi que ce soit : la forme du fil ne dépend que du rang d'un nœud dans la liste.

export const LARGEUR = 300
export const HAUTEUR_LIGNE = 144
export const RAYON = 32

// Décalage horizontal du centre d'un nœud, en pixels, qui se répète toutes les huit lignes :
// du centre vers la droite, retour, puis vers la gauche, retour. 76 + RAYON reste à l'intérieur
// de la demi-largeur (150), étiquette comprise.
const DECALAGES = [0, 48, 76, 48, 0, -48, -76, -48]

export function centre(index: number): { x: number; y: number } {
  return { x: LARGEUR / 2 + DECALAGES[index % DECALAGES.length], y: index * HAUTEUR_LIGNE + RAYON }
}

/** Tracé du fil du nœud `de` au nœud `a` inclus : une courbe en S entre chaque paire de centres.
 * Chaîne vide s'il n'y a rien à tracer (`a` ne dépasse pas `de`). */
export function trace(de: number, a: number): string {
  if (a <= de) return ""
  const premier = centre(de)
  let d = `M ${premier.x} ${premier.y}`
  for (let i = de; i < a; i++) {
    const p = centre(i)
    const q = centre(i + 1)
    const milieu = (p.y + q.y) / 2
    d += ` C ${p.x} ${milieu} ${q.x} ${milieu} ${q.x} ${q.y}`
  }
  return d
}

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

/** Indice du nœud d'où part le fil en pointillé : le premier qui n'est pas maîtrisé, après la
 * série de maîtrisés du début. Le fil est plein jusque-là - le chemin déjà parcouru. */
export function frontiere(maitrises: boolean[]): number {
  const premierNonMaitrise = maitrises.findIndex((m) => !m)
  return premierNonMaitrise === -1 ? maitrises.length - 1 : premierNonMaitrise
}
