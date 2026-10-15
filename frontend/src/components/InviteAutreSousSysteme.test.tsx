import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { auth, ouvrir, updateMe, majUtilisateur } = vi.hoisted(() => ({
  auth: { user: null as unknown },
  ouvrir: vi.fn(),
  updateMe: vi.fn(),
  majUtilisateur: vi.fn(),
}))
vi.mock("@/api/endpoints", () => ({ updateMe }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ isAuthenticated: auth.user !== null, user: auth.user, updateUser: majUtilisateur }),
}))
vi.mock("@/lib/i18n", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/i18n")>()),
  ouvrirDansLangue: ouvrir,
}))

import { definirLangue, LANGUE_STORAGE_KEY } from "@/lib/i18n"
import { InviteAutreSousSysteme } from "./InviteAutreSousSysteme"

beforeEach(() => {
  localStorage.clear()
  ouvrir.mockReset()
  updateMe.mockReset()
  majUtilisateur.mockReset()
  auth.user = null
})

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("InviteAutreSousSysteme", () => {
  it("version française : invite vers le GCE, et le clic recharge la page en anglais", async () => {
    render(<InviteAutreSousSysteme disponible />)
    expect(screen.getByText(/Tu prépares le GCE/)).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Switch to English" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("en"))
    // Le choix est gardé : sinon le prochain chargement sans préfixe repartirait en français.
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("en")
  })

  it("version anglaise : invite vers le BEPC, le Probatoire et le BAC", async () => {
    await definirLangue("en", { persister: false })
    render(<InviteAutreSousSysteme disponible />)
    expect(screen.getByText(/Preparing for the BEPC, Probatoire or BAC/)).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Passer en français" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("fr"))
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("fr")
  })

  it("variante bloc : même invitation, avec un bouton", () => {
    render(<InviteAutreSousSysteme disponible variante="bloc" />)
    expect(screen.getByRole("button", { name: "Switch to English" })).toBeTruthy()
  })

  it("rien quand le pays n'a pas d'examen dans l'autre langue", () => {
    const { container } = render(<InviteAutreSousSysteme disponible={false} />)
    expect(container.innerHTML).toBe("")
  })

  it("rien dès qu'un cursus est préparé : la langue est celle du cursus", () => {
    auth.user = { id: 1, langue: "fr", cursus_prepare: { id: 2, langue: "fr" } }
    const { container } = render(<InviteAutreSousSysteme disponible />)
    expect(container.innerHTML).toBe("")
  })

  it("compte connecté sans cursus : la langue du compte est mise à jour avant le rechargement", async () => {
    auth.user = { id: 1, langue: "fr", cursus_prepare: null }
    updateMe.mockResolvedValue({ id: 1, langue: "en", cursus_prepare: null })
    render(<InviteAutreSousSysteme disponible />)
    fireEvent.click(screen.getByRole("button", { name: "Switch to English" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("en"))
    expect(updateMe).toHaveBeenCalledWith({ langue: "en" })
    expect(majUtilisateur).toHaveBeenCalled()
  })
})
