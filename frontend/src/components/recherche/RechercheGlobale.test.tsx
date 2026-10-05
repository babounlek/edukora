import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, useLocation } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { ReponseRecherche, ResultatRecherche } from "@/api/types"

const rechercher = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ rechercher }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ user: null }) }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/cursusAccueil", () => ({ useCursusAccueil: () => 5 }))

import { RechercheGlobale } from "./RechercheGlobale"

function resultat(surcharge: Partial<ResultatRecherche>): ResultatRecherche {
  return {
    id: 1,
    type: "COURS",
    titre: "Le théorème de Thalès dans un triangle",
    apercu: "",
    annee: null,
    matiere: { code: "MATHS", label: "Mathématiques" },
    cursus: [{ id: 5, label: "BEPC" }],
    cursus_total: 1,
    tous_cursus: false,
    cursus_cible: 5,
    acces: "verrouille",
    nb: null,
    details: { slug: "thales-triangle" },
    ...surcharge,
  }
}

const THEME = resultat({
  id: 10,
  type: "THEME",
  titre: "théorème de Thalès",
  acces: null,
  details: { tag_id: 7, subject_code: "MATHS", nb_cours: 2, nb_quiz: 3, nb_exercices: 0 },
})

function reponse(surcharge: Partial<ReponseRecherche> = {}): ReponseRecherche {
  const groupes = [
    { type: "THEME" as const, libelle: "Thèmes", total: 1, resultats: [THEME] },
    { type: "COURS" as const, libelle: "Cours", total: 1, resultats: [resultat({})] },
  ]
  return {
    q: "thales", corrige: null, indexe: true, trop_court: false, total: 2, groupes, autres_cursus: 0, suggestions: [],
    ...surcharge,
  }
}

function Lieu() {
  const lieu = useLocation()
  return <div data-testid="lieu">{`${lieu.pathname}${lieu.search}`}</div>
}

function monter(ouvert = true) {
  const surChangement = vi.fn()
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/cm"]}>
        <RechercheGlobale open={ouvert} onOpenChange={surChangement} />
        <Lieu />
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return { surChangement, champ: () => screen.getByRole("combobox", { name: "Rechercher" }) }
}

beforeEach(() => {
  rechercher.mockReset()
  localStorage.clear()
})

describe("RechercheGlobale", () => {
  it("propose des pistes quand le champ est vide, sans interroger le serveur", () => {
    monter()
    expect(screen.getByText(/Cherche un thème/)).toBeInTheDocument()
    expect(rechercher).not.toHaveBeenCalled()
  })

  it("n'interroge pas pour un seul caractère", async () => {
    const { champ } = monter()
    await userEvent.type(champ(), "t")
    await new Promise((resolve) => setTimeout(resolve, 350))
    expect(rechercher).not.toHaveBeenCalled()
  })

  it("interroge après une pause de frappe, avec le cursus et le mode rapide, et groupe les résultats", async () => {
    rechercher.mockResolvedValue(reponse())
    const { champ } = monter()
    await userEvent.type(champ(), "thales")

    expect(await screen.findByRole("group", { name: "Thèmes" })).toBeInTheDocument()
    expect(screen.getByRole("group", { name: "Cours" })).toBeInTheDocument()
    // Une seule requête malgré six frappes : c'est la pause qui déclenche, pas chaque lettre.
    expect(rechercher).toHaveBeenCalledTimes(1)
    expect(rechercher).toHaveBeenCalledWith(
      { q: "thales", pays: "cm", cursus: 5, limite: 3, rapide: true },
      expect.anything(),
    )
    // Le résumé d'un thème dit ce qu'on y trouve.
    expect(screen.getByText(/2 cours · 3 questions/)).toBeInTheDocument()
  })

  it("surligne le mot cherché sans tenir compte des accents", async () => {
    rechercher.mockResolvedValue(reponse())
    const { champ } = monter()
    await userEvent.type(champ(), "thales")
    await screen.findByRole("group", { name: "Cours" })
    const marques = Array.from(document.querySelectorAll("mark")).map((m) => m.textContent)
    expect(marques).toContain("Thalès")
  })

  it("flèches puis Entrée ouvrent le résultat choisi", async () => {
    rechercher.mockResolvedValue(reponse())
    const { champ, surChangement } = monter()
    await userEvent.type(champ(), "thales")
    await screen.findByRole("group", { name: "Thèmes" })

    await userEvent.keyboard("{ArrowDown}{ArrowDown}{Enter}")

    await waitFor(() => expect(screen.getByTestId("lieu")).toHaveTextContent("/cours/thales-triangle"))
    expect(surChangement).toHaveBeenCalledWith(false)
  })

  it("Entrée sans sélection mène à la page de résultats avec la requête", async () => {
    rechercher.mockResolvedValue(reponse())
    const { champ } = monter()
    await userEvent.type(champ(), "théorème thalès")
    await screen.findByRole("group", { name: "Thèmes" })

    await userEvent.keyboard("{Enter}")

    await waitFor(() =>
      expect(screen.getByTestId("lieu")).toHaveTextContent(`/cm/recherche?q=${encodeURIComponent("théorème thalès")}`),
    )
  })

  it("annonce la sélection aux lecteurs d'écran", async () => {
    rechercher.mockResolvedValue(reponse())
    const { champ } = monter()
    await userEvent.type(champ(), "thales")
    await screen.findByRole("group", { name: "Thèmes" })

    await userEvent.keyboard("{ArrowDown}")

    const actif = champ().getAttribute("aria-activedescendant")
    expect(actif).toBeTruthy()
    expect(document.getElementById(actif!)).toHaveAttribute("aria-selected", "true")
  })

  it("dit quand rien ne correspond", async () => {
    rechercher.mockResolvedValue(reponse({ total: 0, groupes: [] }))
    const { champ } = monter()
    await userEvent.type(champ(), "xyzzyq")
    expect(await screen.findByText(/Aucun résultat pour « xyzzyq »/)).toBeInTheDocument()
  })

  it("montre la correction proposée par le serveur", async () => {
    rechercher.mockResolvedValue(reponse({ corrige: "thales" }))
    const { champ } = monter()
    await userEvent.type(champ(), "thalez")
    expect(await screen.findByText("Résultats pour « thales »")).toBeInTheDocument()
  })

  it("dit quand l'index n'est pas encore construit", async () => {
    rechercher.mockResolvedValue(reponse({ indexe: false, total: 0, groupes: [] }))
    const { champ } = monter()
    await userEvent.type(champ(), "thales")
    expect(await screen.findByText(/en cours de préparation/)).toBeInTheDocument()
  })

  it("dit quand la recherche est indisponible", async () => {
    rechercher.mockRejectedValue(new Error("réseau"))
    const { champ } = monter()
    await userEvent.type(champ(), "thales")
    expect(await screen.findByText(/momentanément indisponible/)).toBeInTheDocument()
  })

  it("mémorise une recherche validée et la repropose à l'ouverture suivante", async () => {
    rechercher.mockResolvedValue(reponse())
    const { champ } = monter()
    await userEvent.type(champ(), "thales")
    await screen.findByRole("group", { name: "Thèmes" })
    await userEvent.keyboard("{Enter}")

    await waitFor(() => expect(localStorage.getItem("edukamer_recherches_recentes")).toContain("thales"))
  })

  it("ne rend rien tant qu'elle est fermée", () => {
    monter(false)
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument()
  })
})
