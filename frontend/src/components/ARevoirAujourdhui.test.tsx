import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listRevisionsDues = vi.hoisted(() => vi.fn())
const getErreurs = vi.hoisted(() => vi.fn())
const getCartesDues = vi.hoisted(() => vi.fn())
const getNotesARevoir = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ listRevisionsDues, getErreurs, getCartesDues, getNotesARevoir }))

import { ARevoirAujourdhui } from "./ARevoirAujourdhui"

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <ARevoirAujourdhui cursusId={14} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("ARevoirAujourdhui", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    listRevisionsDues.mockResolvedValue([])
    getErreurs.mockResolvedValue({ total: 0, paquet: 0, plus_ancienne: null, matieres: [] })
    getCartesDues.mockResolvedValue({ total: 0, cartes: [] })
    getNotesARevoir.mockResolvedValue({ total: 0 })
  })

  it("réunit les files qui ont quelque chose à faire, avec leur geste", async () => {
    listRevisionsDues.mockResolvedValue([
      { id: 1, theme: "dérivation", theme_id: 7, subject_label: "Mathématiques", cursus: 14 },
      { id: 2, theme: "autre examen", theme_id: 8, subject_label: "SVT", cursus: 99 },
    ])
    getErreurs.mockResolvedValue({ total: 4, paquet: 4, plus_ancienne: null, matieres: [] })
    getNotesARevoir.mockResolvedValue({ total: 2 })
    afficher()

    const theme = await screen.findByRole("link", { name: /Des thèmes à revoir/ })
    expect(theme).toHaveAttribute("href", "/quiz?cursus=14&theme=7")
    expect(await screen.findByRole("link", { name: /4 questions à refaire/ })).toHaveAttribute("href", "/erreurs")
    expect(await screen.findByRole("link", { name: /2 de tes notes|2 notes/ })).toHaveAttribute("href", "/carnet?reviser=1")
    expect(screen.queryByRole("link", { name: /carte/i })).not.toBeInTheDocument()
  })

  it("se tait quand tout est à jour", async () => {
    afficher()

    await vi.waitFor(() => expect(getErreurs).toHaveBeenCalled())
    expect(screen.queryByRole("region", { name: "À revoir aujourd'hui" })).not.toBeInTheDocument()
  })
})
