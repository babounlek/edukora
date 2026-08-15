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

  it("affiche un témoignage publié avec son auteur et sa note", async () => {
    listTemoignages.mockResolvedValue([
      { id: 1, auteur_nom: "Awa", auteur_description: "Terminale D", contenu: "Vraiment utile.", note: 5 },
    ])

    render(<SocialProofSection />)

    expect(await screen.findByText("Vraiment utile.")).toBeInTheDocument()
    expect(screen.getByText("Awa")).toBeInTheDocument()
    expect(screen.getByText(/Terminale D/)).toBeInTheDocument()
  })

  it("n'affiche aucune étoile quand le témoignage n'a pas de note", async () => {
    listTemoignages.mockResolvedValue([
      { id: 2, auteur_nom: "Marc", auteur_description: "", contenu: "Bon contenu.", note: null },
    ])

    const { container } = render(<SocialProofSection />)

    await screen.findByText("Bon contenu.")
    expect(container.querySelectorAll(".fill-gold")).toHaveLength(0)
  })
})
