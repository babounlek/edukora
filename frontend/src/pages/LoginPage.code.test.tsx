import { act, fireEvent, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const requestEmailCode = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({
  requestEmailCode,
  requestOtp: vi.fn(),
  verifyEmailCode: vi.fn(),
  verifyOtp: vi.fn(),
  googleSignIn: vi.fn(),
  listProfils: vi.fn(() => Promise.resolve([])),
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ login: vi.fn() }) }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm", countries: [] }) }))
vi.mock("@/components/GoogleSignInButton", () => ({ GoogleSignInButton: () => null }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { LoginPage } from "./LoginPage"

/** Un envoi d'e-mail dont on décide quand il aboutit : la durée réelle de l'envoi (douze secondes en local) est ce qu'on teste. */
function envoiManuel() {
  let aboutir: () => void = () => {}
  requestEmailCode.mockImplementation(() => new Promise<void>((resolve) => (aboutir = resolve)))
  return () => aboutir()
}

function demanderLeCode() {
  render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  )
  fireEvent.change(screen.getByLabelText("Adresse e-mail"), { target: { value: "parent@exemple.org" } })
  fireEvent.click(screen.getByRole("button", { name: "Recevoir le code" }))
}

describe("LoginPage : l'envoi et l'attente du code (test élève Gogo)", () => {
  beforeEach(() => {
    vi.useFakeTimers()
    requestEmailCode.mockReset()
  })
  afterEach(() => vi.useRealTimers())

  it("annonce un envoi un peu long après quelques secondes, pas avant", async () => {
    envoiManuel()
    demanderLeCode()

    expect(screen.queryByText(/peut prendre quelques secondes/)).not.toBeInTheDocument()
    await act(async () => {
      await vi.advanceTimersByTimeAsync(3100)
    })
    expect(screen.getByText("L'envoi peut prendre quelques secondes…")).toBeInTheDocument()
  })

  it("dit où chercher le code, puis qu'il a expiré au bout de cinq minutes", async () => {
    const aboutir = envoiManuel()
    demanderLeCode()
    await act(async () => {
      aboutir()
      await vi.advanceTimersByTimeAsync(10)
    })

    expect(screen.getByText(/Regarde dans tes courriers indésirables/)).toBeInTheDocument()
    expect(screen.queryByText(/Ce code a expiré/)).not.toBeInTheDocument()

    await act(async () => {
      await vi.advanceTimersByTimeAsync(5 * 60_000 + 100)
    })
    expect(screen.getByRole("alert")).toHaveTextContent("Ce code a expiré")
  })
})
