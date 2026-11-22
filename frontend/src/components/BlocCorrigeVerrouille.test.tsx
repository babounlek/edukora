import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const declare = vi.hoisted(() => ({ id: null as number | null }))

vi.mock("@/lib/cursusAccueil", () => ({ useCursusDeclare: () => declare.id }))
vi.mock("@/components/BoutonParents", () => ({
  BoutonParents: ({ examen }: { examen?: string }) => <p>Montrer à mes parents ({examen ?? "sans examen"})</p>,
  ApercuMessageParents: ({ contenu }: { contenu?: string }) => <p>Aperçu du message : {contenu}</p>,
}))
vi.mock("@/components/ParrainageHint", () => ({ ParrainageHint: () => null }))

import type { Epreuve } from "@/api/types"
import { BlocCorrigeVerrouille } from "./BlocCorrigeVerrouille"

const BAC_C = { id: 20, examen_display: "BAC", series: { code: "C" } }
const BAC_D = { id: 22, examen_display: "BAC", series: { code: "D" } }

function afficher(cursus: unknown[]) {
  const epreuve = { slug: "philosophie-bac-c-et-d-2026", title: "Philosophie BAC C et D 2026", cursus } as unknown as Epreuve
  return render(
    <MemoryRouter>
      <BlocCorrigeVerrouille epreuve={epreuve} pays="cm" />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  declare.id = null
})

describe("BlocCorrigeVerrouille : le verrou dit le prix et où juger avant de payer", () => {
  it("écrit le prix du mois et le moyen de payer dans le bloc", () => {
    afficher([BAC_C])

    expect(screen.getByText("2 000 FCFA par mois, par Mobile Money (Orange ou MTN), sans engagement.")).toBeInTheDocument()
  })

  it("mène aux corrigés gratuits du même examen", () => {
    afficher([BAC_C])

    expect(screen.getByRole("link", { name: "Lis d'abord un corrigé gratuit du BAC C" })).toHaveAttribute(
      "href",
      "/cm/epreuves?gratuit=true&cursus=20",
    )
  })

  it("propose un bouton par examen tant que la personne n'a pas dit lequel elle prépare", () => {
    afficher([BAC_C, BAC_D])

    expect(screen.getByRole("link", { name: "S'abonner (C)" })).toHaveAttribute("href", "/abonnement?cursus=20")
    expect(screen.getByRole("link", { name: "S'abonner (D)" })).toHaveAttribute("href", "/abonnement?cursus=22")
    expect(screen.getByText(/l'abonnement à l'un de ces examens suffit/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Lis d'abord un corrigé gratuit" })).toHaveAttribute("href", "/cm/epreuves?gratuit=true")
  })

  it("ne garde qu'un bouton, pour son examen, à qui a déjà choisi le BAC D", () => {
    declare.id = 22
    afficher([BAC_C, BAC_D])

    expect(screen.getByRole("link", { name: "S'abonner" })).toHaveAttribute("href", "/abonnement?cursus=22")
    expect(screen.queryByRole("link", { name: "S'abonner (C)" })).not.toBeInTheDocument()
    expect(screen.queryByText(/l'un de ces examens/)).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Lis d'abord un corrigé gratuit du BAC D" })).toHaveAttribute(
      "href",
      "/cm/epreuves?gratuit=true&cursus=22",
    )
    expect(screen.getByText("Montrer à mes parents (BAC)")).toBeInTheDocument()
  })

  it("garde tous les boutons si l'examen choisi n'est pas un de ceux de l'épreuve", () => {
    declare.id = 14
    afficher([BAC_C, BAC_D])

    expect(screen.getByRole("link", { name: "S'abonner (C)" })).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "S'abonner (D)" })).toBeInTheDocument()
  })
})
