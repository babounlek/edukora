import { useCallback, useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, Check, CheckCircle2, Clock, Copy, RefreshCw, XCircle, type LucideIcon } from "lucide-react"

import { listMyManualPayments } from "@/api/endpoints"
import type { ManualPayment, ManualPaymentStatus, MobileMoneyOperator } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { catalogueHomePath } from "@/lib/countryPath"
import { useSeo } from "@/lib/seo"
import { cn, formatAmount } from "@/lib/utils"
import { delaiVerificationPaiementAffiche } from "@/lib/delaiVerificationPaiement"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"

/**
 * Un statut = une icône ET un libellé, jamais la couleur seule. « En vérification » reste neutre :
 * ce n'est ni une bonne ni une mauvaise nouvelle, il ne doit pas inquiéter quelqu'un qui a payé il y
 * a une heure. Le rouge est réservé au refus, seul statut qui demande d'agir.
 */
const STATUTS: Record<ManualPaymentStatus, { libelle: string; Icone: LucideIcon; puce: string; segment: string }> = {
  PENDING: { get libelle() { return t("pm.statut_pending") }, Icone: Clock, puce: "text-warning-foreground dark:text-warning", segment: "bg-warning" },
  APPROVED: { get libelle() { return t("pm.statut_approved") }, Icone: CheckCircle2, puce: "text-success", segment: "bg-success" },
  REJECTED: { get libelle() { return t("pm.statut_rejected") }, Icone: XCircle, puce: "text-destructive", segment: "bg-destructive" },
}

// Couleurs des opérateurs (identité de marque, comme sur la page d'abonnement).
const OPERATEURS: Record<MobileMoneyOperator, { tuile: string; sigle: string }> = {
  ORANGE: { tuile: "bg-[#FF7900] text-white", sigle: "OM" },
  MTN: { tuile: "bg-[#FFCC08] text-black", sigle: "MTN" },
}

function dateFr(iso: string): string {
  return new Date(iso).toLocaleDateString(localeCourante(), { day: "numeric", month: "long", year: "numeric" })
}

/** « 1 validé · 1 en vérification » : le coup d'œil avant la liste. */
function resume(payments: ManualPayment[]): string {
  const comptes = (statut: ManualPaymentStatus) => payments.filter((p) => p.status === statut).length
  const parties = [
    [comptes("APPROVED"), (n: number) => tn("pm.valides", n)],
    [comptes("PENDING"), (n: number) => t("pm.verification", { n })],
    [comptes("REJECTED"), (n: number) => tn("pm.refuses", n)],
  ] as const
  return parties
    .filter(([n]) => n > 0)
    .map(([n, texte]) => texte(n))
    .join(" · ")
}

export function MesPaiementsPage() {
  useI18n()
  useSeo({ title: t("compte.paiements") })

  const { isAuthenticated, isLoading } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const [payments, setPayments] = useState<ManualPayment[] | null>(null)
  const [erreur, setErreur] = useState(false)

  const charger = useCallback(() => {
    setErreur(false)
    setPayments(null)
    listMyManualPayments().then(setPayments).catch(() => setErreur(true))
  }, [])

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/mes-paiements" } })
      return
    }
    charger()
  }, [isLoading, isAuthenticated, navigate, charger])

  if (isLoading) return null

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <header className="mb-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("compte.paiements")}</h1>
        <p className="mt-2 max-w-xl text-muted-foreground">
          {t("pm.sous_titre")}
        </p>
        {payments !== null && payments.length > 0 && (
          <p className="mt-3 text-sm font-medium text-foreground/80">{resume(payments)}</p>
        )}
      </header>

      {erreur ? (
        // Une panne n'est pas « aucun paiement » : sans ce cas, l'écran restait sur son chargement,
        // sans rien dire à quelqu'un qui vient vérifier qu'on a bien reçu son argent.
        <div role="alert" className="flex items-center justify-between gap-4 rounded-2xl border border-border bg-card px-5 py-4">
          <p className="text-sm text-muted-foreground">
            {t("pm.erreur")}
          </p>
          <Button onClick={charger} variant="outline" size="sm" className="shrink-0 rounded-full">
            <RefreshCw className="size-3.5" />
            {t("erreur.reessayer")}
          </Button>
        </div>
      ) : payments === null ? (
        <div className="flex flex-col gap-3" aria-busy="true" aria-label={t("pm.chargement")}>
          <Skeleton className="h-28 rounded-2xl" />
          <Skeleton className="h-28 rounded-2xl" />
        </div>
      ) : payments.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border px-6 py-12 text-center">
          <p className="font-display text-lg font-semibold">{t("pm.vide")}</p>
          <p className="mx-auto mt-1.5 max-w-sm text-sm text-muted-foreground">
            {t("pm.vide_texte")}
          </p>
          <Button asChild className="mt-5 rounded-full">
            <Link to="/tarifs">
              {t("ar.formules")}
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      ) : (
        <ul className="flex flex-col gap-3">
          {payments.map((payment, index) => (
            <CartePaiement
              key={payment.id}
              payment={payment}
              accueil={catalogueHomePath(country)}
              style={{ animationDelay: `${Math.min(index, 6) * 60}ms` }}
            />
          ))}
        </ul>
      )}

      <p className="mt-8 text-center text-xs leading-relaxed text-muted-foreground">
        {t("pm.note_campay")}
      </p>
    </div>
  )
}

