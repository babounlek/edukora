import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { ManualPayment } from "@/api/types"

const dernier = vi.hoisted(() => ({ data: null as unknown }))
vi.mock("@/lib/aide/hooks", () => ({ useDernierPaiement: () => dernier }))

import { EtatPaiementAide } from "./EtatPaiementAide"

function paiement(surcharge: Partial<ManualPayment>): ManualPayment {
  return {
    id: 1,
    plan: { id: 1, name: "Jusqu'à l'examen" },
    operator: "MTN",
    operator_display: "MTN MoMo",
    amount_expected: 5000,
    amount_declared: 5000,
    payer_phone_number: "+237600000000",
    transaction_reference: "MP123456",
    paid_at: null,
    status: "PENDING",
    status_display: "En vérification",
    rejection_reason: "",
    rejection_reason_display: "",
    created_at: new Date().toISOString(),
    reviewed_at: null,
    profil: null,
    ...surcharge,
  } as unknown as ManualPayment
}

function afficher() {
  return render(
    <MemoryRouter>
      <EtatPaiementAide />
    </MemoryRouter>,
  )
}

describe("EtatPaiementAide", () => {
  beforeEach(() => {
    dernier.data = null
  })

  it("n'affiche rien sans paiement (visiteur, compte sans paiement ou panne)", () => {
    const { container } = afficher()
    expect(container).toBeEmptyDOMElement()
  })

  it("un paiement récent en vérification : statut et délai annoncé, pas d'alerte de retard", () => {
    dernier.data = paiement({})
    afficher()
    expect(screen.getByText("En vérification")).toBeInTheDocument()
    expect(screen.getByText(/généralement sous 3 heures/)).toBeInTheDocument()
    expect(screen.queryByText(/est dépassé/)).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: /tous mes paiements/i })).toHaveAttribute("href", "/mes-paiements")
  })

  it("un paiement en vérification depuis plus que le délai annoncé donne la référence à transmettre", () => {
    dernier.data = paiement({ created_at: new Date(Date.now() - 5 * 3_600_000).toISOString() })
    afficher()
    expect(screen.getByText(/est dépassé/)).toHaveTextContent("MP123456")
  })

  it("un paiement refusé dit pourquoi", () => {
    dernier.data = paiement({ status: "REJECTED", rejection_reason_display: "Montant incorrect" })
    afficher()
    expect(screen.getByText("Refusé")).toBeInTheDocument()
    expect(screen.getByText(/montant incorrect/)).toBeInTheDocument()
  })

  it("un paiement validé dit que l'accès est activé", () => {
    dernier.data = paiement({ status: "APPROVED" })
    afficher()
    expect(screen.getByText("Validé")).toBeInTheDocument()
    expect(screen.getByText("Ton accès est activé.")).toBeInTheDocument()
  })
})
