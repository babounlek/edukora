import { afterEach, describe, expect, it } from "vitest"

import { connexionEconome } from "./connexion"

function simuler(connexion: unknown) {
  Object.defineProperty(navigator, "connection", { value: connexion, configurable: true })
}

describe("connexionEconome", () => {
  afterEach(() => simuler(undefined))

  it("est faux quand le navigateur ne donne aucune information", () => {
    simuler(undefined)
    expect(connexionEconome()).toBe(false)
  })

  it("est vrai en mode économie de données", () => {
    simuler({ saveData: true, effectiveType: "4g" })
    expect(connexionEconome()).toBe(true)
  })

  it.each(["slow-2g", "2g", "3g"])("est vrai sur une connexion %s", (effectiveType) => {
    simuler({ saveData: false, effectiveType })
    expect(connexionEconome()).toBe(true)
  })

  it("est faux sur une bonne connexion", () => {
    simuler({ saveData: false, effectiveType: "4g" })
    expect(connexionEconome()).toBe(false)
  })
})
