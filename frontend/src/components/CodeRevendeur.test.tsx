import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getRattachementRevendeur = vi.hoisted(() => vi.fn())
const postRattachementRevendeur = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ getRattachementRevendeur, postRattachementRevendeur }))

import { ApiError } from "@/api/client"
import { memoriserCodeRevendeur, codeRevendeurMemorise } from "@/lib/referral"
import { CodeRevendeur } from "./CodeRevendeur"

beforeEach(() => {
  localStorage.clear()
  getRattachementRevendeur.mockReset()
  postRattachementRevendeur.mockReset()
})

describe("CodeRevendeur", () => {
  it("n'affiche rien à quelqu'un qui a déjà un revendeur ou un paiement, et oublie le code mémorisé", async () => {
    memoriserCodeRevendeur("DEMO42")
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: false, revendeur: { nom_affiche: "Marie" } })

    const { container } = render(<CodeRevendeur />)

    await waitFor(() => expect(codeRevendeurMemorise()).toBe(""))
    expect(container).toBeEmptyDOMElement()
  })

  it("ne gêne pas le paiement quand le serveur ne répond pas", async () => {
    getRattachementRevendeur.mockRejectedValue(new Error("réseau"))

    const { container } = render(<CodeRevendeur />)

    await waitFor(() => expect(getRattachementRevendeur).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("propose un lien discret, puis la saisie, et valide le code", async () => {
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: true, revendeur: null })
    postRattachementRevendeur.mockResolvedValue({ revendeur: { nom_affiche: "Marie Tutorat" } })
    const user = userEvent.setup()

    render(<CodeRevendeur />)
    await user.click(await screen.findByRole("button", { name: /code revendeur/i }))
    await user.type(screen.getByLabelText(/code revendeur/i), "demo42")
    await user.click(screen.getByRole("button", { name: /valider/i }))

    expect(postRattachementRevendeur).toHaveBeenCalledWith("DEMO42")
    expect(await screen.findByText(/Marie Tutorat/)).toBeInTheDocument()
  })

  it("préremplit le code d'un lien déjà ouvert, sans l'envoyer tant que la personne n'a pas validé", async () => {
    memoriserCodeRevendeur("DEMO42")
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: true, revendeur: null })

    render(<CodeRevendeur />)

    expect(await screen.findByDisplayValue("DEMO42")).toBeInTheDocument()
    expect(postRattachementRevendeur).not.toHaveBeenCalled()
  })

  it("dit qu'un code n'est pas valable sans dire pourquoi", async () => {
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: true, revendeur: null })
    postRattachementRevendeur.mockRejectedValue(new ApiError(400, { code: "code_invalide" }))
    const user = userEvent.setup()
    memoriserCodeRevendeur("NOPE99")

    render(<CodeRevendeur />)
    await user.click(await screen.findByRole("button", { name: /valider/i }))

    expect(await screen.findByRole("alert")).toHaveTextContent(/pas valable/i)
    expect(codeRevendeurMemorise()).toBe("NOPE99")
  })
})
