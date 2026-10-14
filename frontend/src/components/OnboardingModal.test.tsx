import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { listCursus, updateMe, memoriser } = vi.hoisted(() => ({
  listCursus: vi.fn(),
  updateMe: vi.fn(),
  memoriser: vi.fn(),
}))
vi.mock("@/api/endpoints", () => ({ listCursus, updateMe }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/cursusPrepare", () => ({ memoriserCursusPrepareEnAttente: memoriser }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ isAuthenticated: false, updateUser: vi.fn(), user: null }),
}))
vi.mock("@/context/CountryContext", () => ({
  useCountry: () => ({
    country: "cm",
    countries: [{ id: 1, code: "CM", label: "Cameroun", has_lessons: true }],
    setCountry: vi.fn(),
  }),
}))

import { OnboardingModal } from "./OnboardingModal"

const pays = { id: 1, code: "CM", label: "Cameroun" }
const serie = (id: number, code: string, label: string) => ({ id, code, label })
const CURSUS = [
  { id: 1, country: pays, examen: "BEPC", examen_display: "BEPC", series: null },
  { id: 2, country: pays, examen: "BAC", examen_display: "BAC", series: serie(1, "C", "Maths") },
  { id: 3, country: pays, examen: "BAC", examen_display: "BAC", series: serie(2, "D", "Sciences") },
  { id: 4, country: pays, examen: "GCE_AL", examen_display: "GCE A Level", series: null },
  { id: 5, country: pays, examen: "GCE_AL", examen_display: "GCE A Level", series: serie(9, "GCE_TECHNICAL", "Technical") },
]

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/cm"]}>
      <OnboardingModal />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  localStorage.clear()
  listCursus.mockReset()
  memoriser.mockReset()
  listCursus.mockResolvedValue(CURSUS)
})

describe("OnboardingModal", () => {
  it("GCE : propose la branche générale ET technique, sans mot « Série »", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "GCE A Level" }))
    expect(screen.getByText("Quelle est ta série ?")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Général" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Technical" })).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "Général" }))
    await waitFor(() => expect(memoriser).toHaveBeenCalledWith(4))
  })

  it("GCE technique : déclare le cursus technique", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "GCE A Level" }))
    fireEvent.click(screen.getByRole("button", { name: "Technical" }))
    await waitFor(() => expect(memoriser).toHaveBeenCalledWith(5))
  })

  it("BAC : toujours une liste de séries, inchangée", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "BAC" }))
    expect(screen.getByRole("button", { name: "Série C" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Série D" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Général" })).not.toBeInTheDocument()
  })

  it("BEPC : confirmation sans choix de série, inchangée", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "BEPC" }))
    expect(screen.getByRole("button", { name: "Oui, c'est mon examen" })).toBeInTheDocument()
  })
})
