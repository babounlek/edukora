import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { getMatieres, definirMatieres, utilisateur } = vi.hoisted(() => ({
  getMatieres: vi.fn(),
  definirMatieres: vi.fn(),
  utilisateur: { current: null as unknown },
}))
vi.mock("@/api/endpoints", () => ({ getMatieres, definirMatieres }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ user: utilisateur.current }) }))
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }))

import { ChoixMatieres, InvitationMatieres } from "./ChoixMatieres"

const DISPONIBLES = [
  { id: 1, code: "GCE_MATHS", label: "Mathematics" },
  { id: 2, code: "GCE_PHYSICS", label: "Physics" },
  { id: 3, code: "GCE_HISTORY", label: "History" },
]

function afficher(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}

function eleve(examen: string) {
  utilisateur.current = { id: 1, cursus_prepare: { id: 7, examen } }
}

beforeEach(() => {
  getMatieres.mockReset()
  definirMatieres.mockReset()
  getMatieres.mockResolvedValue({ choisies: [], disponibles: DISPONIBLES })
  eleve("GCE_AL")
})

describe("ChoixMatieres", () => {
  it("liste les matières disponibles et enregistre la sélection", async () => {
    definirMatieres.mockResolvedValue({ choisies: [1, 3], disponibles: DISPONIBLES })
    afficher(<ChoixMatieres />)
    const maths = await screen.findByRole("button", { name: "Mathematics" })
    fireEvent.click(maths)
    fireEvent.click(screen.getByRole("button", { name: "History" }))
    expect(maths).toHaveAttribute("aria-pressed", "true")
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer" }))
    await waitFor(() => expect(definirMatieres).toHaveBeenCalledWith([1, 3]))
  })

  it("n'enregistre rien tant que rien n'a changé", async () => {
    afficher(<ChoixMatieres />)
    await screen.findByRole("button", { name: "Mathematics" })
    expect(screen.getByRole("button", { name: "Enregistrer" })).toBeDisabled()
  })

  it("« Toutes les matières » vide le choix", async () => {
    getMatieres.mockResolvedValue({ choisies: [2], disponibles: DISPONIBLES })
    definirMatieres.mockResolvedValue({ choisies: [], disponibles: DISPONIBLES })
    afficher(<ChoixMatieres />)
    expect(await screen.findByRole("button", { name: "Physics" })).toHaveAttribute("aria-pressed", "true")
    fireEvent.click(screen.getByRole("button", { name: "Toutes les matières" }))
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer" }))
    await waitFor(() => expect(definirMatieres).toHaveBeenCalledWith([]))
  })
})

describe("InvitationMatieres", () => {
  it("invite un élève du GCE qui n'a rien choisi", async () => {
    afficher(<InvitationMatieres />)
    expect(await screen.findByText("Choisis les matières que tu passes")).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "Choisir mes matières" }))
    expect(await screen.findByRole("button", { name: "Mathematics" })).toBeInTheDocument()
  })

  it("se tait hors GCE, sans même interroger le serveur", async () => {
    eleve("BAC")
    const { container } = afficher(<InvitationMatieres />)
    await Promise.resolve()
    expect(container).toBeEmptyDOMElement()
    expect(getMatieres).not.toHaveBeenCalled()
  })

  it("se tait une fois un choix enregistré", async () => {
    getMatieres.mockResolvedValue({ choisies: [1], disponibles: DISPONIBLES })
    const { container } = afficher(<InvitationMatieres />)
    await waitFor(() => expect(getMatieres).toHaveBeenCalled())
    await waitFor(() => expect(container).toBeEmptyDOMElement())
  })

  it("se tait quand il n'y a rien à choisir", async () => {
    getMatieres.mockResolvedValue({ choisies: [], disponibles: [DISPONIBLES[0]] })
    const { container } = afficher(<InvitationMatieres />)
    await waitFor(() => expect(getMatieres).toHaveBeenCalled())
    await waitFor(() => expect(container).toBeEmptyDOMElement())
  })
})
