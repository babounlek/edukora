import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listProfils = vi.hoisted(() => vi.fn())
const activer = vi.hoisted(() => vi.fn())
const ouvrir = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  login: vi.fn(),
  user: { id: 1, pin_parent_actif: false } as Record<string, unknown>,
}))

vi.mock("@/api/endpoints", () => ({ listProfils }))
vi.mock("@/lib/changerProfilActif", () => ({ activerProfilProtege: activer }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "CM" }) }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/apresConnexion", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/apresConnexion")>()),
  ouvrirDestination: ouvrir,
}))

import { QuiEtudiePage } from "./QuiEtudiePage"

const PROFILS = [
  { id: 1, prenom: "Aînée", pin_actif: false },
  { id: 2, prenom: "Cadet", pin_actif: false },
]

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/qui-etudie"]}>
      <QuiEtudiePage />
    </MemoryRouter>,
  )
}

describe("QuiEtudiePage - rappel du code parent", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    auth.user = { id: 1, pin_parent_actif: false }
    listProfils.mockResolvedValue(PROFILS)
  })

  it("rappelle qu'un code parent protège les autres enfants, avec un lien vers la sécurité de Mes accès", async () => {
    afficher()

    expect(await screen.findByText(/Chaque enfant peut voir les abonnements des autres/)).toBeTruthy()
    const lien = screen.getByRole("link", { name: "Protéger avec un code parent" })
    expect(lien.getAttribute("href")).toBe("/mes-acces#securite")
  })

  it("« Plus tard » masque le rappel et s'en souvient", async () => {
    const { unmount } = afficher()
    fireEvent.click(await screen.findByRole("button", { name: "Plus tard" }))
    expect(screen.queryByText(/Chaque enfant peut voir/)).toBeNull()
    unmount()

    afficher()
    await screen.findByText("Cadet")
    expect(screen.queryByText(/Chaque enfant peut voir/)).toBeNull()
  })

  it("n'affiche rien quand un code parent est déjà défini", async () => {
    auth.user = { id: 1, pin_parent_actif: true }
    afficher()

    await screen.findByText("Cadet")
    expect(screen.queryByText(/Chaque enfant peut voir/)).toBeNull()
  })

  it("n'affiche rien quand un enfant a déjà son propre code", async () => {
    listProfils.mockResolvedValue([{ ...PROFILS[0], pin_actif: true }, PROFILS[1]])
    afficher()

    await waitFor(() => expect(screen.getByText("Cadet")).toBeTruthy())
    expect(screen.queryByText(/Chaque enfant peut voir/)).toBeNull()
  })
})

describe("QuiEtudiePage - choix du profil", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    auth.user = { id: 1, pin_parent_actif: false }
    listProfils.mockResolvedValue(PROFILS)
  })

  async function choisirCadet(profilUser: unknown, from?: string) {
    activer.mockResolvedValue({ access: "jeton", user: profilUser })
    render(
      <MemoryRouter initialEntries={[{ pathname: "/qui-etudie", state: from ? { from } : null }]}>
        <QuiEtudiePage />
      </MemoryRouter>,
    )
    fireEvent.click(await screen.findByRole("button", { name: /Cadet/ }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalled())
    return ouvrir.mock.calls[0][0] as { chemin: string; langue: string | null }
  }

  it("profil du GCE, page demandée : la page est conservée et la langue du profil imposée", async () => {
    const destination = await choisirCadet({ cursus_prepare: { id: 5, langue: "en", country: { code: "CM" } } }, "/cm/epreuves/x")
    expect(destination).toEqual({ chemin: "/cm/epreuves/x", langue: "en" })
  })

  it("sans page demandée : l'accueil du pays de l'examen du profil, pas celui du navigateur", async () => {
    const destination = await choisirCadet({ cursus_prepare: { id: 6, langue: "fr", country: { code: "SN" } } })
    expect(destination.chemin).toBe("/sn")
    expect(destination.langue).toBeNull()
  })
})
