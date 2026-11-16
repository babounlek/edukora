import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it, vi } from "vitest"

vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))

import faq from "@/lib/faq-accueil.json"
import { definirLangue } from "@/lib/i18n"
import { PRIX_MOIS_FCFA } from "@/lib/tarifs"
import { formatAmount } from "@/lib/utils"
import { FaqAccueil, questionsAccueil } from "./FaqAccueil"

afterEach(() => definirLangue("fr", { persister: false }))

describe("FaqAccueil : les questions de l'accueil", () => {
  it("le prix du fichier partagé est celui de la grille", () => {
    expect(faq.prix_mois_fcfa).toBe(PRIX_MOIS_FCFA)
    expect(questionsAccueil("fr").some(({ r }) => r.includes(`${formatAmount(PRIX_MOIS_FCFA)} FCFA par mois`))).toBe(true)
    expect(questionsAccueil("fr").some(({ r }) => r.includes("{prix}"))).toBe(false)
  })

  it("la copie du backend (HTML des moteurs) est identique au fichier du frontend", () => {
    const copie = JSON.parse(readFileSync(resolve(__dirname, "../../../backend/catalog/faq_accueil.json"), "utf-8"))
    expect(copie).toEqual(faq)
  })

  it("les deux langues ont le même nombre de questions", () => {
    expect(faq.en).toHaveLength(faq.fr.length)
  })

  it("affiche les questions de la langue de l'interface et mène au centre d'aide", async () => {
    const { unmount } = render(<MemoryRouter><FaqAccueil /></MemoryRouter>)
    expect(screen.getByRole("heading", { level: 2, name: "Questions fréquentes" })).toBeInTheDocument()
    expect(screen.getByText("Qu'est-ce qui est gratuit ?")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Ouvrir le centre d'aide" })).toHaveAttribute("href", "/aide")
    unmount()

    await definirLangue("en", { persister: false })
    render(<MemoryRouter><FaqAccueil /></MemoryRouter>)
    expect(screen.getByText("What is free?")).toBeInTheDocument()
    expect(screen.queryByText("Qu'est-ce qui est gratuit ?")).toBeNull()
  })
})
