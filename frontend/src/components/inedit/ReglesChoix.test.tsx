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

  it("présente une règle « ou » comme une simple consigne", () => {
    render(<ReglesChoix regles={[{ type: "ou", portee: "SECTION II", options: [["a", "b"], ["c"]] }]} traites={new Set()} />)
    expect(screen.getByText("SECTION II : au choix, a, b ou c.")).toBeInTheDocument()
  })
})
