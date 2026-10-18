import { describe, expect, it } from "vitest"

import { TRI_PAR_DEFAUT, triDepuisUrl, triPourApi, valeurUrlDuTri } from "./triEpreuves"

describe("tri de la liste des épreuves", () => {
  it("« Ajoutées récemment » est le tri par défaut", () => {
    expect(TRI_PAR_DEFAUT).toBe("recent")
    expect(triDepuisUrl(null)).toBe("recent")
    expect(triDepuisUrl("")).toBe("recent")
  })

  it("le tri par année se choisit explicitement", () => {
    expect(triDepuisUrl("annee")).toBe("annee")
  })

  it("les anciens liens retombent sur le défaut, sans erreur", () => {
    expect(triDepuisUrl("recent")).toBe("recent")
    expect(triDepuisUrl("year")).toBe("recent")
    expect(triDepuisUrl("popular")).toBe("recent")
    expect(triDepuisUrl("n-importe-quoi")).toBe("recent")
  })

  it("le défaut n'a pas de valeur dans l'URL, l'année en a une", () => {
    expect(valeurUrlDuTri("recent")).toBe("")
    expect(valeurUrlDuTri("annee")).toBe("annee")
  })

  it("l'API reçoit `recent` par défaut, et aucun tri pour l'année (tri par défaut du backend)", () => {
    expect(triPourApi("recent")).toBe("recent")
    expect(triPourApi("annee")).toBeUndefined()
  })
})
