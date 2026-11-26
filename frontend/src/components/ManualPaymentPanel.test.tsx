import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listManualPaymentMethods = vi.hoisted(() => vi.fn())
const declareManualPayment = vi.hoisted(() => vi.fn())
const getRattachementRevendeur = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ listManualPaymentMethods, declareManualPayment, getRattachementRevendeur }))

import type { Plan } from "@/api/types"
import { ManualPaymentPanel } from "./ManualPaymentPanel"

const plan = { id: 7, effective_price: 2000, duration_mode: "MENSUEL" } as Plan

async function ouvrirLeFormulaire() {
  const user = userEvent.setup()
  render(<ManualPaymentPanel plan={plan} mois={3} montant={6000} operator="ORANGE" onDeclared={vi.fn()} />)
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

describe("ManualPaymentPanel : ouvrir le menu Mobile Money depuis le téléphone", () => {
  it("propose de composer le code du bon opérateur, sans rien pré-remplir du transfert", async () => {
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: true, revendeur: null })
    render(<ManualPaymentPanel plan={plan} mois={1} montant={2000} operator="ORANGE" onDeclared={vi.fn()} />)

    const lien = await screen.findByRole("link", { name: "Composer #150# pour ouvrir Orange Money" })
    expect(lien).toHaveAttribute("href", "tel:%23150%23")
    expect(lien.getAttribute("href")).not.toMatch(/699000000|2000/)
  })

  it("donne le code de MTN à qui paie par MTN", async () => {
    listManualPaymentMethods.mockResolvedValue([
      { operator: "MTN", operator_display: "MTN Mobile Money", phone_number: "677000000", account_name: "Edukora" },
    ])
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: true, revendeur: null })
    render(<ManualPaymentPanel plan={plan} mois={1} montant={2000} operator="MTN" onDeclared={vi.fn()} />)

    expect(await screen.findByRole("link", { name: "Composer *126# pour ouvrir MTN Mobile Money" })).toHaveAttribute(
      "href",
      "tel:*126%23",
    )
  })
})

describe("ManualPaymentPanel : compte marchand payé par code", () => {
  const compteMarchand = {
    operator: "ORANGE", operator_display: "Orange Money", phone_number: "", merchant_code: "654321",
    account_name: "EduKora SARL",
  }

  beforeEach(() => {
    getRattachementRevendeur.mockResolvedValue({ peut_saisir_code: true, revendeur: null })
  })

  it("montre le code marchand à la place du numéro et demande de vérifier le nom", async () => {
    listManualPaymentMethods.mockResolvedValue([{ ...compteMarchand, ussd_template: "" }])
    render(<ManualPaymentPanel plan={plan} mois={1} montant={2000} operator="ORANGE" onDeclared={vi.fn()} />)

    expect(await screen.findByText("Code marchand")).toBeInTheDocument()
    expect(screen.getByText("654321")).toBeInTheDocument()
    expect(screen.queryByText("Numéro à créditer")).not.toBeInTheDocument()
    expect(screen.getByText(/vérifie que ton opérateur affiche bien EduKora SARL et 2.000 FCFA/)).toBeInTheDocument()
    // Sans séquence saisie dans l'admin : le menu de l'opérateur, et l'élève y choisit le paiement marchand.
    expect(screen.getByText(/choisis le paiement marchand/)).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Composer #150# pour ouvrir Orange Money" })).toBeInTheDocument()
  })

  it("compose la séquence du kit de l'opérateur avec le code et le montant", async () => {
    listManualPaymentMethods.mockResolvedValue([{ ...compteMarchand, ussd_template: "#150*47*{code}*{montant}#" }])
    render(<ManualPaymentPanel plan={plan} mois={3} montant={6000} operator="ORANGE" onDeclared={vi.fn()} />)

    expect(await screen.findByText("#150*47*654321*6000#")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Composer le paiement" })).toHaveAttribute(
      "href",
      "tel:%23150*47*654321*6000%23",
    )
    expect(screen.queryByRole("link", { name: /pour ouvrir Orange Money/ })).not.toBeInTheDocument()
  })
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
