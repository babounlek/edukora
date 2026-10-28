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
    expect(screen.getByRole("button", { name: "Ouvrir l'espace parent" })).toBeTruthy()
    // Pas de groupe « Aînée » qui afficherait à tort « Choisir un abonnement ».
    expect(screen.queryByText("Aînée")).toBeNull()
    expect(screen.queryByText("Choisir un abonnement")).toBeNull()
    // Verrouillé : ni sécurité des profils ni ajout d'enfant tant que le code parent n'a pas été saisi.
    expect(screen.queryByText("securite-profils")).toBeNull()
    expect(screen.queryByText("Ajouter un enfant")).toBeNull()
    expect(api.listMySubscriptionsFamille).not.toHaveBeenCalled()
  })

  it("« Ouvrir l'espace parent » charge les trois listes de la famille et retire le bandeau", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "Ouvrir l'espace parent" }))

    expect(await screen.findByText("Aînée")).toBeTruthy()
    expect(screen.queryByText(/Tu vois seulement/)).toBeNull()
    // Déverrouillé : la zone de gestion apparaît.
    expect(screen.getByText("securite-profils")).toBeTruthy()
    expect(screen.getByText("Ajouter un enfant")).toBeTruthy()
    expect(api.listMyInscriptionsIneditesFamille).toHaveBeenCalledTimes(1)
    expect(api.listMyInscriptionsRepetiteurFamille).toHaveBeenCalledTimes(1)
  })

  it("annuler la saisie du code parent garde la vue limitée, sans message d'erreur", async () => {
    api.listMySubscriptionsFamille.mockRejectedValue(new ApiError(403, { code: "parent_requis" }))
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "Ouvrir l'espace parent" }))

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
    expect(screen.getByText("securite-profils")).toBeTruthy()
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
    expect(screen.queryByRole("button", { name: "Ouvrir l'espace parent" })).toBeNull()
  })
})

describe("AccesPage - un parent qui a ajouté ses enfants sans rien payer", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    modeParent.actif = false
    auth.user = { id: 1, pin_parent_actif: false, session_restreinte: false, profil_actif: { id: 1, prenom: "Aînée" } }
    api.listProfils.mockResolvedValue(PROFILS)
    api.listMyInscriptionsInedites.mockResolvedValue([])
    api.listMyInscriptionsRepetiteur.mockResolvedValue([])
  })

  it("voit chaque enfant avec son bouton de paiement, au lieu d'un message « aucun accès » générique", async () => {
    api.listMySubscriptions.mockResolvedValue([])
    afficher()

    // Le prénom figure deux fois : dans le résumé (lien vers le bloc) et dans le bloc de l'enfant.
    expect(await screen.findByText("0 sur 2 enfants ont un abonnement actif.")).toBeTruthy()
    expect(screen.getAllByText("Aînée").length).toBeGreaterThanOrEqual(2)
    expect(screen.getAllByText("Cadet").length).toBeGreaterThanOrEqual(2)
    expect(screen.getAllByText("Pas encore abonné")).toHaveLength(2)
    // Un bouton par enfant, qui porte son prénom et emmène vers SES formules.
    expect(screen.getByRole("link", { name: /Payer pour Aînée/ }).getAttribute("href")).toBe("/tarifs?profil=1")
    expect(screen.getByRole("link", { name: /Payer pour Cadet/ }).getAttribute("href")).toBe("/tarifs?profil=2")
    expect(screen.getByText("0 sur 2 enfants ont un abonnement actif.")).toBeTruthy()
  })

  it("distingue l'enfant abonné de celui qui reste à abonner, et le résume", async () => {
    api.listMySubscriptions.mockResolvedValue([abonnement(10, 1)])
    afficher()

    expect(await screen.findByText("1 sur 2 enfants ont un abonnement actif.")).toBeTruthy()
    expect(screen.getByText("Abonné")).toBeTruthy()
    expect(screen.getAllByText("Pas encore abonné")).toHaveLength(1)
    // Seul l'enfant sans abonnement a un bouton de paiement ; le résumé le nomme et renvoie à son bloc.
    expect(screen.queryByRole("link", { name: /Payer pour Aînée/ })).toBeNull()
    expect(screen.getByRole("link", { name: /Payer pour Cadet/ })).toBeTruthy()
    expect(screen.getByRole("link", { name: "Cadet" }).getAttribute("href")).toBe("#profil-2")
  })
})
