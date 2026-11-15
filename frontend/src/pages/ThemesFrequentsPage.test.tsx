import { render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getThemesFrequents = vi.hoisted(() => vi.fn())
const getThemesFrequentsMatieres = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getThemesFrequents, getThemesFrequentsMatieres }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ countries: [] }) }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/filtreCursus", () => ({ useFiltreCursusParDefaut: vi.fn() }))
vi.mock("@/lib/abonneActif", () => ({ useAbonneActif: () => true }))
vi.mock("@/lib/cursusLangue", () => ({
  useAbandonCursusHorsLangue: vi.fn(),
  useCursusListe: () => ({ data: [{ id: 5, examen_display: "BAC", series: { code: "C" } }], isError: false, refetch: vi.fn() }),
}))
vi.mock("@/components/guides/AideContextuelle", () => ({ AideContextuelle: () => null, BoutonAide: () => null }))
vi.mock("@/components/ReviserTabs", () => ({ ReviserTabs: () => null }))

import { ThemesFrequentsPage, prioriteTheme } from "./ThemesFrequentsPage"

const theme = (id: number, tag: string, frequence_pct: number, extra = {}) => ({
  id, tag, nb_epreuves: frequence_pct / 10, frequence_pct, quiz_disponible: true, annees: [], maitrise: null, cours_slug: null, ...extra,
})

const reponse = {
  nb_sessions_disponibles: 10, seuil_minimum: 8, disponible: true, has_access: true, nb_themes_verrouilles: 0,
  themes: [
    theme(1, "suites", 90, { annees: [2019, 2021, 2023], maitrise: { taux: 95, nb_reponses: 8, niveau: "maitrise" }, cours_slug: "les-suites" }),
    theme(2, "probabilités", 60, { annees: [2022], maitrise: { taux: 20, nb_reponses: 5, niveau: "en_cours" } }),
    theme(3, "complexes", 50),
  ],
}

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/cm/themes-frequents?cursus=5&subject=MATHS"]}>
        <Routes>
          <Route path="/:country/themes-frequents" element={<ThemesFrequentsPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  getThemesFrequentsMatieres.mockResolvedValue([{ code: "MATHS", label: "Mathématiques", nb_sessions: 10, disponible: true }])
  getThemesFrequents.mockResolvedValue(reponse)
})

describe("prioriteTheme", () => {
  it("un thème fréquent mal maîtrisé passe avant un thème fréquent acquis, et un thème jamais tenté compte à plein", () => {
    expect(prioriteTheme(reponse.themes[1] as never)).toBeGreaterThan(prioriteTheme(reponse.themes[0] as never))
    expect(prioriteTheme(reponse.themes[2] as never)).toBe(50 * 100)
  })
})

describe("ThemesFrequentsPage, version personnelle", () => {
  it("montre les années de sortie, ma jauge et le lien vers le cours", async () => {
    afficher()

    expect(await screen.findByText("Tombé en 2019, 2021, 2023")).toBeInTheDocument()
    expect(screen.getByText("tu es à 95 %")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Le cours/ })).toHaveAttribute("href", "/cours/les-suites")
  })

  it("« À travailler d'abord » remet en tête le thème fréquent mal maîtrisé", async () => {
    afficher()
    await screen.findByText("Tombé en 2019, 2021, 2023")

    await userEvent.click(screen.getByRole("button", { name: "À travailler d'abord" }))

    const ordonnee = screen.getAllByRole("list").find((l) => l.tagName === "OL")!
    const noms = within(ordonnee).getAllByRole("listitem").map((li) => li.textContent ?? "")
    expect(noms[0]).toContain("Complexes")
    expect(noms[1]).toContain("Probabilités")
  })
})
