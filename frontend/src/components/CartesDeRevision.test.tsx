import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { CarteRevision } from "@/api/types"

const { getCartesCours, getCartesDues, noterCarte } = vi.hoisted(() => ({
  getCartesCours: vi.fn(), getCartesDues: vi.fn(), noterCarte: vi.fn(),
}))
vi.mock("@/api/endpoints", () => ({ getCartesCours, getCartesDues, noterCarte }))
vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <span>{markdown}</span> }))
vi.mock("@/components/JalonsAtteints", () => ({ JalonsAtteints: () => <p>Jalons du paquet</p> }))

import { CartesDuCours, LigneCartes } from "./CartesDeRevision"

const carte = (extra: Partial<CarteRevision> = {}): CarteRevision => ({
  cle: "regle", type: "regle", recto: "Dérivée d'un produit", verso: "u'v + uv'", etat: "nouvelle", due_at: null, ...extra,
})

function monter(ui: React.ReactElement) {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><MemoryRouter>{ui}</MemoryRouter></QueryClientProvider>)
}

describe("CartesDuCours", () => {
  beforeEach(() => {
    getCartesCours.mockReset()
    noterCarte.mockReset()
    noterCarte.mockResolvedValue({})
  })

  it("compte les cartes à réviser et ouvre le paquet", async () => {
    getCartesCours.mockResolvedValue({ cours: { slug: "c", titre: "C" }, cartes: [carte(), carte({ cle: "erreur-0", type: "erreur", recto: "Écrire (uv)'=u'v'", verso: "Faux" })] })
    monter(<CartesDuCours slug="c" />)
    expect(await screen.findByText(/2 cartes à réviser/)).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Réviser" }))
    // Le paquet de cartes se charge à l'ouverture (voir CartesDeRevision) : on l'attend.
    expect(await screen.findByText("Dérivée d'un produit")).toBeTruthy()
    expect(screen.queryByText("u'v + uv'")).toBeNull() // le verso attend « Voir la réponse »
  })

  it("envoie la vraie réponse, carte par carte, puis donne le bilan", async () => {
    getCartesCours.mockResolvedValue({ cours: { slug: "c", titre: "C" }, cartes: [carte(), carte({ cle: "erreur-0", type: "erreur", recto: "Piège", verso: "Faux" })] })
    monter(<CartesDuCours slug="c" />)
    fireEvent.click(await screen.findByRole("button", { name: "Réviser" }))
    fireEvent.click(await screen.findByRole("button", { name: "Voir la réponse" }))
    expect(screen.getByText("u'v + uv'")).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Je savais" }))
    await waitFor(() => expect(noterCarte).toHaveBeenCalledWith("c", "regle", true))
    fireEvent.click(await screen.findByRole("button", { name: "Voir la réponse" }))
    fireEvent.click(screen.getByRole("button", { name: "À revoir" }))
    await waitFor(() => expect(noterCarte).toHaveBeenLastCalledWith("c", "erreur-0", false))
    expect(await screen.findByText(/1 sues, 1 à revoir demain/)).toBeTruthy()
  })

  it("dit que tout est à jour quand rien n'est dû", async () => {
    getCartesCours.mockResolvedValue({ cours: { slug: "c", titre: "C" }, cartes: [carte({ etat: "planifiee", due_at: "2026-11-20" })] })
    monter(<CartesDuCours slug="c" />)
    expect(await screen.findByText(/à jour. Prochaine revue le/)).toBeTruthy()
    expect(screen.queryByRole("button", { name: "Réviser" })).toBeNull()
  })

  it("garde la carte et signale l'erreur quand l'enregistrement échoue", async () => {
    noterCarte.mockRejectedValue(new Error("réseau"))
    getCartesCours.mockResolvedValue({ cours: { slug: "c", titre: "C" }, cartes: [carte()] })
    monter(<CartesDuCours slug="c" />)
    fireEvent.click(await screen.findByRole("button", { name: "Réviser" }))
    fireEvent.click(await screen.findByRole("button", { name: "Voir la réponse" }))
    fireEvent.click(screen.getByRole("button", { name: "Je savais" }))
    expect(await screen.findByRole("alert")).toBeTruthy()
    expect(screen.getByText("Dérivée d'un produit")).toBeTruthy()
  })

  it("ne montre rien pour un cours sans carte", async () => {
    getCartesCours.mockResolvedValue({ cours: { slug: "c", titre: "C" }, cartes: [] })
    const { container } = monter(<CartesDuCours slug="c" />)
    await waitFor(() => expect(getCartesCours).toHaveBeenCalled())
    expect(container.textContent).toBe("")
  })
})

