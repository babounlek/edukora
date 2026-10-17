import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it } from "vitest"

import type { CoursSectionData } from "@/api/types"

import { CoursSection } from "./CoursSection"

/**
 * Tout cours est libre en lecture ; sa section « exercices d'application » est payante. Le serveur la remplace, pour un
 * lecteur sans abonnement, par un marqueur sans contenu : la carte annonce combien d'exercices attendent l'abonné.
 */
function verrouillee(nb: number, difficultes: string[] = []): CoursSectionData {
  return { type: "exercices_application", verrouille: true, nb_exercices: nb, difficultes, items: [] }
}

function afficher(section: CoursSectionData, lienAbonnement?: string) {
  return render(
    <MemoryRouter>
      <CoursSection section={section} lienAbonnement={lienAbonnement} />
    </MemoryRouter>,
  )
}

describe("CoursSection : exercices d'application verrouillés", () => {
  it("annonce le nombre d'exercices et le niveau, sans en montrer aucun", () => {
    afficher(verrouillee(3, ["facile", "moyen", "approfondissement"]))

    expect(screen.getByRole("heading", { name: "Exercices d'application" })).toBeInTheDocument()
    expect(screen.getByText("3 exercices d'application corrigés")).toBeInTheDocument()
    expect(screen.getByText("facile")).toBeInTheDocument()
    expect(screen.getByText("approfondissement")).toBeInTheDocument()
    expect(screen.queryByText(/Exercice 1/)).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: /solution/i })).not.toBeInTheDocument()
  })

  it("dit que le cours lui-même est gratuit", () => {
    afficher(verrouillee(2))

    expect(screen.getByText(/Le cours est gratuit/)).toBeInTheDocument()
  })

  it("accorde au singulier pour un seul exercice", () => {
    afficher(verrouillee(1, ["facile"]))

    expect(screen.getByText("1 exercice d'application corrigé")).toBeInTheDocument()
  })

  it("le bouton d'abonnement mène au lien fourni par le lecteur", () => {
    afficher(verrouillee(2), "/abonnement/7?retour=%2Fcours%2Fx%2Flire")

    expect(screen.getByRole("link", { name: /abonner/i })).toHaveAttribute("href", "/abonnement/7?retour=%2Fcours%2Fx%2Flire")
  })

  it("sans lien fourni, le bouton mène à la page des tarifs", () => {
    afficher(verrouillee(2))

    expect(screen.getByRole("link", { name: /abonner/i })).toHaveAttribute("href", "/tarifs")
  })

  it("une section d'exercices NON verrouillée s'affiche comme avant, avec ses solutions", () => {
    afficher({
      type: "exercices_application",
      items: [{ numero: 1, difficulte: "facile", enonce_markdown: "Calcule 2 + 2.", solution_markdown: "On trouve 4." }],
    })

    expect(screen.getByText("Calcule 2 + 2.")).toBeInTheDocument()
    expect(screen.queryByText(/Le cours est gratuit/)).not.toBeInTheDocument()
  })
})
