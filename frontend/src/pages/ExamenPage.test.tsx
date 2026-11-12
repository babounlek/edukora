import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"
import type { ExamenPageData } from "@/api/types"

const getExamen = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getExamen }))

import { ExamenPage } from "./ExamenPage"

const EXAMEN: ExamenPageData = {
  slug: "bepc",
  country: "cm",
  cursus_id: 14,
  libelle: "BEPC",
  examen_display: "BEPC",
  langue: "fr",
  nb_epreuves: 246,
  nb_epreuves_libres: 14,
  nb_cours: 0,
  nb_matieres: 2,
  annee_min: 1995,
  annee_max: 2026,
  matieres: [
    { label: "Mathématiques", n: 21 },
    { label: "Physique", n: 5 },
  ],
  epreuves: [
    { slug: "maths-bepc-2026", title: "Maths BEPC 2026", year: 2026, matiere: "Mathématiques", libre: true },
    { slug: "maths-bepc-2025", title: "Maths BEPC 2025", year: 2025, matiere: "Mathématiques", libre: false },
    { slug: "physique-bepc-2020", title: "Physique BEPC 2020", year: 2020, matiere: "Physique", libre: false },
  ],
  textes: {
    titre: "Annales BEPC corrigées au Cameroun",
    description: "Plus de 240 annales BEPC au Cameroun (1995 à 2026), avec corrigés détaillés : 14 en accès libre.",
    intro: "EduKora réunit plus de 240 épreuves du BEPC au Cameroun (1995 à 2026), dans 2 matières.",
  },
}

function afficher(chemin = "/cm/examens/bepc") {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={[chemin]}>
        <Routes>
          <Route path="/:country/examens/:slug" element={<ExamenPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  getExamen.mockReset()
})

describe("ExamenPage : la page d'un examen", () => {
  it("montre le titre, l'introduction, les chiffres et les épreuves récentes par matière", async () => {
    getExamen.mockResolvedValue(EXAMEN)
    afficher()

    expect(await screen.findByRole("heading", { level: 1, name: "Annales BEPC corrigées au Cameroun" })).toBeInTheDocument()
    expect(screen.getByText(/EduKora réunit plus de 240 épreuves du BEPC/)).toBeInTheDocument()
    expect(screen.getByText("246")).toBeInTheDocument()
    expect(screen.getByText("corrigés en accès libre")).toBeInTheDocument()
    // Des liens vers les fiches d'épreuve, avec l'état du corrigé.
    expect(screen.getByRole("link", { name: /Maths BEPC 2026/ })).toHaveAttribute("href", "/cm/epreuves/maths-bepc-2026")
    expect(screen.getByText("Corrigé libre")).toBeInTheDocument()
    expect(screen.getAllByText("Sujet libre")).toHaveLength(2)
    // Une sous-section par matière.
    expect(screen.getByRole("heading", { level: 3, name: "Physique" })).toBeInTheDocument()
    expect(getExamen).toHaveBeenCalledWith("cm", "bepc")
  })

  it("renvoie vers la liste filtrée, les thèmes qui tombent et les tarifs", async () => {
    getExamen.mockResolvedValue(EXAMEN)
    afficher()

    expect(await screen.findByRole("link", { name: /Voir toutes les épreuves du BEPC/ })).toHaveAttribute(
      "href",
      "/cm/epreuves?cursus=14",
    )
    expect(screen.getByRole("link", { name: "Les thèmes qui tombent" })).toHaveAttribute(
      "href",
      "/cm/themes-frequents?cursus=14",
    )
    expect(screen.getByRole("link", { name: "Voir les prix" })).toHaveAttribute("href", "/tarifs")
  })

  it("pose un fil d'Ariane avec la page courante", async () => {
    getExamen.mockResolvedValue(EXAMEN)
    afficher()

    await screen.findByRole("heading", { level: 1 })
    const fil = screen.getByRole("navigation", { name: "Fil d'Ariane" })
    expect(fil).toHaveTextContent("Accueil")
    expect(fil.querySelector('[aria-current="page"]')).toHaveTextContent("BEPC")
  })

  it("dit que l'examen n'existe pas sur un 404, avec un lien de retour", async () => {
    getExamen.mockRejectedValue(new ApiError(404, { detail: "Examen introuvable." }))
    afficher("/cm/examens/inconnu")

    expect(await screen.findByText(/n'existe pas ou n'a pas encore d'épreuve publiée/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Retour aux épreuves" })).toHaveAttribute("href", "/cm/epreuves")
  })
})
