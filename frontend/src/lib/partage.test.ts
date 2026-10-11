import { afterEach, describe, expect, it, vi } from "vitest"

import {
  copierLienDePartage, lienDePartage, messageDePartage, ouvrirWhatsApp, partageNatifPrefere, partagerNativement, type DonneesPartageLien,
} from "./partage"

const donnees: DonneesPartageLien = { texte: "Regarde ce corrigé", chemin: "/cm/epreuves/maths-bac-c-2023", codeParrainage: "ABC123" }

afterEach(() => {
  vi.restoreAllMocks()
  Reflect.deleteProperty(navigator, "share")
})

describe("lienDePartage", () => {
  it("construit un lien absolu portant le code de parrainage", () => {
    expect(lienDePartage(donnees)).toBe(`${window.location.origin}/cm/epreuves/maths-bac-c-2023?ref=ABC123`)
  })

  it("n'ajoute aucun paramètre sans code de parrainage (visiteur anonyme)", () => {
    expect(lienDePartage({ ...donnees, codeParrainage: undefined })).toBe(`${window.location.origin}/cm/epreuves/maths-bac-c-2023`)
  })

  it("le message porte l'accroche puis le lien", () => {
    expect(messageDePartage(donnees)).toBe(`Regarde ce corrigé ${window.location.origin}/cm/epreuves/maths-bac-c-2023?ref=ABC123`)
  })
})

describe("partagerNativement", () => {
  it("ouvre le partage du téléphone avec le message", async () => {
    const share = vi.fn(() => Promise.resolve())
    Object.defineProperty(navigator, "share", { value: share, configurable: true })
    expect(await partagerNativement(donnees)).toBe("partage")
    expect((share.mock.calls[0] as unknown as [ShareData])[0].text).toContain("ref=ABC123")
  })

  it("est indisponible quand le navigateur ne sait pas partager", async () => {
    expect(await partagerNativement(donnees)).toBe("indisponible")
  })

  it("ne signale rien quand l'élève ferme le panneau", async () => {
    Object.defineProperty(navigator, "share", {
      value: () => Promise.reject(new DOMException("annulé", "AbortError")), configurable: true,
    })
    expect(await partagerNativement(donnees)).toBe("annule")
  })

  it("retombe sur 'indisponible' pour toute autre erreur", async () => {
    Object.defineProperty(navigator, "share", { value: () => Promise.reject(new Error("boom")), configurable: true })
    expect(await partagerNativement(donnees)).toBe("indisponible")
  })
})

describe("ouvrirWhatsApp", () => {
  it("ouvre wa.me avec le message complet", () => {
    const ouvrir = vi.spyOn(window, "open").mockReturnValue(null)
    ouvrirWhatsApp(donnees)
    expect(String(ouvrir.mock.calls[0][0])).toMatch(/^https:\/\/wa\.me\/\?text=/)
    expect(decodeURIComponent(String(ouvrir.mock.calls[0][0]))).toContain("Regarde ce corrigé")
  })
})

describe("copierLienDePartage", () => {
  it("copie le lien seul", async () => {
    const writeText = vi.fn(() => Promise.resolve())
    Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true })
    expect(await copierLienDePartage(donnees)).toBe(true)
    expect(writeText).toHaveBeenCalledWith(`${window.location.origin}/cm/epreuves/maths-bac-c-2023?ref=ABC123`)
  })

  it("renvoie false quand le presse-papiers est refusé", async () => {
    Object.defineProperty(navigator, "clipboard", { value: { writeText: () => Promise.reject(new Error("refusé")) }, configurable: true })
    expect(await copierLienDePartage(donnees)).toBe(false)
  })
})

describe("partageNatifPrefere", () => {
  afterEach(() => Reflect.deleteProperty(window, "matchMedia"))

  const simuler = (tactile: boolean) => {
    Object.defineProperty(navigator, "share", { value: vi.fn(), configurable: true })
    Object.defineProperty(window, "matchMedia", { value: () => ({ matches: tactile }), configurable: true })
  }

  it("préfère le partage natif sur un appareil tactile", () => {
    simuler(true)
    expect(partageNatifPrefere()).toBe(true)
  })

  it("laisse le menu WhatsApp / copier sur ordinateur, même si le navigateur sait partager", () => {
    simuler(false)
    expect(partageNatifPrefere()).toBe(false)
  })
})
