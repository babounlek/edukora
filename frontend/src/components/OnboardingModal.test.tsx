import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

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

import { definirLangue } from "@/lib/i18n"
import { OnboardingModal } from "./OnboardingModal"

const pays = { id: 1, code: "CM", label: "Cameroun" }
const serie = (id: number, code: string, label: string) => ({ id, code, label })
const CURSUS = [
  { id: 1, country: pays, examen: "BEPC", examen_display: "BEPC", series: null, langue: "fr" },
  { id: 2, country: pays, examen: "BAC", examen_display: "BAC", series: serie(1, "C", "Maths"), langue: "fr" },
  { id: 3, country: pays, examen: "BAC", examen_display: "BAC", series: serie(2, "D", "Sciences"), langue: "fr" },
  { id: 4, country: pays, examen: "GCE_AL", examen_display: "GCE A Level", series: null, langue: "en" },
  { id: 5, country: pays, examen: "GCE_AL", examen_display: "GCE A Level", series: serie(9, "GCE_TECHNICAL", "Technical"), langue: "en" },
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

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("OnboardingModal", () => {
  it("GCE : propose la branche générale ET technique, sans mot « Série »", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "GCE A Level" }))
    expect(screen.getByText("Which series are you in?")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "General" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Technical" })).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "General" }))
    await waitFor(() => expect(memoriser).toHaveBeenCalledWith(4))
  })

  it("GCE technique : déclare le cursus technique", async () => {
    await definirLangue("en", { persister: false })
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

  it("en français, seuls BEPC, Probatoire et BAC sont proposés, jamais le GCE", async () => {
    afficher()
    await screen.findByRole("button", { name: "BAC" })
    expect(screen.getByRole("button", { name: "BEPC" })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "GCE A Level" })).not.toBeInTheDocument()
  })

  it("en anglais, seul le GCE est proposé, jamais BEPC ni BAC", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    await screen.findByRole("button", { name: "GCE A Level" })
    expect(screen.queryByRole("button", { name: "BAC" })).not.toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "BEPC" })).not.toBeInTheDocument()
  })

  it("BEPC : confirmation sans choix de série, inchangée", async () => {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: "BEPC" }))
    expect(screen.getByRole("button", { name: "Oui, c'est mon examen" })).toBeInTheDocument()
  })

  it("invite à passer dans l'autre sous-système, au choix de l'examen", async () => {
    afficher()
    // Version française : seuls BEPC, Probatoire et BAC sont listés, l'élève du GCE est invité à passer en anglais.
    await screen.findByRole("button", { name: "BEPC" })
    expect(screen.getByText(/Tu prépares le GCE/)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Switch to English" })).toBeInTheDocument()
  })

  it("version anglaise : invite vers le BEPC, le Probatoire et le BAC", async () => {
    await definirLangue("en", { persister: false })
    afficher()
    await screen.findByRole("button", { name: "GCE A Level" })
    expect(screen.getByRole("button", { name: "Passer en français" })).toBeInTheDocument()
  })

  it("pas d'invitation quand le pays n'a aucun examen de l'autre langue", async () => {
    listCursus.mockResolvedValue(CURSUS.filter((c) => c.langue === "fr"))
    afficher()
    await screen.findByRole("button", { name: "BEPC" })
    expect(screen.queryByRole("button", { name: "Switch to English" })).not.toBeInTheDocument()
  })
})
