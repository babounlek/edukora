import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

const marquerExerciceFait = vi.hoisted(() => vi.fn())
const toast = vi.hoisted(() => ({ error: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ marquerExerciceFait }))
vi.mock("sonner", () => ({ toast }))

import { PartReussie } from "./PartReussie"

beforeEach(() => {
  vi.clearAllMocks()
  marquerExerciceFait.mockResolvedValue({ exercise_id: 7, fait: true })
})

describe("PartReussie", () => {
  it("propose les quatre réponses, sans rien de choisi ni de points tant que l'élève n'a pas répondu", () => {
    render(<PartReussie exerciseId={7} points="5" />)

    expect(screen.getByText("Qu'as-tu réussi ?")).toBeInTheDocument()
    for (const nom of ["Rien", "La moitié", "Presque tout", "Tout"]) {
      expect(screen.getByRole("button", { name: nom })).toHaveAttribute("aria-pressed", "false")
    }
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
  })

  it("enregistre la réponse et la traduit en points du barème", async () => {
    render(<PartReussie exerciseId={7} points="5" />)

    await userEvent.click(screen.getByRole("button", { name: "Presque tout" }))

    await waitFor(() => expect(marquerExerciceFait).toHaveBeenCalledWith(7, true, 75))
    expect(screen.getByRole("button", { name: "Presque tout" })).toHaveAttribute("aria-pressed", "true")
    expect(screen.getByRole("status")).toHaveTextContent("Environ 3,75 sur 5 points à l'examen.")
  })

  it("reprend la part déjà déclarée, et se corrige", async () => {
    render(<PartReussie exerciseId={7} points="3.5" initiale={50} />)

    expect(screen.getByRole("button", { name: "La moitié" })).toHaveAttribute("aria-pressed", "true")
    expect(screen.getByRole("status")).toHaveTextContent("Environ 1,75 sur 3,5 points")

    await userEvent.click(screen.getByRole("button", { name: "Tout" }))

    await waitFor(() => expect(marquerExerciceFait).toHaveBeenCalledWith(7, true, 100))
    expect(screen.getByRole("status")).toHaveTextContent("Environ 3,5 sur 3,5 points")
  })

  it("sans barème lisible, garde la réponse sans inventer de points", async () => {
    render(<PartReussie exerciseId={7} points="" />)

    await userEvent.click(screen.getByRole("button", { name: "Rien" }))

    await waitFor(() => expect(marquerExerciceFait).toHaveBeenCalledWith(7, true, 0))
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
  })

  it("ne renvoie rien au serveur quand on retouche la réponse déjà choisie", async () => {
    render(<PartReussie exerciseId={7} points="5" initiale={100} />)

    await userEvent.click(screen.getByRole("button", { name: "Tout" }))

    expect(marquerExerciceFait).not.toHaveBeenCalled()
  })

  it("en cas d'échec, revient à la réponse précédente et le dit", async () => {
    marquerExerciceFait.mockRejectedValue(new Error("réseau"))
    render(<PartReussie exerciseId={7} points="5" initiale={50} />)

    await userEvent.click(screen.getByRole("button", { name: "Tout" }))

    await waitFor(() => expect(toast.error).toHaveBeenCalled())
    expect(screen.getByRole("button", { name: "La moitié" })).toHaveAttribute("aria-pressed", "true")
    expect(screen.getByRole("button", { name: "Tout" })).toHaveAttribute("aria-pressed", "false")
  })
})
