import { act, renderHook } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { useDebouncedValue } from "./useDebouncedValue"

describe("useDebouncedValue", () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("retourne la valeur initiale immédiatement", () => {
    const { result } = renderHook(() => useDebouncedValue("a", 300))
    expect(result.current).toBe("a")
  })

  it("ne se met à jour qu'après le délai complet", () => {
    const { result, rerender } = renderHook(({ value }) => useDebouncedValue(value, 300), {
      initialProps: { value: "a" },
    })

    rerender({ value: "ab" })
    act(() => vi.advanceTimersByTime(299))
    expect(result.current).toBe("a")

    act(() => vi.advanceTimersByTime(1))
    expect(result.current).toBe("ab")
  })

  it("redémarre le délai à chaque changement intermédiaire - c'est le mécanisme qui évite une requête par frappe", () => {
    const { result, rerender } = renderHook(({ value }) => useDebouncedValue(value, 300), {
      initialProps: { value: "m" },
    })

    // Simule une frappe rapide : "m" -> "ma" -> "mat" -> "maths", chaque lettre à
    // moins de 300ms d'écart - seule la toute dernière valeur doit finir par sortir,
    // jamais un état intermédiaire (voir CataloguePage, où c'est exactement ce
    // comportement qui évite qu'une requête "search=mat" tardive n'écrase le
    // résultat de "search=maths" plus récent).
    rerender({ value: "ma" })
    act(() => vi.advanceTimersByTime(150))
    rerender({ value: "mat" })
    act(() => vi.advanceTimersByTime(150))
    rerender({ value: "maths" })
    act(() => vi.advanceTimersByTime(150))
    expect(result.current).toBe("m")

    act(() => vi.advanceTimersByTime(150))
    expect(result.current).toBe("maths")
  })

  it("nettoie son timer au démontage sans planter", () => {
    const { rerender, unmount } = renderHook(({ value }) => useDebouncedValue(value, 300), {
      initialProps: { value: "a" },
    })
    rerender({ value: "b" })
    expect(() => unmount()).not.toThrow()
  })
})
