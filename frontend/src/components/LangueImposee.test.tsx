import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { auth, ouvrir, updateMe } = vi.hoisted(() => ({
  auth: { user: null as unknown },
  ouvrir: vi.fn(),
  updateMe: vi.fn(() => Promise.resolve({})),
}))
vi.mock("@/api/endpoints", () => ({ updateMe }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ isAuthenticated: auth.user !== null, user: auth.user, updateUser: vi.fn() }),
}))
vi.mock("@/lib/i18n", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/i18n")>()),
  ouvrirDansLangue: ouvrir,
}))

import { definirLangue, initialiserLangue, LANGUE_STORAGE_KEY } from "@/lib/i18n"
import { BandeauLangueCursus } from "./BandeauLangueCursus"
import { SelecteurLangue, useSynchroLangueCompte } from "./SelecteurLangue"

const utilisateur = (langueCursus: "fr" | "en" | null, langueCompte: "fr" | "en" = "fr", abonne = false) => ({
  id: 1,
  langue: langueCompte,
  abonne_profil_actif: abonne,
  cursus_prepare: langueCursus ? { id: 1, langue: langueCursus } : null,
})

function Sync() {
  useSynchroLangueCompte()
  return null
}

beforeEach(() => {
  localStorage.clear()
  ouvrir.mockReset()
  updateMe.mockClear()
  auth.user = null
  window.history.replaceState(null, "", "/")
})

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("langue imposée par le cursus du profil actif", () => {
  it("le sélecteur reste tant que le profil n'est pas abonné, même avec un examen déclaré, et disparaît ensuite", () => {
    auth.user = utilisateur(null)
    const { unmount } = render(<SelecteurLangue />)
    expect(screen.getByRole("group")).toBeTruthy()
    unmount()
    auth.user = utilisateur("fr")
    const { unmount: unmount2 } = render(<SelecteurLangue />)
    expect(screen.getByRole("group")).toBeTruthy()
    unmount2()
    auth.user = utilisateur("fr", "fr", true)
    render(<SelecteurLangue />)
    expect(screen.queryByRole("group")).toBeNull()
  })

  it("changer de système sans abonnement efface l'examen déclaré avant de recharger dans l'autre langue", async () => {
    auth.user = utilisateur("fr")
    render(<SelecteurLangue />)
    fireEvent.click(screen.getByRole("button", { name: /english|anglais/i }))
    await waitFor(() => expect(ouvrir).toHaveBeenCalledWith("en"))
    expect(updateMe).toHaveBeenCalledWith({ cursus_prepare: null })
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("en")
  })

  it("si l'examen ne peut pas être effacé, la langue ne change pas", async () => {
    updateMe.mockRejectedValueOnce(new Error("réseau"))
    auth.user = utilisateur("fr")
    render(<SelecteurLangue />)
    fireEvent.click(screen.getByRole("button", { name: /english|anglais/i }))
    await waitFor(() => expect(updateMe).toHaveBeenCalled())
    expect(ouvrir).not.toHaveBeenCalled()
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).not.toBe("en")
  })

  it("profil du GCE sur une page française : renvoi vers /en et choix mémorisé aligné", () => {
    auth.user = utilisateur("en")
    render(<Sync />)
    expect(ouvrir).toHaveBeenCalledWith("en")
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("en")
  })

  it("profil français sur un lien /en explicite : la page reste, rien n'est rechargé", async () => {
    window.history.replaceState(null, "", "/en/cm/epreuves/x")
    await initialiserLangue()
    auth.user = utilisateur("fr")
    render(<Sync />)
    expect(ouvrir).not.toHaveBeenCalled()
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("fr")
  })

  it("profil français renvoyé sur /en par un choix mémorisé périmé : retour en français", async () => {
    localStorage.setItem(LANGUE_STORAGE_KEY, "en")
    window.history.replaceState(null, "", "/cm/cours")
    await initialiserLangue()
    auth.user = utilisateur("fr")
    render(<Sync />)
    expect(ouvrir).toHaveBeenCalledWith("fr")
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("fr")
  })

  it("changement de cursus en cours de session : la page suit la nouvelle langue", async () => {
    window.history.replaceState(null, "", "/en/cm")
    await initialiserLangue()
    auth.user = utilisateur("en")
    const { rerender } = render(<Sync />)
    expect(ouvrir).not.toHaveBeenCalled()
    auth.user = utilisateur("fr")
    rerender(<Sync />)
    expect(ouvrir).toHaveBeenCalledWith("fr")
  })

  it("sans cursus, le comportement précédent demeure : le compte anglais ouvre /en", () => {
    auth.user = utilisateur(null, "en")
    render(<Sync />)
    expect(ouvrir).toHaveBeenCalledWith("en")
  })
})

describe("BandeauLangueCursus", () => {
  it("s'affiche pour un élève francophone sur une page anglaise, et propose le français", async () => {
    await definirLangue("en", { persister: false })
    auth.user = utilisateur("fr")
    render(<BandeauLangueCursus />)
    fireEvent.click(screen.getByRole("button", { name: "View in French" }))
    expect(ouvrir).toHaveBeenCalledWith("fr")
  })

  it("n'apparaît ni en français, ni pour un cursus anglais, ni sans cursus", async () => {
    auth.user = utilisateur("fr")
    const { container, rerender } = render(<BandeauLangueCursus />)
    expect(container.innerHTML).toBe("")
    await definirLangue("en", { persister: false })
    auth.user = utilisateur("en")
    rerender(<BandeauLangueCursus />)
    expect(container.innerHTML).toBe("")
    auth.user = utilisateur(null)
    rerender(<BandeauLangueCursus />)
    expect(container.innerHTML).toBe("")
  })
})
