import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listManualPaymentMethods = vi.hoisted(() => vi.fn())
const declareManualPayment = vi.hoisted(() => vi.fn())
const getRattachementRevendeur = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ listManualPaymentMethods, declareManualPayment, getRattachementRevendeur }))

import type { Plan } from "@/api/types"
import { ManualPaymentPanel } from "./ManualPaymentPanel"

const plan = { id: 7, effective_price: 15000 } as Plan

async function ouvrirLeFormulaire() {
  const user = userEvent.setup()
  render(<ManualPaymentPanel plan={plan} operator="ORANGE" onDeclared={vi.fn()} />)
  await user.click(await screen.findByRole("button", { name: /effectué le paiement/i }))
  return user
}

beforeEach(() => {
  listManualPaymentMethods.mockReset().mockResolvedValue([
    { operator: "ORANGE", operator_display: "Orange Money", phone_number: "699000000", account_name: "Edukora" },
  ])
  declareManualPayment.mockReset().mockResolvedValue({ id: 1 })
  getRattachementRevendeur.mockReset()
})

describe("ManualPaymentPanel : paiement avancé par le revendeur", () => {
  it("n'affiche pas la case sans revendeur rattaché", async () => {
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: true, revendeur: null })
    await ouvrirLeFormulaire()

    expect(screen.queryByRole("checkbox")).not.toBeInTheDocument()
  })

  it("propose la case avec le nom du revendeur et envoie la déclaration", async () => {
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: false, revendeur: { nom_affiche: "Marie" } })
    const user = await ouvrirLeFormulaire()

    await user.click(await screen.findByRole("checkbox", { name: /Marie, mon revendeur/ }))
    await user.type(screen.getByLabelText(/numéro/i, { selector: "#payer-phone" }), "699111222")
    await user.type(screen.getByLabelText(/transaction/i, { selector: "#transaction-reference" }), "MP1234")
    await user.click(screen.getByRole("button", { name: /envoyer ma déclaration/i }))

    expect(declareManualPayment).toHaveBeenCalledWith(expect.objectContaining({ payeParRevendeur: true, payerPhoneNumber: "699111222" }))
  })

  it("n'envoie pas la déclaration quand la case reste décochée", async () => {
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: false, revendeur: { nom_affiche: "Marie" } })
    const user = await ouvrirLeFormulaire()
    await screen.findByRole("checkbox")

    await user.type(screen.getByLabelText(/numéro/i, { selector: "#payer-phone" }), "677123456")
    await user.type(screen.getByLabelText(/transaction/i, { selector: "#transaction-reference" }), "MP5678")
    await user.click(screen.getByRole("button", { name: /envoyer ma déclaration/i }))

    expect(declareManualPayment).toHaveBeenCalledWith(expect.objectContaining({ payeParRevendeur: false }))
  })

  it("garde le formulaire utilisable quand la lecture du revendeur échoue", async () => {
    getRattachementRevendeur.mockRejectedValue(new Error("réseau"))
    await ouvrirLeFormulaire()

    expect(screen.queryByRole("checkbox")).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: /envoyer ma déclaration/i })).toBeInTheDocument()
  })
})
