import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { getQuestionExemple } = vi.hoisted(() => ({ getQuestionExemple: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ getQuestionExemple }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))

import { definirLangue } from "@/lib/i18n"
import { DemoQuizQuestion } from "./DemoQuizQuestion"

const REELLE = {
  question: "Which of the following elements is stored under paraffin oil?",
  choix: [
    { lettre: "a", texte: "Phosphorus" },
    { lettre: "b", texte: "Potassium" },
    { lettre: "c", texte: "Aluminium" },
    { lettre: "d", texte: "Zinc" },
  ],
  reponse_correcte: "b",
  numero: "2",
  epreuve: { slug: "chemistry-gce-ordinary-level-2020-paper-1", title: "Chemistry GCE O Level 2020 - Paper 1" },
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <DemoQuizQuestion lienConnexion={<a href="/connexion">Se connecter</a>} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => getQuestionExemple.mockResolvedValue(REELLE))
afterEach(async () => {
  await definirLangue("fr", { persister: false })
  getQuestionExemple.mockReset()
})

describe("DemoQuizQuestion", () => {
  it("en français : la question de démo d'origine, sans légende, sans appel au serveur", () => {
    afficher()
    expect(screen.getByText(/À quelle condition un extremum local/)).toBeInTheDocument()
    expect(screen.getByText("La dérivée s'annule et change de signe")).toBeInTheDocument()
    expect(document.querySelector('a[href*="/epreuves/"]')).toBeNull()
    expect(getQuestionExemple).not.toHaveBeenCalled()
  })

  it("en anglais : une vraie question d'une épreuve gratuite, lue en direct, avec lien et bonne réponse", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    expect(await screen.findByText(REELLE.question)).toBeInTheDocument()
    expect(getQuestionExemple).toHaveBeenCalledWith("en", "cm", expect.anything())
    const source = screen.getByRole("link", { name: "From a free paper: Chemistry GCE O Level 2020 - Paper 1, question 2" })
    expect(source).toHaveAttribute("href", "/cm/epreuves/chemistry-gce-ordinary-level-2020-paper-1/lire")
    expect(screen.queryByText(/extremum/)).not.toBeInTheDocument()
    // La bonne réponse (B) est mise en évidence, pas la lettre A figée de la démo.
    expect(screen.getByText("Potassium").parentElement).toHaveClass("border-success/40")
    expect(screen.getByText("Phosphorus").parentElement).not.toHaveClass("border-success/40")
  })

  it("en anglais, sans question côté serveur : repli sur la question de démonstration, légende comprise", async () => {
    getQuestionExemple.mockRejectedValue(new Error("404"))
    await definirLangue("en", { persister: false })
    afficher()
    expect(await screen.findByText(/hydrochloric acid and potassium hydroxide/)).toBeInTheDocument()
    expect(screen.getByText("Neutralization reaction").parentElement).toHaveClass("border-success/40")
    expect(
      screen.getByRole("link", { name: /Chemistry GCE O Level 2020, Paper 1, question 3/ }),
    ).toHaveAttribute("href", "/cm/epreuves/chemistry-gce-ordinary-level-2020-paper-1/lire")
  })

  it("en anglais, le temps de la réponse : un emplacement neutre, jamais une question de repli qui clignote", async () => {
    getQuestionExemple.mockReturnValue(new Promise(() => {}))
    await definirLangue("en", { persister: false })
    afficher()
    expect(screen.getByTestId("demo-chargement")).toBeInTheDocument()
    expect(screen.queryByText(/hydrochloric acid/)).not.toBeInTheDocument()
    expect(screen.queryByText(REELLE.question)).not.toBeInTheDocument()
  })
})
