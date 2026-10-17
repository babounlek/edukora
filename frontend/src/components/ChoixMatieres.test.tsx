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

const OFFICIELLES = [
  { id: 1, code: "GCE_MATHS", label: "Mathematics", code_officiel: "0570", couverte: true, obligatoire: true },
  { id: 2, code: "GCE_PHYSICS", label: "Physics", code_officiel: "0580", couverte: true, obligatoire: false },
  { id: 4, code: "GCE_ENGLISH", label: "English Language", code_officiel: "0530", couverte: false, obligatoire: true },
  { id: 5, code: "GCE_FRENCH", label: "French", code_officiel: "0545", couverte: false, obligatoire: true },
]
const REGLES_OL = { minimum: 6, maximum: 11, obligatoires: ["GCE_ENGLISH", "GCE_FRENCH", "GCE_MATHS"], derniere: "GCE_RELIGION" }
const REGLES_AL = { minimum: null, maximum: 5, obligatoires: [], derniere: null }

describe("ChoixMatieres : règles du Board", () => {
  beforeEach(() => {
    eleve("GCE_OL")
    getMatieres.mockResolvedValue({
      choisies: [], disponibles: DISPONIBLES, officielles: OFFICIELLES, regles: REGLES_OL, avertissements: [],
    })
  })

  it("liste toutes les matières du Board, marque les obligatoires et grise celles qu'EduKora ne couvre pas encore", async () => {
    afficher(<ChoixMatieres />)
    expect(await screen.findByRole("button", { name: /Mathematics.*obligatoire/ })).toBeInTheDocument()
    const anglais = screen.getByRole("button", { name: /English Language.*obligatoire.*bientôt/ })
    expect(anglais.className).toContain("opacity-60")
    expect(screen.getByRole("button", { name: /Physics/ }).className).not.toContain("opacity-60")
    expect(screen.getByText(/Les matières grisées sont au programme du Board/)).toBeInTheDocument()
    expect(screen.getByText(/Règles d'inscription du GCE Board/)).toBeInTheDocument()
  })

  it("n'affiche ni compteur ni avertissement tant que rien n'est choisi", async () => {
    afficher(<ChoixMatieres />)
    await screen.findByRole("button", { name: /Physics/ })
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
    expect(screen.queryByText(/matière choisie|matières choisies/)).not.toBeInTheDocument()
  })

  it("prévient en direct du minimum et des obligatoires manquantes, sans bloquer l'enregistrement", async () => {
    definirMatieres.mockResolvedValue({
      choisies: [2], disponibles: DISPONIBLES, officielles: OFFICIELLES, regles: REGLES_OL, avertissements: [],
    })
    afficher(<ChoixMatieres />)
    fireEvent.click(await screen.findByRole("button", { name: /Physics/ }))
    expect(screen.getByText("1 matière choisie · le Board en demande de 6 à 11")).toBeInTheDocument()
    const avertissements = screen.getByRole("status")
    expect(avertissements).toHaveTextContent("Le Board demande au moins 6 matières : tu en as 1.")
    expect(avertissements).toHaveTextContent("Mathematics est obligatoire à l'inscription.")
    expect(avertissements).toHaveTextContent("English Language est obligatoire à l'inscription.")
    expect(avertissements).toHaveTextContent("French est obligatoire à l'inscription.")
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer" }))
    await waitFor(() => expect(definirMatieres).toHaveBeenCalledWith([2]))
  })

  it("A Level : compteur « au plus » et avertissement au-delà du maximum", async () => {
    eleve("GCE_AL")
    const six = Array.from({ length: 6 }, (_, i) => ({
      id: 10 + i, code: `A${i}`, label: `Matière ${i}`, code_officiel: null, couverte: true, obligatoire: false,
    }))
    getMatieres.mockResolvedValue({
      choisies: six.map((m) => m.id), disponibles: [], officielles: six, regles: REGLES_AL, avertissements: [],
    })
    afficher(<ChoixMatieres />)
    expect(await screen.findByText("6 matières choisies · 5 au plus")).toBeInTheDocument()
    expect(screen.getByRole("status")).toHaveTextContent("Le Board en autorise 5 au plus : tu en as 6.")
  })

  it("sans matières officielles (hors GCE général), l'écran reste celui d'avant : ni règles ni grisées", async () => {
    getMatieres.mockResolvedValue({ choisies: [], disponibles: DISPONIBLES })
    afficher(<ChoixMatieres />)
    await screen.findByRole("button", { name: "Mathematics" })
    expect(screen.queryByText(/Règles d'inscription du GCE Board/)).not.toBeInTheDocument()
    expect(screen.queryByText(/bientôt/)).not.toBeInTheDocument()
  })

  it("l'invitation compte les matières du Board, pas seulement celles qui ont du contenu", async () => {
    getMatieres.mockResolvedValue({
      choisies: [], disponibles: [DISPONIBLES[0]], officielles: OFFICIELLES, regles: REGLES_OL, avertissements: [],
    })
    afficher(<InvitationMatieres />)
    expect(await screen.findByText("Choisis les matières que tu passes")).toBeInTheDocument()
  })
})
