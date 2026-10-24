import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { act, renderHook, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
import { MemoryRouter, useSearchParams } from "react-router-dom"
import { afterEach, describe, expect, it, vi } from "vitest"

import type { Cursus } from "@/api/types"

const { listCursus } = vi.hoisted(() => ({ listCursus: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ listCursus }))

import { cursusDeLangue, estDeLangue, langueDuChoix, useAbandonCursusHorsLangue } from "./cursusLangue"
import { definirLangue, useI18n } from "./i18n"

const pays = { id: 1, code: "CM", label: "Cameroun" } as Cursus["country"]
const cursus = (id: number, examen: string, langue: Cursus["langue"]): Cursus => ({
  id, country: pays, examen, examen_display: examen, series: null, langue,
})
const LISTE = [cursus(1, "BEPC", "fr"), cursus(2, "PROBATOIRE", "fr"), cursus(3, "BAC", "fr"), cursus(4, "GCE_OL", "en")]

afterEach(async () => {
  await definirLangue("fr", { persister: false })
  listCursus.mockReset()
})

describe("cursusDeLangue", () => {
  it("français : BEPC, Probatoire et BAC, jamais le GCE", () => {
    expect(cursusDeLangue(LISTE, "fr").map((c) => c.examen)).toEqual(["BEPC", "PROBATOIRE", "BAC"])
  })

  it("anglais : le GCE seul", () => {
    expect(cursusDeLangue(LISTE, "en").map((c) => c.examen)).toEqual(["GCE_OL"])
  })

  it("« toutes les langues » (langue indéfinie) garde tout", () => {
    expect(cursusDeLangue(LISTE, undefined)).toHaveLength(4)
  })

  it("les ids à garder (examen choisi) restent proposés, même hors langue (nombre ou texte d'URL)", () => {
    expect(cursusDeLangue(LISTE, "en", [3]).map((c) => c.id)).toEqual([3, 4])
    expect(cursusDeLangue(LISTE, "en", ["2", null, undefined, ""]).map((c) => c.id)).toEqual([2, 4])
  })

  it("un examen sans information de langue est gardé plutôt que perdu", () => {
    const ancien = { ...cursus(9, "BAC", "fr"), langue: undefined } as unknown as Cursus
    expect(cursusDeLangue([ancien], "en")).toHaveLength(1)
    expect(estDeLangue(ancien, "en")).toBe(true)
    expect(estDeLangue(null, "en")).toBe(true)
  })
})

describe("langueDuChoix", () => {
  it("sans examen choisi : la langue demandée", () => {
    expect(langueDuChoix(LISTE, "en")).toBe("en")
    expect(langueDuChoix(LISTE, "en", ["", null])).toBe("en")
  })

  it("un examen choisi dans l'autre langue fixe la langue des pastilles : jamais BEPC et GCE ensemble", () => {
    const langue = langueDuChoix(LISTE, "en", ["1"])
    expect(langue).toBe("fr")
    expect(cursusDeLangue(LISTE, langue, ["1"]).map((c) => c.examen)).toEqual(["BEPC", "PROBATOIRE", "BAC"])
  })

  it("« toutes les langues » reste ouvert, même avec un examen choisi", () => {
    expect(langueDuChoix(LISTE, undefined, [1])).toBeUndefined()
  })
})

describe("useAbandonCursusHorsLangue", () => {
  function monter(urlInitiale: string) {
    listCursus.mockResolvedValue(LISTE)
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={[urlInitiale]}>{children}</MemoryRouter>
      </QueryClientProvider>
    )
    return renderHook(
      () => {
        useI18n() // comme les pages : se réaffiche au changement de langue
        useAbandonCursusHorsLangue("cm")
        return useSearchParams()[0]
      },
      { wrapper },
    )
  }

  it("ne touche pas à un lien partagé ouvert dans l'autre langue", async () => {
    await definirLangue("en", { persister: false })
    const { result } = monter("/cm/epreuves?cursus=3")
    await waitFor(() => expect(listCursus).toHaveBeenCalled())
    await act(async () => {})
    expect(result.current.get("cursus")).toBe("3")
  })

  it("retire l'examen de l'autre langue quand on change de langue, et garde les autres filtres", async () => {
    const { result } = monter("/cm/epreuves?cursus=3&subject=MATHS")
    await waitFor(() => expect(listCursus).toHaveBeenCalled())
    await act(async () => {})
    expect(result.current.get("cursus")).toBe("3")
    await act(async () => {
      await definirLangue("en", { persister: false })
    })
    await waitFor(() => expect(result.current.get("cursus")).toBeNull())
    expect(result.current.get("subject")).toBe("MATHS")
  })

  it("garde un examen de la nouvelle langue", async () => {
    const { result } = monter("/cm/epreuves?cursus=4")
    await waitFor(() => expect(listCursus).toHaveBeenCalled())
    await act(async () => {})
    await act(async () => {
      await definirLangue("en", { persister: false })
    })
    expect(result.current.get("cursus")).toBe("4")
  })

  it("« toutes les langues » désactive le retrait", async () => {
    const { result } = monter("/cm/epreuves?cursus=3&langues=toutes")
    await waitFor(() => expect(listCursus).toHaveBeenCalled())
    await act(async () => {})
    await act(async () => {
      await definirLangue("en", { persister: false })
    })
    expect(result.current.get("cursus")).toBe("3")
  })
})
