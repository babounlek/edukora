import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it } from "vitest"

import { CONTACT_WHATSAPP_URL, EDITEUR_NOM } from "@/lib/site"
import { LigneConfiance } from "./LigneConfiance"

describe("LigneConfiance : qui édite, comment on paie, à qui écrire", () => {
  it("nomme l'éditeur et sa ville, et mène à la page « À propos »", () => {
    render(
      <MemoryRouter>
        <LigneConfiance />
      </MemoryRouter>,
    )

    expect(screen.getByText(`Édité par ${EDITEUR_NOM}`)).toBeInTheDocument()
    expect(screen.getByText("Yaoundé, Cameroun")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Qui sommes-nous ?" })).toHaveAttribute("href", "/a-propos")
  })

  it("dit le moyen de paiement sans logo d'opérateur, et donne le numéro WhatsApp du site", () => {
    const { container } = render(
      <MemoryRouter>
        <LigneConfiance />
      </MemoryRouter>,
    )

    expect(screen.getByText("Paiement par Mobile Money")).toBeInTheDocument()
    expect(screen.getByText("Orange Money")).toBeInTheDocument()
    expect(screen.getByText("MTN MoMo")).toBeInTheDocument()
    expect(container.querySelector("img")).toBeNull()
    expect(screen.getByRole("link", { name: /WhatsApp \+237/ })).toHaveAttribute("href", CONTACT_WHATSAPP_URL)
  })
})
