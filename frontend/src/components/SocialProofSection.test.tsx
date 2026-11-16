import { render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { SocialProofSection } from "./SocialProofSection"

const { listTemoignages } = vi.hoisted(() => ({
  listTemoignages: vi.fn(),
}))

vi.mock("@/api/endpoints", () => ({ listTemoignages }))

describe("SocialProofSection", () => {
  beforeEach(() => {
    listTemoignages.mockReset()
  })

  it("ne rend rien tant qu'aucun témoignage n'est publié", async () => {
    listTemoignages.mockResolvedValue([])

    const { container } = render(<SocialProofSection />)

    await waitFor(() => expect(listTemoignages).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("ne rend rien tant qu'il y a moins de trois avis publiés", async () => {
    listTemoignages.mockResolvedValue([
      { id: 1, auteur_nom: "Awa", auteur_description: "Terminale D", contenu: "Vraiment utile.", note: 5 },
      { id: 2, auteur_nom: "Marc", auteur_description: "", contenu: "Bon contenu.", note: null },
    ])

    const { container } = render(<SocialProofSection />)

    await waitFor(() => expect(listTemoignages).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("demande les avis dans la langue de l'interface", async () => {
    listTemoignages.mockResolvedValue([])

    render(<SocialProofSection />)

    await waitFor(() => expect(listTemoignages).toHaveBeenCalledWith("fr"))
  })

  it("ne les redemande pas quand la page les fournit", () => {
    render(
      <SocialProofSection
        fournis={[
          { id: 1, auteur_nom: "Awa", auteur_description: "BAC - Série D", contenu: "Vraiment utile.", note: 5 },
          { id: 2, auteur_nom: "Marc", auteur_description: "BEPC", contenu: "Bon contenu.", note: 4 },
          { id: 3, auteur_nom: "Brigitte", auteur_description: "Parent d'élève", contenu: "Mon fils révise seul.", note: 5 },
        ]}
      />,
    )

    expect(screen.getByRole("heading", { level: 2 })).toBeInTheDocument()
    expect(screen.getByText("Mon fils révise seul.")).toBeInTheDocument()
    expect(listTemoignages).not.toHaveBeenCalled()
  })

  it("affiche un témoignage publié avec son auteur et sa note", async () => {
    listTemoignages.mockResolvedValue([
      { id: 1, auteur_nom: "Awa", auteur_description: "Terminale D", contenu: "Vraiment utile.", note: 5 },
      { id: 11, auteur_nom: "Inès", auteur_description: "BEPC", contenu: "Clair.", note: 4 },
      { id: 12, auteur_nom: "Paul", auteur_description: "BAC - Série C", contenu: "Efficace.", note: 5 },
    ])

    render(<SocialProofSection />)

    expect(await screen.findByText("Vraiment utile.")).toBeInTheDocument()
    expect(screen.getByText("Awa")).toBeInTheDocument()
    expect(screen.getByText(/Terminale D/)).toBeInTheDocument()
  })

  it("n'affiche aucune étoile quand le témoignage n'a pas de note", async () => {
    listTemoignages.mockResolvedValue([
      { id: 2, auteur_nom: "Marc", auteur_description: "", contenu: "Bon contenu.", note: null },
      { id: 21, auteur_nom: "Inès", auteur_description: "", contenu: "Clair.", note: null },
      { id: 22, auteur_nom: "Paul", auteur_description: "", contenu: "Efficace.", note: null },
    ])

    const { container } = render(<SocialProofSection />)

    await screen.findByText("Bon contenu.")
    expect(container.querySelectorAll(".fill-gold")).toHaveLength(0)
  })
})
