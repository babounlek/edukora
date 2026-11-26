import { useSyncExternalStore } from "react"

/**
 * « Mode concentration » du quiz, sur téléphone : pendant une série de questions, l'en-tête du site, la barre
 * d'onglets et le pied de page s'effacent (la page du quiz a son propre « Quitter le quiz »). Même mécanique que
 * la salle d'examen (voir modeExamen.ts) : un état global minuscule, allumé par la page du quiz, lu seulement par
 * la coquille de l'application. À partir de 1024 px de large, rien ne disparaît : il y a la place.
 */
let actif = false
const abonnes = new Set<() => void>()

export function definirConcentration(valeur: boolean) {
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

export function useConcentration(): boolean {
  return useSyncExternalStore(abonner, () => actif, () => false)
}

/**
 * Plus léger que la concentration : seule la barre d'onglets du bas s'efface, l'en-tête reste. Pour une page de
 * lecture qui a déjà sa propre barre d'action fixée en bas (exercice d'un thème) : sans cela, en-tête, barre
 * d'action, bouton « Note » et barre d'onglets ne laissaient que 565 px sur 812 à l'exercice (audit 20, F13).
 */
let sansOnglets = false

export function definirSansOnglets(valeur: boolean) {
  if (sansOnglets === valeur) return
  sansOnglets = valeur
  abonnes.forEach((rappel) => rappel())
}

export function useSansOnglets(): boolean {
  return useSyncExternalStore(abonner, () => sansOnglets, () => false)
}
