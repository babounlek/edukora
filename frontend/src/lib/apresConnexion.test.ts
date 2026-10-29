import { beforeEach, describe, expect, it } from "vitest"

import { COUNTRY_STORAGE_KEY } from "@/lib/countryPath"
import { destinationApresConnexion, memoriserPaysDuCompte, paysDuCompte } from "./apresConnexion"

const compte = (pays: string | null, langue: "fr" | "en" = "fr") => ({
  cursus_prepare: pays ? ({ id: 1, langue, country: { code: pays.toUpperCase() } } as never) : null,
})

const entree = { paysNavigation: "cm", courante: "fr" as const, urlExplicite: false }

describe("destination après connexion", () => {
  it("sans page demandée : l'accueil du pays de l'examen du compte, pas du dernier pays parcouru", () => {
    expect(destinationApresConnexion({ ...entree, user: compte("sn") }).chemin).toBe("/sn")
  })

  it("sans examen déclaré : le pays que le navigateur affichait", () => {
    expect(destinationApresConnexion({ ...entree, user: compte(null) }).chemin).toBe("/cm")
  })

  it("une page demandée reste la destination", () => {
    expect(destinationApresConnexion({ ...entree, user: compte("sn"), demandee: "/cm/epreuves/x" }).chemin).toBe(
      "/cm/epreuves/x",
    )
  })

  it("un profil du GCE sur une page française : rechargement en anglais ; sinon aucun", () => {
    expect(destinationApresConnexion({ ...entree, user: compte("cm", "en") }).langue).toBe("en")
    expect(destinationApresConnexion({ ...entree, user: compte("cm", "fr") }).langue).toBeNull()
    expect(destinationApresConnexion({ ...entree, user: compte(null) }).langue).toBeNull()
  })

  it("un profil français sur une page anglaise ouverte par le navigateur (pas par un lien /en) : retour au français", () => {
    expect(destinationApresConnexion({ ...entree, user: compte("cm", "fr"), courante: "en" }).langue).toBe("fr")
    expect(
      destinationApresConnexion({ ...entree, user: compte("cm", "fr"), courante: "en", urlExplicite: true }).langue,
    ).toBeNull()
  })
})

describe("pays du compte", () => {
  beforeEach(() => localStorage.clear())

  it("est en minuscule, null sans examen", () => {
    expect(paysDuCompte(compte("SN"))).toBe("sn")
    expect(paysDuCompte(compte(null))).toBeNull()
  })

  it("est retenu pour la prochaine ouverture de « / », sans rien écraser quand le compte n'a pas d'examen", () => {
    localStorage.setItem(COUNTRY_STORAGE_KEY, "cm")
    memoriserPaysDuCompte(compte(null))
    expect(localStorage.getItem(COUNTRY_STORAGE_KEY)).toBe("cm")
    memoriserPaysDuCompte(compte("sn"))
    expect(localStorage.getItem(COUNTRY_STORAGE_KEY)).toBe("sn")
  })
})
