import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { demanderCoursPdf } = vi.hoisted(() => ({ demanderCoursPdf: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ demanderCoursPdf }))

import { telechargerCoursPdf } from "./coursPdf"

beforeEach(() => {
  vi.useFakeTimers()
  demanderCoursPdf.mockReset()
  URL.createObjectURL = vi.fn(() => "blob:test")
  URL.revokeObjectURL = vi.fn()
})

afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
})

describe("telechargerCoursPdf", () => {
  it("redemande tant que le serveur prépare, puis enregistre le fichier sous le nom du cours", async () => {
    const clics: string[] = []
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (this: HTMLAnchorElement) {
      clics.push(this.download)
    })
    demanderCoursPdf
      .mockResolvedValueOnce({ statut: "en_preparation" })
      .mockResolvedValueOnce({ statut: "occupe" })
      .mockResolvedValueOnce(new Blob(["%PDF"], { type: "application/pdf" }))

    const fini = telechargerCoursPdf("les-suites")
    await vi.advanceTimersByTimeAsync(10_000)
    await fini

    expect(demanderCoursPdf).toHaveBeenCalledTimes(3)
    expect(demanderCoursPdf).toHaveBeenCalledWith("les-suites")
    expect(clics).toEqual(["les-suites.pdf"])
  })

  it("abandonne quand le serveur ne l'a toujours pas préparé", async () => {
    demanderCoursPdf.mockResolvedValue({ statut: "en_preparation" })

    const fini = telechargerCoursPdf("les-suites")
    const verifie = expect(fini).rejects.toThrow("pdf_trop_long")
    await vi.advanceTimersByTimeAsync(200_000)
    await verifie
  })

  it("laisse remonter un refus du serveur", async () => {
    demanderCoursPdf.mockRejectedValue(new Error("503"))

    await expect(telechargerCoursPdf("les-suites")).rejects.toThrow("503")
    expect(demanderCoursPdf).toHaveBeenCalledTimes(1)
  })
})
