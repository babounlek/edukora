import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter, useLocation } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { getMatieres, definirAffichageMatieres, utilisateur, cursusDeclare } = vi.hoisted(() => ({
  getMatieres: vi.fn(),
  definirAffichageMatieres: vi.fn(),
  utilisateur: { current: null as unknown },
  cursusDeclare: { current: null as unknown },
}))
vi.mock("@/api/endpoints", () => ({ getMatieres, definirMatieres: vi.fn(), definirAffichageMatieres }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ user: utilisateur.current, isAuthenticated: Boolean(utilisateur.current) }),
}))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/cursusAccueil", () => ({ useCursusPrepareDeclare: () => cursusDeclare.current }))
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }))

import { BandeauVue } from "./BandeauVue"

const DISPONIBLES = [
  { id: 1, code: "GCE_MATHS", label: "Mathematics" },
  { id: 2, code: "GCE_PHYSICS", label: "Physics" },
]
const CURSUS = { id: 7, examen: "GCE_OL", examen_display: "GCE O Level", series: null }

function Lieu() {
  const { search } = useLocation()
  return <output data-testid="lieu">{search}</output>
}

function afficher(entree: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[entree]}>
        <BandeauVue />
        <Lieu />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function compte(abonne: boolean) {
  utilisateur.current = { id: 1, a_un_abonnement_actif: abonne, abonne_profil_actif: abonne, cursus_prepare: CURSUS }
  cursusDeclare.current = CURSUS
}

beforeEach(() => {
  getMatieres.mockReset()
  definirAffichageMatieres.mockReset()
  getMatieres.mockResolvedValue({
    choisies: [1, 2], disponibles: DISPONIBLES, seulement_mes_matieres: true, affichage_restreint: true, nb_affichees: 2,
  })
  compte(true)
})

describe("BandeauVue", () => {
  it("abonné : seulement ses matières et le lien pour les modifier - ni examen, ni sortie, ni « tout voir »", async () => {
    afficher("/epreuves?cursus=7")
    expect(await screen.findByText("Tu vois seulement tes 2 matières.")).toBeInTheDocument()
    expect(screen.queryByText("GCE O Level")).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Modifier mes matières" })).toHaveAttribute("href", "/mes-acces")
    expect(screen.queryByRole("button")).not.toBeInTheDocument()
  })

  it("abonné sans matières choisies : aucun bandeau", async () => {
    getMatieres.mockResolvedValue({ choisies: [], disponibles: DISPONIBLES })
    const { container } = afficher("/epreuves?cursus=7")
    await waitFor(() => expect(getMatieres).toHaveBeenCalled())
    expect(container.querySelector("p")).toBeNull()
  })

  it("abonné, interrupteur éteint dans Mes accès : le bandeau le dit, sans bouton", async () => {
    getMatieres.mockResolvedValue({ choisies: [1, 2], disponibles: DISPONIBLES, seulement_mes_matieres: false })
    afficher("/epreuves?cursus=7")
    expect(await screen.findByText("Tu vois toutes les matières.")).toBeInTheDocument()
    expect(screen.queryByRole("button")).not.toBeInTheDocument()
  })

  it("visiteur : l'examen, les matières s'il y en a, et « Voir tout le catalogue »", async () => {
    compte(false)
    afficher("/epreuves?cursus=7")
    expect(await screen.findByText("GCE O Level")).toBeInTheDocument()
    expect(await screen.findByText(/tes 2 matières/)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Voir tout le catalogue" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Voir toutes les matières" })).not.toBeInTheDocument()
  })

  it("pour un visiteur, la sortie d'examen retire le cursus et mémorise le choix d'élargir", async () => {
    compte(false)
    afficher("/epreuves?cursus=7")
    fireEvent.click(await screen.findByRole("button", { name: "Voir tout le catalogue" }))
    await waitFor(() => expect(screen.getByTestId("lieu")).toHaveTextContent("tout=1"))
    expect(screen.getByTestId("lieu")).not.toHaveTextContent("cursus=")
  })

  it("même un abonné, une fois la liste élargie (ancien lien), peut revenir à son examen", async () => {
    afficher("/epreuves?tout=1")
    expect(await screen.findByText("Tu vois tous les examens.")).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "Revenir à mon examen" }))
    await waitFor(() => expect(screen.getByTestId("lieu")).not.toHaveTextContent("tout=1"))
  })

  it("se tait sans examen déclaré, et quand rien n'est filtré ni élargi", async () => {
    cursusDeclare.current = null
    const sans = afficher("/epreuves")
    await Promise.resolve()
    expect(sans.container.querySelector("p")).toBeNull()
    sans.unmount()
    cursusDeclare.current = CURSUS
    const neutre = afficher("/epreuves")
    await Promise.resolve()
    expect(neutre.container.querySelector("p")).toBeNull()
  })
})
