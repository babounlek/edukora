import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { useFinDeLecture } from "./useFinDeLecture"

function cible(bas: number, hauteur = 800) {
  const el = document.createElement("article")
  el.getBoundingClientRect = () => ({ top: bas - hauteur, bottom: bas, height: hauteur, left: 0, right: 0, width: 0, x: 0, y: 0, toJSON() {} })
  return { current: el }
}

describe("useFinDeLecture", () => {
  beforeEach(() => {
    vi.useFakeTimers()
    Object.defineProperty(window, "innerHeight", { value: 700, configurable: true })
    vi.stubGlobal("requestAnimationFrame", (cb: FrameRequestCallback) => window.setTimeout(() => cb(0), 0))
  })
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it("se déclenche une fois : bas de l'article visible ET délai écoulé", () => {
    const surFin = vi.fn()
    renderHook(() => useFinDeLecture(cible(600), { actif: true, delaiMs: 1000, surFin }))

    act(() => { window.dispatchEvent(new Event("scroll")); vi.advanceTimersByTime(10) })
    expect(surFin).not.toHaveBeenCalled() // arrivé en bas trop vite : ce n'est pas de la lecture

    act(() => { vi.advanceTimersByTime(1000) })
    expect(surFin).toHaveBeenCalledTimes(1)

    act(() => { window.dispatchEvent(new Event("scroll")); vi.advanceTimersByTime(10) })
    expect(surFin).toHaveBeenCalledTimes(1)
  })

  it("ne se déclenche pas tant que le bas de l'article est hors de l'écran", () => {
    const surFin = vi.fn()
    renderHook(() => useFinDeLecture(cible(1500), { actif: true, delaiMs: 100, surFin }))

    act(() => { vi.advanceTimersByTime(500); window.dispatchEvent(new Event("scroll")); vi.advanceTimersByTime(10) })

    expect(surFin).not.toHaveBeenCalled()
  })

  it("ne fait rien quand il est inactif (visiteur)", () => {
    const surFin = vi.fn()
    renderHook(() => useFinDeLecture(cible(600), { actif: false, delaiMs: 100, surFin }))

    act(() => { vi.advanceTimersByTime(500) })

    expect(surFin).not.toHaveBeenCalled()
  })
})
