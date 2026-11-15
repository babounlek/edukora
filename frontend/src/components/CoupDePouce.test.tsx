import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getIndiceQuiz = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getIndiceQuiz }))
vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <p>{markdown}</p> }))

import { CoupDePouce, PastilleDifficulte } from "./CoupDePouce"

beforeEach(() => vi.clearAllMocks())

describe("CoupDePouce", () => {
  it("déplie la méthode à la demande", async () => {
    getIndiceQuiz.mockResolvedValue({ indice_markdown: "Dérive puis étudie le signe." })
    render(<CoupDePouce sessionId={3} questionId={9} />)

    await userEvent.click(screen.getByRole("button", { name: "Un coup de pouce" }))

    expect(await screen.findByText("Dérive puis étudie le signe.")).toBeInTheDocument()
    expect(getIndiceQuiz).toHaveBeenCalledWith(3, 9)
    expect(screen.queryByRole("button", { name: "Un coup de pouce" })).not.toBeInTheDocument()
  })

  it("une panne laisse le bouton pour recommencer", async () => {
    getIndiceQuiz.mockRejectedValue(new Error("réseau"))
    render(<CoupDePouce sessionId={3} questionId={9} />)

    await userEvent.click(screen.getByRole("button", { name: "Un coup de pouce" }))

    expect(await screen.findByRole("alert")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Un coup de pouce" })).toBeEnabled()
  })
})

describe("PastilleDifficulte", () => {
  it("dit la difficulté en mots, et se tait quand elle n'est pas estimée", () => {
    const { rerender, container } = render(<PastilleDifficulte difficulte="ELEVEE" />)
    expect(screen.getByText("Difficile")).toBeInTheDocument()

    rerender(<PastilleDifficulte difficulte={null} />)
    expect(container).toBeEmptyDOMElement()
  })
})
