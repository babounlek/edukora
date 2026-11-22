import { fireEvent, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const config = vi.hoisted(() => ({ campayActif: false, pret: true, beneficiaires: [], smsActif: true }))

vi.mock("@/api/endpoints", () => ({
  requestEmailCode: vi.fn(),
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
vi.mock("@/lib/paymentConfig", () => ({ usePaymentConfig: () => config }))

import { LoginPage } from "./LoginPage"

const CHOIX = "BEPC · 1 mois · 2 000 FCFA"

function afficher(state?: { from?: string; intent?: string; recap?: string }) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: "/connexion", state }]}>
      <LoginPage />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  config.smsActif = true
})

describe("LoginPage : le chemin d'achat (on arrive des prix avec un choix fait)", () => {
  it("dit qu'un compte se crée ici, rappelle le choix et propose le téléphone d'abord", () => {
    afficher({ from: "/abonnement?cursus=14&mois=1", intent: "Ton compte d'abord, le paiement juste après.", recap: CHOIX })

    expect(screen.getByRole("heading", { level: 1, name: "Crée ton compte ou connecte-toi" })).toBeInTheDocument()
    expect(screen.getByText(`Ton choix : ${CHOIX}`)).toBeInTheDocument()
    expect(screen.getByText(/Pas encore de compte \? Il se crée ici, sans mot de passe\./)).toBeInTheDocument()
    expect(screen.getByLabelText("Numéro de téléphone")).toBeInTheDocument()
    expect(screen.queryByLabelText("Adresse e-mail")).not.toBeInTheDocument()
    expect(screen.getByText("Tu reçois un code par SMS, à saisir à l'écran suivant.")).toBeInTheDocument()
  })

  it("garde l'e-mail devant quand aucun SMS ne peut partir : jamais une méthode qui ne marcherait pas", () => {
    config.smsActif = false
    afficher({ recap: CHOIX })

    expect(screen.getByLabelText("Adresse e-mail")).toBeInTheDocument()
    expect(screen.getByText("Tu reçois un code par e-mail, à saisir à l'écran suivant.")).toBeInTheDocument()
  })

  it("laisse l'e-mail à qui le préfère, et ne le lui reprend pas", () => {
    const { rerender } = afficher({ recap: CHOIX })

    fireEvent.click(screen.getByRole("button", { name: "Utiliser plutôt une adresse e-mail" }))
    rerender(
      <MemoryRouter initialEntries={[{ pathname: "/connexion", state: { recap: CHOIX } }]}>
        <LoginPage />
      </MemoryRouter>,
    )

    expect(screen.getByLabelText("Adresse e-mail")).toBeInTheDocument()
  })
})

describe("LoginPage : hors du chemin d'achat, rien ne change d'ordre", () => {
  it("une simple connexion garde le titre « Connexion » et l'e-mail devant, même si le SMS marche", () => {
    afficher()

    expect(screen.getByRole("heading", { level: 1, name: "Connexion" })).toBeInTheDocument()
    expect(screen.getByLabelText("Adresse e-mail")).toBeInTheDocument()
    expect(screen.getByText(/Pas encore de compte \?/)).toBeInTheDocument()
  })
})
