import { describe, expect, it } from "vitest"

import { phraseDeDemain } from "./SeanceDuJour"

const theme = (nom: string) => ({ theme: nom, subject_label: "Mathématiques" })

describe("aperçu de demain, une fois la séance faite", () => {
  it("ne dit rien quand rien n'est dû demain", () => {
    expect(phraseDeDemain(undefined)).toBeNull()
    expect(phraseDeDemain({ themes: [], themes_total: 0, cartes: 0 })).toBeNull()
  })

  it("nomme le thème qui revient", () => {
    expect(phraseDeDemain({ themes: [theme("dérivation")], themes_total: 1, cartes: 0 })).toBe(
      "Demain : « Dérivation » revient en révision.",
    )
  })

  it("compte les thèmes quand il y en a plusieurs, et ajoute les cartes", () => {
    expect(phraseDeDemain({ themes: [theme("limites"), theme("dérivation")], themes_total: 3, cartes: 4 })).toBe(
      "Demain : 3 thèmes reviennent en révision, dont « Limites », avec 4 cartes de révision.",
    )
  })

  it("annonce les cartes seules", () => {
    expect(phraseDeDemain({ themes: [], themes_total: 0, cartes: 1 })).toBe("Demain : 1 carte de révision à revoir.")
  })
})
