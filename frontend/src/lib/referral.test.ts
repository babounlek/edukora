import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  captureReferralCode, clearReferralCode, codeRevendeurMemorise, consumeReferralCode, lienDeRevendeur, oublierCodeRevendeur,
} from "./referral"

function ouvrir(search: string) {
  window.history.replaceState(null, "", `/${search}`)
  captureReferralCode()
}

beforeEach(() => localStorage.clear())
afterEach(() => {
  vi.useRealTimers()
  window.history.replaceState(null, "", "/")
})

describe("code revendeur (?rev=)", () => {
  it("est mémorisé en majuscules depuis le lien", () => {
    ouvrir("?rev=demo42")
    expect(codeRevendeurMemorise()).toBe("DEMO42")
  })

  it("passe avant un code de parrainage à l'inscription, sans l'écraser", () => {
    ouvrir("?ref=abc123")
    ouvrir("?rev=demo42")
    expect(consumeReferralCode()).toBe("DEMO42")
    oublierCodeRevendeur()
    expect(consumeReferralCode()).toBe("ABC123")
  })

  it("ignore une valeur qui n'a pas la forme d'un code", () => {
    ouvrir("?rev=ab")
    ouvrir("?rev=<script>alert(1)</script>")
    ouvrir("?rev=TROPLONGUECODE")
    expect(codeRevendeurMemorise()).toBe("")
  })

  it("expire au bout de 30 jours", () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date("2026-11-01T10:00:00Z"))
    ouvrir("?rev=DEMO42")

    vi.setSystemTime(new Date("2026-11-30T10:00:00Z"))
    expect(codeRevendeurMemorise()).toBe("DEMO42")

    vi.setSystemTime(new Date("2026-12-02T10:00:00Z"))
    expect(codeRevendeurMemorise()).toBe("")
  })

  it("est oublié par une connexion, pour ne pas suivre la personne suivante sur un appareil partagé", () => {
    ouvrir("?rev=DEMO42")
    clearReferralCode()
    expect(consumeReferralCode()).toBe("")
  })

  it("résiste à un stockage corrompu", () => {
    localStorage.setItem("edukamer-revendeur-code", "pas du json")
    expect(codeRevendeurMemorise()).toBe("")
    localStorage.setItem("edukamer-revendeur-code", JSON.stringify({ code: 42, le: "hier" }))
    expect(codeRevendeurMemorise()).toBe("")
  })
})

describe("lienDeRevendeur", () => {
  it("pointe vers l'accueil avec le code", () => {
    expect(lienDeRevendeur("DEMO42")).toBe(`${window.location.origin}/?rev=DEMO42`)
  })
})
