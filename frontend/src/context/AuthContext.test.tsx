import { render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"

const getMe = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ getMe, updateMe: vi.fn() }))
vi.mock("@/lib/pwa", () => ({ viderCacheHorsLigne: vi.fn() }))
vi.mock("@/lib/push", () => ({ oublierPushLocal: vi.fn() }))
vi.mock("sonner", () => ({ toast: { error: vi.fn() } }))
vi.mock("@/api/client", async (importOriginal) => ({ ...(await importOriginal<typeof import("@/api/client")>()), logoutRequest: vi.fn() }))

import { AuthProvider, useAuth } from "./AuthContext"
import { estVisiteurAnonymeConnu, marquerVisiteurAnonyme } from "@/lib/sessionAnonyme"
import { COUNTRY_STORAGE_KEY } from "@/lib/countryPath"
import { FILTERS_SESSION_KEY } from "@/lib/filtresListe"
import { LANGUE_STORAGE_KEY } from "@/lib/i18n"

function Etat() {
  const { isLoading, isAuthenticated } = useAuth()
  return <p>{isLoading ? "chargement" : isAuthenticated ? "connecté" : "anonyme"}</p>
}

function afficher() {
  return render(
    <AuthProvider>
      <Etat />
    </AuthProvider>,
  )
}

beforeEach(() => {
  getMe.mockReset()
  localStorage.clear()
  sessionStorage.clear()
})

describe("AuthProvider : session au chargement", () => {
  it("retrouve une session existante, comme avant", async () => {
    getMe.mockResolvedValue({ id: 1 })
    afficher()
    expect(await screen.findByText("connecté")).toBeInTheDocument()
  })

  it("retient qu'un visiteur est anonyme après un 401", async () => {
    getMe.mockRejectedValue(new ApiError(401, { detail: "non authentifié" }))
    afficher()
    expect(await screen.findByText("anonyme")).toBeInTheDocument()
    expect(estVisiteurAnonymeConnu()).toBe(true)
  })

  it("n'interroge plus le serveur pour un visiteur déjà constaté anonyme", async () => {
    marquerVisiteurAnonyme()
    afficher()
    expect(await screen.findByText("anonyme")).toBeInTheDocument()
    expect(getMe).not.toHaveBeenCalled()
  })

  it("ne conclut rien d'une simple panne réseau", async () => {
    getMe.mockRejectedValue(new TypeError("Failed to fetch"))
    afficher()
    await waitFor(() => expect(screen.getByText("anonyme")).toBeInTheDocument())
    expect(estVisiteurAnonymeConnu()).toBe(false)
  })
})

describe("AuthProvider : traces du compte précédent", () => {
  function Boutons() {
    const { login, logout } = useAuth()
    return (
      <>
        <button onClick={() => login("jeton", { id: 2, cursus_prepare: { id: 9, country: { code: "SN" } } } as never)}>entrer</button>
        <button onClick={logout}>sortir</button>
      </>
    )
  }

  it("la connexion retient le pays de l'examen et oublie les filtres de liste d'avant", async () => {
    getMe.mockRejectedValue(new ApiError(401, { detail: "non authentifié" }))
    sessionStorage.setItem(FILTERS_SESSION_KEY, "cursus=3")
    render(<AuthProvider><Boutons /></AuthProvider>)
    await waitFor(() => expect(estVisiteurAnonymeConnu()).toBe(true))
    screen.getByText("entrer").click()
    await waitFor(() => expect(localStorage.getItem(COUNTRY_STORAGE_KEY)).toBe("sn"))
    expect(sessionStorage.getItem(FILTERS_SESSION_KEY)).toBeNull()
  })

  it("la déconnexion oublie la langue et les filtres du compte qui part", async () => {
    getMe.mockResolvedValue({ id: 1 })
    localStorage.setItem(LANGUE_STORAGE_KEY, "en")
    sessionStorage.setItem(FILTERS_SESSION_KEY, "cursus=3")
    render(<AuthProvider><Boutons /></AuthProvider>)
    await waitFor(() => expect(screen.getByText("sortir")).toBeInTheDocument())
    screen.getByText("sortir").click()
    await waitFor(() => expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBeNull())
    expect(sessionStorage.getItem(FILTERS_SESSION_KEY)).toBeNull()
  })
})
