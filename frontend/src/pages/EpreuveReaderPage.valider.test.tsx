import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { EpreuveExercise } from "@/api/types"

const api = vi.hoisted(() => ({ marquerExerciceFait: vi.fn() }))
vi.mock("@/api/endpoints", async (importOriginal) => ({ ...(await importOriginal<object>()), ...api }))

const auth = vi.hoisted(() => ({ isAuthenticated: false }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ isAuthenticated: auth.isAuthenticated, isLoading: false, user: null }),
}))

import { ValiderResolution } from "./EpreuveReaderPage"

function afficher(exercise: Partial<EpreuveExercise> = {}) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/cm/epreuves/bac-maths-2024/lire"]}>
        <ValiderResolution exercise={{ id: 12, fait: false, ...exercise } as EpreuveExercise} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  api.marquerExerciceFait.mockReset()
})

describe("ValiderResolution (lecteur d'épreuve)", () => {
  it("n'offre pas « Je l'ai fait » à un visiteur : le suivi s'enregistre sur un profil, le clic échouait", () => {
    auth.isAuthenticated = false
    afficher()

    expect(screen.queryByRole("button", { name: /Je l'ai fait/ })).not.toBeInTheDocument()
    expect(screen.getByText(/Connecte-toi pour garder la trace/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Connexion" })).toHaveAttribute("href", "/connexion")
    expect(api.marquerExerciceFait).not.toHaveBeenCalled()
  })

  it("garde le bouton pour un connecté", () => {
    auth.isAuthenticated = true
    afficher()

    expect(screen.getByRole("button", { name: /Je l'ai fait/ })).toBeInTheDocument()
    expect(screen.queryByText(/Connecte-toi pour garder la trace/)).not.toBeInTheDocument()
  })

  it("n'affiche rien pour un exercice sans identifiant, connecté ou non", () => {
    auth.isAuthenticated = false
    const { container } = afficher({ id: undefined })

    expect(container).toBeEmptyDOMElement()
  })
})
