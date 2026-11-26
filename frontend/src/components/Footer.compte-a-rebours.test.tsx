import { render } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it, vi } from "vitest"

vi.mock("@tanstack/react-query", () => ({ useQuery: () => ({ data: undefined }) }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/abonneActif", () => ({ useAbonneActif: () => false }))
vi.mock("@/lib/cursusLangue", () => ({ useCursusListe: () => ({ data: [] }) }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: {
      a_un_abonnement_actif: false,
      cursus_prepare: null,
      compte_a_rebours: { session_label: "BEPC 2027", jours_restants: 186, estimee: false },
    },
  }),
}))

import { Footer } from "./Footer"

describe("compte à rebours du pied de page", () => {
  it("met en gras l'examen et le délai, sans changer la phrase", () => {
    const { container } = render(
      <MemoryRouter initialEntries={["/cm/epreuves"]}>
        <Footer />
      </MemoryRouter>,
    )

    expect(Array.from(container.querySelectorAll("strong"), (e) => e.textContent)).toEqual(["BEPC 2027", "186 jours"])
    expect(container).toHaveTextContent("BEPC 2027 dans 186 jours. Débloque tous les corrigés")
  })
})
