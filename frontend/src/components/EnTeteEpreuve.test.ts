import { describe, expect, it } from "vitest"

import { faitsEpreuve } from "./EnTeteEpreuve"

describe("faitsEpreuve", () => {
  it("annonce le paper et le code de matière d'une épreuve du GCE, avant la durée", () => {
    const textes = faitsEpreuve({ exercices: 15, duree: "2h30", paper: 2, codeMatiere: "0570" }).map((f) => f.texte)
    // Durées au format unique de libelleDuree (« 2 h 30 »), comme dans les listes.
    expect(textes).toEqual(["Paper 2", "15 exercices", "2 h 30", "Code 0570"])
  })

  it("ne change rien pour une épreuve francophone", () => {
    const textes = faitsEpreuve({ exercices: 1, duree: "4h", coefficient: "7", paper: null, codeMatiere: null }).map((f) => f.texte)
    expect(textes).toEqual(["1 exercice", "4 h", "Coefficient 7"])
  })
})
