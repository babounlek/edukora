import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const api = vi.hoisted(() => ({
  listMySubscriptions: vi.fn(),
  listMyInscriptionsInedites: vi.fn(),
  listMyInscriptionsRepetiteur: vi.fn(),
  listMySubscriptionsFamille: vi.fn(),
  listMyInscriptionsIneditesFamille: vi.fn(),
  listMyInscriptionsRepetiteurFamille: vi.fn(),
  listProfils: vi.fn(),
  createProfil: vi.fn(),
  renameProfil: vi.fn(),
}))

const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  user: {
    id: 1,
    pin_parent_actif: true,
    session_restreinte: false,
    profil_actif: { id: 2, prenom: "Cadet" },
  } as Record<string, unknown>,
}))

const modeParent = vi.hoisted(() => ({ actif: false }))

vi.mock("@/api/endpoints", () => api)
vi.mock("@/api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/client")>()),
  modeParentActif: () => modeParent.actif,
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/components/SecuriteProfils", () => ({ SecuriteProfils: () => <p>securite-profils</p> }))
vi.mock("@/components/ChoixMatieres", () => ({ ChoixMatieres: () => null }))

import { ApiError } from "@/api/client"
import { AccesPage } from "./AccesPage"

const BEPC = { id: 14, examen: "BEPC", examen_display: "BEPC", series: null, country: { code: "CM" } }
const PROFILS = [
  { id: 1, prenom: "Aînée", pin_actif: false },
  { id: 2, prenom: "Cadet", pin_actif: false },
]
const abonnement = (id: number, profilId: number) => ({
  id,
  cursus: BEPC,
  profil: { id: profilId, prenom: profilId === 1 ? "Aînée" : "Cadet" },
  is_active: true,
  expires_at: "2027-06-01T00:00:00Z",
  duration_mode: "JUSQUA_EXAMEN",
  plan_name: null,
})

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/mes-acces"]}>
      <AccesPage />
    </MemoryRouter>,
  )
}

describe("AccesPage - portée de la famille (code parent)", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    modeParent.actif = false
    auth.user = { id: 1, pin_parent_actif: true, session_restreinte: false, profil_actif: { id: 2, prenom: "Cadet" } }
    api.listProfils.mockResolvedValue(PROFILS)
    // Le serveur ne rend que le profil actif tant que le mode parent est fermé.
    api.listMySubscriptions.mockResolvedValue([abonnement(20, 2)])
    api.listMyInscriptionsInedites.mockResolvedValue([])
    api.listMyInscriptionsRepetiteur.mockResolvedValue([])
    api.listMySubscriptionsFamille.mockResolvedValue([abonnement(10, 1), abonnement(20, 2)])
    api.listMyInscriptionsIneditesFamille.mockResolvedValue([])
    api.listMyInscriptionsRepetiteurFamille.mockResolvedValue([])
  })

  it("avec un code parent hors mode parent, ne montre que le profil actif et propose la famille", async () => {
    afficher()

    expect(await screen.findByText(/Tu vois seulement les accès de Cadet/)).toBeTruthy()
    expect(screen.getByRole("button", { name: "Voir toute la famille" })).toBeTruthy()
    // Pas de groupe « Aînée » qui afficherait à tort « Choisir un abonnement ».
    expect(screen.queryByText("Aînée")).toBeNull()
    expect(screen.queryByText("Choisir un abonnement")).toBeNull()
    expect(api.listMySubscriptionsFamille).not.toHaveBeenCalled()
  })

  it("« Voir toute la famille » charge les trois listes de la famille et retire le bandeau", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "Voir toute la famille" }))

    expect(await screen.findByText("Aînée")).toBeTruthy()
    expect(screen.queryByText(/Tu vois seulement/)).toBeNull()
    expect(api.listMyInscriptionsIneditesFamille).toHaveBeenCalledTimes(1)
    expect(api.listMyInscriptionsRepetiteurFamille).toHaveBeenCalledTimes(1)
  })

  it("annuler la saisie du code parent garde la vue limitée, sans message d'erreur", async () => {
    api.listMySubscriptionsFamille.mockRejectedValue(new ApiError(403, { code: "parent_requis" }))
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "Voir toute la famille" }))

    await waitFor(() => expect(api.listMySubscriptionsFamille).toHaveBeenCalledTimes(1))
    expect(api.listMyInscriptionsIneditesFamille).not.toHaveBeenCalled()
    expect(screen.getByText(/Tu vois seulement les accès de Cadet/)).toBeTruthy()
    expect(screen.queryByText("Aînée")).toBeNull()
  })

  it("en mode parent, toute la famille est déjà là : pas de bandeau", async () => {
    modeParent.actif = true
    api.listMySubscriptions.mockResolvedValue([abonnement(10, 1), abonnement(20, 2)])
    afficher()

    expect(await screen.findByText("Aînée")).toBeTruthy()
    expect(screen.queryByText(/Tu vois seulement/)).toBeNull()
  })

  it("sans code parent, tout reste ouvert comme avant", async () => {
    auth.user = { ...auth.user, pin_parent_actif: false }
    api.listMySubscriptions.mockResolvedValue([abonnement(10, 1), abonnement(20, 2)])
    afficher()

    expect(await screen.findByText("Aînée")).toBeTruthy()
    expect(screen.queryByText(/Tu vois seulement/)).toBeNull()
  })

  it("une session enfant ne voit que son profil et n'a pas le bouton de la famille", async () => {
    auth.user = { ...auth.user, session_restreinte: true }
    afficher()

    await screen.findByText("Cadet")
    expect(screen.queryByText("Aînée")).toBeNull()
    expect(screen.queryByRole("button", { name: "Voir toute la famille" })).toBeNull()
  })
})
