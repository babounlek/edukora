import { describe, expect, it } from "vitest"

import { TRI_PAR_DEFAUT, nouveauGermeAleatoire, triDepuisUrl, triPourApi, valeurUrlDuTri } from "./triEpreuves"

describe("tri de la liste des épreuves", () => {
  it("« Aléatoire » est le tri par défaut", () => {
    expect(TRI_PAR_DEFAUT).toBe("aleatoire")
    expect(triDepuisUrl(null)).toBe("aleatoire")
    expect(triDepuisUrl("")).toBe("aleatoire")
  })

  it("« Ajoutées récemment » et le tri par année se choisissent explicitement", () => {
    expect(triDepuisUrl("recent")).toBe("recent")
    expect(triDepuisUrl("annee")).toBe("annee")
  })

  it("les anciens liens retombent sur le défaut, sans erreur", () => {
    expect(triDepuisUrl("aleatoire")).toBe("aleatoire")
    expect(triDepuisUrl("year")).toBe("aleatoire")
    expect(triDepuisUrl("popular")).toBe("aleatoire")
    expect(triDepuisUrl("n-importe-quoi")).toBe("aleatoire")
  })

  it("le défaut n'a pas de valeur dans l'URL, les autres tris en ont une", () => {
    expect(valeurUrlDuTri("aleatoire")).toBe("")
    expect(valeurUrlDuTri("recent")).toBe("recent")
    expect(valeurUrlDuTri("annee")).toBe("annee")
  })

  it("l'API reçoit `random` par défaut, `recent` pour les ajouts, et aucun tri pour l'année", () => {
    expect(triPourApi("aleatoire")).toBe("random")
    expect(triPourApi("recent")).toBe("recent")
    expect(triPourApi("annee")).toBeUndefined()
  })

  it("le germe aléatoire est un entier positif que le backend sait relire", () => {
    const germe = nouveauGermeAleatoire()
    expect(Number.isInteger(germe)).toBe(true)
    expect(germe).toBeGreaterThanOrEqual(0)
    expect(germe).toBeLessThan(2 ** 31)
  })
})
