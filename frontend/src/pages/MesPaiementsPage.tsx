import { useCallback, useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import {
  ArrowRight, Check, CheckCircle2, Clock, Copy, Loader2, Receipt, RefreshCw, ShieldCheck, Sparkles, XCircle,
  type LucideIcon,
} from "lucide-react"

import { listMyManualPayments } from "@/api/endpoints"
import type { ManualPayment, ManualPaymentStatus, MobileMoneyOperator } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { EnteteCompte, EtatVide, Section } from "@/components/CompteSection"
import { Button } from "@/components/ui/button"
import { catalogueHomePath } from "@/lib/countryPath"
import { useSeo } from "@/lib/seo"
import { cn, formatAmount } from "@/lib/utils"

/**
 * Un statut de paiement = une couleur ET une icône, jamais la couleur seule. En attente n'est ni une
 * bonne ni une mauvaise nouvelle : il reste neutre-orangé, pour ne pas inquiéter quelqu'un qui a
 * simplement payé il y a une heure. Le rouge est réservé au refus, seul statut qui demande d'agir.
 */
const STATUTS: Record<ManualPaymentStatus, { libelle: string; Icone: LucideIcon; puce: string; filet: string }> = {
  PENDING: { libelle: "En vérification", Icone: Clock, puce: "bg-warning/15 text-warning-foreground dark:text-warning", filet: "bg-warning" },
  APPROVED: { libelle: "Validé", Icone: CheckCircle2, puce: "bg-success/15 text-success", filet: "bg-success" },
  REJECTED: { libelle: "Refusé", Icone: XCircle, puce: "bg-destructive/10 text-destructive", filet: "bg-destructive" },
}

// Couleurs des opérateurs (identité de marque, comme sur la page d'abonnement).
const OPERATEURS: Record<MobileMoneyOperator, { tuile: string; sigle: string }> = {
  ORANGE: { tuile: "bg-[#FF7900] text-white", sigle: "OM" },
  MTN: { tuile: "bg-[#FFCC08] text-black", sigle: "MTN" },
}

/** Les trois étapes d'une déclaration manuelle : ce qui est fait, ce qui se passe, ce qui vient. */
const ETAPES = ["Déclaré", "Vérification", "Accès activé"] as const

function etapeCourante(statut: ManualPaymentStatus): number {
  // Index de l'étape en cours : 1 = vérification (les deux premières sont acquises), 3 = tout est fait.
  return statut === "PENDING" ? 1 : statut === "APPROVED" ? 3 : 1
}

function dateFr(iso: string): string {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })
}

