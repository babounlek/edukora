import { useSyncExternalStore } from "react"

/**
 * « Salle d'examen » : tant qu'une épreuve chronométrée est en cours, tout ce qui n'est pas
 * l'épreuve disparaît (en-tête, bandeaux, barre d'onglets, pied de page). Un état global
 * minuscule plutôt qu'un contexte : la page d'épreuve l'allume et l'éteint, et seule la
 * coquille de l'application (App.tsx) le lit - aucun composant intermédiaire n'a à le relayer.
 */
let actif = false
const abonnes = new Set<() => void>()

export function definirModeExamen(valeur: boolean) {
  if (actif === valeur) return
  actif = valeur
  abonnes.forEach((rappel) => rappel())
}

function abonner(rappel: () => void) {
  abonnes.add(rappel)
  return () => {
    abonnes.delete(rappel)
  }
}

export function useModeExamen(): boolean {
  return useSyncExternalStore(abonner, () => actif, () => false)
}
