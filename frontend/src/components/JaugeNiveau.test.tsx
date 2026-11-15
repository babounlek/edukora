import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { JaugeNiveau, ProgressionNiveau } from "./JaugeNiveau"

describe("JaugeNiveau", () => {
  it("dit le cran en toutes lettres", () => {
    render(<JaugeNiveau niveau="solide" />)
    expect(screen.getByText("Solide")).toBeInTheDocument()
  })

  it("ne montre rien pour un thème jamais tenté", () => {
    const { container } = render(<JaugeNiveau niveau={null} />)
    expect(container).toBeEmptyDOMElement()
  })
})

describe("ProgressionNiveau", () => {
  it("annonce le passage d'un cran à l'autre", () => {
    render(<ProgressionNiveau avant="en_cours" apres="solide" />)
    expect(screen.getByText("En cours → Solide")).toBeInTheDocument()
  })

  it("un premier quiz annonce le cran gagné", () => {
    render(<ProgressionNiveau avant={null} apres="decouvert" />)
    expect(screen.getByText(/Découvert/)).toBeInTheDocument()
  })

  it("si le cran n'a pas bougé, montre simplement la jauge", () => {
    render(<ProgressionNiveau avant="en_cours" apres="en_cours" />)
    expect(screen.queryByText(/→/)).not.toBeInTheDocument()
    expect(screen.getByText("En cours")).toBeInTheDocument()
  })
})
