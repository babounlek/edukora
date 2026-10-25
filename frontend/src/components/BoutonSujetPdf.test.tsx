import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { QuotaPdf } from "@/api/types"

const getQuotaPdf = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getQuotaPdf, ouvrirSujetClassique: vi.fn() }))

import { BoutonSujetPdf } from "./BoutonSujetPdf"

function quota(surcharge: Partial<QuotaPdf> = {}): QuotaPdf {
  return {
    actif: true, profil: "visiteur", limite: 3, utilise: 1, restant: 2, motif: "",
    reinitialisation: "2099-10-25T00:00:00+01:00", fuseau: "Africa/Douala", gratuits: [], ...surcharge,
  }
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <BoutonSujetPdf epreuveId={7} url="/sujet.pdf" />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  getQuotaPdf.mockReset()
})

describe("BoutonSujetPdf", () => {
  it("met le compteur dans le bouton, en pastille, sans note dessous", async () => {
    getQuotaPdf.mockResolvedValue(quota())
    afficher()

    const bouton = await screen.findByRole("button", { name: /Télécharger l'épreuve/ })
    expect(await screen.findByText("2 restants")).toBeInTheDocument()
    expect(bouton).toHaveTextContent("2 restants")
    expect(bouton).toHaveAttribute("title", "Il te reste 2 téléchargements PDF aujourd'hui.")
  })

  it("marque en pastille un sujet déjà téléchargé aujourd'hui", async () => {
    getQuotaPdf.mockResolvedValue(quota({ utilise: 3, restant: 0, motif: "quota_depasse", gratuits: ["lesson:7"] }))
    afficher()

    expect(await screen.findByText("Déjà téléchargé")).toBeInTheDocument()
    expect(screen.queryByText(/limite quotidienne/)).not.toBeInTheDocument()
  })

  it("garde le message complet, sous le bouton, quand le quota est épuisé", async () => {
    getQuotaPdf.mockResolvedValue(quota({ utilise: 3, restant: 0, motif: "quota_depasse" }))
    afficher()

    expect(await screen.findByText(/limite quotidienne/)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Télécharger l'épreuve/ })).not.toHaveTextContent("restant")
  })

  it("n'affiche rien de plus que le bouton tant que le compteur n'est pas connu", async () => {
    getQuotaPdf.mockRejectedValue(new Error("réseau"))
    afficher()

    expect(await screen.findByRole("button", { name: "Télécharger l'épreuve" })).toBeEnabled()
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
  })
})