function CartePaiement({
  payment, accueil, style,
}: { payment: ManualPayment; accueil: string; style: React.CSSProperties }) {
  const statut = STATUTS[payment.status]
  const operateur = OPERATEURS[payment.operator]
  const cursus = payment.plan.cursus
  const [copie, setCopie] = useState(false)

  function copierReference() {
    navigator.clipboard.writeText(payment.transaction_reference)
    setCopie(true)
    setTimeout(() => setCopie(false), 2000)
  }

  return (
    <li style={style} className="animate-fade-up rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start gap-3.5">
        <span className={cn("flex size-10 shrink-0 items-center justify-center rounded-xl text-xs font-bold", operateur.tuile)}>
          {operateur.sigle}
        </span>
        <div className="min-w-0 flex-1">
          <p className="font-display text-base font-semibold leading-tight">
            {cursus.examen_display}
            {cursus.series ? ` - ${t("prix.serie", { code: cursus.series.code })}` : ""}
          </p>
          <p className="mt-0.5 text-sm text-muted-foreground">
            {payment.operator_display} · {dateFr(payment.created_at)}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <p className="font-display text-lg font-semibold tabular-nums leading-tight">
            {formatAmount(payment.amount_declared)}
            <span className="ml-1 text-xs font-medium text-muted-foreground">FCFA</span>
          </p>
          <p className={cn("mt-1 inline-flex items-center gap-1 text-xs font-semibold", statut.puce)}>
            <statut.Icone className="size-3.5" aria-hidden="true" />
            {statut.libelle}
          </p>
        </div>
      </div>

      {payment.status !== "REJECTED" && <Avancement statut={payment.status} />}

      {payment.status === "PENDING" && (
        <p className="mt-3 text-sm text-muted-foreground">
          {t("pm.verifie", { delai: delaiVerificationPaiementAffiche() })}
        </p>
      )}

      {payment.status === "REJECTED" && (
        <div role="alert" className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-foreground">
            {t("pm.refuse")}
            {payment.rejection_reason_display ? t("pm.refuse_motif", { motif: payment.rejection_reason_display.toLowerCase() }) : "."}
          </p>
          <Button asChild size="sm" variant="outline" className="rounded-full">
            <Link to={`/abonnement?cursus=${cursus.id}`}>
              {t("pm.refaire")}
              <ArrowRight className="size-3.5" />
            </Link>
          </Button>
        </div>
      )}

      {payment.status === "APPROVED" && (
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-muted-foreground">{t("pm.active")}</p>
          <Link to={accueil} className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline">
            {t("pm.commencer")}
            <ArrowRight className="size-3.5" />
          </Link>
        </div>
      )}

      <div className="mt-4 flex items-center gap-1.5 border-t border-border/60 pt-3 text-xs text-muted-foreground">
        <span>{t("pm.ref")}</span>
        <span className="font-mono text-foreground/80">{payment.transaction_reference}</span>
        <button
          type="button"
          onClick={copierReference}
          aria-label={t("pm.copier_aria")}
          className="flex size-6 items-center justify-center rounded-full transition-colors hover:bg-muted hover:text-foreground"
        >
          {copie ? <Check className="size-3.5 text-success" /> : <Copy className="size-3.5" />}
        </button>
        <span className="ml-auto">{payment.plan.name}</span>
      </div>
    </li>
  )
}

/** Trois segments fins : déclaré, en vérification, accès activé - sans étiquettes ni pastilles. */
function Avancement({ statut }: { statut: ManualPaymentStatus }) {
  const faits = statut === "APPROVED" ? 3 : 2
  const actif = STATUTS[statut].segment
  return (
    <div
      role="img"
      aria-label={statut === "APPROVED" ? t("pm.avancement_ok") : t("pm.avancement_cours")}
      className="mt-4 flex gap-1.5"
    >
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          aria-hidden
          className={cn(
            "h-1 flex-1 rounded-full",
            i < faits ? actif : "bg-muted",
            statut === "PENDING" && i === 1 && "animate-pulse",
          )}
        />
      ))}
    </div>
  )
}
