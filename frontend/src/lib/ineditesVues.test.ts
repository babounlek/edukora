import { describe, expect, it } from "vitest"

import { ineditesNouvelles } from "./ineditesVues"

describe("ineditesNouvelles", () => {
  it("allume le point tant que rien n'a été vu", () => {
    expect(ineditesNouvelles(12, null)).toBe(true)
  })

  it("l'éteint une fois la plus récente vue", () => {
    expect(ineditesNouvelles(12, 12)).toBe(false)
    expect(ineditesNouvelles(12, 20)).toBe(false)
  })

  it("le rallume quand une inédite plus récente est publiée", () => {
    expect(ineditesNouvelles(13, 12)).toBe(true)
  })

  it("reste éteint quand il n'y a aucune inédite", () => {
    expect(ineditesNouvelles(undefined, null)).toBe(false)
  })
})
