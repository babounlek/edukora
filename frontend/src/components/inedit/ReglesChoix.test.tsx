import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { RegleChoix } from "@/api/types"
import { ReglesChoix } from "./ReglesChoix"

const PARMI: RegleChoix = { type: "parmi", portee: "SECTION A", repondre: 2, sur: 3, exercices: [1, 2, 3] }

describe("ReglesChoix", () => {
  it("ne montre rien sans règle", () => {
    const { container } = render(<ReglesChoix regles={[]} traites={new Set()} />)
    expect(container).toBeEmptyDOMElement()
  })

  it("annonce « n sur m » et le nombre d'exercices déjà traités", () => {
    render(<ReglesChoix regles={[PARMI]} traites={new Set([1])} />)
    expect(screen.getByText(/SECTION A : traite 2 exercices parmi 3/)).toBeInTheDocument()
    expect(screen.getByText("Traités : 1 / 2")).toBeInTheDocument()
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
  })

  it("prévient quand on dépasse le nombre demandé", () => {
    render(<ReglesChoix regles={[PARMI]} traites={new Set([1, 2, 3])} />)
    expect(screen.getByRole("status")).toHaveTextContent("seuls les 2 meilleurs seront comptés")
  })

  it("ne compte que les exercices de la règle", () => {
    render(<ReglesChoix regles={[PARMI]} traites={new Set([1, 2, 99, 98])} />)
    expect(screen.getByText("Traités : 2 / 2")).toBeInTheDocument()
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
  })

  it("sur un sujet lu en ligne (sans simulation), dit seulement quoi traiter : ni « meilleurs comptent » ni compteur", () => {
    render(<ReglesChoix regles={[PARMI]} />)
    expect(screen.getByText("SECTION A : traite 2 exercices parmi 3.")).toBeInTheDocument()
    expect(screen.queryByText(/Traités/)).not.toBeInTheDocument()
    expect(screen.queryByText(/meilleurs/)).not.toBeInTheDocument()
  })

  it("annonce « toutes les questions dans une seule section »", () => {
    const regle: RegleChoix = { type: "section_unique", portee: "PAPER 3", repondre: 4, exercices: [1, 2, 3, 4, 5] }
    const { unmount } = render(<ReglesChoix regles={[regle]} />)
    expect(screen.getByText("PAPER 3 : traite 4 exercices, tous dans une seule section.")).toBeInTheDocument()
    unmount()

    // En simulation : compteur d'exercices traités, et seuls les meilleurs comptent.
    render(<ReglesChoix regles={[regle]} traites={new Set([1, 2])} />)
    expect(screen.getByText(/PAPER 3 : traite 4 exercices, tous dans une seule section. Seuls les 4 meilleurs comptent/)).toBeInTheDocument()
    expect(screen.getByText("Traités : 2 / 4")).toBeInTheDocument()
  })

  it("accorde « exercice » au singulier", () => {
    render(<ReglesChoix regles={[{ type: "section_unique", portee: "PAPER 2", repondre: 1 }]} />)
    expect(screen.getByText("PAPER 2 : traite 1 exercice, dans une seule section.")).toBeInTheDocument()
  })

  it("affiche une consigne libre telle quelle, dans la langue du sujet", () => {
    render(
      <ReglesChoix regles={[{ type: "consigne", portee: "SECTION I", texte: "Le candidat traitera deux sujets de genres différents." }]} />,
    )
    expect(
      screen.getByText("SECTION I : Le candidat traitera deux sujets de genres différents."),
    ).toBeInTheDocument()
  })

  it("présente une règle « ou » comme une simple consigne", () => {
    render(<ReglesChoix regles={[{ type: "ou", portee: "SECTION II", options: [["a", "b"], ["c"]] }]} traites={new Set()} />)
    expect(screen.getByText("SECTION II : au choix, a, b ou c.")).toBeInTheDocument()
  })
})
