import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { CompteARebours, Cursus } from "@/api/types"

const api = vi.hoisted(() => ({ getCompteAReboursCursus: vi.fn() }))
vi.mock("@/api/endpoints", () => api)

const etat = vi.hoisted(() => ({
  isAuthenticated: false,
  user: null as unknown,
  declare: null as unknown,
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ isAuthenticated: etat.isAuthenticated, user: etat.user }) }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/cursusAccueil", () => ({ useCursusPrepareDeclare: () => etat.declare }))

import { CompteAReboursBadge } from "./CompteAReboursBadge"

const bacD = { id: 7, examen_display: "BAC", series: { code: "D" } } as unknown as Cursus
const compte = (surcharge: Partial<CompteARebours> = {}): CompteARebours => ({
  date_examen: "2027-05-24", jours_restants: 244, session_label: "BAC 2027", estimee: false, ...surcharge,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <CompteAReboursBadge />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  api.getCompteAReboursCursus.mockReset()
  etat.isAuthenticated = false
  etat.user = null
  etat.declare = null
})

describe("CompteAReboursBadge", () => {
  it("donne le décompte à un visiteur qui a choisi son examen, sans répéter l'examen déjà dans la pastille voisine", async () => {
    etat.declare = bacD
    api.getCompteAReboursCursus.mockResolvedValue(compte())
    afficher()

    expect(await screen.findByText("J-244")).toBeInTheDocument()
    expect(screen.queryByText(/BAC D/)).not.toBeInTheDocument()
    expect(api.getCompteAReboursCursus).toHaveBeenCalledWith(7, expect.anything())
  })

  it("dit « vers mai 2027 » quand la date n'est qu'estimée, jamais un nombre de jours inventé", async () => {
    etat.declare = bacD
    api.getCompteAReboursCursus.mockResolvedValue(compte({ estimee: true, jours_restants: 613 }))
    afficher()

    expect(await screen.findByText(/mai 2027/)).toBeInTheDocument()
    expect(screen.queryByText(/J-613/)).not.toBeInTheDocument()
  })

  it("n'affiche rien, et ne demande rien, tant que le visiteur n'a pas choisi son examen", () => {
    const { container } = afficher()

    expect(container).toBeEmptyDOMElement()
    expect(api.getCompteAReboursCursus).not.toHaveBeenCalled()
  })

  it("n'affiche rien quand aucune session d'examen n'est saisie", async () => {
    etat.declare = bacD
    api.getCompteAReboursCursus.mockResolvedValue(null)
    const { container } = afficher()

    await vi.waitFor(() => expect(api.getCompteAReboursCursus).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("garde pour un compte son affichage d'avant (examen + jours, reçus avec le profil), sans rien demander", () => {
    etat.isAuthenticated = true
    etat.user = { cursus_prepare: bacD, compte_a_rebours: compte() }
    etat.declare = bacD
    afficher()

    expect(screen.getByText("BAC D · J-244")).toBeInTheDocument()
    expect(api.getCompteAReboursCursus).not.toHaveBeenCalled()
  })
})
