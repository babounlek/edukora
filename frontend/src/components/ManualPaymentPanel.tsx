import { useEffect, useState, type FormEvent } from "react"
import { AlertTriangle, Check, Copy, Loader2, ShieldAlert } from "lucide-react"

import { declareManualPayment, listManualPaymentMethods } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ManualPayment, MobileMoneyAccount, MobileMoneyOperator, Plan } from "@/api/types"
import { cn, formatAmount } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface ManualPaymentPanelProps {
  plan: Plan
  operator: MobileMoneyOperator
  onDeclared: (payment: ManualPayment) => void
}

// Mêmes couleurs de marque que le sélecteur de moyen de paiement (SubscribePage) -
// l'utilisateur doit reconnaître d'un coup d'oeil qu'il est toujours sur le même
// opérateur qu'il vient de choisir.
const OPERATOR_STYLES: Record<MobileMoneyOperator, { initials: string; badgeClass: string; cardClass: string }> = {
  ORANGE: {
    initials: "OM",
    badgeClass: "bg-[#FF7900] text-white",
    cardClass: "border-[#FF7900]/30 bg-[#FF7900]/5",
  },
  MTN: {
    initials: "MTN",
    badgeClass: "bg-[#FFCC08] text-black",
    cardClass: "border-[#FFCC08]/40 bg-[#FFCC08]/10",
  },
}

/**
 * Instructions + formulaire de déclaration pour le paiement Mobile Money manuel.
 * `plan.effective_price` alimente l'affichage "montant à payer" mais ne sert qu'à
 * préremplir amount_declared côté formulaire - le serveur recalcule toujours
 * amount_expected lui-même depuis plan.effective_price() au moment de la
 * déclaration (voir payments.serializers) - jamais depuis `plan.price` brut, qui
 * n'est qu'un plafond pour un Plan JUSQUA_EXAMEN (voir subscriptions.models.Plan).
 *
 * Ne demande que les trois informations qui identifient le versement (numéro payeur,
 * référence de transaction, montant) : `paid_at` et `proof` restent acceptés par
 * l'API et affichés dans l'admin pour les déclarations passées, mais ne sont
 * volontairement plus saisis ici - un formulaire long est un formulaire abandonné,
 * et l'horodatage comme la capture ne faisaient que redire ce que la référence de
 * transaction permet déjà de vérifier auprès de l'opérateur.
 */
