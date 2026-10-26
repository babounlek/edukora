import { useEffect, useState, type FormEvent } from "react"
import { toast } from "sonner"
import { AlertTriangle, Check, Copy, Loader2, ShieldAlert } from "lucide-react"

import { declareManualPayment, getRattachementRevendeur, listManualPaymentMethods } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ManualPayment, MobileMoneyAccount, MobileMoneyOperator, Plan } from "@/api/types"
import { cn, formatAmount } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { chiffresNumeroLocal } from "@/lib/telephone"
import { t, useI18n } from "@/lib/i18n"

interface ManualPaymentPanelProps {
  plan: Plan
  operator: MobileMoneyOperator
  onDeclared: (payment: ManualPayment) => void
  // L'enfant pour qui cet achat est fait - voir SubscribePage.tsx, même rôle que
  // InitiatePaymentParams.profilId.
  profilId?: number
  // Numéro du compte, proposé d'office comme numéro payeur (le plus souvent le même).
  defaultPayerPhone?: string
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
 * `plan.effective_price` alimente l'affichage "montant à payer" ; le serveur recalcule toujours
 * amount_expected lui-même depuis plan.effective_price() au moment de la
 * déclaration (voir payments.serializers) - jamais depuis `plan.price` brut, qui
 * n'est qu'un plafond pour un Plan JUSQUA_EXAMEN (voir subscriptions.models.Plan).
 *
 * Ne demande que les deux informations qui identifient le versement (numéro payeur,
 * référence de transaction) : le montant est connu (plan.effective_price), le serveur le
 * reprend de lui-même ; `paid_at` et `proof` restent acceptés par
 * l'API et affichés dans l'admin pour les déclarations passées, mais ne sont
 * volontairement plus saisis ici - un formulaire long est un formulaire abandonné,
 * et l'horodatage comme la capture ne faisaient que redire ce que la référence de
 * transaction permet déjà de vérifier auprès de l'opérateur.
 */
export function ManualPaymentPanel({ plan, operator, onDeclared, profilId, defaultPayerPhone }: ManualPaymentPanelProps) {
  useI18n()
  const [accounts, setAccounts] = useState<MobileMoneyAccount[] | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [copied, setCopied] = useState(false)
  const [copiedAmount, setCopiedAmount] = useState(false)
  const [payerPhoneNumber, setPayerPhoneNumber] = useState(() =>
    defaultPayerPhone && /^6\d{8}$/.test(defaultPayerPhone) ? defaultPayerPhone : "",
  )
  const [transactionReference, setTransactionReference] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  // Revendeur rattaché au compte : il peut avoir avancé la somme depuis son numéro (accompagnement).
  const [revendeurNom, setRevendeurNom] = useState<string | null>(null)
  const [payeParRevendeur, setPayeParRevendeur] = useState(false)

  useEffect(() => {
    getRattachementRevendeur()
      .then((r) => setRevendeurNom(r.revendeur?.nom_affiche ?? null))
      .catch(() => {
        // Simple confort : sans lui, la case n'apparaît pas et le paiement se déclare comme d'habitude.
      })
  }, [])

  useEffect(() => {
    listManualPaymentMethods().then(setAccounts).catch(() => setAccounts([]))
  }, [])

  // Changer d'opérateur ou de plan repart d'un formulaire propre - éviter qu'une
  // déclaration en cours de saisie pour Orange se retrouve soumise par erreur pour MTN.
  useEffect(() => {
    setShowForm(false)
    setError(null)
  }, [operator, plan.id])

  const account = accounts?.find((a) => a.operator === operator) ?? null
  const style = OPERATOR_STYLES[operator]

  // Le « Copié » ne s'affiche qu'une fois la copie réellement faite : navigator.clipboard est absent
  // hors contexte sécurisé et refusé dans certains navigateurs intégrés. Ici l'élève recopie un
  // montant et un numéro à la main sinon - un échec silencieux risque un transfert au mauvais montant.
  function copier(texte: string, marquerCopie: (copie: boolean) => void) {
    Promise.resolve()
      .then(() => navigator.clipboard.writeText(texte))
      .then(() => {
        marquerCopie(true)
        setTimeout(() => marquerCopie(false), 2000)
      })
      .catch(() => toast.error(t("mp.copie_erreur")))
  }

  function handleCopyAmount() {
    copier(String(plan.effective_price), setCopiedAmount)
  }

  function handleCopyNumber() {
    if (!account) return
    copier(account.phone_number, setCopied)
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    if (!/^6\d{8}$/.test(payerPhoneNumber)) {
      setError(t("mp.erreur_numero"))
      return
    }
    if (!transactionReference.trim()) {
      setError(t("mp.erreur_reference"))
      return
    }

    setSubmitting(true)
    try {
      const payment = await declareManualPayment({
        planId: plan.id,
        operator,
        payerPhoneNumber,
        transactionReference,
        profilId,
        payeParRevendeur: revendeurNom !== null && payeParRevendeur,
      })
      onDeclared(payment)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("mp.erreur_declaration"))
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
        {t("mp.indisponible")}
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

        <p className="mt-4 text-xs uppercase tracking-wide text-muted-foreground">{t("mp.montant")}</p>
        <div className="flex items-center justify-between gap-3">
          <p className="font-display text-3xl font-semibold text-primary">
            {formatAmount(plan.effective_price)} <span className="text-base font-normal text-muted-foreground">FCFA</span>
          </p>
          <Button type="button" variant="outline" size="sm" onClick={handleCopyAmount} className="shrink-0">
            {copiedAmount ? <Check className="size-3.5 text-success" /> : <Copy className="size-3.5" />}
            {copiedAmount ? t("mp.copie") : t("mp.copier")}
          </Button>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          {t("mp.envoie", { prix: formatAmount(plan.effective_price) })}
        </p>

        <div className="mt-3.5 flex items-center justify-between gap-3 rounded-lg border border-border bg-background/70 px-3.5 py-2.5">
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground">{t("mp.numero_a_crediter")}</p>
            <p className="truncate font-mono text-lg font-semibold tracking-wide">{account.phone_number}</p>
          </div>
          <Button type="button" variant="outline" size="sm" onClick={handleCopyNumber} className="shrink-0">
            {copied ? <Check className="size-3.5 text-success" /> : <Copy className="size-3.5" />}
            {copied ? t("mp.copie") : t("mp.copier")}
          </Button>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">{t("mp.beneficiaire", { nom: account.account_name })}</p>

        <p className="mt-3.5 flex items-start gap-1.5 text-xs text-muted-foreground">
          <AlertTriangle className="mt-0.5 size-3.5 shrink-0" />
          {t("mp.sms")}
        </p>
      </div>

      {!showForm ? (
        <Button type="button" size="lg" className="w-full" onClick={() => setShowForm(true)}>
          {t("mp.jai_paye")}
        </Button>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{t("mp.declare")}</p>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="payer-phone">{t("mp.numero_paye")}</Label>
              <Input
                id="payer-phone"
                type="tel"
                inputMode="numeric"
                autoComplete="tel-national"
                placeholder="677123456"
                value={payerPhoneNumber}
                // Pas de maxLength : il tronquait un collage « +237 6… » ; le helper retire
                // l'indicatif et ramène à 9 chiffres.
                onChange={(e) => setPayerPhoneNumber(chiffresNumeroLocal(e.target.value))}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="transaction-reference">{t("mp.reference")}</Label>
              <Input
                id="transaction-reference"
                placeholder={t("mp.reference_placeholder")}
                value={transactionReference}
                onChange={(e) => setTransactionReference(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                {t("mp.reference_aide", { operateur: account.operator_display })}
              </p>
            </div>
          </div>

          {revendeurNom && (
            <label className="flex cursor-pointer items-start gap-2.5 rounded-lg border border-border bg-muted/30 px-3.5 py-3 text-sm">
              <input
                type="checkbox"
                checked={payeParRevendeur}
                onChange={(e) => setPayeParRevendeur(e.target.checked)}
                className="mt-0.5 size-4 shrink-0 accent-primary"
              />
              <span>
                <span className="font-medium">{t("rev.avance_case", { nom: revendeurNom })}</span>
                <span className="mt-0.5 block text-xs text-muted-foreground">{t("rev.avance_aide")}</span>
              </span>
            </label>
          )}

          {error && <p role="alert" className="text-sm text-destructive">{error}</p>}

          <Button type="submit" size="lg" className="w-full" disabled={submitting}>
            {submitting ? <Loader2 className="size-4 animate-spin" /> : t("mp.envoyer")}
          </Button>
        </form>
      )}
    </div>
  )
}
