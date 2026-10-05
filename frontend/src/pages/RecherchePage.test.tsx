import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { ReponseRecherche, ResultatRecherche } from "@/api/types"

const rechercher = vi.hoisted(() => vi.fn())
const trackEvent = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ rechercher, listCursus: vi.fn(() => Promise.resolve([])) }))
vi.mock("@/lib/analytics", () => ({ trackEvent }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ user: null }) }))
vi.mock("@/lib/cursusAccueil", () => ({ useCursusAccueil: () => null }))

import { RecherchePage } from "./RecherchePage"

function resultat(surcharge: Partial<ResultatRecherche>): ResultatRecherche {
  return {
    id: 1, type: "COURS", titre: "Demi-tangente verticale", apercu: "", annee: null,
    matiere: { code: "MATHS", label: "Mathématiques" },
    cursus: [{ id: 20, label: "BAC C" }], cursus_total: 1, tous_cursus: false, cursus_cible: 20,
    acces: "verrouille", nb: null, details: { slug: "demi-tangente" },
    ...surcharge,
  }
}

const THEME_MATHS = resultat({
  id: 10, type: "THEME", titre: "Tangente", acces: null,
  details: { tag_id: 7, subject_code: "MATHS", nb_cours: 65, nb_exercices: 57, nb_quiz: 12 },
})
const THEME_VIDE = resultat({ id: 11, type: "THEME", titre: "Tangente vide", acces: null, details: { tag_id: 8, subject_code: "MATHS" } })
const THEME_CHIMIE = resultat({
  id: 12, type: "THEME", titre: "méthode des tangentes", acces: null, matiere: { code: "CHIMIE", label: "Chimie" },
  details: { tag_id: 9, subject_code: "CHIMIE", nb_cours: 14, nb_quiz: 6 },
})

function reponse(surcharge: Partial<ReponseRecherche> = {}): ReponseRecherche {
  return {
    q: "tange", corrige: null, indexe: true, trop_court: false, total: 30, autres_cursus: 0, suggestions: [],
    matieres: [{ code: "MATHS", label: "Mathématiques", total: 20 }, { code: "CHIMIE", label: "Chimie", total: 10 }],
    groupes: [
      { type: "THEME", libelle: "Thèmes", total: 3, resultats: [THEME_VIDE, THEME_MATHS, THEME_CHIMIE] },
      { type: "COURS", libelle: "Cours", total: 12, resultats: [resultat({})] },
    ],
    ...surcharge,
  }
}

function Lieu() {
  const lieu = useLocation()
  return <div data-testid="lieu">{`${lieu.pathname}${lieu.search}`}</div>
}

function monter(url = "/cm/recherche?q=tange") {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[url]}>
        <Routes>
          <Route path="/:country/recherche" element={<RecherchePage />} />
        </Routes>
        <Lieu />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  rechercher.mockReset()
  trackEvent.mockReset()
  localStorage.clear()
})

describe("RecherchePage", () => {
  it("met en avant le meilleur thème AYANT de quoi agir, avec trois tuiles et un bouton quiz", async () => {
    rechercher.mockResolvedValue(reponse())
    monter()

    const vedette = await screen.findByRole("region", { name: /Tangente/ })
    // « Tangente vide » est premier du classement mais n'a rien à proposer : il n'est pas mis en avant.
    expect(within(vedette).getByText("Commence par ici")).toBeInTheDocument()
    expect(within(vedette).getByText(/65 cours, 57 exercices et 12 questions de quiz t'attendent/)).toBeInTheDocument()
    expect(within(vedette).getByRole("link", { name: /65\s*cours/ })).toHaveAttribute("href", expect.stringContaining("/cm/cours?theme=7"))
    expect(within(vedette).getByRole("link", { name: /Tester mes connaissances/ })).toHaveAttribute("href", expect.stringContaining("/quiz?"))
  })

  it("ne répète pas le thème mis en avant dans la liste des thèmes", async () => {
    rechercher.mockResolvedValue(reponse())
    monter()
    const liste = await screen.findByRole("region", { name: /Thèmes/ })
    expect(within(liste).queryByRole("link", { name: "Tangente" })).not.toBeInTheDocument()
    expect(within(liste).getByRole("link", { name: "méthode des tangentes" })).toBeInTheDocument()
  })

  it("propose les autres thèmes en pastilles qui relancent la recherche", async () => {
    rechercher.mockResolvedValue(reponse())
    monter()
    await screen.findByText("À explorer aussi :")
    await userEvent.click(screen.getByRole("button", { name: "méthode des tangentes" }))
    await waitFor(() => expect(screen.getByTestId("lieu")).toHaveTextContent(new URLSearchParams({ q: "méthode des tangentes" }).toString()))
  })

  it("dit combien de résultats, et en quelles matières", async () => {
    rechercher.mockResolvedValue(reponse())
    monter()
    expect(await screen.findByText(/résultats pour « tange »/)).toHaveTextContent("30 résultats pour « tange »")
    const matieres = screen.getByRole("group", { name: "Matière" })
    expect(within(matieres).getByRole("button", { name: /Toutes les matières\s*30/ })).toHaveAttribute("aria-pressed", "true")
    expect(within(matieres).getByRole("button", { name: /Chimie\s*10/ })).toBeInTheDocument()
  })

  it("choisir une matière relance la recherche filtrée, sans perdre les autres pastilles", async () => {
    rechercher.mockResolvedValue(reponse())
    monter()
    const matieres = await screen.findByRole("group", { name: "Matière" })
    await userEvent.click(within(matieres).getByRole("button", { name: /Chimie/ }))

    await waitFor(() => expect(screen.getByTestId("lieu")).toHaveTextContent("matiere=CHIMIE"))
    await waitFor(() =>
      expect(rechercher).toHaveBeenCalledWith(expect.objectContaining({ q: "tange", matiere: "CHIMIE" }), expect.anything()),
    )
  })

  it("n'affiche pas de pastilles de matière quand une seule est concernée", async () => {
    rechercher.mockResolvedValue(reponse({ matieres: [{ code: "MATHS", label: "Mathématiques", total: 30 }] }))
    monter()
    await screen.findByText("Commence par ici")
    expect(screen.queryByRole("group", { name: "Matière" })).not.toBeInTheDocument()
  })

  it("note l'ouverture d'un résultat avec son rang, sans le texte tapé", async () => {
    rechercher.mockResolvedValue(reponse())
    monter()
    const liste = await screen.findByRole("region", { name: /Cours/ })
    await userEvent.click(within(liste).getByRole("link", { name: /Demi-tangente verticale/ }))
    expect(trackEvent).toHaveBeenCalledWith("recherche_resultat_clique", {
      source: "page", type: "COURS", rang: 1, acces: "verrouille",
    })
    expect(JSON.stringify(trackEvent.mock.calls)).not.toContain("tange")
  })

  it("propose des thèmes quand rien ne correspond", async () => {
    rechercher.mockResolvedValue(reponse({ total: 0, groupes: [], matieres: [], suggestions: [THEME_MATHS] }))
    monter("/cm/recherche?q=xyzzyq")
    expect(await screen.findByText(/Aucun résultat pour « xyzzyq »/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Tangente/ })).toBeInTheDocument()
  })
})
