import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { User } from "@/api/types"

const updateMe = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ user: null as unknown, updateUser: vi.fn() }))
const toast = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }))

vi.mock("@/api/endpoints", () => ({ updateMe }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("sonner", () => ({ toast }))

import { InterrupteurRappelsEmail, InviteRappels } from "./RappelsEmail"

function eleve(extra: Partial<User> = {}): User {
  return {
    id: 1, phone_number: "677000000", email: "a@b.cm", email_verified: true, full_name: "Awa", pseudo: null,
    date_joined: "2026-09-01T00:00:00Z", referral_code: "X", filleuls_count: 0, credit_parrainage_disponible: 0,
    auth_methods: ["phone"], cursus_prepare: null, compte_a_rebours: null, a_un_abonnement_actif: true,
    rappels_actifs: false, rappels_invite_refusee: false, ...extra,
  } as User
}

function afficher(element: React.ReactElement) {
  return render(<MemoryRouter>{element}</MemoryRouter>)
}

beforeEach(() => {
  updateMe.mockReset()
  auth.updateUser.mockReset()
  toast.error.mockReset()
})

describe("InviteRappels", () => {
  it("propose d'activer le rappel à un élève dont l'e-mail est confirmé", async () => {
    auth.user = eleve()
    updateMe.mockResolvedValue(eleve({ rappels_actifs: true }))
    afficher(<InviteRappels />)

    await userEvent.click(screen.getByRole("button", { name: "Activer le rappel" }))

    await waitFor(() => expect(updateMe).toHaveBeenCalledWith({ rappels_actifs: true }))
    expect(auth.updateUser).toHaveBeenCalled()
  })

  it("renvoie vers l'ajout de l'e-mail quand il manque", () => {
    auth.user = eleve({ email: "", email_verified: false })
    afficher(<InviteRappels />)

    expect(screen.getByRole("link", { name: "Ajouter mon e-mail" })).toHaveAttribute("href", "/compte")
    expect(screen.queryByRole("button", { name: "Activer le rappel" })).not.toBeInTheDocument()
  })

  it("mémorise le refus et ne se réaffiche plus", async () => {
    auth.user = eleve()
    updateMe.mockResolvedValue(eleve({ rappels_invite_refusee: true }))
    afficher(<InviteRappels />)

    await userEvent.click(screen.getByRole("button", { name: "Non merci" }))

    await waitFor(() => expect(updateMe).toHaveBeenCalledWith({ rappels_invite_refusee: true }))
  })

  it("ne s'affiche pas si les rappels sont déjà actifs ou l'invitation déjà écartée", () => {
    auth.user = eleve({ rappels_actifs: true })
    const { container, rerender } = afficher(<InviteRappels />)
    expect(container).toBeEmptyDOMElement()

    auth.user = eleve({ rappels_invite_refusee: true })
    rerender(<MemoryRouter><InviteRappels /></MemoryRouter>)
    expect(container).toBeEmptyDOMElement()
  })
})

describe("InterrupteurRappelsEmail", () => {
  it("bloque l'interrupteur et dit pourquoi tant que l'e-mail n'est pas confirmé", () => {
    auth.user = eleve({ email_verified: false })
    afficher(<InterrupteurRappelsEmail />)

    expect(screen.getByRole("switch")).toBeDisabled()
    expect(screen.getByText(/Ajoute et confirme d'abord ton e-mail/)).toBeInTheDocument()
  })

  it("active puis coupe les rappels", async () => {
    auth.user = eleve()
    updateMe.mockResolvedValue(eleve({ rappels_actifs: true }))
    afficher(<InterrupteurRappelsEmail />)

    await userEvent.click(screen.getByRole("switch"))

    await waitFor(() => expect(updateMe).toHaveBeenCalledWith({ rappels_actifs: true }))
  })

  it("laisse toujours couper un rappel actif, même si l'e-mail n'est plus confirmé", () => {
    auth.user = eleve({ rappels_actifs: true, email_verified: false })
    afficher(<InterrupteurRappelsEmail />)
    expect(screen.getByRole("switch")).toBeEnabled()
  })
})
