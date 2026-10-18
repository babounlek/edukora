import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it, vi } from "vitest"

vi.mock("@/api/endpoints", () => ({ getQuestionExemple: vi.fn() }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))

import { definirLangue } from "@/lib/i18n"
import { QuizCompletVisiteur } from "./QuizCompletVisiteur"

function afficher(connecte: boolean) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>
        <QuizCompletVisiteur connecte={connecte} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("QuizCompletVisiteur", () => {
  it("visiteur : un seul appel principal (créer un compte), la connexion et les prix en liens secondaires", () => {
    afficher(false)
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("Le Quiz retient tes thèmes fragiles à ta place.")
    const compte = screen.getByRole("link", { name: /Créer mon compte/ })
    expect(compte).toHaveAttribute("href", "/connexion")
    expect(screen.getByRole("link", { name: /Déjà un compte/ })).toHaveAttribute("href", "/connexion")
    expect(screen.getByRole("link", { name: "Voir les prix" })).toHaveAttribute("href", "/tarifs")
    // Plus de quatrième appel à l'action dans la question d'exemple.
    expect(screen.queryByRole("link", { name: "Lancer une vraie séance" })).toBeNull()
    expect(screen.getAllByRole("listitem")).toHaveLength(3)
  })

  it("inscrit sans abonnement : l'appel principal mène aux prix, sans lien de connexion", () => {
    afficher(true)
    expect(screen.getByRole("link", { name: /Voir les prix/ })).toHaveAttribute("href", "/tarifs")
    expect(screen.queryByRole("link", { name: /Déjà un compte/ })).toBeNull()
    expect(screen.queryByRole("link", { name: /Créer mon compte/ })).toBeNull()
  })

  it("en anglais : titre et appel traduits", async () => {
    await definirLangue("en", { persister: false })
    afficher(false)
    expect(screen.getByRole("heading", { level: 2 })).toHaveTextContent("The Quiz remembers your weak topics for you.")
    expect(screen.getByRole("link", { name: /Create my account/ })).toBeInTheDocument()
  })
})