export function MesPaiementsPage() {
  useSeo({ title: "Mes paiements" })

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

  const refuses = payments?.filter((p) => p.status === "REJECTED").length ?? 0

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:py-10 sm:px-6">
      <EnteteCompte
        icone={Receipt}
        titre="Mes paiements"
        sousTitre="L'état de tes déclarations Mobile Money (Orange Money, MTN MoMo), de la déclaration à l'activation de ton accès."
      />

      <Section icone={Receipt} titre="Déclarations Mobile Money">
        {payments === null && !erreur ? (
          <p className="text-sm text-muted-foreground">Chargement…</p>
        ) : erreur ? (
          // Une panne n'est pas "aucun paiement" : sans ce cas, l'écran restait sur son indicateur de
          // chargement, sans rien dire à quelqu'un qui vient vérifier qu'on a bien reçu son argent.
          <div role="alert" className="flex items-center justify-between gap-3 rounded-xl border border-dashed border-destructive/40 bg-destructive/[0.04] px-4 py-4">
            <p className="text-sm text-muted-foreground">
              Ta connexion ou notre service a eu un raté, et la liste n'a pas pu s'afficher.
            </p>
            <Button onClick={charger} variant="outline" size="sm" className="shrink-0 rounded-full">
              <RefreshCw className="size-3.5" />
              Réessayer
            </Button>
          </div>
        ) : payments!.length === 0 ? (
          <EtatVide
            texte="Aucune déclaration pour l'instant. Quand tu paies par Orange Money ou MTN MoMo en déclarant toi-même ton transfert, le suivi apparaît ici."
            lien="/tarifs"
            libelleLien="Voir les formules"
          />
        ) : (
          <ul className="flex flex-col gap-4">
            {payments!.map((payment, index) => (
              <CartePaiement
                key={payment.id}
                payment={payment}
                accueil={catalogueHomePath(country)}
                style={{ animationDelay: `${Math.min(index, 6) * 60}ms` }}
              />
            ))}
          </ul>
        )}

        {refuses > 0 && (
          <p className="mt-4 text-sm text-muted-foreground">
            Un paiement refusé peut être redéclaré : le motif t'indique ce qu'il faut corriger.
          </p>
        )}
      </Section>

      <p className="mt-4 flex items-start gap-2 rounded-2xl bg-muted/50 px-4 py-3 text-sm text-muted-foreground">
        <ShieldCheck className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
        <span>
          Les paiements Mobile Money automatiques (Campay) activent ton accès en quelques secondes et n'ont pas besoin de
          suivi : seuls les transferts que tu déclares toi-même apparaissent ici.
        </span>
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
    <li
      style={style}
      className="animate-fade-up relative overflow-hidden rounded-3xl border border-border bg-card shadow-sm"
    >
      <div aria-hidden className={cn("h-1.5 w-full", statut.filet)} />
      <div className="p-4 sm:p-6">
        <div className="flex items-start gap-3">
          <span className={cn("flex size-11 shrink-0 items-center justify-center rounded-xl text-xs font-bold", operateur.tuile)}>
            {operateur.sigle}
          </span>
          <div className="min-w-0 flex-1">
            <p className="font-display text-lg font-semibold leading-tight">
              {cursus.examen_display}
              {cursus.series ? ` - Série ${cursus.series.code}` : ""}
            </p>
            <p className="text-sm text-muted-foreground">
              {payment.plan.name} · {payment.operator_display}
            </p>
          </div>
          <div className="shrink-0 text-right">
            <p className="font-display text-xl font-semibold tabular-nums leading-tight">
              {formatAmount(payment.amount_declared)}
              <span className="ml-1 text-sm font-medium text-muted-foreground">FCFA</span>
            </p>
            <span className={cn("mt-1 inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold", statut.puce)}>
              <statut.Icone className="size-3" aria-hidden="true" />
              {statut.libelle}
            </span>
          </div>
        </div>

        {payment.status !== "REJECTED" && <Parcours statut={payment.status} />}

        {payment.status === "PENDING" && (
          <p className="mt-4 rounded-xl bg-muted/50 px-3.5 py-2.5 text-sm text-muted-foreground">
            Notre équipe vérifie ton transfert à la main, généralement en quelques heures. Tu n'as rien à faire : ton
            accès s'active dès la validation.
          </p>
        )}

        {payment.status === "REJECTED" && (
          <div role="alert" className="mt-4 rounded-2xl border border-destructive/25 bg-destructive/[0.06] px-4 py-3">
            <p className="text-sm font-semibold text-destructive">Ce paiement n'a pas pu être validé</p>
            {payment.rejection_reason_display && (
              <p className="mt-0.5 text-sm text-foreground">Motif : {payment.rejection_reason_display}</p>
            )}
            <Button asChild size="sm" className="mt-3 rounded-full">
              <Link to={`/abonnement?cursus=${cursus.id}`}>
                Refaire ma déclaration
                <ArrowRight className="size-3.5" />
              </Link>
            </Button>
          </div>
        )}

        {payment.status === "APPROVED" && (
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-success/25 bg-success/[0.07] px-4 py-3">
            <p className="flex items-center gap-2 text-sm font-medium">
              <Sparkles className="size-4 shrink-0 text-success" aria-hidden="true" />
              Ton accès est activé.
            </p>
            <Button asChild size="sm" className="rounded-full">
              <Link to={accueil}>
                Commencer à réviser
                <ArrowRight className="size-3.5" />
              </Link>
            </Button>
          </div>
        )}

        <dl className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-border/70 pt-3 text-sm text-muted-foreground">
          <div className="inline-flex items-center gap-1.5">
            <dt className="sr-only">Date de déclaration</dt>
            <dd>Déclaré le {dateFr(payment.created_at)}</dd>
          </div>
          <div className="inline-flex items-center gap-1.5">
            <dt>Réf.</dt>
            <dd className="font-mono text-foreground">{payment.transaction_reference}</dd>
            <button
              type="button"
              onClick={copierReference}
              aria-label="Copier la référence de transaction"
              className="flex size-7 items-center justify-center rounded-full text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              {copie ? <Check className="size-3.5 text-success" /> : <Copy className="size-3.5" />}
            </button>
          </div>
        </dl>
      </div>
    </li>
  )
}

/** Le chemin d'une déclaration : trois étapes, ce qui est fait en plein, ce qui se passe en cours. */
function Parcours({ statut }: { statut: ManualPaymentStatus }) {
  const courante = etapeCourante(statut)
  return (
    <ol className="mt-5 flex items-center" aria-label="Avancement de la déclaration">
      {ETAPES.map((etape, index) => {
        const faite = index < courante
        const enCours = index === courante && statut === "PENDING"
        return (
          <li key={etape} className={cn("flex items-center", index < ETAPES.length - 1 && "flex-1")}>
            <span className="flex items-center gap-2">
              <span
                className={cn(
                  "flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
                  faite && "bg-success text-success-foreground",
                  enCours && "bg-warning/20 text-warning-foreground ring-4 ring-warning/10 dark:text-warning",
                  !faite && !enCours && "bg-muted text-muted-foreground",
                )}
                aria-current={enCours ? "step" : undefined}
              >
                {faite ? <Check className="size-3.5" strokeWidth={3} /> : enCours ? <Loader2 className="size-3.5 animate-spin" /> : index + 1}
              </span>
              <span className={cn("text-sm", faite || enCours ? "font-medium text-foreground" : "text-muted-foreground")}>
                {etape}
              </span>
            </span>
            {index < ETAPES.length - 1 && (
              <span aria-hidden className={cn("mx-2 h-px flex-1 sm:mx-3", index < courante ? "bg-success/50" : "bg-border")} />
            )}
          </li>
        )
      })}
    </ol>
  )
}
