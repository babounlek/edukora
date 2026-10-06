import { render, screen, waitFor, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { ReponseRecherche, ResultatRecherche } from "@/api/types"

const rechercher = vi.hoisted(() => vi.fn())
const trackEvent = vi.hoisted(() => vi.fn())

const getMyProgression = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ rechercher, getMyProgression, listCursus: vi.fn(() => Promise.resolve([])) }))
vi.mock("@/lib/analytics", () => ({ trackEvent }))
const auth = vi.hoisted(() => ({ user: null as null | { id: number }, isAuthenticated: false }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/cursusAccueil", () => ({ useCursusAccueil: () => null }))
vi.mock("@/context/CountryContext", () => ({
  useCountry: () => ({ country: "cm", countries: [{ code: "CM", label: "Cameroun" }] }),
}))

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

function monter(url = "/cm/recherche?q=tange", etat?: unknown) {
  const adresse = new URL(url, "http://localhost")
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[{ pathname: adresse.pathname, search: adresse.search, state: etat }]}>
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
  getMyProgression.mockReset()
  auth.user = null
  auth.isAuthenticated = false
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
    const matieres = screen.getByRole("group", { name: "Filtrer par matière" })
    expect(within(matieres).getByRole("button", { name: /Toutes les matières\s*30/ })).toHaveAttribute("aria-pressed", "true")
    expect(within(matieres).getByRole("button", { name: /Chimie\s*10/ })).toBeInTheDocument()
  })

  it("choisir une matière relance la recherche filtrée, sans perdre les autres pastilles", async () => {
    rechercher.mockResolvedValue(reponse())
    monter()
    const matieres = await screen.findByRole("group", { name: "Filtrer par matière" })
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
    expect(screen.queryByRole("group", { name: "Filtrer par matière" })).not.toBeInTheDocument()
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

describe("RecherchePage dans « Réviser »", () => {
  it("affiche les onglets Réviser (aucun actif), sans le lien de recherche : le grand champ est juste dessous", async () => {
    rechercher.mockResolvedValue(reponse())
    monter()
    const onglets = await screen.findByRole("navigation", { name: "Réviser" })
    for (const nom of ["Épreuves", "Cours", "Thèmes", "Quiz"]) {
      const lien = within(onglets).getByRole("link", { name: nom })
      expect(lien).not.toHaveAttribute("aria-current")
    }
    expect(within(onglets).queryByRole("link", { name: "Rechercher sur tout le site" })).not.toBeInTheDocument()
  })
})

describe("onglets de résultats harmonisés avec « Réviser »", () => {
  const EPREUVE = resultat({ id: 30, type: "EPREUVE", titre: "Mathématiques BAC C 2019", details: { slug: "maths-2019" } })
  const EXERCICE = resultat({ id: 31, type: "EXERCICE", titre: "Exercice 2 · Mathématiques BAC C 2019", details: { slug: "maths-2019", ancre: "exercice-2" } })
  const QUIZ = resultat({ id: 32, type: "QUIZ", titre: "limites", nb: 2, details: { tag_id: 7 } })

  function complet() {
    return reponse({
      total: 30,
      groupes: [
        { type: "THEME", libelle: "Thèmes", total: 3, resultats: [THEME_MATHS] },
        { type: "COURS", libelle: "Cours", total: 12, resultats: [resultat({})] },
        { type: "EPREUVE", libelle: "Épreuves", total: 3, resultats: [EPREUVE] },
        { type: "EXERCICE", libelle: "Exercices", total: 5, resultats: [EXERCICE] },
        { type: "QUIZ", libelle: "Questions de quiz", total: 2, resultats: [QUIZ] },
      ],
    })
  }

  it("mêmes onglets et même ordre que Réviser, les exercices rejoignant les épreuves", async () => {
    rechercher.mockResolvedValue(complet())
    monter()
    const onglets = await screen.findByRole("group", { name: "Filtrer par type" })
    const libelles = within(onglets).getAllByRole("button").map((b) => b.textContent)
    expect(libelles).toEqual(["Tout 30", "Épreuves 8", "Cours 12", "Thèmes 3", "Quiz 2"])
  })

  it("l'onglet Épreuves affiche épreuves et exercices, chacun avec sa propre liste paginée", async () => {
    rechercher.mockImplementation((filtres: { type?: string }) =>
      Promise.resolve(
        filtres.type
          ? reponse({ groupes: complet().groupes.filter((g) => g.type === filtres.type) })
          : complet(),
      ),
    )
    monter("/cm/recherche?q=tange&type=EPREUVE")

    expect(await screen.findByRole("heading", { name: /Épreuves/ })).toBeInTheDocument()
    expect(await screen.findByRole("heading", { name: /Exercices/ })).toBeInTheDocument()
    expect(await screen.findByRole("link", { name: "Mathématiques BAC C 2019" })).toBeInTheDocument()
    await waitFor(() =>
      expect(rechercher).toHaveBeenCalledWith(expect.objectContaining({ type: "EXERCICE", limite: 20, decalage: 0 }), expect.anything()),
    )
    expect(screen.getByRole("button", { name: /^Épreuves\s*8$/ })).toHaveAttribute("aria-pressed", "true")
  })

  it("un ancien lien ?type=EXERCICE mène à l'onglet Épreuves", async () => {
    rechercher.mockImplementation((filtres: { type?: string }) =>
      Promise.resolve(filtres.type ? reponse({ groupes: complet().groupes.filter((g) => g.type === filtres.type) }) : complet()),
    )
    monter("/cm/recherche?q=tange&type=EXERCICE")
    expect(await screen.findByRole("button", { name: /^Épreuves\s*8$/ })).toHaveAttribute("aria-pressed", "true")
  })

  it("« Voir les N » d'une section ouvre l'onglet correspondant", async () => {
    rechercher.mockResolvedValue(complet())
    monter()
    const cours = await screen.findByRole("region", { name: /Cours/ })
    await userEvent.click(within(cours).getByRole("button", { name: /Voir les 12/ }))
    await waitFor(() => expect(screen.getByTestId("lieu")).toHaveTextContent("type=COURS"))
  })
})

describe("page de recherche avant toute requête", () => {
  const THEME_A = resultat({ id: 40, type: "THEME", titre: "limites", acces: null, matiere: { code: "MATHS", label: "Mathématiques" }, details: { tag_id: 1 } })
  const THEME_B = resultat({ id: 41, type: "THEME", titre: "Mendel", acces: null, matiere: { code: "SVT", label: "Sciences de la Vie et de la Terre" }, details: { tag_id: 2 } })

  function vide(surcharge: Partial<ReponseRecherche> = {}) {
    return reponse({ q: "", total: 0, groupes: [], matieres: [], suggestions: [THEME_A, THEME_B], ...surcharge })
  }

  it("demande les thèmes sans requête, en mode rapide, et les propose", async () => {
    rechercher.mockResolvedValue(vide())
    monter("/cm/recherche")
    expect(await screen.findByRole("button", { name: /limites/ })).toBeInTheDocument()
    expect(rechercher).toHaveBeenCalledWith({ q: "", pays: "cm", cursus: null, rapide: true }, expect.anything())
    expect(screen.getByRole("heading", { name: "Des thèmes pour commencer" })).toBeInTheDocument()
  })

  it("un thème proposé lance sa recherche et la note sans le texte", async () => {
    rechercher.mockResolvedValue(vide())
    monter("/cm/recherche")
    await userEvent.click(await screen.findByRole("button", { name: /Mendel/ }))
    await waitFor(() => expect(screen.getByTestId("lieu")).toHaveTextContent("q=Mendel"))
    expect(trackEvent).toHaveBeenCalledWith("recherche_lancee", { source: "page" })
    expect(JSON.stringify(trackEvent.mock.calls)).not.toContain("Mendel")
  })

  it("propose les recherches récentes, les relance, et les efface", async () => {
    localStorage.setItem("edukamer_recherches_recentes", JSON.stringify(["thalès", "mendel"]))
    rechercher.mockResolvedValue(vide())
    monter("/cm/recherche")
    const section = await screen.findByRole("region", { name: "Tes dernières recherches" })
    expect(within(section).getAllByRole("button").map((b) => b.textContent)).toEqual(["Effacer", "thalès", "mendel"])

    await userEvent.click(within(section).getByRole("button", { name: "Effacer" }))
    expect(screen.queryByRole("region", { name: "Tes dernières recherches" })).not.toBeInTheDocument()
    expect(localStorage.getItem("edukamer_recherches_recentes")).toBeNull()
  })

  it("sans recherche récente, pas de section récentes", async () => {
    rechercher.mockResolvedValue(vide())
    monter("/cm/recherche")
    await screen.findByRole("button", { name: /limites/ })
    expect(screen.queryByText("Tes dernières recherches")).not.toBeInTheDocument()
  })

  it("propose de reprendre la lecture d'un élève connecté", async () => {
    auth.user = { id: 7 }
    auth.isAuthenticated = true
    getMyProgression.mockResolvedValue({ lessons: [{ title: "Mathématiques BAC C 2019", slug: "maths-2019", subject: { country: { code: "CM" } } }] })
    rechercher.mockResolvedValue(vide())
    monter("/cm/recherche")
    const lien = await screen.findByRole("link", { name: /Reprendre ma lecture/ })
    expect(lien).toHaveAttribute("href", "/cm/epreuves/maths-2019/lire")
    expect(lien).toHaveTextContent("Mathématiques BAC C 2019")
  })

  it("n'interroge pas la progression d'un visiteur", async () => {
    rechercher.mockResolvedValue(vide())
    monter("/cm/recherche")
    await screen.findByRole("button", { name: /limites/ })
    expect(getMyProgression).not.toHaveBeenCalled()
    expect(screen.queryByText("Reprendre ma lecture")).not.toBeInTheDocument()
  })
})

describe("arrivée par la loupe ou un raccourci", () => {
  it("met le champ en saisie et sélectionne le texte déjà tapé", async () => {
    rechercher.mockResolvedValue(reponse())
    monter("/cm/recherche?q=tange", { focusRecherche: true })
    const champ = await screen.findByRole("searchbox", { name: "Rechercher" })
    await waitFor(() => expect(champ).toHaveFocus())
    expect((champ as HTMLInputElement).selectionStart).toBe(0)
    expect((champ as HTMLInputElement).selectionEnd).toBe("tange".length)
  })

  it("sans cet état, un champ déjà rempli n'est pas pris en main", async () => {
    rechercher.mockResolvedValue(reponse())
    monter("/cm/recherche?q=tange")
    const champ = await screen.findByRole("searchbox", { name: "Rechercher" })
    expect(champ).not.toHaveFocus()
  })
})
