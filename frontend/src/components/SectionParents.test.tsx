import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it } from "vitest"

import { PRIX_MOIS_FCFA } from "@/lib/tarifs"
import { formatAmount } from "@/lib/utils"
import { SectionParents } from "./SectionParents"

describe("SectionParents : l'accueil parle aussi au parent qui paie", () => {
  it("annonce les prix de la grille (jamais écrits en dur) et ce que le parent contrôle", () => {
    render(
      <MemoryRouter>
        <SectionParents />
      </MemoryRouter>,
    )

    expect(screen.getByRole("heading", { level: 2, name: "Vous êtes parent ?" })).toBeInTheDocument()
    expect(screen.getByText(new RegExp(`${formatAmount(PRIX_MOIS_FCFA)} FCFA par mois`))).toBeInTheDocument()
    expect(screen.getByText(/au même prix/)).toBeInTheDocument()
    expect(screen.getByText(/sans prélèvement automatique/)).toBeInTheDocument()
    expect(screen.getByText(/Un code parent réserve les paiements/)).toBeInTheDocument()
  })

  it("porte le mot du fondateur, signé comme parent et fondateur", () => {
    render(
      <MemoryRouter>
        <SectionParents />
      </MemoryRouter>,
    )

    expect(screen.getByText("Pourquoi j'ai créé EduKora")).toBeInTheDocument()
    expect(screen.getByText(/parent d'un élève de 3e et fondateur d'EduKora/)).toBeInTheDocument()
  })

  it("mène à l'aide sur le paiement ; le bouton des prix est celui du bloc suivant de l'accueil", () => {
    render(
      <MemoryRouter>
        <SectionParents />
      </MemoryRouter>,
    )

    expect(screen.queryByRole("link", { name: /Voir les prix/ })).toBeNull()
    expect(screen.getByRole("link", { name: "Comment payer ?" })).toHaveAttribute("href", "/aide/comment-payer")
  })
})
