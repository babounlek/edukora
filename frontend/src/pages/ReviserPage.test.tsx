import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { getErreurs, getCartesDues, getNotesARevoir, listEpreuves, session } = vi.hoisted(() => ({
  getErreurs: vi.fn(),
  getCartesDues: vi.fn(),
  getNotesARevoir: vi.fn(),
  listEpreuves: vi.fn(),
  session: { connecte: true },
}))

vi.mock("@/api/endpoints", () => ({ getErreurs, getCartesDues, getNotesARevoir, listEpreuves, noterCarte: vi.fn(), getCartesCours: vi.fn() }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({
    isAuthenticated: session.connecte,
    user: session.connecte ? { cursus_prepare: { id: 7 } } : null,
  }),
}))

import { ReviserPage } from "./ReviserPage"

function monter() {
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <ReviserPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

const adresse = (nom: RegExp) => screen.getByRole("link", { name: nom }).getAttribute("href")

describe("ReviserPage", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    session.connecte = true
    getErreurs.mockResolvedValue({ total: 0 })
    getCartesDues.mockResolvedValue({ total: 0 })
    getNotesARevoir.mockResolvedValue({ total: 0 })
    listEpreuves.mockResolvedValue({ count: 0, results: [] })
  })

  it("montre les neuf entrées, même quand il n'y a rien à revoir", async () => {
    monter()
    await waitFor(() => expect(getErreurs).toHaveBeenCalledWith(7, expect.anything()))
    expect(screen.getAllByRole("listitem")).toHaveLength(9)
    expect(adresse(/^Épreuves/)).toBe("/cm/epreuves")
    expect(adresse(/^Quiz/)).toBe("/quiz")
    expect(adresse(/^Examens blancs/)).toBe("/examens-blancs")
    expect(adresse(/^Cours/)).toBe("/cm/cours")
    expect(adresse(/^Fiches/)).toBe("/fiches-edukora")
    expect(adresse(/^Thèmes/)).toBe("/cm/themes-frequents")
    expect(adresse(/^Mes erreurs/)).toBe("/erreurs")
    expect(adresse(/^Mes cartes/)).toBe("/cartes")
    expect(adresse(/^Mes notes/)).toBe("/carnet")
  })

  it("dit ce qui attend, et la carte des notes ouvre alors la révision", async () => {
    getErreurs.mockResolvedValue({ total: 12 })
    getCartesDues.mockResolvedValue({ total: 3 })
    getNotesARevoir.mockResolvedValue({ total: 2 })
    monter()
    expect(await screen.findByRole("link", { name: /^Mes erreurs.*12/ })).toBeTruthy()
    expect(await screen.findByRole("link", { name: /^Mes cartes.*3/ })).toBeTruthy()
    expect(await screen.findByRole("link", { name: /^Mes notes.*2 notes/ })).toHaveAttribute("href", "/carnet?reviser=1")
  })

  it("une inédite pas encore vue : la carte Épreuves le dit et mène aux inédites", async () => {
    listEpreuves.mockResolvedValue({ count: 1, results: [{ id: 999999 }] })
    monter()
    await waitFor(() => expect(adresse(/^Épreuves/)).toBe("/cm/epreuves?origine=INEDITE"))
  })

  it("sans compte, les cartes sont là et aucune file personnelle n'est demandée", async () => {
    session.connecte = false
    monter()
    await waitFor(() => expect(listEpreuves).toHaveBeenCalled())
    expect(screen.getAllByRole("listitem")).toHaveLength(9)
    expect(getErreurs).not.toHaveBeenCalled()
    expect(getCartesDues).not.toHaveBeenCalled()
    expect(getNotesARevoir).not.toHaveBeenCalled()
  })
})
