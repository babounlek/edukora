import { beforeEach, describe, expect, it } from "vitest"

import type { QuizQuestion, QuizSession } from "@/api/types"
import { avecQuestionCorrigee, lireEssai, memoriserEssai, oublierEssai, scoreEssai } from "./quizEssai"

function question(id: number, theme: string, reponse?: boolean): QuizQuestion {
  return {
    id, ordre: id, enonce_markdown: `Q${id}`, type_reponse: "OUVERTE", choix: [], subject_label: "Maths", theme,
    ...(reponse === undefined
      ? {}
      : { reponse: { reponse_choisie: "", resultat_declare: reponse ? "REUSSI" : "ECHEC", est_correcte: reponse, xp_gagne: 0 } }),
  } as QuizQuestion
}

function essai(questions: QuizQuestion[]): QuizSession {
  return {
    id: 0, essai: true, mode: "PRATIQUE", cursus: 1, subject: 2, cursus_display: "BEPC",
    started_at: "2026-10-12T10:00:00Z", completed_at: null, total_questions: questions.length, questions,
  }
}

describe("quizEssai", () => {
  beforeEach(() => sessionStorage.clear())

  it("relit l'essai mémorisé, et l'oublie", () => {
    memoriserEssai(essai([question(1, "limites")]))
    expect(lireEssai()?.questions).toHaveLength(1)
    oublierEssai()
    expect(lireEssai()).toBeNull()
  })

  it("ignore un contenu stocké qui n'est pas un essai", () => {
    sessionStorage.setItem("edukora:quiz-essai", JSON.stringify({ id: 5, questions: [question(1, "x")] }))
    expect(lireEssai()).toBeNull()
    sessionStorage.setItem("edukora:quiz-essai", "pas du json")
    expect(lireEssai()).toBeNull()
  })

  it("réécrit la question corrigée sans toucher aux autres", () => {
    const session = essai([question(1, "limites"), question(2, "limites")])
    const apres = avecQuestionCorrigee(session, question(2, "limites", true))
    expect(apres.questions[0].reponse).toBeUndefined()
    expect(apres.questions[1].reponse?.est_correcte).toBe(true)
  })

  it("calcule le score par thème, sur les seules questions répondues", () => {
    const session = essai([question(1, "limites", true), question(2, "limites", false), question(3, "dérivée", true), question(4, "dérivée")])
    const score = scoreEssai(session)
    expect(score).toMatchObject({ total: 4, repondues: 3, reussies: 2 })
    expect(score.parTheme).toEqual([
      { theme: "limites", total: 2, reussies: 1 },
      { theme: "dérivée", total: 1, reussies: 1 },
    ])
  })
})
