import { render, screen } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getPlanDuJour = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getPlanDuJour, marquerEtapeOuverte: vi.fn(() => Promise.resolve()) }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ isAuthenticated: true }) }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))

import { BarreSeance, EtapeSuivante } from "./BarreSeance"

const plan = {
  etat: "plan_pret",
  cursus: { id: 20 },
  seance: {
    id: 297,
    verrouillee: false,
    theme: { id: 12 },
    subject: { code: "MATHS" },
    etapes: [
      {
        type: "exercice", cle: "exercice-345", ouverte: true, libelle: "Un exercice", exercise_id: 345,
        lesson_slug: "maths-bac-c-2024", lesson_title: "Maths BAC C 2024", lesson_year: 2024, numero_exercice: "2", duree_min: 12,
      },
      { type: "quiz", cle: "quiz", ouverte: false, libelle: "6 questions", mode: "PRATIQUE", n: 6, duree_min: 6 },
    ],
  },
}

function afficher(chemin: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[chemin]}>
        <BarreSeance />
        <EtapeSuivante />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

const QUIZ = "/quiz?cursus=20&theme=12&seance=297&n=6"

beforeEach(() => {
  getPlanDuJour.mockReset()
  getPlanDuJour.mockResolvedValue(plan)
})

describe("le fil de la séance du jour", () => {
  it("tient sur l'exercice ouvert par thème : la barre et le bouton mènent au quiz qui valide la séance", async () => {
    afficher("/cm/themes-frequents/12/exercices/345?subject=MATHS&cursus=20")

    expect(await screen.findByRole("link", { name: /Passer au quiz/ })).toHaveAttribute("href", QUIZ)
    expect(screen.getByRole("link", { name: /Continuer/ })).toHaveAttribute("href", QUIZ)
  })

  it("tient aussi sur le lecteur d'épreuve (repli quand la séance n'a pas de thème)", async () => {
    afficher("/cm/epreuves/maths-bac-c-2024/lire")

    expect(await screen.findByRole("link", { name: /Passer au quiz/ })).toHaveAttribute("href", QUIZ)
  })

  it("ne dit rien sur un autre exercice du même thème, hors séance", async () => {
    afficher("/cm/themes-frequents/12/exercices/999?subject=MATHS&cursus=20")

    await vi.waitFor(() => expect(getPlanDuJour).toHaveBeenCalled())
    expect(screen.queryByRole("link", { name: /Passer au quiz/ })).not.toBeInTheDocument()
    expect(screen.queryByRole("link", { name: /Continuer/ })).not.toBeInTheDocument()
  })

  it("n'interroge pas le plan sur une page qui n'est pas une étape de lecture", () => {
    afficher("/cm/themes-frequents")

    expect(getPlanDuJour).not.toHaveBeenCalled()
  })
})
