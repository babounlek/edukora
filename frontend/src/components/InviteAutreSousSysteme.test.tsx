import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import type { ReactNode } from "react"
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

import {
  lireCursusPrepareEnAttente,
  memoriserCursusPrepareEnAttente,
  oublierCursusPrepareEnAttente,
} from "@/lib/cursusPrepare"
import { definirLangue, LANGUE_STORAGE_KEY } from "@/lib/i18n"
import { InviteAutreSousSysteme } from "./InviteAutreSousSysteme"

let client: QueryClient

function afficher(ui: ReactNode) {
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}

beforeEach(() => {
  client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  oublierCursusPrepareEnAttente()
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
    afficher(<InviteAutreSousSysteme disponible />)
    expect(screen.getByText(/Tu prépares le GCE/)).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Switch to English" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("en"))
    // Le choix est gardé : sinon le prochain chargement sans préfixe repartirait en français.
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("en")
  })

  it("version anglaise : invite vers le BEPC, le Probatoire et le BAC", async () => {
    await definirLangue("en", { persister: false })
    afficher(<InviteAutreSousSysteme disponible />)
    expect(screen.getByText(/Preparing for the BEPC, Probatoire or BAC/)).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Passer en français" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("fr"))
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("fr")
  })

  it("variante bloc : même invitation, avec un bouton", () => {
    afficher(<InviteAutreSousSysteme disponible variante="bloc" />)
    expect(screen.getByRole("button", { name: "Switch to English" })).toBeTruthy()
  })

  it("rien quand le pays n'a pas d'examen dans l'autre langue", () => {
    const { container } = afficher(<InviteAutreSousSysteme disponible={false} />)
    expect(container.innerHTML).toBe("")
  })

  it("rien une fois le profil abonné à son examen : la langue est celle du cursus", () => {
    auth.user = { id: 1, langue: "fr", cursus_prepare: { id: 2, langue: "fr" }, abonne_profil_actif: true }
    const { container } = afficher(<InviteAutreSousSysteme disponible />)
    expect(container.innerHTML).toBe("")
  })

  it("reste proposée avec un examen déclaré tant que le profil n'est pas abonné", () => {
    auth.user = { id: 1, langue: "fr", cursus_prepare: { id: 2, langue: "fr" }, abonne_profil_actif: false }
    afficher(<InviteAutreSousSysteme disponible />)
    expect(screen.getByRole("button", { name: "Switch to English" })).toBeTruthy()
  })

  it("compte connecté sans cursus : la langue du compte est mise à jour avant le rechargement", async () => {
    auth.user = { id: 1, langue: "fr", cursus_prepare: null }
    updateMe.mockResolvedValue({ id: 1, langue: "en", cursus_prepare: null })
    afficher(<InviteAutreSousSysteme disponible />)
    fireEvent.click(screen.getByRole("button", { name: "Switch to English" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("en"))
    expect(updateMe).toHaveBeenCalledWith({ langue: "en" })
    expect(majUtilisateur).toHaveBeenCalled()
  })
})

describe("InviteAutreSousSysteme : l'examen déclaré par un visiteur", () => {
  const BAC = { id: 2, examen: "BAC", langue: "fr" }
  const GCE = { id: 3, examen: "GCE_OL", langue: "en" }

  it("un visiteur qui passe du GCE au français perd l'examen de l'ancien système (la pastille ne le montre plus)", async () => {
    await definirLangue("en", { persister: false })
    client.setQueryData(["cursus", "cm"], [BAC, GCE])
    memoriserCursusPrepareEnAttente(3)
    afficher(<InviteAutreSousSysteme disponible />)
    fireEvent.click(screen.getByRole("button", { name: "Passer en français" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("fr"))
    expect(lireCursusPrepareEnAttente()).toBeNull()
  })

  it("un examen déjà de la langue visée est gardé (arrivé par un lien /en, retour au français)", async () => {
    await definirLangue("en", { persister: false })
    client.setQueryData(["cursus", "cm"], [BAC, GCE])
    memoriserCursusPrepareEnAttente(2)
    afficher(<InviteAutreSousSysteme disponible />)
    fireEvent.click(screen.getByRole("button", { name: "Passer en français" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("fr"))
    expect(lireCursusPrepareEnAttente()).toBe(2)
  })
})

describe("InviteAutreSousSysteme, variante compacte", () => {
  it("tient en une phrase courte et un lien, dans la langue de l'examen visé", () => {
    afficher(<InviteAutreSousSysteme disponible variante="compacte" />)
    expect(screen.getByText("Preparing the GCE?")).toBeTruthy()
    expect(screen.getByRole("button", { name: "Switch to English" })).toBeTruthy()
    // La ligne française qui doublait la phrase anglaise (3 lignes sur 375 px, test élève Guyguy) n'y est plus.
    expect(screen.queryByText(/sous-système anglophone/)).toBeNull()
  })

  it("le clic recharge la page en anglais, comme la version complète", async () => {
    afficher(<InviteAutreSousSysteme disponible variante="compacte" />)
    fireEvent.click(screen.getByRole("button", { name: "Switch to English" }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("en"))
  })

  it("version anglaise : invite vers le BEPC, le Probatoire et le BAC en une ligne", async () => {
    await definirLangue("en", { persister: false })
    afficher(<InviteAutreSousSysteme disponible variante="compacte" />)
    expect(screen.getByText("Preparing for the BEPC, Probatoire or BAC?")).toBeTruthy()
    expect(screen.getByRole("button", { name: "Passer en français" })).toBeTruthy()
  })

  it("rien quand le pays n'a pas d'examen dans l'autre langue", () => {
    const { container } = afficher(<InviteAutreSousSysteme disponible={false} variante="compacte" />)
    expect(container.innerHTML).toBe("")
  })
})
