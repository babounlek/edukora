import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getCandidatureRevendeur = vi.hoisted(() => vi.fn())
const putCandidatureRevendeur = vi.hoisted(() => vi.fn())
const envoyerCodeCandidature = vi.hoisted(() => vi.fn())
const verifierNumeroCandidature = vi.hoisted(() => vi.fn())
const soumettreCandidature = vi.hoisted(() => vi.fn())
const retirerCandidature = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: true, isLoading: false, user: { id: 1 } }))

vi.mock("@/api/endpoints", () => ({
  getCandidatureRevendeur, putCandidatureRevendeur, envoyerCodeCandidature, verifierNumeroCandidature,
  soumettreCandidature, retirerCandidature,
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { ApiError } from "@/api/client"
import type { CandidatureRevendeur, EtatCandidature } from "@/api/types"
import { DevenirRevendeurPage } from "./DevenirRevendeurPage"

const candidature = (surcharges: Partial<CandidatureRevendeur> = {}): CandidatureRevendeur => ({
  id: 1,
  statut: "BROUILLON",
  type: "REPETITEUR",
  nom_affiche: "Paul Mbarga Cours",
  ville: "Douala",
  presentation: "Cours à domicile",
  etablissement: "",
  fonction: "",
  operateur_versement: "ORANGE",
  numero_versement: "699222333",
  numero_verifie: false,
  motif: "",
  code: "",
  soumise_le: null,
  etudiee_le: null,
  ...surcharges,
})

const etat = (surcharges: Partial<EtatCandidature> = {}): EtatCandidature => ({
  candidature: null,
  peut_candidater: true,
  raison: null,
  reouverture_le: null,
  charte_version: "0.1",
  ...surcharges,
})

function rendre() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <DevenirRevendeurPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  for (const f of [
    getCandidatureRevendeur, putCandidatureRevendeur, envoyerCodeCandidature, verifierNumeroCandidature,
    soumettreCandidature, retirerCandidature,
  ]) f.mockReset()
  auth.isAuthenticated = true
  putCandidatureRevendeur.mockResolvedValue(candidature())
})

describe("DevenirRevendeurPage", () => {
  it("explique le principe à un visiteur avant de lui demander de se connecter", async () => {
    auth.isAuthenticated = false

    rendre()

    expect(await screen.findByText("Comment ça marche")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Se connecter pour candidater" })).toHaveAttribute("href", "/connexion")
    expect(getCandidatureRevendeur).not.toHaveBeenCalled()
  })

  it("propose le formulaire à un compte qui peut candidater", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat())

    rendre()

    expect(await screen.findByLabelText("Nom affiché")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Envoyer ma candidature" })).toBeInTheDocument()
    expect(screen.queryByLabelText("Nom de l'établissement")).not.toBeInTheDocument()
  })

  it("demande l'établissement et la fonction pour une école ou un centre", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat())
    const user = userEvent.setup()

    rendre()
    await user.click(await screen.findByLabelText("École ou centre"))

    expect(screen.getByLabelText("Nom de l'établissement")).toBeInTheDocument()
    expect(screen.getByLabelText("Votre fonction")).toBeInTheDocument()
  })

  it("enregistre le brouillon, envoie le code SMS puis vérifie le numéro", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({ candidature: candidature() }))
    envoyerCodeCandidature.mockResolvedValue({ message: "ok" })
    verifierNumeroCandidature.mockResolvedValue(candidature({ numero_verifie: true }))
    const user = userEvent.setup()

    rendre()
    await user.click(await screen.findByRole("button", { name: "Recevoir le code" }))

    expect(putCandidatureRevendeur).toHaveBeenCalledWith(expect.objectContaining({ numero_versement: "699222333", nom_affiche: "Paul Mbarga Cours" }))
    expect(envoyerCodeCandidature).toHaveBeenCalled()
    expect(await screen.findByText("Code envoyé au 699222333.")).toBeInTheDocument()

    await user.type(screen.getByLabelText("Code reçu par SMS"), "123456")
    await user.click(screen.getByRole("button", { name: "Vérifier" }))

    expect(verifierNumeroCandidature).toHaveBeenCalledWith("123456")
    expect(await screen.findByText("Numéro vérifié")).toBeInTheDocument()
  })

  it("dit qu'un code est faux sans révéler autre chose", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({ candidature: candidature() }))
    envoyerCodeCandidature.mockResolvedValue({ message: "ok" })
    verifierNumeroCandidature.mockRejectedValue(new ApiError(400, { code: "code_invalide" }))
    const user = userEvent.setup()

    rendre()
    await user.click(await screen.findByRole("button", { name: "Recevoir le code" }))
    await user.type(await screen.findByLabelText("Code reçu par SMS"), "000000")
    await user.click(screen.getByRole("button", { name: "Vérifier" }))

    expect(await screen.findByRole("alert")).toHaveTextContent(/pas valable|expiré/)
  })

  it("annule la vérification quand le numéro change", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({ candidature: candidature({ numero_verifie: true }) }))
    const user = userEvent.setup()

    rendre()
    expect(await screen.findByText("Numéro vérifié")).toBeInTheDocument()
    const champ = screen.getByLabelText("Numéro de versement")
    await user.clear(champ)
    await user.type(champ, "699444555")

    expect(screen.queryByText("Numéro vérifié")).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Recevoir le code" })).toBeEnabled()
  })

  it("envoie la candidature avec la version de la charte et l'acceptation", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({ candidature: candidature({ numero_verifie: true }) }))
    soumettreCandidature.mockResolvedValue(candidature({ statut: "SOUMISE", numero_verifie: true }))
    const user = userEvent.setup()

    rendre()
    await user.click(await screen.findByRole("checkbox"))
    await user.click(screen.getByRole("button", { name: "Envoyer ma candidature" }))

    await waitFor(() => expect(soumettreCandidature).toHaveBeenCalledWith("0.1", true))
    expect(putCandidatureRevendeur).toHaveBeenCalled()
  })

  it("traduit l'erreur du serveur quand la charte n'est pas acceptée", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({ candidature: candidature({ numero_verifie: true }) }))
    soumettreCandidature.mockRejectedValue(new ApiError(400, { code: "charte_non_acceptee" }))
    const user = userEvent.setup()

    rendre()
    await user.click(await screen.findByRole("button", { name: "Envoyer ma candidature" }))

    expect(await screen.findByRole("alert")).toHaveTextContent("Acceptez la charte du revendeur")
  })

  it("affiche le texte de la charte à la demande", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat())
    const user = userEvent.setup()

    rendre()
    await user.click(await screen.findByRole("button", { name: /Charte du revendeur, version 0.1/ }))

    expect(screen.getByText("Un prix unique")).toBeInTheDocument()
    expect(screen.getByText("Les données des familles")).toBeInTheDocument()
  })

  it("montre la question de l'équipe quand un complément est demandé", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({
      candidature: candidature({ statut: "A_COMPLETER", motif: "Précisez vos zones de vente" }),
    }))

    rendre()

    expect(await screen.findByText("L'équipe a besoin d'un complément")).toBeInTheDocument()
    expect(screen.getByText(/Précisez vos zones de vente/)).toBeInTheDocument()
    expect(screen.getByLabelText("Nom affiché")).toHaveValue("Paul Mbarga Cours")
  })

  it("montre l'état d'une candidature envoyée et permet de la retirer", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({
      candidature: candidature({ statut: "SOUMISE", numero_verifie: true }), peut_candidater: false, raison: "candidature_ouverte",
    }))
    retirerCandidature.mockResolvedValue(candidature({ statut: "RETIREE" }))
    const user = userEvent.setup()

    rendre()
    expect(await screen.findByText("Candidature envoyée")).toBeInTheDocument()
    await user.click(screen.getByRole("button", { name: "Retirer ma candidature" }))

    expect(retirerCandidature).toHaveBeenCalled()
  })

  it("annonce l'acceptation avec le code et le lien vers l'espace", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({
      candidature: candidature({ statut: "ACCEPTEE", code: "PAULM42" }), peut_candidater: false, raison: "deja_revendeur",
    }))

    rendre()

    expect(await screen.findByText(/PAULM42/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Ouvrir mon espace revendeur" })).toHaveAttribute("href", "/espace-revendeur")
  })

  it("explique un refus récent avec la date de réouverture", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({
      candidature: candidature({ statut: "REFUSEE", motif: "Zone déjà couverte" }),
      peut_candidater: false, raison: "refus_recent", reouverture_le: "2026-12-01T10:00:00Z",
    }))

    rendre()

    expect(await screen.findByText("Candidature non retenue")).toBeInTheDocument()
    expect(screen.getByText(/Zone déjà couverte/)).toBeInTheDocument()
    expect(screen.getByText(/Vous pourrez candidater de nouveau à partir du/)).toBeInTheDocument()
    expect(screen.queryByLabelText("Nom affiché")).not.toBeInTheDocument()
  })

  it("renvoie un revendeur vers son espace", async () => {
    getCandidatureRevendeur.mockResolvedValue(etat({ peut_candidater: false, raison: "deja_revendeur" }))

    rendre()

    expect(await screen.findByText("Vous êtes déjà revendeur Edukora.")).toBeInTheDocument()
  })
})
