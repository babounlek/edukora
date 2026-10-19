import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter, useLocation } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { listCursus, updateMe, memoriser, getMatieres, definirMatieres, auth, updateUser } = vi.hoisted(() => ({
  listCursus: vi.fn(),
  updateMe: vi.fn(),
  memoriser: vi.fn(),
  getMatieres: vi.fn(),
  definirMatieres: vi.fn(),
  updateUser: vi.fn(),
  auth: { current: { isAuthenticated: false, user: null } as { isAuthenticated: boolean; user: unknown } },
}))
vi.mock("@/api/endpoints", () => ({ listCursus, updateMe, getMatieres, definirMatieres }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/cursusPrepare", () => ({ memoriserCursusPrepareEnAttente: memoriser }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ isAuthenticated: auth.current.isAuthenticated, updateUser, user: auth.current.user }),
}))
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }))
vi.mock("@/context/CountryContext", () => ({
  useCountry: () => ({
    country: "cm",
    countries: [{ id: 1, code: "CM", label: "Cameroun", has_lessons: true }],
    setCountry: vi.fn(),
  }),
}))

import { definirLangue } from "@/lib/i18n"
import { OnboardingModal } from "./OnboardingModal"

const pays = { id: 1, code: "CM", label: "Cameroun" }
const serie = (id: number, code: string, label: string) => ({ id, code, label })
const CURSUS = [
  { id: 1, country: pays, examen: "BEPC", examen_display: "BEPC", series: null, langue: "fr" },
  { id: 2, country: pays, examen: "BAC", examen_display: "BAC", series: serie(1, "C", "Maths"), langue: "fr" },
  { id: 3, country: pays, examen: "BAC", examen_display: "BAC", series: serie(2, "D", "Sciences"), langue: "fr" },
  { id: 4, country: pays, examen: "GCE_AL", examen_display: "GCE A Level", series: null, langue: "en" },
  { id: 5, country: pays, examen: "GCE_AL", examen_display: "GCE A Level", series: serie(9, "GCE_TECHNICAL", "Technical"), langue: "en" },
]

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/cm"]}>
      <OnboardingModal />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  localStorage.clear()
  listCursus.mockReset()
  memoriser.mockReset()
  getMatieres.mockReset()
  definirMatieres.mockReset()
  updateMe.mockReset()
  updateUser.mockReset()
  auth.current = { isAuthenticated: false, user: null }
  listCursus.mockResolvedValue(CURSUS)
})

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("OnboardingModal", () => {
  it("GCE : propose la branche générale ET technique, sans mot « Série »", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "GCE A Level" }))
    expect(screen.getByText("Which series are you in?")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "General" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Technical" })).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "General" }))
    await waitFor(() => expect(memoriser).toHaveBeenCalledWith(4))
  })

  it("GCE technique : déclare le cursus technique", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "GCE A Level" }))
    fireEvent.click(screen.getByRole("button", { name: "Technical" }))
    await waitFor(() => expect(memoriser).toHaveBeenCalledWith(5))
  })

  it("BAC : toujours une liste de séries, inchangée", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "BAC" }))
    expect(screen.getByRole("button", { name: "Série C" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Série D" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Général" })).not.toBeInTheDocument()
  })

  it("en français, seuls BEPC, Probatoire et BAC sont proposés, jamais le GCE", async () => {
    afficher()
    await screen.findByRole("button", { name: "BAC" })
    expect(screen.getByRole("button", { name: "BEPC" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "GCE A Level" })).not.toBeInTheDocument()
  })

  it("en anglais, seul le GCE est proposé, jamais BEPC ni BAC", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    await screen.findByRole("button", { name: "GCE A Level" })
    expect(screen.queryByRole("button", { name: "BAC" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "BEPC" })).not.toBeInTheDocument()
  })

  it("BEPC : confirmation sans choix de série, inchangée", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "BEPC" }))
    expect(screen.getByRole("button", { name: "Oui, c'est mon examen" })).toBeInTheDocument()
  })

  it("BAC série C : le choix mémorisé, l'élève reste sur l'accueil et non sur le catalogue", async () => {
    afficherAvecLieu()
    fireEvent.click(await screen.findByRole("button", { name: "BAC" }))
    fireEvent.click(await screen.findByRole("button", { name: "Série C" }))

    await waitFor(() => expect(memoriser).toHaveBeenCalledWith(2))
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument())
    expect(screen.getByTestId("lieu")).toHaveTextContent(/^\/cm$/)
  })

  it("invite à passer dans l'autre sous-système, au choix de l'examen", async () => {
    afficher()
    // Version française : seuls BEPC, Probatoire et BAC sont listés, l'élève du GCE est invité à passer en anglais.
    await screen.findByRole("button", { name: "BEPC" })
    expect(screen.getByText(/Tu prépares le GCE/)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Switch to English" })).toBeInTheDocument()
  })

  it("version anglaise : invite vers le BEPC, le Probatoire et le BAC", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    await screen.findByRole("button", { name: "GCE A Level" })
    expect(screen.getByRole("button", { name: "Passer en français" })).toBeInTheDocument()
  })

  it("pas d'invitation quand le pays n'a aucun examen de l'autre langue", async () => {
    listCursus.mockResolvedValue(CURSUS.filter((c) => c.langue === "fr"))
    afficher()
    await screen.findByRole("button", { name: "BEPC" })
    expect(screen.queryByRole("button", { name: "Switch to English" })).not.toBeInTheDocument()
  })
})


