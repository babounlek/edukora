import { QueryClient } from "@tanstack/react-query"
import { beforeEach, describe, expect, it, vi } from "vitest"

const toast = vi.hoisted(() => ({ success: vi.fn() }))
const jouerRetour = vi.hoisted(() => vi.fn())
vi.mock("sonner", () => ({ toast }))
vi.mock("@/lib/retours", () => ({ jouerRetour }))

import { annoncerGain } from "./gainXp"

const jour = { xp: 12, objectif: 20, atteint: false, objectifs_possibles: [10, 20, 30] }

beforeEach(() => {
  toast.success.mockReset()
  jouerRetour.mockReset()
})

describe("annoncerGain", () => {
  it("annonce les points et où en est l'objectif, puis rafraîchit le plan du jour", () => {
    const client = new QueryClient()
    const invalidate = vi.spyOn(client, "invalidateQueries")

    annoncerGain(client, 5, jour)

    expect(toast.success).toHaveBeenCalledWith("+5 points", { description: "12 / 20 points" })
    expect(jouerRetour).toHaveBeenCalledWith("juste")
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["plan-du-jour"] })
  })

  it("ne promet rien quand rien n'est gagné (déjà compté, plafond du jour)", () => {
    const client = new QueryClient()

    annoncerGain(client, 0, jour)
    annoncerGain(client, undefined)

    expect(toast.success).not.toHaveBeenCalled()
    expect(jouerRetour).not.toHaveBeenCalled()
  })

  it("dit « objectif atteint » quand le gain le fait atteindre", () => {
    annoncerGain(new QueryClient(), 5, { ...jour, xp: 20, atteint: true })

    expect(toast.success).toHaveBeenCalledWith("+5 points", { description: "Objectif atteint" })
  })
})
