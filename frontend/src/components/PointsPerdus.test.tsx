import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getMesPertes = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getMesPertes }))

import { PointsPerdus } from "./PointsPerdus"

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <PointsPerdus />
    </QueryClientProvider>,
  )
}

beforeEach(() => vi.clearAllMocks())

describe("PointsPerdus", () => {
  it("dit où partent les points quand une cause est nommée", async () => {
    getMesPertes.mockResolvedValue({
      copies: 3, total_perdu: 10,
      causes: [
        { cause: "CALCUL", libelle: "Erreur de calcul", points: 6, part: 60 },
        { cause: "TEMPS", libelle: "Manque de temps", points: 4, part: 40 },
      ],
    })
    afficher()

    expect(await screen.findByText("Tes points partent surtout en erreur de calcul (60 %).")).toBeInTheDocument()
    expect(screen.getByText("Sur tes 3 dernières copies rendues")).toBeInTheDocument()
  })

  it("invite à nommer les causes quand elles ne sont pas précisées", async () => {
    getMesPertes.mockResolvedValue({
      copies: 1, total_perdu: 4, causes: [{ cause: "NON_PRECISEE", libelle: "Cause non précisée", points: 4, part: 100 }],
    })
    afficher()

    expect(await screen.findByText(/dis pourquoi tu as perdu des points/)).toBeInTheDocument()
  })

  it("ne montre rien sans copie ni en cas de panne", async () => {
    getMesPertes.mockResolvedValue({ copies: 0, total_perdu: 0, causes: [] })
    const { container } = afficher()

    await vi.waitFor(() => expect(getMesPertes).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })
})
