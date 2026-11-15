import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

const signalerQuestionQuiz = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ signalerQuestionQuiz }))

import { SignalerQuestion } from "./SignalerQuestion"

beforeEach(() => vi.clearAllMocks())

describe("SignalerQuestion", () => {
  it("envoie le motif et le mot de l'élève, puis remercie", async () => {
    signalerQuestionQuiz.mockResolvedValue({ id: 1 })
    render(<SignalerQuestion sessionId={7} questionId={42} />)

    await userEvent.click(screen.getByRole("button", { name: /Signaler cette question/ }))
    const envoyer = screen.getByRole("button", { name: "Envoyer" })
    expect(envoyer).toBeDisabled() // sans motif, rien ne part
    await userEvent.click(screen.getByRole("radio", { name: "La bonne réponse me semble fausse" }))
    await userEvent.type(screen.getByLabelText(/Un mot pour nous aider/), " la clé est B ")
    await userEvent.click(envoyer)

    expect(signalerQuestionQuiz).toHaveBeenCalledWith(7, 42, { motif: "REPONSE_FAUSSE", commentaire: "la clé est B" })
    expect(await screen.findByText(/c'est signalé/)).toBeInTheDocument()
  })

  it("une panne reste visible et laisse recommencer", async () => {
    signalerQuestionQuiz.mockRejectedValue(new Error("réseau"))
    render(<SignalerQuestion sessionId={7} questionId={42} />)

    await userEvent.click(screen.getByRole("button", { name: /Signaler cette question/ }))
    await userEvent.click(screen.getByRole("radio", { name: "Autre chose" }))
    await userEvent.click(screen.getByRole("button", { name: "Envoyer" }))

    expect(await screen.findByRole("alert")).toHaveTextContent("pas parti")
    expect(screen.getByRole("button", { name: "Envoyer" })).toBeEnabled()
  })
});
