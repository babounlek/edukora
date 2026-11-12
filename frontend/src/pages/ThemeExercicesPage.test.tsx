import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { describe, expect, it, vi } from "vitest"

const getThemeExercices = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getThemeExercices, getThemesFrequents: vi.fn() }))
vi.mock("@/lib/cursusLangue", () => ({ useCursusListe: () => ({ data: [], tous: [] }) }))
vi.mock("@/lib/abonneActif", () => ({ useAbonneActif: () => false, useCursusAbonne: () => null }))
vi.mock("@/components/ReviserTabs", () => ({ ReviserTabs: () => null }))

import { ThemeExercicesPage } from "./ThemeExercicesPage"

function afficher(chemin: string) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={[chemin]}>
        <Routes>
          <Route path="/:country/themes-frequents/:tagId/exercices" element={<ThemeExercicesPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("ThemeExercicesPage : un lien sans examen ni matière", () => {
  it("n'affiche pas « Aucun exercice trouvé » mais dit comment retrouver le thème", async () => {
    afficher("/cm/themes-frequents/11947/exercices")

    expect(await screen.findByText(/Ce lien ne dit pas pour quel examen ni quelle matière/)).toBeInTheDocument()
    expect(screen.queryByText(/Aucun exercice trouvé/)).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Voir les thèmes qui tombent" })).toHaveAttribute("href", "/cm/themes-frequents")
    // Rien n'est demandé au serveur sans examen ni matière.
    expect(getThemeExercices).not.toHaveBeenCalled()
  })
})
