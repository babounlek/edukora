import { act, fireEvent, render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

const api = vi.hoisted(() => ({
  confirmerReinitialisationPinParent: vi.fn(),
  demanderReinitialisationPinParent: vi.fn(),
  verifierPinParent: vi.fn(),
}))
const client = vi.hoisted(() => ({ handler: null as null | (() => Promise<boolean>) }))

vi.mock("@/api/endpoints", () => api)
vi.mock("@/api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/api/client")>()),
  setParentModeHandler: (h: null | (() => Promise<boolean>)) => {
    client.handler = h
  },
  setParentToken: vi.fn(),
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ updateUser: vi.fn() }) }))

import { PinDialogs } from "./PinDialogs"

async function ouvrirLeCodeEnvoye() {
  render(<PinDialogs />)
  await act(async () => {
    void client.handler?.()
  })
  fireEvent.click(await screen.findByRole("button", { name: "Code oublié ?" }))
  fireEvent.click(await screen.findByRole("button", { name: "Envoyer le code de vérification" }))
}

describe("PinDialogs - code parent oublié : par où le code est parti", () => {
  beforeEach(() => vi.clearAllMocks())

  it("dit que le code est parti par SMS, vers le numéro masqué", async () => {
    api.demanderReinitialisationPinParent.mockResolvedValue({ message: "Code envoyé.", canal: "sms", destination: "••••••001" })
    await ouvrirLeCodeEnvoye()

    expect(await screen.findByText(/envoyé par SMS au ••••••001/)).toBeTruthy()
  })

  it("dit que le code est parti par e-mail, vers l'adresse masquée", async () => {
    api.demanderReinitialisationPinParent.mockResolvedValue({ message: "Code envoyé.", canal: "email", destination: "p•••@exemple.com" })
    await ouvrirLeCodeEnvoye()

    expect(await screen.findByText(/envoyé par e-mail à p•••@exemple.com/)).toBeTruthy()
  })

  it("garde le texte générique si le serveur ne précise pas la voie", async () => {
    api.demanderReinitialisationPinParent.mockResolvedValue({ message: "Code envoyé." })
    await ouvrirLeCodeEnvoye()

    expect(await screen.findByText(/Saisis le code à 6 chiffres reçu\./)).toBeTruthy()
  })
})
