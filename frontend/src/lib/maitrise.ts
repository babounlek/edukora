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

/** Une part (0-1) en pourcentage entier, bornée : un arrondi qui dépasserait 100 %
 * ou passerait sous 0 casserait les barres et l'anneau (voir components/Progression). */
export function pourcent(part: number): number {
  return Math.round(Math.min(1, Math.max(0, part)) * 100)
}
