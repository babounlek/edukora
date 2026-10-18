import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { ExerciceLabelSource } from "@/components/EpreuveSommaire"

import { ExerciceNav } from "./ExerciceNav"

function exercice(numero: string, groupes: string[]): ExerciceLabelSource {
  return { numero_exercice: numero, titre: "", groupes }
}

/** `parSection` exercices numérotés de suite dans chacune des sections. */
function epreuve(sections: string[], parSection: number) {
  const sortie: ExerciceLabelSource[] = []
  for (const section of sections) {
    for (let i = 0; i < parSection; i += 1) sortie.push(exercice(String(sortie.length + 1), [section]))
  }
  return sortie
}

describe("ExerciceNav", () => {
  it("nomme les voisins par leur numéro", () => {
    render(<ExerciceNav exercises={epreuve(["A"], 4)} index={1} />)
    expect(screen.getByRole("link", { name: /Ex\. 1/ })).toHaveAttribute("href", "#exercice-1")
    expect(screen.getByRole("link", { name: /Ex\. 3/ })).toHaveAttribute("href", "#exercice-3")
  })

  it("dit la section du voisin quand on en change, dans une longue épreuve", () => {
    const exercices = epreuve(["SECTION 2.1", "SECTION 2.2"], 3)
    // Dernière question de la section 2.1 : le suivant ouvre la section 2.2, le précédent reste dans la sienne.
    render(<ExerciceNav exercises={exercices} index={2} />)
    expect(screen.getByRole("link", { name: /Ex\. 4 · SECTION 2\.2/ })).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /^Ex\. 2$/ })).toBeInTheDocument()
  })

  it("ne précise pas la section pour un voisin de la même section", () => {
    render(<ExerciceNav exercises={epreuve(["SECTION 2.1", "SECTION 2.2"], 3)} index={4} />)
    expect(screen.getByRole("link", { name: /^Ex\. 4$/ })).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /^Ex\. 6$/ })).toBeInTheDocument()
  })

  it("ne précise jamais la section d'une épreuve courte", () => {
    render(<ExerciceNav exercises={epreuve(["SECTION 2.1", "SECTION 2.2"], 2)} index={1} />)
    expect(screen.getByRole("link", { name: /^Ex\. 3$/ })).toBeInTheDocument()
  })
})
