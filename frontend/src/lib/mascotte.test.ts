import { afterEach, describe, expect, it } from "vitest"

import { en } from "./i18n/en"
import { fr } from "./i18n/fr"
import { definirLangue } from "./i18n"
import {
  humeurMascotte, phraseJourMascotte, phraseMascotte, situationJourMascotte, situationMascotte, VARIANTES_JOUR_MASCOTTE, VARIANTES_MASCOTTE,
  type SituationJourMascotte, type SituationMascotte,
} from "./mascotte"

const SITUATIONS: SituationMascotte[] = ["record", "serie", "retour", "progres", "succes", "moyen", "faible"]

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("situationMascotte", () => {
  it("préfère le record, puis la série, puis le score", () => {
    expect(situationMascotte({ pourcentage: 10, recordBattu: true, serieJours: 9 })).toBe("record")
    expect(situationMascotte({ pourcentage: 10, serieJours: 3 })).toBe("serie")
    expect(situationMascotte({ pourcentage: 10, serieJours: 2 })).toBe("faible")
    expect(situationMascotte({ pourcentage: 70 })).toBe("succes")
    expect(situationMascotte({ pourcentage: 40 })).toBe("moyen")
    expect(situationMascotte({ pourcentage: 39 })).toBe("faible")
  })

  it("se souvient : retour après une absence, progrès sur le dernier quiz", () => {
    expect(situationMascotte({ pourcentage: 30, souvenir: { pourcentage: 80, jours: 5 } })).toBe("retour")
    expect(situationMascotte({ pourcentage: 60, souvenir: { pourcentage: 40, jours: 1 } })).toBe("progres")
    expect(situationMascotte({ pourcentage: 45, souvenir: { pourcentage: 40, jours: 1 } })).toBe("moyen")
    expect(situationMascotte({ pourcentage: 30, recordBattu: true, souvenir: { pourcentage: 10, jours: 9 } })).toBe("record")
  })

  it("donne une humeur à chaque situation", () => {
    expect(humeurMascotte("record")).toBe("fete")
    expect(humeurMascotte("succes")).toBe("content")
    expect(humeurMascotte("faible")).toBe("courage")
  })
})

describe("phrases de la mascotte", () => {
  it("existent en français ET en anglais pour chaque situation et chaque variante", () => {
    for (const situation of SITUATIONS) {
      for (let i = 1; i <= VARIANTES_MASCOTTE; i++) {
        const cle = `mascotte.${situation}_${i}`
        expect(fr, cle).toHaveProperty([cle])
        expect(en, cle).toHaveProperty([cle])
        // Les variables {n} doivent être les mêmes dans les deux langues.
        const vars = (s: string) => (s.match(/\{\w+\}/g) ?? []).join()
        expect(vars((en as Record<string, string>)[cle])).toBe(vars((fr as Record<string, string>)[cle]))
      }
    }
  })

  it("tire une variante selon le hasard, sans sortir de la plage", () => {
    const contexte = { pourcentage: 90 }
    expect(phraseMascotte("succes", contexte, 0)).toBe(fr["mascotte.succes_1"])
    expect(phraseMascotte("succes", contexte, 0.99)).toBe(fr["mascotte.succes_3"])
  })

  it("cite le score d'avant et l'absence", () => {
    const contexte = { pourcentage: 80, souvenir: { pourcentage: 50, jours: 6 } }
    expect(phraseMascotte("progres", contexte, 0)).toContain("50 %")
    expect(phraseMascotte("retour", contexte, 0)).toContain("6 jours")
  })

  it("insère la série et suit la langue", async () => {
    expect(phraseMascotte("serie", { pourcentage: 50, serieJours: 5 }, 0)).toContain("5 jours")
    await definirLangue("en", { persister: false })
    expect(phraseMascotte("serie", { pourcentage: 50, serieJours: 5 }, 0)).toContain("5 days")
  })
})

describe("rappel du jour de la mascotte", () => {
  const SITUATIONS_JOUR: SituationJourMascotte[] = ["atteint", "serie", "debut", "reste"]

  it("choisit la situation du jour", () => {
    expect(situationJourMascotte({ xp: 25, atteint: true }, { jours: 0 })).toBe("atteint")
    expect(situationJourMascotte({ xp: 5, atteint: false }, { jours: 4 })).toBe("serie")
    expect(situationJourMascotte({ xp: 0, atteint: false }, { jours: 1 })).toBe("debut")
    expect(situationJourMascotte({ xp: 5, atteint: false }, { jours: 1 })).toBe("reste")
  })

  it("a ses phrases en français ET en anglais, avec les mêmes variables", () => {
    for (const situation of SITUATIONS_JOUR) {
      for (let i = 1; i <= VARIANTES_JOUR_MASCOTTE; i++) {
        const cle = `mascotte.jour_${situation}_${i}`
        expect(fr, cle).toHaveProperty([cle])
        expect(en, cle).toHaveProperty([cle])
        const vars = (x: string) => (x.match(/{w+}/g) ?? []).join()
        expect(vars((en as Record<string, string>)[cle])).toBe(vars((fr as Record<string, string>)[cle]))
      }
    }
  })

  it("dit les points qui restent", () => {
    expect(phraseJourMascotte("reste", { xp: 5, objectif: 20 }, { jours: 1 }, 0)).toContain("15 points")
  })
})
