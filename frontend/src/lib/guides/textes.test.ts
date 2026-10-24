import { afterEach, describe, expect, it } from "vitest"

import { definirLangue } from "@/lib/i18n"
import {
  texteAideCours, texteAideExercice, texteAideSeance, texteBienvenueEtapes, texteBienvenueSeance,
  texteDecouverteContenu, titreBienvenueEtapes,
} from "./textes"

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("textes dynamiques : ce que la page montre", () => {
  it("séance : cite le bouton, les étapes, le quiz express, les réglages", () => {
    const texte = texteAideSeance({ bouton: "Commencer : faire un exercice", phases: ["S'entraîner", "Vérifier"], quiz: true, quizExpress: true })
    expect(texte).toContain("« Commencer : faire un exercice »")
    expect(texte).toContain("S'entraîner → Vérifier")
    expect(texte).toContain("C'est le quiz qui valide ta séance.")
    expect(texte).toContain("Quiz express")
    expect(texte).toContain("choisir ta durée")
  })

  it("séance : sans quiz express ni quiz, aucune phrase à leur sujet", () => {
    const texte = texteAideSeance({ bouton: "Commencer : lire le cours", phases: ["Comprendre"], quiz: false, quizExpress: false })
    expect(texte).not.toMatch(/quiz/i)
  })

  it("séance verrouillée : pas de réglages à promettre", () => {
    expect(texteAideSeance({ bouton: "Débloquer ma séance", phases: ["Vérifier"], verrouillee: true })).not.toContain("durée")
  })

  it("sans publication de la page, une formulation générale vraie dans le cas courant", () => {
    expect(texteAideSeance(undefined)).toContain("bouton principal")
    expect(texteBienvenueSeance(undefined)).toContain("ce bouton")
    expect(titreBienvenueEtapes(undefined)).toBe("Les étapes de ta séance")
    expect(texteBienvenueEtapes(undefined)).toContain("Comprendre le cours")
    expect(texteDecouverteContenu(undefined)).toContain("Comprendre le cours")
    expect(texteAideCours(undefined)).toContain("règle à retenir")
    expect(texteAideExercice(undefined)).toContain("Essaie d'abord")
  })

  it("titre des étapes : le bon nombre", () => {
    expect(titreBienvenueEtapes({ phases: ["a"] })).toBe("Une seule étape aujourd'hui")
    expect(titreBienvenueEtapes({ phases: ["a", "b"] })).toBe("Deux étapes, dans l'ordre")
    expect(titreBienvenueEtapes({ phases: ["a", "b", "c"] })).toBe("Trois étapes, dans l'ordre")
  })

  it("cours : le suivi n'est mentionné que s'il est offert", () => {
    expect(texteAideCours({ sections: ["La règle"], suivi: true })).toContain("Marque chaque partie")
    expect(texteAideCours({ sections: ["La règle"], suivi: false })).not.toContain("Marque chaque partie")
  })

  it("cours : le bouton PDF est mentionné, avec ou sans contexte de page", () => {
    expect(texteAideCours(undefined)).toContain("Télécharger en PDF")
    expect(texteAideCours({ sections: ["La règle"], suivi: false })).toContain("Télécharger en PDF")
  })

  it("exercice : trois cas, selon l'accès et le mode de lecture", () => {
    expect(texteAideExercice({ acces: true, essai: true })).toContain("replié")
    expect(texteAideExercice({ acces: true, essai: false })).toContain("Tous les corrigés sont affichés")
    expect(texteAideExercice({ acces: false })).toContain("abonnement")
  })

  it("parle anglais", async () => {
    await definirLangue("en", { persister: false })
    expect(texteAideSeance({ bouton: "Start: do an exercise", phases: ["Practise", "Check"], quiz: true })).toContain('Tap "Start: do an exercise"')
    expect(titreBienvenueEtapes({ phases: ["a", "b"] })).toBe("Two steps, in order")
  })
})