export function ManualPaymentPanel({ plan, operator, onDeclared }: ManualPaymentPanelProps) {
  const [accounts, setAccounts] = useState<MobileMoneyAccount[] | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [copied, setCopied] = useState(false)
  const [payerPhoneNumber, setPayerPhoneNumber] = useState("")
  const [transactionReference, setTransactionReference] = useState("")
  const [amountDeclared, setAmountDeclared] = useState(String(plan.effective_price))
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listManualPaymentMethods().then(setAccounts).catch(() => setAccounts([]))
  }, [])

  // Changer d'opérateur ou de plan repart d'un formulaire propre - éviter qu'une
  // déclaration en cours de saisie pour Orange se retrouve soumise par erreur pour MTN.
  useEffect(() => {
    setShowForm(false)
    setError(null)
    setAmountDeclared(String(plan.effective_price))
  }, [operator, plan.id, plan.effective_price])

  const account = accounts?.find((a) => a.operator === operator) ?? null
  const style = OPERATOR_STYLES[operator]

  function handleCopyNumber() {
    if (!account) return
    navigator.clipboard.writeText(account.phone_number)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    if (!/^6\d{8}$/.test(payerPhoneNumber)) {
      setError("Entre le numéro Mobile Money ayant servi au paiement (9 chiffres, commence par 6).")
      return
    }
    if (!transactionReference.trim()) {
      setError("Le numéro de transaction est obligatoire.")
      return
    }
    const amount = Number(amountDeclared)
    if (!amount || amount <= 0) {
      setError("Indique le montant réellement payé.")
      return
    }
    if (amount < plan.effective_price) {
      setError(`Le montant payé ne peut pas être inférieur au prix de l'offre (${formatAmount(plan.effective_price)} FCFA).`)
      return
    }

    setSubmitting(true)
    try {
      const payment = await declareManualPayment({
        planId: plan.id,
        operator,
        amountDeclared: amount,
        payerPhoneNumber,
        transactionReference,
      })
      onDeclared(payment)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "La déclaration n'a pas pu être enregistrée.")
    } finally {
      setSubmitting(false)
    }
  }

  if (accounts === null) {
    return (
      <div className="flex justify-center py-6">
        <Loader2 className="size-6 animate-spin text-primary" />
      </div>
    )
  }

  if (!account) {
    return (
      <div className="flex items-start gap-2 rounded-lg border border-warning/40 bg-warning/10 px-3.5 py-3 text-sm">
        <ShieldAlert className="mt-0.5 size-4 shrink-0" />
        Ce moyen de paiement n'est pas disponible actuellement. Choisis Campay ou l'autre opérateur Mobile Money.
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className={cn("rounded-xl border px-4 py-4", style.cardClass)}>
        <div className="flex items-center gap-2.5">
          <span className={cn("flex size-7 items-center justify-center rounded-full text-xs font-bold", style.badgeClass)}>
            {style.initials}
          </span>
          <p className="font-display font-medium">{account.operator_display}</p>
        </div>

        <p className="mt-4 text-xs uppercase tracking-wide text-muted-foreground">Montant à payer</p>
        <p className="font-display text-3xl font-semibold text-primary">
          {formatAmount(plan.effective_price)} <span className="text-base font-normal text-muted-foreground">FCFA</span>
        </p>

        <div className="mt-3.5 flex items-center justify-between gap-3 rounded-lg border border-border bg-background/70 px-3.5 py-2.5">
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground">Numéro à créditer</p>
            <p className="truncate font-mono text-lg font-semibold tracking-wide">{account.phone_number}</p>
          </div>
          <Button type="button" variant="outline" size="sm" onClick={handleCopyNumber} className="shrink-0">
            {copied ? <Check className="size-3.5 text-success" /> : <Copy className="size-3.5" />}
            {copied ? "Copié" : "Copier"}
          </Button>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">Bénéficiaire : {account.account_name}</p>

        <p className="mt-3.5 flex items-start gap-1.5 text-xs text-muted-foreground">
          <AlertTriangle className="mt-0.5 size-3.5 shrink-0" />
          Conserve le SMS de confirmation envoyé par ton opérateur - il te sera utile en cas de vérification.
        </p>
      </div>

      {!showForm ? (
        <Button type="button" size="lg" className="w-full" onClick={() => setShowForm(true)}>
          J'ai effectué le paiement
        </Button>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Déclare ton paiement</p>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="payer-phone">Numéro ayant payé</Label>
              <Input
                id="payer-phone"
                inputMode="numeric"
                placeholder="677123456"
                value={payerPhoneNumber}
                onChange={(e) => setPayerPhoneNumber(e.target.value.replace(/\D/g, ""))}
                maxLength={9}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="transaction-reference">N° de transaction</Label>
              <Input
                id="transaction-reference"
                placeholder="Ex : OM240101.1234"
                value={transactionReference}
                onChange={(e) => setTransactionReference(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-2 sm:col-span-2">
              <Label htmlFor="amount-declared">Montant payé (FCFA)</Label>
              <Input
                id="amount-declared"
                inputMode="numeric"
                value={amountDeclared}
                onChange={(e) => setAmountDeclared(e.target.value.replace(/\D/g, ""))}
              />
            </div>
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <Button type="submit" size="lg" className="w-full" disabled={submitting}>
            {submitting ? <Loader2 className="size-4 animate-spin" /> : "Envoyer ma déclaration"}
          </Button>
        </form>
      )}
    </div>
  )
}
