import { Link } from "react-router-dom"
import { CheckCircle2, Clock, XCircle, type LucideIcon } from "lucide-react"

import type { ManualPaymentStatus } from "@/api/types"
import { useDernierPaiement } from "@/lib/aide/hooks"
import { DELAI_VERIFICATION_PAIEMENT_MANUEL_HEURES, delaiVerificationPaiementAffiche } from "@/lib/delaiVerificationPaiement"
import { localeCourante, t, useI18n } from "@/lib/i18n"
import { cn, formatAmount } from "@/lib/utils"

/** Les articles qui répondent à « où en est mon paiement ? » : l'état du dernier paiement s'affiche en tête. */
export const ARTICLES_ETAT_PAIEMENT = ["paiement-en-verification", "paiement-refuse", "delai-activation"]

const STATUTS: Record<
  ManualPaymentStatus,
  { cle: "pm.statut_pending" | "pm.statut_approved" | "pm.statut_rejected"; Icone: LucideIcon; puce: string }
> = {
  PENDING: { cle: "pm.statut_pending", Icone: Clock, puce: "text-warning-foreground dark:text-warning" },
  APPROVED: { cle: "pm.statut_approved", Icone: CheckCircle2, puce: "text-success" },
  REJECTED: { cle: "pm.statut_rejected", Icone: XCircle, puce: "text-destructive" },
}

/**
 * « Où en est mon paiement ? » sans quitter l'aide : l'état du paiement manuel le plus récent du compte connecté,
 * avec le motif d'un refus et, si le délai annoncé est dépassé, la marche à suivre. Rien pour un visiteur, un compte
 * sans paiement ou une panne : l'article se lit alors tel quel. Le détail (référence, tous les paiements) reste dans
 * Mes paiements, une seule page de vérité.
 */
export function EtatPaiementAide({ className }: { className?: string }) {
  useI18n()
  const { data: paiement } = useDernierPaiement()
  if (!paiement) return null

  const statut = STATUTS[paiement.status]
  const depot = new Date(paiement.created_at)
  const quand = depot.toLocaleString(localeCourante(), { day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" })
  const delaiDepasse =
    paiement.status === "PENDING" &&
    Date.now() - depot.getTime() > DELAI_VERIFICATION_PAIEMENT_MANUEL_HEURES * 3_600_000

  return (
    <section aria-labelledby="aide-etat-paiement" className={cn("rounded-2xl border border-border bg-card p-4", className)}>
      <h2 id="aide-etat-paiement" className="text-sm font-semibold text-muted-foreground">{t("aide.etat.titre")}</h2>
      <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm">
          <span className="font-medium">{paiement.operator_display}</span> · {formatAmount(paiement.amount_declared)} FCFA ·{" "}
          {t("aide.etat.depose", { date: quand })}
        </p>
        <p className={cn("inline-flex items-center gap-1 text-sm font-semibold", statut.puce)}>
          <statut.Icone className="size-4" aria-hidden="true" />
          {t(statut.cle)}
        </p>
      </div>
      {paiement.status === "PENDING" && (
        <p role="status" className="mt-2 text-sm text-muted-foreground">
          {delaiDepasse
            ? t("aide.etat.depasse", { delai: delaiVerificationPaiementAffiche(), ref: paiement.transaction_reference })
            : t("pm.verifie", { delai: delaiVerificationPaiementAffiche() })}
        </p>
      )}
      {paiement.status === "REJECTED" && (
        <p role="status" className="mt-2 text-sm">
          {t("pm.refuse")}
          {paiement.rejection_reason_display ? t("pm.refuse_motif", { motif: paiement.rejection_reason_display.toLowerCase() }) : "."}
        </p>
      )}
      {paiement.status === "APPROVED" && <p className="mt-2 text-sm text-muted-foreground">{t("pm.active")}</p>}
      <Link to="/mes-paiements" className="mt-2 inline-flex min-h-8 items-center text-sm font-medium text-primary underline underline-offset-2">
        {t("aide.etat.voir")}
      </Link>
    </section>
  )
}
