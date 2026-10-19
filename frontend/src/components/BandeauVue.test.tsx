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
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ user: utilisateur.current }) }))
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
  utilisateur.current = { id: 1, a_un_abonnement_actif: abonne, cursus_prepare: CURSUS }
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
  it("dit l'examen ET les matières en une phrase", async () => {
    afficher("/epreuves?cursus=7")
    expect(await screen.findByText(/tes 2 matières/)).toBeInTheDocument()
    expect(screen.getByText("GCE O Level")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Modifier mes matières" })).toHaveAttribute("href", "/mes-acces")
  })

  it("un abonné n'a aucune sortie d'examen : son accès est celui de son examen", async () => {
    afficher("/epreuves?cursus=7")
    expect(await screen.findByText("GCE O Level")).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Voir tout le catalogue" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: /autre examen/ })).not.toBeInTheDocument()
  })

  it("sans abonnement, la sortie reste « Voir tout le catalogue »", async () => {
    compte(false)
    afficher("/epreuves?cursus=7")
    expect(await screen.findByRole("button", { name: "Voir tout le catalogue" })).toBeInTheDocument()
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

  it("l'interrupteur de matières garde l'examen et passe à « toutes les matières »", async () => {
    definirAffichageMatieres.mockResolvedValue({ choisies: [1, 2], disponibles: DISPONIBLES, seulement_mes_matieres: false })
    afficher("/epreuves?cursus=7")
    getMatieres.mockResolvedValue({ choisies: [1, 2], disponibles: DISPONIBLES, seulement_mes_matieres: false })
    fireEvent.click(await screen.findByRole("button", { name: "Voir toutes les matières" }))
    await waitFor(() => expect(definirAffichageMatieres).toHaveBeenCalledWith(false))
    expect(await screen.findByText(/toutes les matières/, { selector: "span" })).toBeInTheDocument()
    expect(screen.getByTestId("lieu")).toHaveTextContent("cursus=7")
  })

  it("sans matières choisies, le bandeau ne parle que de l'examen", async () => {
    getMatieres.mockResolvedValue({ choisies: [], disponibles: DISPONIBLES })
    afficher("/epreuves?cursus=7")
    expect(await screen.findByText("GCE O Level")).toBeInTheDocument()
    expect(screen.queryByText(/matières/)).not.toBeInTheDocument()
    expect(screen.queryByRole("link", { name: "Modifier mes matières" })).not.toBeInTheDocument()
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
