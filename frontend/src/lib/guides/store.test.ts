import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  cleDeLIdentite, definirAidesAuto, estAJour, lireDonnees, memoriser, reinitialiserStockage,
  reporterAnonymeSur, toutOublier,
} from "./store"

beforeEach(() => {
  reinitialiserStockage()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe("GuideStore", () => {
  it("part d'une mémoire vide, aides automatiques actives", () => {
    const donnees = lireDonnees("7:1")
    expect(donnees.guides).toEqual({})
    expect(donnees.prefs.aidesAuto).toBe(true)
  })

  it("garde ce qui a été terminé ou écarté, et sa version", () => {
    memoriser("7:1", "bienvenue", 1, "termine")
    memoriser("7:1", "seance-du-jour", 2, "ignore")
    const donnees = lireDonnees("7:1")
    expect(donnees.guides.bienvenue).toMatchObject({ version: 1, statut: "termine" })
    expect(donnees.guides["seance-du-jour"]).toMatchObject({ version: 2, statut: "ignore" })
  })

  it("une nouvelle version majeure repropose le guide, une même version non", () => {
    memoriser("7:1", "bienvenue", 1, "termine")
    const donnees = lireDonnees("7:1")
    expect(estAJour(donnees, "bienvenue", 1)).toBe(true)
    expect(estAJour(donnees, "bienvenue", 2)).toBe(false)
    expect(estAJour(donnees, "jamais-vu", 1)).toBe(false)
  })

  it("la mémoire de chaque compte et de chaque profil reste la sienne", () => {
    memoriser("7:1", "bienvenue", 1, "termine")
    expect(lireDonnees("7:2").guides).toEqual({})
    expect(lireDonnees("8:1").guides).toEqual({})
    expect(lireDonnees("anonyme").guides).toEqual({})
  })

  it("mémorise les préférences d'affichage sans toucher aux guides", () => {
    memoriser("7:1", "bienvenue", 1, "termine")
    definirAidesAuto("7:1", false)
    const donnees = lireDonnees("7:1")
    expect(donnees.prefs.aidesAuto).toBe(false)
    expect(donnees.guides.bienvenue).toBeDefined()
  })

  it("« tout revoir » oublie les guides vus mais garde les préférences", () => {
    memoriser("7:1", "bienvenue", 1, "termine")
    definirAidesAuto("7:1", false)
    toutOublier("7:1")
    const donnees = lireDonnees("7:1")
    expect(donnees.guides).toEqual({})
    expect(donnees.prefs.aidesAuto).toBe(false)
  })

  describe("données invalides", () => {
    it("un JSON illisible repart d'une mémoire vide, sans exception", () => {
      localStorage.setItem(cleDeLIdentite("7:1"), "{pas du json")
      expect(lireDonnees("7:1").guides).toEqual({})
    })

    it("un format inconnu est ignoré", () => {
      localStorage.setItem(cleDeLIdentite("7:1"), JSON.stringify({ v: 99, guides: { bienvenue: { version: 1, statut: "termine" } } }))
      expect(lireDonnees("7:1").guides).toEqual({})
    })

    it("écarte l'entrée altérée mais garde les autres", () => {
      localStorage.setItem(
        cleDeLIdentite("7:1"),
        JSON.stringify({
          v: 1,
          guides: {
            bienvenue: { version: 1, statut: "termine", date: 5 },
            casse: { version: "un", statut: "termine" },
            etrange: { version: 1, statut: "reussi" },
            nul: null,
          },
          prefs: { aidesAuto: "oui" },
        }),
      )
      const donnees = lireDonnees("7:1")
      expect(Object.keys(donnees.guides)).toEqual(["bienvenue"])
      expect(donnees.prefs.aidesAuto).toBe(true)
    })
  })

  describe("stockage indisponible", () => {
    it("écriture refusée (navigation privée, quota) : retombe sur la mémoire de la page, sans exception", () => {
      vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
        throw new DOMException("quota", "QuotaExceededError")
      })
      expect(() => memoriser("7:1", "bienvenue", 1, "termine")).not.toThrow()
      expect(lireDonnees("7:1").guides.bienvenue).toMatchObject({ statut: "termine" })
    })

    it("lecture et écriture refusées : aucune exception, comportement de premier passage", () => {
      vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
        throw new DOMException("bloqué", "SecurityError")
      })
      vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
        throw new DOMException("bloqué", "SecurityError")
      })
      expect(lireDonnees("7:1").guides).toEqual({})
      expect(() => memoriser("7:1", "bienvenue", 1, "ignore")).not.toThrow()
      expect(() => definirAidesAuto("7:1", false)).not.toThrow()
      expect(lireDonnees("7:1").prefs.aidesAuto).toBe(false)
    })
  })

  describe("reporterAnonymeSur", () => {
    it("reprend ce que le visiteur avait fermé, pour ne pas le lui remontrer une fois connecté", () => {
      memoriser("anonyme", "bienvenue-visiteur", 1, "ignore")
      reporterAnonymeSur("7:1")
      expect(lireDonnees("7:1").guides["bienvenue-visiteur"]).toMatchObject({ statut: "ignore" })
    })

    it("n'écrase jamais ce que le compte a déjà", () => {
      memoriser("anonyme", "bienvenue", 1, "ignore")
      memoriser("7:1", "bienvenue", 1, "termine")
      reporterAnonymeSur("7:1")
      expect(lireDonnees("7:1").guides.bienvenue.statut).toBe("termine")
    })

    it("complète quand la version anonyme est plus récente", () => {
      memoriser("anonyme", "bienvenue", 2, "ignore")
      memoriser("7:1", "bienvenue", 1, "termine")
      reporterAnonymeSur("7:1")
      expect(lireDonnees("7:1").guides.bienvenue).toMatchObject({ version: 2, statut: "ignore" })
    })

    it("sans effet quand l'anonyme n'a rien vu", () => {
      reporterAnonymeSur("7:1")
      expect(localStorage.getItem(cleDeLIdentite("7:1"))).toBeNull()
    })
  })
})
