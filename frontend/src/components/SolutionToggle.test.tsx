import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { SolutionToggle, SolutionsOuvertesContext } from "./SolutionToggle"

describe("SolutionToggle", () => {
  it("garde la solution derrière un bouton tant que rien n'a été demandé", () => {
    render(<SolutionToggle>La solution détaillée</SolutionToggle>)

    expect(screen.queryByText("La solution détaillée")).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole("button"))
    expect(screen.getByText("La solution détaillée")).toBeInTheDocument()
  })

  it("montre la solution sans bouton quand l'élève a déjà demandé la correction (quiz)", () => {
    render(
      <SolutionsOuvertesContext.Provider value>
        <SolutionToggle>La solution détaillée</SolutionToggle>
      </SolutionsOuvertesContext.Provider>,
    )

    // Avant : un second bouton « Afficher la solution » apparaissait dans la correction (test élève Gogo).
    expect(screen.getByText("La solution détaillée")).toBeInTheDocument()
    expect(screen.queryByRole("button")).not.toBeInTheDocument()
  })
})
