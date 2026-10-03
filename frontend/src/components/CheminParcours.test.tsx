import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import { CheminParcours, type ItemChemin } from "./CheminParcours"

const items: ItemChemin[] = [
  { id: 1, titre: "Suites", rang: 1, bucket: "maitrise", taux: 90, frequencePct: 80 },
  { id: 2, titre: "Limites", rang: 2, bucket: "en_cours", taux: 40, frequencePct: 60 },
  { id: 3, titre: "Dérivées", rang: 3, bucket: "en_revision", taux: 30, frequencePct: 20 },
  { id: 4, titre: "Intégrales", rang: 4, bucket: "a_decouvrir", taux: null, frequencePct: 10 },
  { id: 5, titre: "Complexes", rang: 5, bucket: "sans_contenu", taux: null, frequencePct: null },
]

describe("CheminParcours", () => {
  it("rend un nœud accessible par thème, avec son état", () => {
    render(<CheminParcours items={items} prochainId={null} seuilOr={null} onSelect={() => {}} />)
    expect(screen.getByRole("button", { name: "Suites, Maîtrisé" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Limites, En cours" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Dérivées, À réviser" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Intégrales, À découvrir" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Complexes, Contenu à venir" })).toBeInTheDocument()
  })

  it("signale ce qui tombe souvent à l'examen, seulement au-dessus du seuil", () => {
    render(<CheminParcours items={items} prochainId={null} seuilOr={60} onSelect={() => {}} />)
    expect(screen.getByRole("button", { name: "Suites, Maîtrisé, tombe souvent à l'examen" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Limites, En cours, tombe souvent à l'examen" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Dérivées, À réviser" })).toBeInTheDocument()
  })

  it("ne dore rien sans seuil (programme classique)", () => {
    render(<CheminParcours items={items} prochainId={null} seuilOr={null} onSelect={() => {}} />)
    expect(screen.queryByRole("button", { name: /tombe souvent/ })).not.toBeInTheDocument()
  })

  it("marque le prochain pas recommandé, une seule fois", () => {
    render(<CheminParcours items={items} prochainId={3} seuilOr={null} onSelect={() => {}} />)
    expect(screen.getAllByText("Commence ici")).toHaveLength(1)
  })

  it("ouvre le détail du thème au clic", () => {
    const onSelect = vi.fn()
    render(<CheminParcours items={items} prochainId={null} seuilOr={null} onSelect={onSelect} />)
    fireEvent.click(screen.getByRole("button", { name: "Limites, En cours" }))
    expect(onSelect).toHaveBeenCalledWith(2)
  })

  it("n'affiche rien sans thème", () => {
    const { container } = render(<CheminParcours items={[]} prochainId={null} seuilOr={null} onSelect={() => {}} />)
    expect(container).toBeEmptyDOMElement()
  })
})
