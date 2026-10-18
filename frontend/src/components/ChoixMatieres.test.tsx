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
  { id: 6, code: "GCE_GEOGRAPHY", label: "Geography", code_officiel: "0750", couverte: false, obligatoire: false },
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
    // Une obligatoire sans contenu reste signalée « bientôt » même pré-cochée ; une autre, non cochée, est grisée.
    expect(screen.getByRole("button", { name: /English Language.*obligatoire.*bientôt/ })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Geography.*bientôt/ }).className).toContain("opacity-60")
    expect(screen.getByRole("button", { name: /Physics/ }).className).not.toContain("opacity-60")
    expect(screen.getByText(/Les matières grisées sont au programme du Board/)).toBeInTheDocument()
    expect(screen.getByText(/Règles d'inscription du GCE Board/)).toBeInTheDocument()
  })

  it("sans rien d'enregistré, propose les obligatoires pré-cochées sans avertissement, et l'enregistrement reste possible", async () => {
    definirMatieres.mockResolvedValue({
      choisies: [1, 4, 5], disponibles: DISPONIBLES, officielles: OFFICIELLES, regles: REGLES_OL, avertissements: [],
    })
    afficher(<ChoixMatieres />)
    expect(await screen.findByRole("button", { name: /Mathematics/ })).toHaveAttribute("aria-pressed", "true")
    expect(screen.getByRole("button", { name: /English Language/ })).toHaveAttribute("aria-pressed", "true")
    expect(screen.getByRole("button", { name: /French/ })).toHaveAttribute("aria-pressed", "true")
    expect(screen.getByRole("button", { name: /Physics/ })).toHaveAttribute("aria-pressed", "false")
    expect(screen.getByText("3 matières choisies · le Board en demande de 6 à 11")).toBeInTheDocument()
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
    expect(screen.getByText(/Les matières obligatoires sont pré-cochées/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer" }))
    await waitFor(() => expect(definirMatieres).toHaveBeenCalledWith([1, 4, 5]))
  })

  it("une matière obligatoire cochée ne se décoche pas ; une autre, si", async () => {
    afficher(<ChoixMatieres />)
    const maths = await screen.findByRole("button", { name: /Mathematics/ })
    expect(maths).toHaveAttribute("aria-disabled", "true")
    fireEvent.click(maths)
    expect(maths).toHaveAttribute("aria-pressed", "true")
    const physique = screen.getByRole("button", { name: /Physics/ })
    expect(physique).not.toHaveAttribute("aria-disabled")
    fireEvent.click(physique)
    expect(physique).toHaveAttribute("aria-pressed", "true")
    fireEvent.click(physique)
    expect(physique).toHaveAttribute("aria-pressed", "false")
  })

  it("« Toutes les matières » lève le choix par défaut : plus rien n'est coché, ni verrouillé", async () => {
    definirMatieres.mockResolvedValue({
      choisies: [], disponibles: DISPONIBLES, officielles: OFFICIELLES, regles: REGLES_OL, avertissements: [],
    })
    afficher(<ChoixMatieres />)
    await screen.findByRole("button", { name: /Mathematics/ })
    fireEvent.click(screen.getByRole("button", { name: "Toutes les matières" }))
    const maths = screen.getByRole("button", { name: /Mathematics/ })
    expect(maths).toHaveAttribute("aria-pressed", "false")
    expect(maths).not.toHaveAttribute("aria-disabled")
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer" }))
    await waitFor(() => expect(definirMatieres).toHaveBeenCalledWith([]))
  })

  it("un profil déjà enregistré n'est pas modifié d'office : pas de pré-coche, l'avertissement habituel, et une obligatoire cochée se verrouille", async () => {
    getMatieres.mockResolvedValue({
      choisies: [2], disponibles: DISPONIBLES, officielles: OFFICIELLES, regles: REGLES_OL, avertissements: [],
    })
    definirMatieres.mockResolvedValue({
      choisies: [2, 1], disponibles: DISPONIBLES, officielles: OFFICIELLES, regles: REGLES_OL, avertissements: [],
    })
    afficher(<ChoixMatieres />)
    const maths = await screen.findByRole("button", { name: /Mathematics/ })
    expect(maths).toHaveAttribute("aria-pressed", "false")
    expect(screen.getByRole("button", { name: "Enregistrer" })).toBeDisabled()
    const avant = screen.getByRole("status")
    expect(avant).toHaveTextContent("Le Board demande au moins 6 matières : tu en as 1.")
    expect(avant).toHaveTextContent("Mathematics est obligatoire à l'inscription.")
    fireEvent.click(maths)
    expect(maths).toHaveAttribute("aria-pressed", "true")
    expect(maths).toHaveAttribute("aria-disabled", "true")
    const apres = screen.getByRole("status")
    expect(apres).toHaveTextContent("Le Board demande au moins 6 matières : tu en as 2.")
    expect(apres).not.toHaveTextContent("Mathematics est obligatoire")
    expect(apres).toHaveTextContent("English Language est obligatoire à l'inscription.")
    expect(apres).toHaveTextContent("French est obligatoire à l'inscription.")
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer" }))
    await waitFor(() => expect(definirMatieres).toHaveBeenCalledWith([2, 1]))
  })

  it("A Level : aucune matière obligatoire, donc rien de pré-coché ni de verrouillé", async () => {
    eleve("GCE_AL")
    const matieres = [
      { id: 1, code: "GCE_PHYSICS", label: "Physics", code_officiel: "0780", couverte: true, obligatoire: false },
      { id: 2, code: "GCE_ECONOMICS", label: "Economics", code_officiel: "0725", couverte: true, obligatoire: false },
    ]
    getMatieres.mockResolvedValue({
      choisies: [], disponibles: matieres, officielles: matieres, regles: REGLES_AL, avertissements: [],
    })
    afficher(<ChoixMatieres />)
    const physique = await screen.findByRole("button", { name: /Physics/ })
    expect(physique).toHaveAttribute("aria-pressed", "false")
    expect(screen.getByRole("button", { name: /Economics/ })).toHaveAttribute("aria-pressed", "false")
    expect(screen.queryByText(/Les matières obligatoires sont pré-cochées/)).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Enregistrer" })).toBeDisabled()
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
