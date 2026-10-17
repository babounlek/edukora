import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { getCoursTitres } = vi.hoisted(() => ({ getCoursTitres: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ getCoursTitres }))

import { reinitialiserTitresCours } from "@/lib/coursTitres"

import { EpreuveMarkdown } from "./EpreuveMarkdown"

const TITRES: Record<string, string> = {
  "mole-concept": "Mole Concept: from grams to moles",
  halogens: "Halogens: reactivity and tests",
}

function afficher(markdown: string) {
  return render(
    <MemoryRouter>
      <EpreuveMarkdown markdown={markdown} directCoursLinks />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  reinitialiserTitresCours()
  getCoursTitres.mockReset()
  getCoursTitres.mockImplementation(async (slugs: string[]) =>
    Object.fromEntries(slugs.filter((s) => TITRES[s]).map((s) => [s, TITRES[s]])),
  )
})

/**
 * Les marqueurs « [COURS_LINK:slug] » d'un corrigé ne portent que le slug : deux boutons « See the full lesson »
 * côte à côte étaient indiscernables. Chaque lien affiche maintenant le titre de son cours.
 */
describe("EpreuveMarkdown : liens vers les cours nommés par leur titre", () => {
  it("un groupe de liens affiche le titre de chaque cours, vers le bon cours", async () => {
    afficher("Corrigé.\n\n[COURS_LINK:mole-concept]\n\n[COURS_LINK:halogens]")

    const mole = await screen.findByRole("link", { name: /Mole Concept: from grams to moles/ })
    const halogens = await screen.findByRole("link", { name: /Halogens: reactivity and tests/ })

    expect(mole).toHaveAttribute("href", "/cours/mole-concept/lire")
    expect(halogens).toHaveAttribute("href", "/cours/halogens/lire")
    expect(getCoursTitres).toHaveBeenCalledTimes(1) // une seule requête pour toute la page
  })

  it("un lien isolé garde son libellé et y ajoute le titre", async () => {
    afficher("Corrigé.\n\n[COURS_LINK:mole-concept]")

    const lien = await screen.findByRole("link", { name: /Mole Concept: from grams to moles/ })

    expect(lien).toHaveTextContent("Voir le cours complet")
    expect(lien).toHaveAttribute("href", "/cours/mole-concept/lire")
  })

  it("le lien d'un encadré « Rappel de méthode » porte aussi le titre", async () => {
    afficher("### Rappel de méthode\n\nUne règle générale.\n\n[COURS_LINK:halogens]\n")

    const lien = await screen.findByRole("link", { name: /Halogens: reactivity and tests/ })

    expect(lien).toHaveTextContent("Voir le cours complet")
  })

  it("sans titre connu, le lien garde son libellé générique", async () => {
    afficher("Corrigé.\n\n[COURS_LINK:inconnu]")

    const lien = await screen.findByRole("link", { name: "Voir le cours complet" })
    await vi.waitFor(() => expect(getCoursTitres).toHaveBeenCalled())

    expect(lien).toHaveAttribute("href", "/cours/inconnu/lire")
    expect(lien).not.toHaveTextContent("·")
  })

  it("si la requête des titres échoue, les liens restent utilisables", async () => {
    getCoursTitres.mockRejectedValue(new Error("réseau"))
    afficher("Corrigé.\n\n[COURS_LINK:mole-concept]")

    const lien = await screen.findByRole("link", { name: "Voir le cours complet" })
    await vi.waitFor(() => expect(getCoursTitres).toHaveBeenCalled())

    expect(lien).toHaveAttribute("href", "/cours/mole-concept/lire")
  })
})
