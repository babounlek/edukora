import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getErreurs = vi.hoisted(() => vi.fn())
const refaireErreurs = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getErreurs, refaireErreurs }))

import { LigneErreurs } from "./MesErreurs"

function afficher(element: React.ReactNode) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/cm"]}>
        <Routes>
          <Route path="/cm" element={element} />
          <Route path="/quiz/session/:id" element={<p>Quiz des erreurs</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe("LigneErreurs (accueil)", () => {
  it("ne dit rien sans erreur", () => {
    const { container } = afficher(<LigneErreurs total={0} cursusId={14} />)

    expect(container).toBeEmptyDOMElement()
  })

  it("annonce le nombre, mène à la page, et refait un paquet en un geste", async () => {
    refaireErreurs.mockResolvedValue({ id: 5 })
    afficher(<LigneErreurs total={12} cursusId={14} />)

    expect(screen.getByRole("link", { name: /12 erreurs à corriger/ })).toHaveAttribute("href", "/erreurs")
    await userEvent.click(screen.getByRole("button", { name: /Refaire/ }))

    await waitFor(() => expect(refaireErreurs).toHaveBeenCalledWith({ cursus: 14 }))
    expect(await screen.findByText("Quiz des erreurs")).toBeInTheDocument()
  })

  it("accorde au singulier", () => {
    afficher(<LigneErreurs total={1} cursusId={14} />)

    expect(screen.getByText("1 erreur à corriger")).toBeInTheDocument()
  })
})
