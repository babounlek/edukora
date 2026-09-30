/**
 * Le seul chiffre qui juge l'accueil : combien de temps s'écoule entre l'affichage de la
 * page et le lancement de la séance. L'accueil note le moment où il apparaît, le bouton
 * "Commencer" lit le délai et l'envoie avec l'évènement plan_seance_demarree.
 *
 * Un module et non un contexte React : le bouton vit dans SeanceDuJour, qui sert aussi
 * la vitrine (sans accueil abonné au-dessus) - là, le délai est simplement absent.
 */
let affichageA: number | null = null

export function marquerAffichageAccueil() {
  affichageA = typeof performance !== "undefined" ? performance.now() : Date.now()
}

/** Secondes depuis l'affichage de l'accueil, ou undefined s'il n'a pas été affiché. */
export function delaiDepuisAffichageAccueil(): number | undefined {
  if (affichageA === null) return undefined
  const maintenant = typeof performance !== "undefined" ? performance.now() : Date.now()
  return Math.round((maintenant - affichageA) / 100) / 10
}

/** Pour les tests. */
export function oublierAffichageAccueil() {
  affichageA = null
}
