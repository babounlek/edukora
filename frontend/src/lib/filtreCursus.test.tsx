import { act, renderHook, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import type { ReactNode } from "react"
import { MemoryRouter, useLocation, useSearchParams } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  user: { cursus_prepare: { id: 20, examen_display: "BAC", series: { code: "C" } as { code: string }, langue: undefined as string | undefined } },
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
const listCursus = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ listCursus, listEpreuves: vi.fn() }))

import { memoriserCursusPrepareEnAttente, oublierCursusPrepareEnAttente } from "./cursusPrepare"
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
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={[urlInitiale]}>{children}</MemoryRouter>
      </QueryClientProvider>
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

  it("ne pré-filtre pas sur un examen déclaré dans l'autre langue que l'interface", async () => {
    auth.user.cursus_prepare.langue = "en"
    try {
      const { result } = monter("/cm/epreuves")
      expect(result.current.params.get("cursus")).toBeNull()
    } finally {
      delete (auth.user.cursus_prepare as { langue?: string }).langue
    }
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

describe("useFiltreCursusParDefaut : visiteur sans compte", () => {
  const BAC_C = { id: 20, examen: "BAC", examen_display: "BAC", series: { code: "C" }, langue: "fr" }
  const GCE_AL = { id: 1416, examen: "GCE_AL", examen_display: "GCE A Level", series: null, langue: "en" }

  function monterVisiteur(urlInitiale: string) {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={[urlInitiale]}>{children}</MemoryRouter>
      </QueryClientProvider>
    )
    return renderHook(
      () => {
        useFiltreCursusParDefaut()
        return useSearchParams()[0]
      },
      { wrapper },
    )
  }

  beforeEach(() => {
    auth.isAuthenticated = false
    localStorage.clear()
    oublierCursusPrepareEnAttente()
    listCursus.mockReset()
    listCursus.mockResolvedValue([BAC_C, GCE_AL])
  })
  afterEach(() => {
    auth.isAuthenticated = true
    oublierCursusPrepareEnAttente()
  })

  it("réduit la liste à la série choisie à l'arrivée", async () => {
    memoriserCursusPrepareEnAttente(20)
    const { result } = monterVisiteur("/cm/epreuves")

    await waitFor(() => expect(result.current.get("cursus")).toBe("20"))
  })

  it("sans examen choisi, la liste reste entière et le catalogue n'est pas demandé", async () => {
    const { result } = monterVisiteur("/cm/epreuves")

    await new Promise((r) => setTimeout(r, 30))
    expect(result.current.get("cursus")).toBeNull()
    expect(listCursus).not.toHaveBeenCalled()
  })

  it("un examen gardé qui n'est pas de ce pays ne filtre rien", async () => {
    memoriserCursusPrepareEnAttente(999)
    const { result } = monterVisiteur("/cm/epreuves")

    await waitFor(() => expect(listCursus).toHaveBeenCalled())
    expect(result.current.get("cursus")).toBeNull()
  })

  it("un examen d'une autre langue que l'interface ne filtre pas", async () => {
    memoriserCursusPrepareEnAttente(1416)
    const { result } = monterVisiteur("/cm/epreuves")

    await waitFor(() => expect(listCursus).toHaveBeenCalled())
    expect(result.current.get("cursus")).toBeNull()
  })

  it("« Voir tout » est respecté : tout=1 empêche le pré-filtrage", async () => {
    memoriserCursusPrepareEnAttente(20)
    const { result } = monterVisiteur("/cm/epreuves?tout=1")

    await waitFor(() => expect(listCursus).toHaveBeenCalled())
    expect(result.current.get("cursus")).toBeNull()
  })

  it("un cursus demandé dans l'URL l'emporte sur l'examen du visiteur", async () => {
    memoriserCursusPrepareEnAttente(20)
    const { result } = monterVisiteur("/cm/epreuves?cursus=35")

    await waitFor(() => expect(listCursus).toHaveBeenCalled())
    expect(result.current.get("cursus")).toBe("35")
  })
})
