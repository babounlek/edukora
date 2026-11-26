import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { getFiches, getFichesMatieres } from "@/api/endpoints"
import { LienFiches } from "@/components/fiches/LienFiches"
import { trackEvent } from "@/lib/analytics"

vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ getFiches: vi.fn(), getFichesMatieres: vi.fn() }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ isAuthenticated: false, user: null }) }))

const maths = { matiere_id: 10, matiere: "Mathématiques", matiere_code: "MATHS", total: 33, gratuites: 5 }
const ecm = { matiere_id: 222, matiere: "Éducation Civique", matiere_code: "EDUCATION_CIVIQUE", total: 29, gratuites: 5 }

function afficher(matiereCode?: string | null, themes?: number[]) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <LienFiches source="cours" cursusId={14} matiereCode={matiereCode} themes={themes} />
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

  it("ouvre la fiche du thème le plus fragile qui en a une", async () => {
    const fiche = (id: number, theme: number, terme: string) => ({ id, terme, theme: { id: theme } })
    vi.mocked(getFiches).mockResolvedValue({ abonne: false, fiches: [fiche(1, 70, "Moyenne"), fiche(2, 80, "Thalès")] } as never)
    afficher("MATHS", [99, 80, 70])
    await screen.findByText("Thalès")
    expect(screen.getByRole("link").getAttribute("href")).toBe("/fiches-edukora?cursus=14&matiere=10&fiche=2")
  })

  it("mesure le clic avec son point de départ", async () => {
    afficher("MATHS")
    fireEvent.click(await screen.findByRole("link"))
    expect(trackEvent).toHaveBeenCalledWith("fiche_lien_clic", { source: "cours", cursus_id: 14, matiere_id: 10 })
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
