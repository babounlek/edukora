import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getNoteEstimee = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getNoteEstimee }))

import { BulletinPrevisionnel } from "./BulletinPrevisionnel"

function afficher() {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <BulletinPrevisionnel />
    </QueryClientProvider>,
  )
}

const estimee = (surcharges = {}) => ({
  subject_id: 1, subject_label: "Mathématiques", subject_code: "MATHS", statut: "estimee", bas: 9, haut: 11, calibre: false,
  examens_blancs: 0, reponses: 40, themes_rentables: [{ theme: "Dérivées", points: 1.5, reponses: 8 }], ...surcharges,
})

beforeEach(() => vi.clearAllMocks())

describe("BulletinPrevisionnel", () => {
  it("ne montre rien tant que le serveur ne l'active pas", async () => {
    getNoteEstimee.mockResolvedValue({ actif: false })
    const { container } = afficher()
    await new Promise((r) => setTimeout(r, 20))
    expect(container.textContent).toBe("")
  })

  it("montre une fourchette, jamais un chiffre, avec les thèmes qui rapportent le plus", async () => {
    getNoteEstimee.mockResolvedValue({ actif: true, relecture: false, matieres: [estimee()], moyenne: { bas: 9, haut: 11, matieres: 1, total: 3 } })
    afficher()
    expect(await screen.findByText("9 à 11 sur 20")).toBeInTheDocument()
    expect(screen.getByText(/Dérivées \(\+1,5\)/)).toBeInTheDocument()
    expect(screen.getByText("À confirmer par un examen blanc.")).toBeInTheDocument()
    expect(screen.queryByText(/relecture/i)).not.toBeInTheDocument()
  })

  it("dit combien il manque au lieu de deviner", async () => {
    getNoteEstimee.mockResolvedValue({
      actif: true, relecture: false, moyenne: null,
      matieres: [{ subject_id: 2, subject_label: "Physique", subject_code: "PCT", statut: "pas_assez", reponses: 8, reponses_min: 20, couverture_pct: 60, couverture_min_pct: 40 }],
    })
    afficher()
    expect(await screen.findByText("Encore 12 réponses pour estimer ta note.")).toBeInTheDocument()
    expect(screen.queryByText(/sur 20/)).not.toBeInTheDocument()
  })

  it("avertit le personnel que c'est un aperçu de relecture", async () => {
    getNoteEstimee.mockResolvedValue({ actif: true, relecture: true, matieres: [estimee()], moyenne: null })
    afficher()
    expect(await screen.findByText(/Aperçu de relecture/)).toBeInTheDocument()
  })
})
