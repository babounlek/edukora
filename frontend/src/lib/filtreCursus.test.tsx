import { act, renderHook } from "@testing-library/react"
import type { ReactNode } from "react"
import { MemoryRouter, useLocation, useSearchParams } from "react-router-dom"
import { describe, expect, it, vi } from "vitest"

const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  user: { cursus_prepare: { id: 20, examen_display: "BAC", series: { code: "C" } } },
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))

import { desactiverFiltreCursus, useFiltreCursusParDefaut } from "./filtreCursus"

describe("desactiverFiltreCursus", () => {
  it("retire le cursus et pose tout=1 sans toucher aux autres filtres", () => {
    const params = new URLSearchParams("cursus=20&subject=MATHS")
    const suivant = desactiverFiltreCursus(params)
    expect(suivant.get("cursus")).toBeNull()
    expect(suivant.get("tout")).toBe("1")
    expect(suivant.get("subject")).toBe("MATHS")
  })

  it("est idempotent", () => {
    const params = desactiverFiltreCursus(desactiverFiltreCursus(new URLSearchParams("cursus=20")))
    expect(params.toString()).toBe("tout=1")
  })
})

describe("useFiltreCursusParDefaut", () => {
  function monter(urlInitiale: string) {
    const wrapper = ({ children }: { children: ReactNode }) => (
      <MemoryRouter initialEntries={[urlInitiale]}>{children}</MemoryRouter>
    )
    return renderHook(
      () => {
        useFiltreCursusParDefaut()
        const [params, setParams] = useSearchParams()
        return { params, setParams, search: useLocation().search }
      },
      { wrapper },
    )
  }

  it("applique le cursus par défaut à une arrivée sans paramètres", () => {
    const { result } = monter("/cm/epreuves")
    expect(result.current.params.get("cursus")).toBe("20")
  })

  it("ne remet pas le cursus une fois retiré avec desactiverFiltreCursus", () => {
    const { result } = monter("/cm/epreuves")
    expect(result.current.params.get("cursus")).toBe("20")
    act(() => result.current.setParams((prev) => desactiverFiltreCursus(new URLSearchParams(prev))))
    expect(result.current.params.get("cursus")).toBeNull()
    expect(result.current.params.get("tout")).toBe("1")
  })

  it("laisse un cursus choisi explicitement ensuite", () => {
    const { result } = monter("/cm/epreuves?tout=1")
    expect(result.current.params.get("cursus")).toBeNull()
    act(() =>
      result.current.setParams((prev) => {
        const suivant = new URLSearchParams(prev)
        suivant.set("cursus", "35")
        return suivant
      }),
    )
    expect(result.current.params.get("cursus")).toBe("35")
  })
})
