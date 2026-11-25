import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { FicheEdukora } from "@/api/types"
import { grouperParRubrique } from "@/lib/rubriquesFiches"
import { BlocsFiche, Sessions } from "./BlocsFiche"

function fiche(extra: Partial<FicheEdukora> = {}): FicheEdukora {
  return {
    id: 1, terme: "Comment factoriser ?", definition: "La méthode.", exemple: "", sessions: [], gratuit: true,
    verrouillee: false, gardee: false, a_relire: false, matiere_id: 1, ...extra,
  }
}

describe("BlocsFiche", () => {
  it("garde la réponse cachée jusqu'à ce que l'élève la demande", () => {
    render(<BlocsFiche fiche={fiche({ piege: "Les parenthèses.", exercice: "Factorise.", reponse: "Résultat attendu" })} />)
    expect(screen.getByText("Les parenthèses.")).toBeTruthy()
    expect(screen.queryByText("Résultat attendu")).toBeNull()
    fireEvent.click(screen.getByRole("button", { name: "Voir la réponse" }))
    expect(screen.getByText("Résultat attendu")).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Masquer la réponse" }))
    expect(screen.queryByText("Résultat attendu")).toBeNull()
  })

  it("ne montre aucun bloc vide pour une fiche de définition", () => {
    const { container } = render(<BlocsFiche fiche={fiche()} />)
    expect(container.textContent).toBe("")
  })
})

describe("Sessions", () => {
  const annees = [2001, 2005, 2009, 2012, 2018, 2022].map((annee) => ({ annee, origine: "OFFICIEL" }))

  it("replie les années les plus anciennes et les rend à la demande", () => {
    render(<Sessions fiche={fiche({ sessions: annees })} />)
    expect(screen.queryByText("2001")).toBeNull()
    expect(screen.getByText("2022")).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Voir 2 années plus anciennes" }))
    expect(screen.getByText("2001")).toBeTruthy()
    expect(screen.queryByRole("button")).toBeNull()
  })

  it("ne propose rien à déplier quand quatre années suffisent", () => {
    render(<Sessions fiche={fiche({ sessions: annees.slice(0, 4) })} />)
    expect(screen.queryByRole("button")).toBeNull()
  })
})

describe("grouperParRubrique", () => {
  it("range les rubriques dans un ordre fixe et garde l'ordre des fiches", () => {
    const groupes = grouperParRubrique([
      fiche({ id: 1, rubrique: "Statistiques" }), fiche({ id: 2, rubrique: "Calcul" }),
      fiche({ id: 3 }), fiche({ id: 4, rubrique: "Calcul" }), fiche({ id: 5, rubrique: "Géométrie" }),
    ])
    expect(groupes.map((g) => g.rubrique)).toEqual(["Calcul", "Géométrie", "Statistiques", ""])
    expect(groupes[0].fiches.map((f) => f.id)).toEqual([2, 4])
  })
})
