// La série de bonnes réponses à l'intérieur d'un quiz (à ne pas confondre avec la série de JOURS, voir FlammeSerie).
// Pur calcul, hors de lib/retours : les tests de page remplacent ce module-là par un faux.

type QuestionJouee = { id: number; reponse?: { est_correcte?: boolean } | null }

/** 5 et 10 d'affilée : fêtés à part (phrase et son), pour que la série ait des étapes au lieu d'une ligne répétée. */
export const PALIERS_SERIE: readonly number[] = [5, 10]

/** Bonnes réponses consécutives jusqu'à la question `id` incluse ; une erreur ou une question passée remet à zéro. */
export function serieJusqua(questions: readonly QuestionJouee[], id: number): number {
  let serie = 0
  for (const q of questions) {
    serie = q.reponse?.est_correcte ? serie + 1 : 0
    if (q.id === id) break
  }
  return serie
}

export function estPalierDeSerie(serie: number): boolean {
  return PALIERS_SERIE.includes(serie)
}