describe("LigneCartes", () => {
  beforeEach(() => {
    getCartesDues.mockReset()
    noterCarte.mockReset()
    noterCarte.mockResolvedValue({})
  })

  it("se tait sans carte due", async () => {
    getCartesDues.mockResolvedValue({ total: 0, cartes: [] })
    const { container } = monter(<LigneCartes />)
    await waitFor(() => expect(getCartesDues).toHaveBeenCalled())
    expect(container.textContent).toBe("")
  })

  it("note chaque carte dans son propre cours", async () => {
    getCartesDues.mockResolvedValue({ total: 1, cartes: [carte({ etat: "a_revoir", cours: { slug: "derivees", titre: "Dérivées" } })] })
    monter(<LigneCartes />)
    expect(await screen.findByText("1 carte à revoir aujourd'hui")).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Réviser" }))
    expect(await screen.findByText(/Dérivées/)).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Voir la réponse" }))
    fireEvent.click(screen.getByRole("button", { name: "À revoir" }))
    await waitFor(() => expect(noterCarte).toHaveBeenCalledWith("derivees", "regle", false))
  })
})

describe("CartesDuCours : les points des cartes", () => {
  beforeEach(() => {
    getCartesCours.mockReset()
    noterCarte.mockReset()
    getCartesCours.mockResolvedValue({
      cours: { slug: "c", titre: "C" },
      cartes: [carte(), carte({ cle: "erreur-0", type: "erreur", recto: "Piège", verso: "Faux" }), carte({ cle: "erreur-1", type: "erreur", recto: "Autre piège", verso: "Faux aussi" })],
    })
  })

  async function revoir(bouton: "Je savais" | "À revoir") {
    fireEvent.click(await screen.findByRole("button", { name: "Voir la réponse" }))
    fireEvent.click(screen.getByRole("button", { name: bouton }))
  }

  it("affiche les points au fil du paquet puis à la fin, tels que le serveur les a crédités", async () => {
    const jour = (xp: number) => ({ xp, objectif: 20, atteint: false, objectifs_possibles: [10, 20, 30] })
    noterCarte
      .mockResolvedValueOnce({ xp_gagne: 1, xp_jour: jour(6) })
      .mockResolvedValueOnce({ xp_gagne: 1, xp_jour: jour(7) })
      .mockResolvedValueOnce({ xp_gagne: 0 }) // plafond du jour atteint : rien de promis
    monter(<CartesDuCours slug="c" />)
    fireEvent.click(await screen.findByRole("button", { name: "Réviser" }))

    await revoir("Je savais")
    expect(await screen.findByText("+1 point")).toBeTruthy()
    await revoir("À revoir") // une carte « à revoir » rapporte aussi : c'est la revue qui compte
    expect(await screen.findByText("+2 points")).toBeTruthy()
    await revoir("Je savais")

    expect(await screen.findByText("Paquet terminé")).toBeTruthy()
    expect(screen.getByText("+2 points")).toBeTruthy()
    expect(screen.getByText("7 points · objectif 20")).toBeTruthy()
    // Un jalon gagné avec ce paquet se fête ici (voir JalonsAtteints), pas au prochain quiz.
    expect(screen.getByText("Jalons du paquet")).toBeTruthy()
  })

  it("ne parle pas de points quand le paquet n'en a rapporté aucun", async () => {
    noterCarte.mockResolvedValue({ xp_gagne: 0 })
    monter(<CartesDuCours slug="c" />)
    fireEvent.click(await screen.findByRole("button", { name: "Réviser" }))
    await revoir("Je savais")
    await revoir("Je savais")
    await revoir("Je savais")

    expect(await screen.findByText("Paquet terminé")).toBeTruthy()
    expect(screen.queryByText(/\+\d+ point/)).toBeNull()
  })
})
