import { act, render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { QuotaPdf } from "@/api/types"

const getQuotaPdf = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getQuotaPdf }))

import { signalerChangementQuota } from "@/lib/quotaPdf"

import { QuotaPdfInfo } from "./QuotaPdfInfo"

function quota(surcharge: Partial<QuotaPdf> = {}): QuotaPdf {
  return {
    actif: true, profil: "visiteur", limite: 3, utilise: 1, restant: 2, motif: "",
    reinitialisation: "2099-10-25T00:00:00+01:00", fuseau: "Africa/Douala", gratuits: [], ...surcharge,
  }
}

function afficher(doc?: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <QuotaPdfInfo doc={doc} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  getQuotaPdf.mockReset()
})

describe("QuotaPdfInfo", () => {
  it("dit combien de téléchargements il reste, avant tout clic", async () => {
    getQuotaPdf.mockResolvedValue(quota())
    afficher()

    expect(await screen.findByText("Il te reste 2 téléchargements PDF aujourd'hui.")).toBeInTheDocument()
  })

  it("accorde le singulier quand il n'en reste qu'un", async () => {
    getQuotaPdf.mockResolvedValue(quota({ utilise: 2, restant: 1 }))
    afficher()

    expect(await screen.findByText("Il te reste 1 téléchargement PDF aujourd'hui.")).toBeInTheDocument()
  })

  it("dit qu'un document déjà téléchargé aujourd'hui peut être repris sans compter", async () => {
    getQuotaPdf.mockResolvedValue(quota({ utilise: 3, restant: 0, motif: "quota_depasse", gratuits: ["cours:les-suites"] }))
    afficher("cours:les-suites")

    expect(await screen.findByText(/Déjà téléchargé aujourd'hui/)).toBeInTheDocument()
    // Le décompte reste visible, et rien n'annonce un quota épuisé pour un document qu'on peut reprendre.
    expect(screen.getByText("Il te reste 0 téléchargement PDF aujourd'hui.")).toBeInTheDocument()
    expect(screen.queryByText(/limite quotidienne/)).not.toBeInTheDocument()
  })

  it("demande au serveur l'état du document de la page", async () => {
    getQuotaPdf.mockResolvedValue(quota())
    afficher("lesson:12")

    await screen.findByRole("status")
    expect(getQuotaPdf).toHaveBeenCalledWith(["lesson:12"], expect.anything())
  })

  it("invite un visiteur au quota épuisé à se connecter, sans le presser de s'abonner", async () => {
    getQuotaPdf.mockResolvedValue(quota({ utilise: 3, restant: 0, motif: "quota_depasse" }))
    afficher()

    expect(await screen.findByText(/limite quotidienne/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Connecte-toi pour retrouver ton espace personnel." })).toHaveAttribute("href", "/connexion")
    expect(screen.queryByRole("link", { name: /offres/ })).not.toBeInTheDocument()
  })

  it("montre les offres à un connecté sans abonnement dont le quota est épuisé", async () => {
    getQuotaPdf.mockResolvedValue(quota({ profil: "connecte", utilise: 3, restant: 0, motif: "quota_depasse" }))
    afficher()

    expect(await screen.findByRole("link", { name: "Découvre les offres disponibles." })).toHaveAttribute("href", "/tarifs")
  })

  it("ne propose jamais de s'abonner à un abonné", async () => {
    getQuotaPdf.mockResolvedValue(quota({ profil: "abonne", limite: 12, utilise: 12, restant: 0, motif: "quota_depasse" }))
    afficher()

    expect(await screen.findByText(/limite quotidienne/)).toBeInTheDocument()
    expect(screen.queryByRole("link")).not.toBeInTheDocument()
  })

  it("n'affiche rien quand le compteur est introuvable (réseau coupé) : le bouton reste utilisable", async () => {
    getQuotaPdf.mockRejectedValue(new TypeError("Failed to fetch"))
    const { container } = afficher()

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50)) // laisse l'échec arriver jusqu'au composant
    })
    expect(getQuotaPdf).toHaveBeenCalled()
    expect(container).toBeEmptyDOMElement()
  })

  it("n'affiche rien quand les quotas sont suspendus", async () => {
    getQuotaPdf.mockResolvedValue(quota({ actif: false }))
    const { container } = afficher()

    await vi.waitFor(() => expect(getQuotaPdf).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("se met à jour après un téléchargement, avec le chiffre du serveur", async () => {
    getQuotaPdf.mockResolvedValueOnce(quota()).mockResolvedValue(quota({ utilise: 2, restant: 1 }))
    afficher()
    await screen.findByText("Il te reste 2 téléchargements PDF aujourd'hui.")

    signalerChangementQuota()

    expect(await screen.findByText("Il te reste 1 téléchargement PDF aujourd'hui.")).toBeInTheDocument()
  })
})
