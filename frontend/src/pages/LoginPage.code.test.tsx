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

import { ApiError } from "@/api/client"
import { definirLangue } from "@/lib/i18n"
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

  it("après un renvoi en échec, dit combien attendre et garde le bouton grisé avec un décompte", async () => {
    const aboutir = envoiManuel()
    demanderLeCode()
    await act(async () => {
      aboutir()
      await vi.advanceTimersByTimeAsync(10)
    })
    // Le décompte du premier envoi s'écoule : « Renvoyer » devient actif.
    await act(async () => {
      await vi.advanceTimersByTimeAsync(61_000)
    })
    requestEmailCode.mockRejectedValue(
      new ApiError(503, { error: "Envoi du code impossible…", code: "envoi_indisponible", retry_after: 60 }),
    )
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Renvoyer le code" }))
      await vi.advanceTimersByTimeAsync(10)
    })

    expect(screen.getByRole("alert")).toHaveTextContent("Le code n'a pas pu être envoyé pour le moment. Réessaie dans 60 secondes.")
    const bouton = screen.getByRole("button", { name: /Renvoyer le code \(\d+s\)/ })
    expect(bouton).toBeDisabled()
  })

  it("un renvoi trop tôt (429) dit la durée restante, sans bouton actif", async () => {
    const aboutir = envoiManuel()
    demanderLeCode()
    await act(async () => {
      aboutir()
      await vi.advanceTimersByTimeAsync(10)
    })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(61_000)
    })
    requestEmailCode.mockRejectedValue(
      new ApiError(429, { error: "Merci de patienter…", code: "code_renvoi_trop_tot", retry_after: 42 }),
    )
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Renvoyer le code" }))
      await vi.advanceTimersByTimeAsync(10)
    })

    expect(screen.getByRole("alert")).toHaveTextContent("Tu pourras en redemander un dans 42 secondes")
    expect(screen.getByRole("button", { name: /Renvoyer le code \(4\ds\)/ })).toBeDisabled()
  })
})

describe("ApiError : les échecs d'envoi de code suivent la langue de la page", () => {
  afterEach(async () => {
    await definirLangue("fr", { persister: false })
  })

  it("écrit le message en anglais sur une page anglaise, avec la durée", async () => {
    await definirLangue("en", { persister: false })
    const message = (code: string, retry_after?: number) =>
      new ApiError(429, { error: "Texte français du serveur", code, retry_after }).message

    expect(message("code_renvoi_trop_tot", 42)).toBe("A code was just sent. You can ask for another one in 42 seconds.")
    expect(message("code_trop_de_demandes", 3500)).toBe("Too many code requests from this connection. Try again in 59 minutes.")
    expect(message("envoi_indisponible")).toBe("Sending the code is temporarily unavailable. Try again later.")
  })

  it("garde le message du serveur pour une erreur qui n'est pas un échec d'envoi", () => {
    expect(new ApiError(400, { error: "Code invalide ou expiré." }).message).toBe("Code invalide ou expiré.")
  })
})
