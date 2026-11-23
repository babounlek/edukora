import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { BandePreuves } from "./BandePreuves"

describe("BandePreuves : les chiffres du corpus, en grand, sous le hero", () => {
  it("affiche les quatre chiffres reçus, chacun avec son libellé", () => {
    render(<BandePreuves chiffres={{ epreuves: 1621, cours: 14158, matieres: 26, inedites: 327 }} />)

    expect(screen.getByRole("heading", { level: 2, name: "Ce que tu trouves sur EduKora" })).toBeInTheDocument()
    expect(screen.getByText("1 621")).toBeInTheDocument()
    expect(screen.getByText("épreuves corrigées")).toBeInTheDocument()
    expect(screen.getByText("14 158")).toBeInTheDocument()
    expect(screen.getByText("26")).toBeInTheDocument()
    expect(screen.getByText("327")).toBeInTheDocument()
    expect(screen.getByText("épreuves inédites")).toBeInTheDocument()
  })

  it("n'affiche pas un chiffre à zéro ni un chiffre qui n'est pas encore arrivé", () => {
    render(<BandePreuves chiffres={{ epreuves: 12, cours: 40, matieres: 0 }} />)

    expect(screen.getAllByRole("term")).toHaveLength(2)
    expect(screen.queryByText(/inédite/)).toBeNull()
    expect(screen.queryByText(/matière/)).toBeNull()
  })

  it("garde sa place pendant le chargement : le titre est là, sans aucun chiffre inventé", () => {
    render(<BandePreuves chiffres={undefined} />)

    expect(screen.getByRole("heading", { level: 2 })).toBeInTheDocument()
    expect(screen.queryAllByRole("term")).toHaveLength(0)
  })
})
