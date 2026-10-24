import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { QuotaPdf } from "@/api/types"

const api = vi.hoisted(() => ({
  getQuotaPdf: vi.fn(),
  getQuizFichePdfStatus: vi.fn(),
  requestQuizFichePdf: vi.fn(),
  downloadQuizSujetPdf: vi.fn(),
  downloadQuizCorrigePdf: vi.fn(),
}))
vi.mock("@/api/endpoints", () => api)

import { QuizFichePdfButtons } from "./QuizFichePdfButtons"

function quota(surcharge: Partial<QuotaPdf> = {}): QuotaPdf {
  return {
    actif: true, profil: "abonne", limite: 12, utilise: 0, restant: 12, motif: "",
    reinitialisation: "2099-10-25T00:00:00+01:00", fuseau: "Africa/Douala", gratuits: [], ...surcharge,
  }
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <QuizFichePdfButtons sessionId={5} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  api.getQuotaPdf.mockReset()
  api.getQuizFichePdfStatus.mockReset().mockResolvedValue({ statut: "PRETE", sujet_pdf_disponible: true, corrige_pdf_disponible: true })
})

describe("QuizFichePdfButtons", () => {
  it("met le compteur dans chaque bouton, sans note dessous qui décale la barre du bas", async () => {
    api.getQuotaPdf.mockResolvedValue(quota())
    afficher()

    expect(await screen.findByRole("button", { name: /1\. Fiche.*12 restants/ })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /2\. Correction.*12 restants/ })).toBeInTheDocument()
    // La phrase complète n'existe que pour les lecteurs d'écran : rien de visible sous les boutons.
    for (const phrase of screen.getAllByRole("status")) expect(phrase).toHaveClass("sr-only")
  })

  it("signale un PDF déjà téléchargé aujourd'hui dans son bouton", async () => {
    api.getQuotaPdf.mockImplementation(async (docs: string[]) =>
      quota({ restant: 11, gratuits: docs.filter((d) => d === "quiz:5:sujet") }),
    )
    afficher()

    expect(await screen.findByRole("button", { name: /1\. Fiche.*Déjà téléchargé/ })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /2\. Correction.*11 restants/ })).toBeInTheDocument()
  })

  it("dit une seule fois que le quota est atteint, sous les boutons", async () => {
    api.getQuotaPdf.mockResolvedValue(quota({ profil: "abonne", utilise: 12, restant: 0, motif: "quota_depasse" }))
    afficher()

    expect(await screen.findAllByText(/limite quotidienne/)).toHaveLength(1)
    expect(screen.getByRole("button", { name: /1\. Fiche/ })).toBeInTheDocument()
    expect(screen.queryByText(/restants/)).not.toBeInTheDocument()
  })

  it("garde les boutons utilisables quand le compteur est introuvable", async () => {
    api.getQuotaPdf.mockRejectedValue(new TypeError("Failed to fetch"))
    afficher()

    expect(await screen.findByRole("button", { name: "1. Fiche" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "2. Correction" })).toBeEnabled()
  })
})
