import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { getFichesMatieres } from "@/api/endpoints"
import { LienFiches } from "@/components/fiches/LienFiches"

vi.mock("@/api/endpoints", () => ({ getFichesMatieres: vi.fn() }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ isAuthenticated: false, user: null }) }))

const maths = { matiere_id: 10, matiere: "Mathématiques", matiere_code: "MATHS", total: 33, gratuites: 5 }
const ecm = { matiere_id: 222, matiere: "Éducation Civique", matiere_code: "EDUCATION_CIVIQUE", total: 29, gratuites: 5 }

function afficher(matiereCode?: string | null) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <LienFiches cursusId={14} matiereCode={matiereCode} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("LienFiches", () => {
  beforeEach(() => {
    vi.mocked(getFichesMatieres).mockReset()
    vi.mocked(getFichesMatieres).mockResolvedValue({ abonne: false, matieres: [maths, ecm] })
  })

  it("annonce toutes les fiches de l'examen", async () => {
    afficher()
    const lien = await screen.findByRole("link")
    expect(lien).toHaveTextContent("62 Fiches EduKora pour ton examen")
    expect(lien.getAttribute("href")).toBe("/fiches-edukora?cursus=14")
  })

  it("mène aux fiches de la matière du contenu", async () => {
    afficher("MATHS")
    const lien = await screen.findByRole("link")
    expect(lien).toHaveTextContent("Mathématiques : 33 Fiches EduKora")
    expect(lien.getAttribute("href")).toBe("/fiches-edukora?cursus=14&matiere=10")
  })

  it.each([["une matière sans fiches", "SVT"], ["une matière inconnue", null]])("ne promet rien pour %s", async (_, code) => {
    const { container } = afficher(code)
    await waitFor(() => expect(getFichesMatieres).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("ne promet rien pour un examen sans fiches", async () => {
    vi.mocked(getFichesMatieres).mockResolvedValue({ abonne: false, matieres: [] })
    const { container } = afficher()
    await waitFor(() => expect(getFichesMatieres).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })
})
