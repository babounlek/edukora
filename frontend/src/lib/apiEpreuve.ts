import {
  completeSimulation,
  completeTentative,
  getSimulation,
  getTentativeInedite,
  marquerSimulationExercice,
  noterSimulationExercice,
  noterTentativeQuestion,
  startExamMode,
  startSimulationExam,
  toggleQuestionMarquee,
} from "@/api/endpoints"
import type { NoterTentativeQuestionParams } from "@/api/endpoints"
import { epreuvesListPath } from "@/lib/countryPath"

/** D'où vient l'épreuve passée : une épreuve inédite de la plateforme, ou une annale officielle
 * simulée en conditions d'examen (voir simulations côté backend). Même page, mêmes gestes : seule
 * l'API et quelques chemins changent. */
export type SourceEpreuve = "inedit" | "officielle"

/** Les appels de la page d'épreuve, selon la source. Des fonctions qui appellent à la demande,
 * jamais des références figées : chaque appel lit l'import au moment où il s'exécute. */
export function apiPour(source: SourceEpreuve) {
  if (source === "officielle") {
    return {
      charger: (id: number) => getSimulation(id),
      lancerExamen: (id: number, options: { papier?: boolean }) => startSimulationExam(id, options),
      noter: (id: number, unite: number, params: NoterTentativeQuestionParams) =>
        noterSimulationExercice(id, unite, params),
      marquer: (id: number, unite: number) => marquerSimulationExercice(id, unite),
      terminer: (id: number) => completeSimulation(id),
    }
  }
  return {
    charger: (id: number) => getTentativeInedite(id),
    lancerExamen: (id: number, options: { papier?: boolean }) => startExamMode(id, options),
    noter: (id: number, unite: number, params: NoterTentativeQuestionParams) =>
      noterTentativeQuestion(id, unite, params),
    marquer: (id: number, unite: number) => toggleQuestionMarquee(id, unite),
    terminer: (id: number) => completeTentative(id),
  }
}

/** Où renvoyer l'élève qui quitte l'épreuve : le catalogue des inédites, ou celui des annales. */
export function cheminRetour(source: SourceEpreuve, country: string): string {
  const pays = country.toLowerCase()
  return source === "officielle" ? epreuvesListPath(pays) : `${epreuvesListPath(pays)}?origine=INEDITE`
}

export function cheminEpreuve(source: SourceEpreuve, id: number): string {
  return source === "officielle" ? `/simulation/${id}` : `/inedit/tentative/${id}`
}

export function cheminResultat(source: SourceEpreuve, id: number): string {
  return `${cheminEpreuve(source, id)}/resultat`
}
