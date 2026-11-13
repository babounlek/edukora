import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"
import type { QuizSession } from "@/api/types"

const api = vi.hoisted(() => ({
  creerCompteInvite: vi.fn(),
  startQuizSession: vi.fn(),
  startQuizEssai: vi.fn(),
}))
vi.mock("@/api/endpoints", () => api)
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))

import { clearJetonInvite, setJetonInvite } from "@/lib/invite"
import { lireDefiMemorise } from "@/lib/defiEssai"
import { lireEssai } from "@/lib/quizEssai"
import { lancerQuizGratuit } from "./quizGratuit"

const base = { cursus: 4, subject: 5, theme: 6, source: "essai_anonyme" }
const session = (id: number, essai = false) => ({ id, essai, questions: [{ id: 1, theme_id: 6 }] }) as unknown as QuizSession
const refus = (status: number) => new ApiError(status, "refus")

beforeEach(() => {
  Object.values(api).forEach((m) => m.mockReset())
  sessionStorage.clear()
  clearJetonInvite()
  // Ouvrir un compte invité garde son jeton, comme le fait la vraie fonction.
  api.creerCompteInvite.mockImplementation(async () => setJetonInvite("jeton-invite"))
})

describe("lancerQuizGratuit", () => {
  it("un visiteur reçoit un compte invité puis joue une vraie séance", async () => {
    api.startQuizSession.mockResolvedValue(session(42))

    const chemin = await lancerQuizGratuit({ ...base, connecte: false })

    expect(chemin).toBe("/quiz/session/42")
    expect(api.creerCompteInvite).toHaveBeenCalledTimes(1)
    expect(api.startQuizSession).toHaveBeenCalledWith({ cursus: 4, subject: 5, theme: 6, mode: "PRATIQUE", n: 10 })
    expect(api.startQuizEssai).not.toHaveBeenCalled()
  })

  it("un invité déjà ouvert sur cet appareil est réutilisé, jamais un second", async () => {
    setJetonInvite("jeton-existant")
    api.startQuizSession.mockResolvedValue(session(43))

    await lancerQuizGratuit({ ...base, connecte: false })

    expect(api.creerCompteInvite).not.toHaveBeenCalled()
  })

  it("un connecté joue sur son profil : aucun invité, une vraie séance", async () => {
    api.startQuizSession.mockResolvedValue(session(44))

    const chemin = await lancerQuizGratuit({ ...base, connecte: true })

    expect(chemin).toBe("/quiz/session/44")
    expect(api.creerCompteInvite).not.toHaveBeenCalled()
  })

  it("quand l'invité ne peut pas s'ouvrir (plafond, réseau), retombe sur l'essai sans enregistrement", async () => {
    api.creerCompteInvite.mockRejectedValue(refus(429))
    api.startQuizEssai.mockResolvedValue(session(0, true))

    const chemin = await lancerQuizGratuit({ ...base, connecte: false })

    expect(chemin).toBe("/quiz/essai")
    expect(api.startQuizSession).not.toHaveBeenCalled()
    expect(lireEssai()).not.toBeNull()
  })

  it("un jeton d'invité refusé (401) retombe aussi sur l'essai", async () => {
    setJetonInvite("jeton-perime")
    api.startQuizSession.mockRejectedValue(refus(401))
    api.startQuizEssai.mockResolvedValue(session(0, true))

    expect(await lancerQuizGratuit({ ...base, connecte: false })).toBe("/quiz/essai")
  })

  it("un thème devenu payant (403) remonte tel quel, sans essai de repli", async () => {
    api.startQuizSession.mockRejectedValue(refus(403))

    await expect(lancerQuizGratuit({ ...base, connecte: false })).rejects.toMatchObject({ status: 403 })
    expect(api.startQuizEssai).not.toHaveBeenCalled()
  })

  it("le défi d'un lien suit CETTE séance, pas les suivantes", async () => {
    api.startQuizSession.mockResolvedValue(session(50))

    await lancerQuizGratuit({ ...base, connecte: false, defi: { reussies: 3, total: 5 } })

    expect(lireDefiMemorise(50)).toEqual({ reussies: 3, total: 5 })
    expect(lireDefiMemorise(51)).toBeNull()
    expect(lireDefiMemorise()).toBeNull() // et ce n'est pas celui d'un essai

    api.startQuizSession.mockResolvedValue(session(51))
    await lancerQuizGratuit({ ...base, connecte: false })
    expect(lireDefiMemorise(50)).toBeNull() // un lancement sans défi efface le précédent
  })
})
