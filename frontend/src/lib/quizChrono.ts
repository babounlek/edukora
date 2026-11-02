import { useEffect, useState } from "react"

import { maintenantServeur } from "@/lib/horlogeServeur"

/**
 * Quiz chronométrés (facultatifs, voir quiz.chrono côté backend). Le compte à rebours n'est qu'un
 * affichage : l'échéance est celle du serveur, lue sur son horloge (voir lib/horlogeServeur) et
 * recalculée à chaque tick plutôt que décrémentée, pour résister à un onglet mis en arrière-plan.
 */

/** Secondes restantes avant l'échéance (ISO 8601), jamais négatives. `ceil` : le compteur ne tombe pas à 0 avant l'échéance. */
export function secondesRestantes(echeance: string, maintenant: number = maintenantServeur()): number {
  return Math.max(0, Math.ceil((Date.parse(echeance) - maintenant) / 1000))
}

/**
 * Temps restant, recalculé chaque seconde ; `null` sans échéance (quiz libre). Un quiz rouvert après
 * l'échéance part directement à 0.
 */
export function useSecondesRestantes(echeance: string | null | undefined): number | null {
  const [restant, setRestant] = useState<number | null>(() => (echeance ? secondesRestantes(echeance) : null))
  useEffect(() => {
    if (!echeance) {
      setRestant(null)
      return
    }
    const tick = () => setRestant(secondesRestantes(echeance))
    tick()
    const interval = window.setInterval(tick, 1000)
    return () => window.clearInterval(interval)
  }, [echeance])
  return restant
}

/** Temps alloué estimé à l'écran de lancement, avec le temps additionnel choisi (même formule que le serveur). */
export function dureeEstimeeSecondes(nbQuestions: number, secondesParQcm: number, tempsAdditionnelPct: number): number {
  return Math.ceil((nbQuestions * secondesParQcm * (100 + tempsAdditionnelPct)) / 100)
}

const CLE_MASQUE = "edukora:quiz-chrono-masque"

/** L'élève peut cacher le chrono sans l'arrêter (certains se bloquent à le voir tourner) ; mémorisé sur l'appareil. */
export function chronoEstMasque(): boolean {
  try {
    return localStorage.getItem(CLE_MASQUE) === "1"
  } catch {
    return false
  }
}

export function memoriserChronoMasque(masque: boolean) {
  try {
    if (masque) localStorage.setItem(CLE_MASQUE, "1")
    else localStorage.removeItem(CLE_MASQUE)
  } catch {
    // Mode privé ou stockage bloqué : le choix vaut pour la page seulement, rien de grave.
  }
}
