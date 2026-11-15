import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { QcmEpreuve } from "@/api/types"
import { QcmDExercice } from "./QcmDExercice"

const qcm: QcmEpreuve[] = [
  {
    id: 1, numero: "1", enonce_markdown: "Quelle est la capitale du Cameroun ?",
    choix: [{ lettre: "a", texte: "Douala" }, { lettre: "b", texte: "Yaoundé" }, { lettre: "c", texte: "Garoua" }], reponse_correcte: "b",
  },
  {
    id: 2, numero: "2", enonce_markdown: "2 + 2 = ?",
    choix: [{ lettre: "a", texte: "3" }, { lettre: "b", texte: "4" }], reponse_correcte: "b",
  },
]

describe("QcmDExercice", () => {
  it("reste replié derrière un bouton qui dit combien de QCM", () => {
    render(<QcmDExercice qcm={qcm} />)
    expect(screen.getByRole("button", { name: "Répondre aux 2 QCM en cliquant" })).toBeInTheDocument()
    expect(screen.queryByText("Quelle est la capitale du Cameroun ?")).not.toBeInTheDocument()
  })

  it("s'ouvre d'emblée en « Essaie d'abord »", () => {
    render(<QcmDExercice qcm={qcm} defaultOpen />)
    expect(screen.getByText("Quelle est la capitale du Cameroun ?")).toBeInTheDocument()
  })

  it("dit juste ou faux au clic, montre la bonne réponse et verrouille le choix", () => {
    render(<QcmDExercice qcm={qcm} defaultOpen />)
    fireEvent.click(screen.getByRole("button", { name: /Douala/ }))

    expect(screen.getByLabelText("Mauvaise réponse")).toBeInTheDocument()
    expect(screen.getByLabelText("Bonne réponse")).toBeInTheDocument() // la bonne lettre se révèle
    expect(screen.getByRole("button", { name: /Yaoundé/ })).toBeDisabled() // plus de second essai
    expect(screen.getByText(/0 bonne\(s\) sur 1 répondue\(s\)/)).toBeInTheDocument()
  })

  it("compte le score et conclut quand tout est répondu", () => {
    render(<QcmDExercice qcm={qcm} defaultOpen />)
    fireEvent.click(screen.getByRole("button", { name: /Yaoundé/ }))
    expect(screen.queryByText(/Le corrigé explique/)).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: /^b\s*4/ }))

    expect(screen.getByText(/2 bonne\(s\) sur 2 répondue\(s\)/)).toBeInTheDocument()
    expect(screen.getByText("2 sur 2. Le corrigé explique chaque réponse.")).toBeInTheDocument()
  })

  it("ne rend rien sans QCM", () => {
    const { container } = render(<QcmDExercice qcm={[]} />)
    expect(container.textContent).toBe("")
  })
})
