import { afterEach, describe, expect, it, vi } from "vitest"

import { carteEnImage, partagerScore, textePartage, type DonneesPartage } from "./partageScore"

const donnees: DonneesPartage = { score: 7, total: 8, xp: 60, serie: 12, nomSite: "EduKora", lien: "https://edukora.africa/?ref=ABC123" }

afterEach(() => {
  vi.restoreAllMocks()
  Reflect.deleteProperty(navigator, "share")
  Reflect.deleteProperty(navigator, "canShare")
})

describe("textePartage", () => {
  it("dit le score, l'XP et la série, et porte le lien de parrainage", () => {
    expect(textePartage(donnees)).toBe(
      "J'ai eu 7/8 à mon quiz sur EduKora (+60 XP, 12 jours de suite). Tu fais mieux ? https://edukora.africa/?ref=ABC123",
    )
  })

  it("n'invente rien : sans XP ni série, le score et le lien suffisent", () => {
    const texte = textePartage({ ...donnees, xp: 0, serie: 1 })
    expect(texte).toBe("J'ai eu 7/8 à mon quiz sur EduKora. Tu fais mieux ? https://edukora.africa/?ref=ABC123")
  })
})

describe("carteEnImage", () => {
  it("renvoie null quand le navigateur ne sait pas dessiner", async () => {
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null)
    expect(await carteEnImage(donnees)).toBeNull()
  })
})

describe("partagerScore", () => {
  it("passe par le partage du téléphone avec la carte quand il sait partager un fichier", async () => {
    const share = vi.fn(() => Promise.resolve())
    Object.defineProperty(navigator, "share", { value: share, configurable: true })
    Object.defineProperty(navigator, "canShare", { value: () => true, configurable: true })
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue({
      fillRect: vi.fn(), beginPath: vi.fn(), arc: vi.fn(), fill: vi.fn(), fillText: vi.fn(),
    } as unknown as CanvasRenderingContext2D)
    vi.spyOn(HTMLCanvasElement.prototype, "toBlob").mockImplementation((cb) => cb(new Blob(["x"], { type: "image/png" })))

    expect(await partagerScore(donnees)).toBe("partage")
    const arg = (share.mock.calls[0] as unknown as [ShareData])[0]
    expect(arg.files).toHaveLength(1)
    expect(arg.text).toContain("7/8")
  })

  it("partage le texte seul quand le fichier n'est pas partageable", async () => {
    const share = vi.fn(() => Promise.resolve())
    Object.defineProperty(navigator, "share", { value: share, configurable: true })
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null)
    expect(await partagerScore(donnees)).toBe("partage")
    expect((share.mock.calls[0] as unknown as [ShareData])[0].files).toBeUndefined()
  })

  it("ouvre WhatsApp quand le navigateur ne sait pas partager", async () => {
    const ouvrir = vi.spyOn(window, "open").mockReturnValue(null)
    expect(await partagerScore(donnees)).toBe("lien")
    expect(ouvrir.mock.calls[0][0]).toMatch(/^https:\/\/wa\.me\/\?text=/)
    expect(decodeURIComponent(String(ouvrir.mock.calls[0][0]))).toContain("ref=ABC123")
  })

  it("ne signale rien quand l'élève ferme le panneau de partage", async () => {
    Object.defineProperty(navigator, "share", {
      value: () => Promise.reject(new DOMException("annulé", "AbortError")), configurable: true,
    })
    const ouvrir = vi.spyOn(window, "open").mockReturnValue(null)
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null)
    expect(await partagerScore(donnees)).toBe("annule")
    expect(ouvrir).not.toHaveBeenCalled()
  })

  it("retombe sur WhatsApp quand le partage natif échoue", async () => {
    Object.defineProperty(navigator, "share", { value: () => Promise.reject(new Error("boum")), configurable: true })
    const ouvrir = vi.spyOn(window, "open").mockReturnValue(null)
    vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(null)
    expect(await partagerScore(donnees)).toBe("lien")
    expect(ouvrir).toHaveBeenCalled()
  })
})
