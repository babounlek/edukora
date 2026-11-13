// Seuil de maîtrise d'un thème (voir quiz.services.maitrise_par_theme côté backend,
// qui ne porte lui-même aucun seuil - purement un choix d'affichage frontend). Un
// thème sous ce taux est considéré "à réviser" (voir QuizStartPage/AccountPage) ; au-
// dessus, il disparaît des listes de révision.
export const SEUIL_MAITRISE = 70

/** Couleur de la barre de progression d'un thème, du rouge (à revoir en priorité) au
 * vert (maîtrisé), avec un palier or entre les deux. */
export function tauxBarClassName(taux: number): string {
  if (taux < 40) return "bg-destructive"
  if (taux < SEUIL_MAITRISE) return "bg-gold"
  return "bg-success"
}

/**
 * Sous ce pourcentage de préparation, l'élève démarre : on lui montre ce qu'il a gagné et le prochain palier, pas « 1 % ».
 * Un chiffre minuscule le jour 1 se lit comme un échec (passe Guyguy 2026-11-07 : « 1 % », « Anglais 0 % »). Partagé par
 * « Où j'en suis » (accueil) et « Ma progression », qui doivent dire la même chose du même élève.
 */
export const SEUIL_DEBUT_PCT = 10
const PALIERS_SAVOIRS = [5, 10, 25, 50, 100, 200, 400, 800, 1600]

/** Le prochain nombre rond de savoirs maîtrisés à viser. */
export function prochainPalier(maitrises: number): number {
  return PALIERS_SAVOIRS.find((p) => p > maitrises) ?? maitrises + 100
}

/** Une part (0-1) en pourcentage entier, bornée : un arrondi qui dépasserait 100 %
 * ou passerait sous 0 casserait les barres et l'anneau (voir components/Progression). */
export function pourcent(part: number): number {
  return Math.round(Math.min(1, Math.max(0, part)) * 100)
}
