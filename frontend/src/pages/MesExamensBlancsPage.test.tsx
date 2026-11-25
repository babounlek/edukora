import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMySimulations = vi.hoisted(() => vi.fn())
const getMesPertes = vi.hoisted(() => vi.fn())
const listMyTentativesInedites = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: true, isLoading: false, user: { id: 1, cursus_prepare: { id: 14 } } }))
vi.mock("@/api/endpoints", () => ({ listMySimulations, getMesPertes, listMyTentativesInedites }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { MesExamensBlancsPage } from "./MesExamensBlancsPage"

const copie = (surcharges: Record<string, unknown>) => ({
  id: 1, epreuve: 5, epreuve_titre: "Maths BEPC 2025", epreuve_slug: "maths-bepc-2025", matiere: "Mathématiques", pays: "cm",
  started_at: "2026-11-01T08:00:00Z", submitted_at: "2026-11-01T10:00:00Z", chrono_en_cours: false,
  note_obtenue: 10, bareme_snapshot: 20, score_obtenu: 50, ...surcharges,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/examens-blancs"]}>
        <Routes>
          <Route path="/examens-blancs" element={<MesExamensBlancsPage />} />
          <Route path="/connexion" element={<p>Écran de connexion</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  auth.isAuthenticated = true
  listMyTentativesInedites.mockResolvedValue([])
})

const inedite = (surcharges: Record<string, unknown>) => ({
  id: 70, epreuve: 8, epreuve_titre: "Mini maths", genre: "mini", subject_label: "Mathématiques", cursus_display: "BEPC",
  started_at: "2026-11-12T08:00:00Z", exam_mode_started_at: "2026-11-12T08:00:00Z", echeance: null,
  submitted_at: "2026-11-12T09:00:00Z", score_obtenu: 8, note_obtenue: 16, bareme_snapshot: 20, ...surcharges,
})

describe("MesExamensBlancsPage", () => {
  it("un visiteur qui a fait un essai sans compte retrouve sa copie, sans les annales", async () => {
    auth.isAuthenticated = false
    localStorage.setItem("edukora-invite", "jeton-invite")
    listMyTentativesInedites.mockResolvedValue([inedite({ id: 71, epreuve_titre: "Inédite offerte" })])
    afficher()

    const lien = await screen.findByRole("link", { name: /Inédite offerte/ })
    expect(lien).toHaveAttribute("href", "/inedit/tentative/71/resultat")
    expect(screen.getByText("Garde ta copie et ta note.")).toBeInTheDocument()
    expect(listMySimulations).not.toHaveBeenCalled()
    localStorage.removeItem("edukora-invite")
  })

  it("met la copie dont le chrono tourne en tête, avec de quoi la reprendre", async () => {
    listMySimulations.mockResolvedValue([
      copie({ id: 9, epreuve_titre: "Physique BEPC 2024", submitted_at: null, note_obtenue: null, bareme_snapshot: null, chrono_en_cours: true }),
    ])
    afficher()

    const lien = await screen.findByRole("link", { name: /Physique BEPC 2024/ })
    expect(lien).toHaveAttribute("href", "/simulation/9")
    expect(lien).toHaveTextContent("Reprendre")
    expect(screen.queryByText("Aucun examen blanc pour l'instant")).not.toBeInTheDocument()
  })

  it("liste les notes rendues, la meilleure et l'évolution depuis le premier", async () => {
    listMySimulations.mockResolvedValue([
      copie({ id: 3, note_obtenue: 15, submitted_at: "2026-11-10T10:00:00Z" }),
      copie({ id: 2, note_obtenue: 12, submitted_at: "2026-11-05T10:00:00Z" }),
      copie({ id: 1, note_obtenue: 8, submitted_at: "2026-11-01T10:00:00Z" }),
    ])
    afficher()

    expect(await screen.findByText("75 %", { selector: "p" })).toBeInTheDocument()
    expect(screen.getByText("3 examens blancs passés")).toBeInTheDocument()
    expect(screen.getByText(/\+35/)).toBeInTheDocument()
    expect(screen.getAllByRole("link", { name: /Maths BEPC 2025/ })[0]).toHaveAttribute("href", "/simulation/3/resultat")
  })

  it("une seule copie rendue : pas de tendance inventée", async () => {
    listMySimulations.mockResolvedValue([copie({})])
    afficher()

    expect(await screen.findByText("1 examen blanc passé")).toBeInTheDocument()
    expect(screen.queryByText(/^\+/)).not.toBeInTheDocument()
  })

  it("sans copie, explique comment en passer une et mène aux annales", async () => {
    listMySimulations.mockResolvedValue([])
    afficher()

    expect(await screen.findByText("Aucun examen blanc pour l'instant")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Choisir une annale/ })).toHaveAttribute("href", "/cm/epreuves")
  })

  it("une panne n'est pas « aucun examen blanc »", async () => {
    listMySimulations.mockRejectedValue(new Error("réseau"))
    afficher()

    expect(await screen.findByRole("alert")).toBeInTheDocument()
    expect(screen.queryByText("Aucun examen blanc pour l'instant")).not.toBeInTheDocument()
  })

  it("montre à un visiteur pourquoi se connecter, avec un lien vers la connexion", () => {
    auth.isAuthenticated = false
    afficher()

    // Un visiteur voit ce que la page contient et pourquoi un compte est nécessaire, puis un lien vers la connexion (plus de redirection sèche).
    expect(screen.getByRole("link", { name: "Se connecter" })).toHaveAttribute("href", "/connexion")
  })

  it("mêle annales, inédites, minis et défis, chacun avec sa pastille et le lien de son résultat", async () => {
    listMySimulations.mockResolvedValue([copie({ id: 3, note_obtenue: 12, submitted_at: "2026-11-10T10:00:00Z" })])
    listMyTentativesInedites.mockResolvedValue([
      inedite({ id: 70, genre: "mini", submitted_at: "2026-11-12T09:00:00Z" }),
      inedite({ id: 71, genre: "defi", epreuve_titre: "Défi du lundi", submitted_at: "2026-11-11T09:00:00Z" }),
    ])
    afficher()

    expect(await screen.findByText("3 examens blancs passés")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Mini maths/ })).toHaveAttribute("href", "/inedit/tentative/70/resultat")
    expect(screen.getByRole("link", { name: /Défi du lundi/ })).toHaveAttribute("href", "/inedit/tentative/71/resultat")
    expect(screen.getByRole("link", { name: /Maths BEPC 2025/ })).toHaveAttribute("href", "/simulation/3/resultat")
    expect(screen.getByText("Mini-inédite")).toBeInTheDocument()
    expect(screen.getByText("Défi de la semaine")).toBeInTheDocument()
    expect(screen.getByText("Annale")).toBeInTheDocument()
    // La meilleure note ne compte que les épreuves entières : la mini à 16/20 ne passe pas devant l'annale à 12/20.
    expect(screen.getByText("60 %", { selector: "p" })).toBeInTheDocument()
    expect(screen.getByText("sur les épreuves entières (hors minis et défis)")).toBeInTheDocument()
  })

  it("une inédite chronométrée non rendue se reprend ; une copie libre entamée n'y figure pas", async () => {
    listMySimulations.mockResolvedValue([])
    listMyTentativesInedites.mockResolvedValue([
      inedite({ id: 80, genre: "inedite", epreuve_titre: "Inédite en cours", submitted_at: null, note_obtenue: null, bareme_snapshot: null }),
      inedite({ id: 81, epreuve_titre: "Brouillon libre", submitted_at: null, exam_mode_started_at: null, note_obtenue: null, bareme_snapshot: null }),
    ])
    afficher()

    const lien = await screen.findByRole("link", { name: /Inédite en cours/ })
    expect(lien).toHaveAttribute("href", "/inedit/tentative/80")
    expect(screen.queryByText("Brouillon libre")).not.toBeInTheDocument()
  })

  it("une copie rendue mais pas encore notée dit « À noter » sans fausser la meilleure note", async () => {
    listMySimulations.mockResolvedValue([])
    listMyTentativesInedites.mockResolvedValue([inedite({ id: 90, note_obtenue: null, bareme_snapshot: null })])
    afficher()

    expect(await screen.findByText("À noter")).toBeInTheDocument()
    expect(screen.queryByText(/NaN/)).not.toBeInTheDocument()
  })

  it("sans accès aux inédites, les annales restent affichées", async () => {
    listMySimulations.mockResolvedValue([copie({})])
    listMyTentativesInedites.mockRejectedValue(new Error("403"))
    afficher()

    expect(await screen.findByText("1 examen blanc passé")).toBeInTheDocument()
    expect(screen.queryByRole("alert")).not.toBeInTheDocument()
  })
})
