import { describe, expect, it } from "vitest"

import { TRI_PAR_DEFAUT, nouveauGermeAleatoire, triDepuisUrl, triPourApi, valeurUrlDuTri } from "./triEpreuves"

describe("tri de la liste des épreuves", () => {
  it("« Plus récentes (année) » est le tri par défaut", () => {
    expect(TRI_PAR_DEFAUT).toBe("annee")
    expect(triDepuisUrl(null)).toBe("annee")
    expect(triDepuisUrl("")).toBe("annee")
  })

  it("« Ajoutées récemment » et l'aléatoire se choisissent explicitement", () => {
    expect(triDepuisUrl("recent")).toBe("recent")
    expect(triDepuisUrl("aleatoire")).toBe("aleatoire")
  })

  it("les anciens liens retombent sur le défaut, sans erreur", () => {
    expect(triDepuisUrl("annee")).toBe("annee")
    expect(triDepuisUrl("year")).toBe("annee")
    expect(triDepuisUrl("popular")).toBe("annee")
    expect(triDepuisUrl("n-importe-quoi")).toBe("annee")
  })

  it("le défaut n'a pas de valeur dans l'URL, les autres tris en ont une", () => {
    expect(valeurUrlDuTri("annee")).toBe("")
    expect(valeurUrlDuTri("recent")).toBe("recent")
    expect(valeurUrlDuTri("aleatoire")).toBe("aleatoire")
  })

  it("l'API ne reçoit aucun tri par défaut, `recent` pour les ajouts et `random` pour l'aléatoire", () => {
    expect(triPourApi("annee")).toBeUndefined()
    expect(triPourApi("recent")).toBe("recent")
    expect(triPourApi("aleatoire")).toBe("random")
  })

  it("le germe aléatoire est un entier positif que le backend sait relire", () => {
    const germe = nouveauGermeAleatoire()
    expect(Number.isInteger(germe)).toBe(true)
    expect(germe).toBeGreaterThanOrEqual(0)
    expect(germe).toBeLessThan(2 ** 31)
  })
})
