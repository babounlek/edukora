import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { getCoursTitres } = vi.hoisted(() => ({ getCoursTitres: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ getCoursTitres }))

import { reinitialiserTitresCours, titreDuCours } from "./coursTitres"

beforeEach(() => {
  vi.useFakeTimers()
  getCoursTitres.mockReset()
  reinitialiserTitresCours()
})

afterEach(() => {
  vi.useRealTimers()
})

async function laisserPasserLaFenetre() {
  await vi.advanceTimersByTimeAsync(60)
}

describe("titreDuCours", () => {
  it("regroupe en UNE requête tous les slugs demandés dans la même fenêtre", async () => {
    getCoursTitres.mockResolvedValue({ a: "Titre A", b: "Titre B", c: "Titre C" })
    const promesses = [titreDuCours("a"), titreDuCours("b"), titreDuCours("c")]
    await laisserPasserLaFenetre()

    expect(getCoursTitres).toHaveBeenCalledTimes(1)
    expect(getCoursTitres.mock.calls[0][0].sort()).toEqual(["a", "b", "c"])
    expect(await Promise.all(promesses)).toEqual(["Titre A", "Titre B", "Titre C"])
  })

  it("ne redemande jamais un slug déjà connu", async () => {
    getCoursTitres.mockResolvedValue({ a: "Titre A" })
    const premiere = titreDuCours("a")
    await laisserPasserLaFenetre()
    await premiere

    expect(await titreDuCours("a")).toBe("Titre A")
    await laisserPasserLaFenetre()
    expect(getCoursTitres).toHaveBeenCalledTimes(1)
  })

  it("un slug sans titre (inconnu, non publié) donne null", async () => {
    getCoursTitres.mockResolvedValue({ a: "Titre A" })
    const [a, inconnu] = [titreDuCours("a"), titreDuCours("inconnu")]
    await laisserPasserLaFenetre()

    expect(await a).toBe("Titre A")
    expect(await inconnu).toBeNull()
  })

  it("découpe en lots de 50 slugs au plus", async () => {
    getCoursTitres.mockResolvedValue({})
    const slugs = Array.from({ length: 120 }, (_, i) => `s${i}`)
    const promesses = slugs.map((s) => titreDuCours(s))
    await laisserPasserLaFenetre()
    await Promise.all(promesses)

    expect(getCoursTitres.mock.calls.map((c) => c[0].length)).toEqual([50, 50, 20])
  })

  it("un slug vide donne null sans aucune requête", async () => {
    expect(await titreDuCours("")).toBeNull()
    await laisserPasserLaFenetre()

    expect(getCoursTitres).not.toHaveBeenCalled()
  })

  it("une requête en échec donne null, et le slug pourra être redemandé plus tard", async () => {
    getCoursTitres.mockRejectedValueOnce(new Error("réseau"))
    const echec = titreDuCours("a")
    await laisserPasserLaFenetre()
    expect(await echec).toBeNull()

    getCoursTitres.mockResolvedValueOnce({ a: "Titre A" })
    const reprise = titreDuCours("a")
    await laisserPasserLaFenetre()
    expect(await reprise).toBe("Titre A")
  })
})
