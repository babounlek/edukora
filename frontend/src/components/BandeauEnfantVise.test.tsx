import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const profils = vi.hoisted(() => ({ liste: [] as { id: number; prenom: string }[] }))
vi.mock("@/lib/changerProfilActif", () => ({ useProfils: () => profils.liste }))

import { BandeauEnfantVise } from "./BandeauEnfantVise"

function afficher(profilId: string | null) {
  return render(
    <MemoryRouter>
      <BandeauEnfantVise profilId={profilId} />
    </MemoryRouter>,
  )
}

describe("BandeauEnfantVise", () => {
  beforeEach(() => {
    profils.liste = [
      { id: 9, prenom: "Awa" },
      { id: 12, prenom: "Paul" },
    ]
  })

  it("dit pour quel enfant on choisit la formule, et renvoie vers Mes accès", () => {
    afficher("9")

    expect(screen.getByRole("status")).toHaveTextContent("Tu choisis l'abonnement de Awa.")
    expect(screen.getByRole("link", { name: /pas le bon enfant/i }).getAttribute("href")).toBe("/mes-acces")
  })

  it("n'affiche rien sans paramètre", () => {
    const { container } = afficher(null)
    expect(container).toBeEmptyDOMElement()
  })

  it("n'affiche rien pour un profil qui n'est pas un enfant de ce compte", () => {
    const { container } = afficher("999")
    expect(container).toBeEmptyDOMElement()
  })
})
