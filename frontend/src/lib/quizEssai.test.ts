import { beforeEach, describe, expect, it } from "vitest"

import type { QuizQuestion, QuizSession } from "@/api/types"
import {
  avecQuestionCorrigee, bat, cheminEssai, lireEssai, lireRecord, memoriserEssai, memoriserRecord, oublierEssai,
  pointsEssai, scoreEssai, texteDePartageEssai,
} from "./quizEssai"

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

  it("donne le lien qui relance l'essai, et son accroche de partage", () => {
    const q = { ...question(1, "limites"), theme_id: 77, subject_label: "Mathématiques" } as QuizQuestion
    const session = essai([q])
    expect(cheminEssai(session)).toBe("/quiz/essai/1/2/77")
    expect(texteDePartageEssai(session)).toBe("Teste-toi sur « limites » (Mathématiques, BEPC) : un quiz gratuit, sans compte.")
  })

  it("ne propose aucun lien pour une session qui n'est pas un essai", () => {
    expect(cheminEssai({ ...essai([question(1, "x")]), essai: false })).toBeNull()
    expect(cheminEssai({ ...essai([question(1, "x")]), subject: null })).toBeNull()
  })
  it("compte les points comme le serveur : QCM juste 10, ouverte réussie 5, partielle 2, le reste 0", () => {
    const qcm = (id: number, juste: boolean) =>
      ({ ...question(id, "x"), type_reponse: "QCM", reponse: { reponse_choisie: "A", resultat_declare: "", est_correcte: juste, xp_gagne: 0 } }) as QuizQuestion
    const ouverte = (id: number, resultat: string) =>
      ({ ...question(id, "x"), reponse: { reponse_choisie: "", resultat_declare: resultat, est_correcte: resultat === "REUSSI", xp_gagne: 0 } }) as QuizQuestion
    const session = essai([qcm(1, true), qcm(2, false), ouverte(3, "REUSSI"), ouverte(4, "PARTIEL"), ouverte(5, "ECHEC"), question(6, "x")])
    expect(pointsEssai(session)).toBe(17)
  })

  describe("record", () => {
    beforeEach(() => localStorage.clear())
    const session = () => essai([{ ...question(1, "limites"), theme_id: 77 } as QuizQuestion])

    it("ne bat un record que strictement, et pas au premier essai", () => {
      expect(bat(null, 5, 5)).toBe(false)
      expect(bat({ reussies: 3, total: 5 }, 3, 5)).toBe(false)
      expect(bat({ reussies: 3, total: 5 }, 4, 5)).toBe(true)
      expect(bat({ reussies: 3, total: 5 }, 7, 10)).toBe(true) // 70 % > 60 % même sur un autre nombre de questions
    })

    it("garde le premier résultat puis seulement un meilleur", () => {
      expect(lireRecord(session())).toBeNull()
      memoriserRecord(session(), 3, 5)
      expect(lireRecord(session())).toEqual({ reussies: 3, total: 5 })
      memoriserRecord(session(), 2, 5)
      expect(lireRecord(session())).toEqual({ reussies: 3, total: 5 })
      memoriserRecord(session(), 4, 5)
      expect(lireRecord(session())).toEqual({ reussies: 4, total: 5 })
    })

    it("ignore un contenu illisible", () => {
      localStorage.setItem("edukora:records-essai", "pas du json")
      expect(lireRecord(session())).toBeNull()
      memoriserRecord(session(), 1, 5)
      expect(lireRecord(session())).toEqual({ reussies: 1, total: 5 })
    })
  })
})
