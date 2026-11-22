import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { MotDuFondateur } from "./MotDuFondateur"

describe("MotDuFondateur : une personne, son nom, et son lien avec le site", () => {
  it("dit pourquoi le site existe, sous un titre qui n'est pas celui d'un avis", () => {
    render(<MotDuFondateur />)

    expect(screen.getByText("Pourquoi j'ai créé EduKora")).toBeInTheDocument()
    expect(screen.getByText(/pour mon fils, qui prépare le BEPC/)).toBeInTheDocument()
    expect(screen.getByText(/au lieu de payer un répétiteur/)).toBeInTheDocument()
  })

  it("signe du nom et des deux qualités : parent ET fondateur, jamais un parent anonyme", () => {
    render(<MotDuFondateur />)

    expect(screen.getByText("Serge G. Babounlek")).toBeInTheDocument()
    expect(screen.getByText(/parent d'un élève de 3e et fondateur d'EduKora/)).toBeInTheDocument()
  })

  it("ne promet rien pour l'enfant d'un autre : c'est une expérience, pas une garantie", () => {
    render(<MotDuFondateur />)

    const citation = screen.getByText(/pour mon fils/).textContent ?? ""
    expect(citation).not.toMatch(/votre enfant|ton enfant|garanti|réussi/i)
  })
})
