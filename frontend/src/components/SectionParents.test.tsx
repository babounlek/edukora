import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it } from "vitest"

import { PRIX_MOIS_ENFANT_SUPPLEMENTAIRE_FCFA, PRIX_MOIS_FCFA } from "@/lib/tarifs"
import { formatAmount } from "@/lib/utils"
import { SectionParents } from "./SectionParents"

describe("SectionParents : l'accueil parle aussi au parent qui paie", () => {
  it("annonce les prix de la grille (jamais écrits en dur) et ce que le parent contrôle", () => {
    render(
      <MemoryRouter>
        <SectionParents />
      </MemoryRouter>,
    )

    expect(screen.getByRole("heading", { level: 2, name: "Tu es parent ?" })).toBeInTheDocument()
    expect(screen.getByText(new RegExp(`${formatAmount(PRIX_MOIS_FCFA)} FCFA par mois`))).toBeInTheDocument()
    expect(screen.getByText(new RegExp(`${formatAmount(PRIX_MOIS_ENFANT_SUPPLEMENTAIRE_FCFA)} FCFA par mois`))).toBeInTheDocument()
    expect(screen.getByText(/sans prélèvement automatique/)).toBeInTheDocument()
    expect(screen.getByText(/Un code parent réserve les paiements/)).toBeInTheDocument()
  })

  it("mène aux tarifs et à l'aide sur le paiement", () => {
    render(
      <MemoryRouter>
        <SectionParents />
      </MemoryRouter>,
    )

    expect(screen.getByRole("link", { name: /Voir les prix/ })).toHaveAttribute("href", "/tarifs")
    expect(screen.getByRole("link", { name: "Comment payer ?" })).toHaveAttribute("href", "/aide/comment-payer")
  })
})
