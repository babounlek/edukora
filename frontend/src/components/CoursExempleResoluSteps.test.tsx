import { fireEvent, render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { CoursSectionExempleResoluEtape } from "@/api/types"

vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <span>{markdown}</span> }))

import { CoursExempleResoluSteps } from "./CoursExempleResoluSteps"

const etape = (n: number, extra: Partial<CoursSectionExempleResoluEtape> = {}): CoursSectionExempleResoluEtape => ({
  numero: n, action: `Action ${n}`, justification: `Pourquoi ${n}`, resultat_markdown: `Résultat ${n}`, body_markdown: null, ...extra,
})

function afficher(etapes = [etape(1), etape(2)]) {
  return render(<CoursExempleResoluSteps enonce_markdown="Énoncé" etapes={etapes} conclusion_markdown="Conclusion" />)
}

describe("CoursExempleResoluSteps : l'exemple se dévoile pas à pas", () => {
  beforeEach(() => localStorage.clear())

  it("montre d'abord ce qu'on fait, et garde le résultat et la suite pour après", () => {
    afficher()

    expect(screen.getByText("Énoncé")).toBeVisible()
    expect(screen.getByText("Action 1")).toBeVisible()
    expect(screen.getByText("Résultat 1")).not.toBeVisible()
    expect(screen.getByText("Pourquoi 1")).not.toBeVisible()
    expect(screen.getByText("Action 2")).not.toBeVisible()
    expect(screen.getByText("Conclusion")).not.toBeVisible()
    expect(screen.getByText("Étape 1 sur 2")).toBeVisible()
  })

  it("dévoile une étape à la fois, puis la conclusion", () => {
    afficher()

    fireEvent.click(screen.getByRole("button", { name: "Voir le résultat" }))
    expect(screen.getByText("Résultat 1")).toBeVisible()
    expect(screen.getByText("Action 2")).toBeVisible()
    expect(screen.getByText("Résultat 2")).not.toBeVisible()
    expect(screen.getByText("Conclusion")).not.toBeVisible()

    fireEvent.click(screen.getByRole("button", { name: "Voir le résultat" }))
    expect(screen.getByText("Résultat 2")).toBeVisible()
    expect(screen.getByText("Conclusion")).toBeVisible()
    expect(screen.queryByRole("button", { name: "Voir le résultat" })).toBeNull()
    expect(screen.getByText(/Exemple terminé/)).toBeVisible()
  })

  it("se refait depuis le début", () => {
    afficher()
    fireEvent.click(screen.getByRole("button", { name: "Voir le résultat" }))
    fireEvent.click(screen.getByRole("button", { name: "Voir le résultat" }))

    fireEvent.click(screen.getByRole("button", { name: "Refaire l'exemple" }))

    expect(screen.getByText("Résultat 1")).not.toBeVisible()
    expect(screen.getByText("Action 2")).not.toBeVisible()
  })

  it("« Tout afficher » montre tout et se retient d'une visite à l'autre", () => {
    const { unmount } = afficher()
    fireEvent.click(screen.getByRole("button", { name: "Tout afficher" }))

    expect(screen.getByText("Résultat 2")).toBeVisible()
    expect(screen.getByText("Conclusion")).toBeVisible()
    expect(screen.queryByRole("button", { name: "Voir le résultat" })).toBeNull()
    expect(screen.queryByText(/Exemple terminé/)).toBeNull()

    unmount()
    afficher()
    expect(screen.getByText("Résultat 1")).toBeVisible()
    expect(screen.getByText("Conclusion")).toBeVisible()
  })

  it("passe d'elle-même une étape qui n'a rien à dévoiler", () => {
    // Étape en texte nu (pas d'action) puis étape sans suite : rien à chercher, on va droit à la troisième.
    afficher([
      etape(1, { action: null, justification: null, resultat_markdown: null, body_markdown: "Texte de l'étape 1" }),
      etape(2, { justification: null, resultat_markdown: null }),
      etape(3, { resultat_markdown: null }),
    ])

    expect(screen.getByText("Texte de l'étape 1")).toBeVisible()
    expect(screen.getByText("Action 2")).toBeVisible()
    expect(screen.getByText("Action 3")).toBeVisible()
    expect(screen.getByText("Pourquoi 3")).not.toBeVisible()
    // Sans résultat encadré, le bouton parle d'explication.
    fireEvent.click(screen.getByRole("button", { name: "Voir l'explication" }))
    expect(screen.getByText("Pourquoi 3")).toBeVisible()
  })

  it("n'affiche ni bascule ni bouton quand aucune étape n'a de suite à dévoiler", () => {
    afficher([etape(1, { action: null, justification: null, resultat_markdown: null, body_markdown: "Tout le texte" })])

    expect(screen.getByText("Tout le texte")).toBeVisible()
    expect(screen.getByText("Conclusion")).toBeVisible()
    expect(screen.queryByRole("button")).toBeNull()
  })
})
