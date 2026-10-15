import { render, screen, within } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it, vi } from "vitest"

vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm", countries: [] }) }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { definirLangue } from "@/lib/i18n"
import { CONTACT_TELEPHONE_AFFICHAGE, CONTACT_TELEPHONE_URL, EDITEUR_NOM } from "@/lib/site"
import { PrivacyPage } from "./PrivacyPage"
import { TermsPage } from "./TermsPage"

function afficher(page: "cgu" | "confidentialite") {
  return render(
    <MemoryRouter>{page === "cgu" ? <TermsPage /> : <PrivacyPage />}</MemoryRouter>,
  )
}

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("l'éditeur : Kora SARL", () => {
  it("les constantes", () => {
    expect(EDITEUR_NOM).toBe("Kora SARL")
    expect(CONTACT_TELEPHONE_AFFICHAGE).toBe("+237 698 19 29 91")
    expect(CONTACT_TELEPHONE_URL).toBe("tel:+237698192991")
  })

  for (const page of ["cgu", "confidentialite"] as const) {
    it(`${page} : la carte de l'éditeur nomme l'entreprise et son téléphone, plus aucune personne`, () => {
      const { container } = afficher(page)

      expect(screen.getByRole("heading", { name: "Kora SARL", level: 2 })).toBeInTheDocument()
      expect(container.textContent).not.toMatch(/BABOUNLEK|Serge|Guyguy|BSG/)
      const tel = container.querySelector(`a[href="${CONTACT_TELEPHONE_URL}"]`)
      expect(tel).not.toBeNull()
      expect(tel?.textContent).toContain("+237 698 19 29 91")
      // Le WhatsApp reste un contact distinct, avec son propre numéro.
      const whatsapp = container.querySelector('a[href^="https://wa.me/"]')
      expect(whatsapp?.textContent).toMatch(/WhatsApp/)
      expect(whatsapp?.getAttribute("href")).not.toContain("698192991")
    })
  }

  it("CGU : une section Éditeur nomme l'entité avec laquelle les conditions sont conclues", () => {
    afficher("cgu")
    const section = screen.getAllByText(/est édité par Kora SARL/)[0]

    expect(section.textContent).toContain("société à responsabilité limitée établie à Yaoundé (Cameroun)")
    expect(section.textContent).toContain("+237 698 19 29 91")
    expect(section.textContent).toContain("conclues avec Kora SARL")
  })

  it("confidentialité : une section nomme le responsable du traitement", () => {
    afficher("confidentialite")
    const section = screen.getByText(/Le responsable du traitement de tes données est Kora SARL/)

    expect(section.textContent).toContain("+237 698 19 29 91")
  })

  it("en anglais : les mêmes mentions, traduites", async () => {
    await definirLangue("en", { persister: false })
    const { container } = afficher("cgu")

    expect(screen.getByText(/is published by Kora SARL, a limited liability company based in Yaoundé \(Cameroon\)/)).toBeInTheDocument()
    expect(container.textContent).toContain("Publisher of the platform - Yaoundé, Cameroon")
    expect(container.textContent).not.toMatch(/Éditeur de la plateforme/)
    within(container).getByText("+237 698 19 29 91", { selector: "a" })
  })

  it("la date de mise à jour est celle de cette révision", () => {
    const { container } = afficher("cgu")
    expect(container.textContent).toMatch(/15 octobre 2026/)
  })
})
