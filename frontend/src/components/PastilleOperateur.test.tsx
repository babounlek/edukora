import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { PastilleOperateur } from "./PastilleOperateur"

describe("PastilleOperateur", () => {
  it("pastille neutre : le texte n'est jamais posé sur l'aplat de marque (contraste), le point seul porte la couleur", () => {
    render(<PastilleOperateur operateur="ORANGE">Orange Money</PastilleOperateur>)
    const pastille = screen.getByText("Orange Money")
    expect(pastille.className).not.toContain("bg-[#FF7900]")
    expect(pastille.className).not.toContain("text-white")
    const point = pastille.querySelector("[aria-hidden=true]")!
    expect(point.className).toContain("bg-[#FF7900]")
  })

  it("MTN utilise le même jaune que les pages de paiement", () => {
    render(<PastilleOperateur operateur="MTN">MTN MoMo</PastilleOperateur>)
    expect(screen.getByText("MTN MoMo").querySelector("[aria-hidden=true]")!.className).toContain("bg-[#FFCC08]")
  })
})
