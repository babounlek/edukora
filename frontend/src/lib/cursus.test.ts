import { describe, expect, it } from "vitest"
import type { Cursus } from "@/api/types"
import { codeSerieAffiche, EXAMEN_ORDER, examCodesFor, formatCursusGroups, trierCursus } from "./cursus"

const pays = { id: 1, code: "CM", label: "Cameroun" } as Cursus["country"]

function cursus(examen: string, display: string, series: Cursus["series"] = null): Cursus {
  return { id: 1, country: pays, examen, examen_display: display, series, langue: examen.startsWith("GCE") ? "en" : "fr" }
}

describe("cursus GCE", () => {
  it("place le GCE après les diplômes francophones, jamais en tête", () => {
    const liste = [
      cursus("GCE_AL", "GCE A Level"),
      cursus("BAC", "BAC", { id: 1, code: "C", label: "Maths" }),
      cursus("GCE_OL", "GCE O Level"),
      cursus("BEPC", "BEPC"),
    ]
    expect(examCodesFor(liste).map((e) => e.code)).toEqual(["BEPC", "BAC", "GCE_OL", "GCE_AL"])
    expect(EXAMEN_ORDER.indexOf("GCE_OL")).toBeGreaterThan(EXAMEN_ORDER.indexOf("BAC"))
  })

  it("écrit la branche technique par son libellé court, pas par son code interne", () => {
    const technique = { id: 9, code: "GCE_TECHNICAL", label: "Technical" }
    expect(codeSerieAffiche(technique)).toBe("Technical")
    expect(codeSerieAffiche({ code: "C", label: "Maths" })).toBe("C")
    expect(formatCursusGroups([cursus("GCE_AL", "GCE A Level", technique)])).toEqual([
      { key: "GCE_AL", label: "GCE A Level Technical" },
    ])
  })

  it("garde le format des séries francophones", () => {
    const liste = [
      cursus("BAC", "BAC", { id: 1, code: "C", label: "Maths" }),
      cursus("BAC", "BAC", { id: 2, code: "E", label: "Maths-Tech" }),
    ]
    expect(formatCursusGroups(liste)).toEqual([{ key: "BAC", label: "BAC C et E" }])
  })
})

describe("trierCursus", () => {
  const serie = (code: string) => ({ id: 1, code, label: code }) as Cursus["series"]

  it("suit le parcours scolaire, pas l'alphabet : BEPC, Probatoire, BAC, puis le GCE", () => {
    const liste = [
      cursus("BAC", "BAC", serie("C")),
      cursus("GCE_AL", "GCE A Level"),
      cursus("PROBATOIRE", "Probatoire", serie("A")),
      cursus("BEPC", "BEPC"),
      cursus("BAC", "BAC", serie("A")),
    ]
    expect(trierCursus(liste).map((c) => `${c.examen}${c.series ? ` ${c.series.code}` : ""}`)).toEqual([
      "BEPC",
      "PROBATOIRE A",
      "BAC A",
      "BAC C",
      "GCE_AL",
    ])
  })

  it("ne modifie pas la liste reçue et place un examen inconnu en dernier", () => {
    const liste = [cursus("INCONNU", "X"), cursus("BEPC", "BEPC")]
    expect(trierCursus(liste).map((c) => c.examen)).toEqual(["BEPC", "INCONNU"])
    expect(liste.map((c) => c.examen)).toEqual(["INCONNU", "BEPC"])
  })
})