function Lieu() {
  const lieu = useLocation()
  return <p data-testid="lieu">{lieu.pathname + lieu.search}</p>
}

function afficherAvecLieu() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={["/cm"]}>
        <OnboardingModal />
        <Lieu />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

/** Fin de l'écran : la fenêtre est partie et l'élève est resté sur l'accueil, sans filtre d'épreuves. */
async function finiSurLAccueil() {
  await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument())
  expect(screen.getByTestId("lieu")).toHaveTextContent(/^\/cm$/)
}

const MATIERES = {
  choisies: [],
  disponibles: [{ id: 1, code: "GCE_MATHS", label: "Mathematics" }],
  officielles: [{ id: 1, code: "GCE_MATHS", label: "Mathematics", code_officiel: "0570", couverte: true, obligatoire: true }],
  regles: { minimum: null, maximum: 5, obligatoires: [], derniere: null },
  avertissements: [],
}

describe("OnboardingModal : étape des matières (GCE, élève connecté)", () => {
  /** Élève connecté sans cursus ; sa déclaration (updateMe) le met à jour comme le ferait updateUser. */
  function eleveSansCursus(echecDeclaration = false) {
    auth.current = { isAuthenticated: true, user: { id: 1, cursus_prepare: null } }
    if (echecDeclaration) {
      updateMe.mockRejectedValue(new Error("réseau"))
      return
    }
    updateMe.mockImplementation((donnees: { cursus_prepare: number }) => {
      auth.current = { isAuthenticated: true, user: { id: 1, cursus_prepare: { id: donnees.cursus_prepare, examen: "GCE_AL" } } }
      return Promise.resolve({ id: 1 })
    })
  }

  async function jusquALaBrancheGenerale() {
    await definirLangue("en", { persister: false })
    afficherAvecLieu()
    fireEvent.click(await screen.findByRole("button", { name: "GCE A Level" }))
    fireEvent.click(screen.getByRole("button", { name: "General" }))
  }

  it("déclare le cursus puis demande les matières avant de partir", async () => {
    eleveSansCursus()
    getMatieres.mockResolvedValue(MATIERES)
    await jusquALaBrancheGenerale()
    await waitFor(() => expect(updateMe).toHaveBeenCalledWith({ cursus_prepare: 4 }))
    expect(await screen.findByText("Which subjects are you sitting?")).toBeInTheDocument()
    // La fenêtre reste ouverte et on n'a pas encore quitté l'accueil.
    expect(screen.getByTestId("lieu")).toHaveTextContent("/cm")
    expect(screen.getByTestId("lieu")).not.toHaveTextContent("cursus=")
  })

  it("« Continue » ferme la fenêtre et reste sur l'accueil", async () => {
    eleveSansCursus()
    getMatieres.mockResolvedValue(MATIERES)
    await jusquALaBrancheGenerale()
    fireEvent.click(await screen.findByRole("button", { name: "Continue" }))
    await finiSurLAccueil()
  })

  it("enregistrer ses matières ramène aussi sur l'accueil", async () => {
    eleveSansCursus()
    getMatieres.mockResolvedValue(MATIERES)
    definirMatieres.mockResolvedValue({ ...MATIERES, choisies: [1] })
    await jusquALaBrancheGenerale()
    fireEvent.click(await screen.findByRole("button", { name: /Mathematics/ }))
    fireEvent.click(screen.getByRole("button", { name: "Save" }))
    await waitFor(() => expect(definirMatieres).toHaveBeenCalledWith([1]))
    await finiSurLAccueil()
  })

  it("« Skip » à cette étape quitte sans rien enregistrer", async () => {
    eleveSansCursus()
    getMatieres.mockResolvedValue(MATIERES)
    await jusquALaBrancheGenerale()
    await screen.findByText("Which subjects are you sitting?")
    fireEvent.click(screen.getByRole("button", { name: "Skip" }))
    await finiSurLAccueil()
    expect(definirMatieres).not.toHaveBeenCalled()
  })

  it("si la déclaration du cursus échoue, l'élève retombe quand même sur l'accueil", async () => {
    eleveSansCursus(true)
    await jusquALaBrancheGenerale()
    await finiSurLAccueil()
  })

  it("la branche technique n'a pas d'étape de matières", async () => {
    eleveSansCursus()
    await definirLangue("en", { persister: false })
    afficherAvecLieu()
    fireEvent.click(await screen.findByRole("button", { name: "GCE A Level" }))
    fireEvent.click(screen.getByRole("button", { name: "Technical" }))
    await finiSurLAccueil()
    expect(screen.queryByText("Which subjects are you sitting?")).not.toBeInTheDocument()
  })

  it("un visiteur anonyme ne voit pas l'étape : son choix se fera après connexion", async () => {
    await jusquALaBrancheGenerale()
    await waitFor(() => expect(memoriser).toHaveBeenCalledWith(4))
    expect(screen.queryByText("Which subjects are you sitting?")).not.toBeInTheDocument()
    expect(getMatieres).not.toHaveBeenCalled()
  })
})
