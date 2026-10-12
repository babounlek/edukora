import { render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"

const getMe = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ getMe, updateMe: vi.fn() }))
vi.mock("@/lib/pwa", () => ({ viderCacheHorsLigne: vi.fn() }))
vi.mock("@/lib/push", () => ({ oublierPushLocal: vi.fn() }))
vi.mock("sonner", () => ({ toast: { error: vi.fn() } }))

import { AuthProvider, useAuth } from "./AuthContext"
import { estVisiteurAnonymeConnu, marquerVisiteurAnonyme } from "@/lib/sessionAnonyme"

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
