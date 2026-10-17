import { describe, expect, it } from "vitest"

import type { ReglesInscription } from "@/api/types"

import { avertissementsInscription } from "./inscription"

const OL: ReglesInscription = {
  minimum: 6,
  maximum: 11,
  obligatoires: ["GCE_ENGLISH", "GCE_FRENCH", "GCE_MATHS"],
  derniere: "GCE_RELIGION",
}
const AL: ReglesInscription = { minimum: null, maximum: 5, obligatoires: [], derniere: null }

const COMPLET = ["GCE_ENGLISH", "GCE_FRENCH", "GCE_MATHS", "GCE_PHYSICS", "GCE_CHEMISTRY", "GCE_BIOLOGY"]
const codes = (a: { code: string }[]) => a.map((x) => x.code)

describe("avertissementsInscription", () => {
  it("ne dit rien sans règles ni choix", () => {
    expect(avertissementsInscription(null, ["GCE_MATHS"])).toEqual([])
    expect(avertissementsInscription(undefined, ["GCE_MATHS"])).toEqual([])
    expect(avertissementsInscription(OL, [])).toEqual([])
  })

  it("signale le minimum et chaque matière obligatoire manquante", () => {
    const res = avertissementsInscription(OL, ["GCE_PHYSICS", "GCE_CHEMISTRY", "GCE_BIOLOGY"])
    expect(res.find((a) => a.code === "minimum")).toEqual({ code: "minimum", attendu: 6, actuel: 3 })
    expect(res.filter((a) => a.code === "obligatoire").map((a) => a.matiere)).toEqual(["GCE_ENGLISH", "GCE_FRENCH", "GCE_MATHS"])
  })

  it("accepte une inscription complète", () => {
    expect(avertissementsInscription(OL, COMPLET)).toEqual([])
  })

  it("exige Religious Studies comme onzième matière", () => {
    const onze = [...COMPLET, "GCE_GEOGRAPHY", "GCE_HISTORY", "GCE_ECONOMICS", "GCE_LITERATURE", "GCE_COMMERCE"]
    expect(avertissementsInscription(OL, onze)).toEqual([{ code: "derniere_matiere", matiere: "GCE_RELIGION" }])
    expect(avertissementsInscription(OL, [...onze.slice(0, -1), "GCE_RELIGION"])).toEqual([])
  })

  it("signale plus de onze matières au O Level", () => {
    const douze = [...COMPLET, "GCE_GEOGRAPHY", "GCE_HISTORY", "GCE_ECONOMICS", "GCE_LITERATURE", "GCE_COMMERCE", "GCE_RELIGION"]
    expect(avertissementsInscription(OL, douze)).toEqual([{ code: "maximum", attendu: 11, actuel: 12 }])
  })

  it("A Level : cinq matières au plus, aucune obligatoire", () => {
    expect(avertissementsInscription(AL, ["A", "B", "C"])).toEqual([])
    expect(codes(avertissementsInscription(AL, ["A", "B", "C", "D", "E", "F"]))).toEqual(["maximum"])
  })
})
