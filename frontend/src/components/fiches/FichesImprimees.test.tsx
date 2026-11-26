import { act, render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import type { FicheEdukora } from "@/api/types"
import { useImpression } from "@/lib/useImpression"
import { FichesImprimees } from "./FichesImprimees"

function fiche(extra: Partial<FicheEdukora> = {}): FicheEdukora {
  return {
    id: 1, terme: "Comment factoriser ?", definition: "La méthode.", exemple: "", sessions: [], gratuit: true,
    verrouillee: false, gardee: false, a_relire: false, matiere_id: 1, ...extra,
  }
}

describe("FichesImprimees", () => {
  it("regroupe les réponses après les fiches, sous le numéro de leur fiche", () => {
    const { container } = render(
      <FichesImprimees
        titre="Mathématiques"
        fiches={[fiche(), fiche({ id: 2, terme: "Comment développer ?", exercice: "Développe.", reponse: "Résultat attendu" })]}
      />,
    )
    const texte = container.textContent ?? ""
    expect(texte.indexOf("Résultat attendu")).toBeGreaterThan(texte.indexOf("Développe."))
    expect(texte).toContain("2.Résultat attendu")
    expect(screen.queryByRole("button")).toBeNull()
  })

  it("laisse de côté les fiches verrouillées, et ne sort rien s'il n'y a qu'elles", () => {
    const verrouillee = fiche({ id: 2, terme: "Fiche réservée", definition: null, verrouillee: true })
    const { container, rerender } = render(<FichesImprimees titre="Maths" fiches={[fiche(), verrouillee]} />)
    expect(container.textContent).not.toContain("Fiche réservée")
    rerender(<FichesImprimees titre="Maths" fiches={[verrouillee]} />)
    expect(container.innerHTML).toBe("")
  })
})

describe("useImpression", () => {
  function Temoin() {
    return <p>{useImpression() ? "impression" : "écran"}</p>
  }

  it("suit le début et la fin de l'impression du navigateur", () => {
    render(<Temoin />)
    expect(screen.getByText("écran")).toBeTruthy()
    act(() => void window.dispatchEvent(new Event("beforeprint")))
    expect(screen.getByText("impression")).toBeTruthy()
    act(() => void window.dispatchEvent(new Event("afterprint")))
    expect(screen.getByText("écran")).toBeTruthy()
  })
})
