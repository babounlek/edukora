import { describe, expect, it } from "vitest"

import { estPalierDeSerie, serieJusqua } from "./serieQuiz"

const juste = (id: number) => ({ id, reponse: { est_correcte: true } })
const fausse = (id: number) => ({ id, reponse: { est_correcte: false } })
const sansReponse = (id: number) => ({ id, reponse: null })

describe("série de bonnes réponses dans un quiz", () => {
  it("compte les bonnes réponses consécutives jusqu'à la question demandée", () => {
    expect(serieJusqua([juste(1), juste(2), juste(3)], 3)).toBe(3)
    expect(serieJusqua([juste(1), juste(2), juste(3)], 2)).toBe(2)
  })

  it("repart de zéro après une erreur ou une question passée", () => {
    expect(serieJusqua([juste(1), fausse(2), juste(3)], 3)).toBe(1)
    expect(serieJusqua([juste(1), sansReponse(2), juste(3), juste(4)], 4)).toBe(2)
    expect(serieJusqua([juste(1), fausse(2)], 2)).toBe(0)
  })

  it("ne fête que 5 et 10 d'affilée", () => {
    expect([3, 4, 5, 6, 9, 10, 11, 15].filter(estPalierDeSerie)).toEqual([5, 10])
  })
})
