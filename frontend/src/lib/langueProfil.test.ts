import { describe, expect, it } from "vitest"

import { langueACharger, langueImposee } from "./langueProfil"

const cursus = (langue: "fr" | "en") => ({ cursus_prepare: { langue } }) as never

describe("langueImposee", () => {
  it("suit le cursus du profil actif, abonné ou non", () => {
    expect(langueImposee(cursus("fr"))).toBe("fr")
    expect(langueImposee(cursus("en"))).toBe("en")
  })

  it("rien d'imposé sans cursus déclaré ni utilisateur", () => {
    expect(langueImposee({ cursus_prepare: null })).toBeNull()
    expect(langueImposee(null)).toBeNull()
    expect(langueImposee(undefined)).toBeNull()
  })

  it("ignore une réponse ancienne sans langue de cursus", () => {
    expect(langueImposee({ cursus_prepare: {} } as never)).toBeNull()
  })
})

describe("langueACharger", () => {
  const base = { urlExplicite: false, changement: false }

  it("ne fait rien quand la page est déjà dans la langue du cursus", () => {
    expect(langueACharger({ ...base, imposee: "fr", courante: "fr" })).toBeNull()
    expect(langueACharger({ ...base, imposee: "en", courante: "en", urlExplicite: true })).toBeNull()
  })

  it("cursus anglais : une page française passe toujours en anglais", () => {
    expect(langueACharger({ ...base, imposee: "en", courante: "fr" })).toBe("en")
  })

  it("cursus français : une page anglaise revient en français quand le lien n'était pas explicite", () => {
    // Anglais venu du choix mémorisé du navigateur, pas d'un lien /en.
    expect(langueACharger({ ...base, imposee: "fr", courante: "en" })).toBe("fr")
  })

  it("cursus français : un lien /en explicite est respecté", () => {
    expect(langueACharger({ ...base, imposee: "fr", courante: "en", urlExplicite: true })).toBeNull()
  })

  it("cursus français : un changement de cursus en cours de session ramène en français, même sur /en", () => {
    expect(langueACharger({ imposee: "fr", courante: "en", urlExplicite: true, changement: true })).toBe("fr")
  })
})
