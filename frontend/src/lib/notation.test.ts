import { describe, expect, it } from "vitest"

import type { TentativeInediteQuestion } from "@/api/types"

import { arrondiQuart, estANoter, formatNote, formatPoints, libellePoints, pointsDuNiveau } from "./notation"

function question(partiel: Partial<TentativeInediteQuestion>): TentativeInediteQuestion {
  return {
    id: 1, numero: "1", ordre: 1, groupe_local: "", enonce_markdown: "", type_reponse: "OUVERTE", choix: [],
    traitee: false, points: 2, bareme_estime: true, ...partiel,
  }
}

describe("formatage des points", () => {
  it("utilise la virgule française et supprime les zéros inutiles", () => {
    expect(formatPoints(12.5)).toBe("12,5")
    expect(formatPoints(4)).toBe("4")
    expect(formatPoints(1.25)).toBe("1,25")
    expect(formatPoints(null)).toBe("—")
  })

  it("compose la note sur son barème", () => {
    expect(formatNote(12.5, 20)).toBe("12,5 / 20")
    expect(formatNote(null, 20)).toBe("—")
  })

  it("accorde « point » au singulier jusqu'à 2 exclu", () => {
    expect(libellePoints(1)).toBe("1 point")
    expect(libellePoints(1.5)).toBe("1,5 point")
    expect(libellePoints(2)).toBe("2 points")
  })
})

describe("niveaux rapides de notation", () => {
  it("arrondit au quart de point", () => {
    expect(arrondiQuart(1.13)).toBe(1.25)
    expect(arrondiQuart(0.37)).toBe(0.25)
  })

  it("déduit les points de chaque niveau", () => {
    expect(pointsDuNiveau("echec", 3)).toBe(0)
    expect(pointsDuNiveau("reussi", 3)).toBe(3)
    expect(pointsDuNiveau("partiel", 3)).toBe(1.5)
    expect(pointsDuNiveau("partiel", 1.25)).toBe(0.75)
  })
})

describe("estANoter", () => {
  it("vrai seulement pour une question ouverte traitée mais pas encore notée", () => {
    expect(estANoter(question({ traitee: true }))).toBe(true)
    expect(estANoter(question({ traitee: true, reponse: { reponse_choisie: "", resultat_declare: "", notee: true } }))).toBe(false)
    expect(estANoter(question({ traitee: false }))).toBe(false)
    expect(estANoter(question({ type_reponse: "QCM", traitee: true }))).toBe(false)
  })
})
