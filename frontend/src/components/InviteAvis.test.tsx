import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { InviteAvis, type RoleAvis } from "./InviteAvis"

const { getEtatAvis, envoyerAvis, auth } = vi.hoisted(() => ({
  getEtatAvis: vi.fn(),
  envoyerAvis: vi.fn(),
  auth: { isAuthenticated: true, user: { profil_actif: { id: 7 } } as { profil_actif: { id: number } } | null },
}))

vi.mock("@/api/endpoints", () => ({ getEtatAvis, envoyerAvis }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))

const ETAT = { eleve: true, parent: true, prenom: "Aïcha", examen: "BAC - Série D" }

function rendre(role: RoleAvis = "eleve") {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <InviteAvis role={role} />
    </QueryClientProvider>,
  )
}

describe("InviteAvis", () => {
  beforeEach(() => {
    localStorage.clear()
    getEtatAvis.mockReset().mockResolvedValue(ETAT)
    envoyerAvis.mockReset().mockResolvedValue({ enregistre: true })
    auth.isAuthenticated = true
  })

  it("ne rend rien quand le serveur n'attend pas d'avis", async () => {
    getEtatAvis.mockResolvedValue({ ...ETAT, eleve: false })
    const { container } = rendre()
    await waitFor(() => expect(getEtatAvis).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("n'interroge pas le serveur pour un visiteur", () => {
    auth.isAuthenticated = false
    const { container } = rendre()
    expect(getEtatAvis).not.toHaveBeenCalled()
    expect(container).toBeEmptyDOMElement()
  })

  it("ne montre que les étoiles tant qu'aucune note n'est donnée", async () => {
    rendre()
    expect(await screen.findByRole("radiogroup")).toBeInTheDocument()
    expect(screen.getAllByRole("radio")).toHaveLength(5)
    expect(screen.queryByRole("checkbox")).not.toBeInTheDocument()
  })

  it("la case de consentement n'est jamais cochée d'office, et sans elle l'avis part comme interne", async () => {
    rendre()
    fireEvent.click((await screen.findAllByRole("radio"))[3])
    const consentement = screen.getByRole("checkbox")
    expect(consentement).not.toBeChecked()
    // Le prénom ne se demande que pour un avis à afficher.
    expect(screen.queryByLabelText("Ton prénom")).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Envoyer mon avis" }))

    await waitFor(() =>
      expect(envoyerAvis).toHaveBeenCalledWith({
        origine: "ELEVE", note: 4, contenu: "", prenom: "Aïcha", consentement: false, langue: "fr",
      }),
    )
    expect(await screen.findByRole("status")).toHaveTextContent("Il reste entre nous")
  })

  it("avec la case, le prénom du profil est proposé et l'écran annonce la relecture", async () => {
    rendre()
    fireEvent.click((await screen.findAllByRole("radio"))[4])
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "  Les corrigés sont clairs.  " } })
    fireEvent.click(screen.getByRole("checkbox"))
    expect(screen.getByRole("checkbox").closest("div")).toHaveTextContent("BAC - Série D")
    expect(screen.getByLabelText("Ton prénom")).toHaveValue("Aïcha")

    fireEvent.click(screen.getByRole("button", { name: "Envoyer mon avis" }))

    await waitFor(() =>
      expect(envoyerAvis).toHaveBeenCalledWith({
        origine: "ELEVE", note: 5, contenu: "Les corrigés sont clairs.", prenom: "Aïcha", consentement: true, langue: "fr",
      }),
    )
    expect(await screen.findByRole("status")).toHaveTextContent("relu par l'équipe")
  })

  it("refuse d'envoyer un avis à afficher sans prénom", async () => {
    getEtatAvis.mockResolvedValue({ ...ETAT, prenom: "" })
    rendre()
    fireEvent.click((await screen.findAllByRole("radio"))[4])
    fireEvent.click(screen.getByRole("checkbox"))
    fireEvent.click(screen.getByRole("button", { name: "Envoyer mon avis" }))

    expect(await screen.findByRole("alert")).toHaveTextContent("prénom")
    expect(envoyerAvis).not.toHaveBeenCalled()
  })

  it("dit quand le serveur refuse le prénom, et garde ce qui a été écrit", async () => {
    envoyerAvis.mockRejectedValue(Object.assign(new Error("refus"), { status: 400 }))
    rendre()
    fireEvent.click((await screen.findAllByRole("radio"))[4])
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "Utile." } })
    fireEvent.click(screen.getByRole("checkbox"))
    fireEvent.click(screen.getByRole("button", { name: "Envoyer mon avis" }))

    expect(await screen.findByRole("alert")).toHaveTextContent("lettres seulement")
    expect(screen.getAllByRole("textbox")[0]).toHaveValue("Utile.")
  })

  it("« Ne plus me demander » est retenu sur l'appareil, pour ce profil et ce rôle", async () => {
    const premier = rendre()
    fireEvent.click(await screen.findByRole("button", { name: "Ne plus me demander" }))
    expect(premier.container).toBeEmptyDOMElement()
    premier.unmount()

    getEtatAvis.mockClear()
    const second = rendre()
    expect(second.container).toBeEmptyDOMElement()
    expect(getEtatAvis).not.toHaveBeenCalled()
    second.unmount()

    // L'avis du parent reste demandé : c'est une autre personne.
    rendre("parent")
    expect(await screen.findByText("Vous êtes parent ? Votre avis compte")).toBeInTheDocument()
  })

  it("le parent écrit son propre prénom, jamais celui de l'enfant", async () => {
    rendre("parent")
    fireEvent.click((await screen.findAllByRole("radio"))[4])
    fireEvent.click(screen.getByRole("checkbox"))
    expect(screen.getByLabelText("Votre prénom")).toHaveValue("")
    fireEvent.change(screen.getByLabelText("Votre prénom"), { target: { value: "Brigitte" } })
    fireEvent.click(screen.getByRole("button", { name: "Envoyer mon avis" }))

    await waitFor(() =>
      expect(envoyerAvis).toHaveBeenCalledWith(expect.objectContaining({ origine: "PARENT", prenom: "Brigitte", consentement: true })),
    )
  })
})
