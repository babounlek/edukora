import { beforeEach, describe, expect, it, vi } from "vitest"

import { effacerMarqueAnonyme, estVisiteurAnonymeConnu, marquerVisiteurAnonyme } from "@/lib/sessionAnonyme"

beforeEach(() => {
  localStorage.clear()
  vi.useRealTimers()
})

describe("sessionAnonyme", () => {
  it("ne présume rien d'un navigateur jamais examiné", () => {
    expect(estVisiteurAnonymeConnu()).toBe(false)
  })

  it("retient un visiteur constaté anonyme, puis l'oublie dès qu'un jeton est obtenu", () => {
    marquerVisiteurAnonyme()
    expect(estVisiteurAnonymeConnu()).toBe(true)
    effacerMarqueAnonyme()
    expect(estVisiteurAnonymeConnu()).toBe(false)
  })

  it("revérifie après une semaine", () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date("2026-10-01T10:00:00Z"))
    marquerVisiteurAnonyme()
    vi.setSystemTime(new Date("2026-10-09T10:00:00Z"))
    expect(estVisiteurAnonymeConnu()).toBe(false)
  })
})
