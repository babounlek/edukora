import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError } from "@/api/client"

const startSimulation = vi.hoisted(() => vi.fn())
const toast = vi.hoisted(() => ({ error: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ startSimulation }))
vi.mock("sonner", () => ({ toast }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))

import { BoutonSimulation } from "./BoutonSimulation"

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/cm/epreuves/maths"]}>
      <Routes>
        <Route path="/cm/epreuves/maths" element={<BoutonSimulation epreuveId={42} />} />
        <Route path="/simulation/:id" element={<p>Écran de la simulation</p>} />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  startSimulation.mockReset()
  toast.error.mockReset()
})

describe("BoutonSimulation", () => {
  it("ouvre la simulation puis conduit à son briefing", async () => {
    startSimulation.mockResolvedValue({ id: 9 })
    afficher()

    await userEvent.click(screen.getByRole("button", { name: /Passer en conditions d'examen/ }))

    await waitFor(() => expect(startSimulation).toHaveBeenCalledWith(42))
    expect(await screen.findByText("Écran de la simulation")).toBeInTheDocument()
  })

  it("dit pourquoi la simulation ne peut pas démarrer", async () => {
    startSimulation.mockRejectedValue(new ApiError(403, { error: "Abonnement requis pour simuler cette épreuve." }))
    afficher()

    await userEvent.click(screen.getByRole("button", { name: /Passer en conditions d'examen/ }))

    await waitFor(() => expect(toast.error).toHaveBeenCalledWith("Abonnement requis pour simuler cette épreuve."))
    expect(screen.getByRole("button", { name: /Passer en conditions d'examen/ })).toBeEnabled()
  })
})
