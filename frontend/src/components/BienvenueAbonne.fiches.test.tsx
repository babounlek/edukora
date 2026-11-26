import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it, vi } from "vitest"

import { getFichesMatieres } from "@/api/endpoints"
import { BienvenueAbonne } from "@/components/BienvenueAbonne"

vi.mock("@/api/endpoints", () => ({
  getFichesMatieres: vi.fn(),
  getPriorites: vi.fn().mockResolvedValue({ a_deja_repondu: false }),
  getPlanDuJour: vi.fn(),
  startQuizSession: vi.fn(),
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ isAuthenticated: true, user: null }) }))
vi.mock("@/components/RappelsEmail", () => ({ InterrupteurBilanParent: () => null }))

function afficher() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <BienvenueAbonne cursusId={14} country="cm" inclutInedit />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("l'écran après paiement et les fiches", () => {
  it("les cite quand l'examen en a", async () => {
    vi.mocked(getFichesMatieres).mockResolvedValue({
      abonne: true,
      matieres: [{ matiere_id: 10, matiere: "Mathématiques", matiere_code: "MATHS", total: 33, gratuites: 5 }],
    })
    afficher()
    expect(await screen.findByText("Toutes les Fiches EduKora de ton examen")).toBeInTheDocument()
  })

  it("n'en parle pas pour un examen sans fiches", async () => {
    vi.mocked(getFichesMatieres).mockResolvedValue({ abonne: true, matieres: [] })
    afficher()
    await waitFor(() => expect(getFichesMatieres).toHaveBeenCalled())
    expect(screen.queryByText("Toutes les Fiches EduKora de ton examen")).not.toBeInTheDocument()
  })
})
