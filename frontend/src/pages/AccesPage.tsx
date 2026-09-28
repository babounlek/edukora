import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, CalendarClock, Check, Sparkles } from "lucide-react"

import {
  listMyInscriptionsInedites,
  listMyInscriptionsRepetiteur,
  listMySubscriptions,
} from "@/api/endpoints"
import type { InscriptionInedite, InscriptionRepetiteur, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

// En dessous, la fin de l'abonnement se voit : la jauge passe à l'orange et "Prolonger" devient
// l'action principale de la ligne. Assez tôt pour renouveler sans coupure, assez tard pour ne pas
// harceler quelqu'un qui vient de payer.
const JOURS_AVANT_RENOUVELLEMENT = 14

function joursRestants(expiresAt: string): number {
  return Math.ceil((new Date(expiresAt).getTime() - Date.now()) / 86_400_000)
}

function dateFr(iso: string): string {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })
}

function libelleCursus(cursus: Subscription["cursus"]): string {
  return `${cursus.examen_display}${cursus.series ? ` - Série ${cursus.series.code}` : ""}`
}

/**
 * Un accès (abonnement ou add-on) : ce qu'il donne, jusqu'à quand, et - surtout - ce qu'il faut faire.
 * Les jours restants se lisent d'un coup d'œil et "Prolonger" apparaît AVANT l'expiration : renouveler
 * quand on est encore en pleine révision, pas après avoir perdu l'accès. Une prolongation repart de
 * l'échéance existante (voir Subscription.extend) : rien n'est perdu à le faire tôt.
 */
function LigneAcces({
  titre, sous_titre, expiresAt, actif, cursusId, renouvelable = true, style,
}: {
  titre: string
  sous_titre?: string
  expiresAt: string
  actif: boolean
  cursusId: number
  renouvelable?: boolean
  style?: React.CSSProperties
}) {
  const jours = joursRestants(expiresAt)
  const bientot = actif && jours <= JOURS_AVANT_RENOUVELLEMENT
  return (
    <li style={style} className="animate-fade-up rounded-3xl border border-border bg-card p-4 shadow-sm sm:p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-display text-base font-semibold leading-snug">{titre}</p>
          {sous_titre && <p className="text-xs text-muted-foreground">{sous_titre}</p>}
        </div>
        {actif ? (
          <Badge variant="success" className="shrink-0 gap-1">
            <Check className="size-3" strokeWidth={3} />
            Actif
          </Badge>
        ) : (
          <Badge variant="outline" className="shrink-0">Expiré</Badge>
        )}
      </div>

      {actif ? (
        <div className="mt-3 flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-t border-border/70 pt-3 text-xs">
          <span className={cn("inline-flex items-center gap-1.5 whitespace-nowrap", bientot ? "font-medium text-warning-foreground dark:text-warning" : "text-muted-foreground")}>
            <CalendarClock className="size-3.5" aria-hidden="true" />
            {jours > 1 ? `${jours} jours restants` : jours === 1 ? "Dernier jour" : "Expire aujourd'hui"}
          </span>
          <span className="text-muted-foreground">jusqu'au {dateFr(expiresAt)}</span>
        </div>
      ) : (
        <p className="mt-3 border-t border-border/70 pt-3 text-xs text-muted-foreground">Expiré le {dateFr(expiresAt)}.</p>
      )}

      {renouvelable && (!actif || bientot) && (
        <Button asChild size="sm" variant={actif ? "default" : "outline"} className="mt-3 rounded-full">
          <Link to={`/abonnement?cursus=${cursusId}`}>
            {actif ? "Prolonger" : "Se réabonner"}
            <ArrowRight className="size-3.5" />
          </Link>
        </Button>
      )}
    </li>
  )
}

export function AccesPage() {
  useSeo({ title: "Mes accès" })

  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [inscriptionsInedites, setInscriptionsInedites] = useState<InscriptionInedite[] | null>(null)
  const [inscriptionsRepetiteur, setInscriptionsRepetiteur] = useState<InscriptionRepetiteur[] | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/mes-acces" } })
      return
    }
    listMySubscriptions().then(setSubscriptions)
    listMyInscriptionsInedites().then(setInscriptionsInedites)
    listMyInscriptionsRepetiteur().then(setInscriptionsRepetiteur)
  }, [isLoading, isAuthenticated, navigate])

  if (isLoading) return null

  const charge = inscriptionsInedites !== null && inscriptionsRepetiteur !== null

  // Les trois sources d'accès (abonnement, add-on inédites, add-on répétiteur) partagent la même
  // forme (cursus/expires_at/is_active) : une seule liste plutôt que trois blocs distincts qui
  // répètent chacun leur propre état vide.
  const acces = [
    ...subscriptions.map((sub) => ({
      key: `sub-${sub.id}`,
      titre: libelleCursus(sub.cursus),
      sous_titre: sub.plan_name ?? (sub.duration_mode === "JUSQUA_EXAMEN" ? "Jusqu'à l'Examen" : "Mensuel"),
      expiresAt: sub.expires_at,
      actif: sub.is_active,
      cursusId: sub.cursus.id,
      // Un accès "Jusqu'à l'Examen" couvre déjà l'échéance : lui proposer de prolonger n'aurait
      // aucun sens tant qu'il est actif.
      renouvelable: sub.duration_mode !== "JUSQUA_EXAMEN" || !sub.is_active,
    })),
    ...(inscriptionsInedites ?? []).map((i) => ({
      key: `inedit-${i.id}`,
      titre: libelleCursus(i.cursus),
      sous_titre: "Épreuves inédites",
      expiresAt: i.expires_at,
      actif: i.is_active,
      cursusId: i.cursus.id,
      renouvelable: true,
    })),
    ...(inscriptionsRepetiteur ?? []).map((i) => ({
      key: `repet-${i.id}`,
      titre: libelleCursus(i.cursus),
      sous_titre: "Add-on Fiches",
      expiresAt: i.expires_at,
      actif: i.is_active,
      cursusId: i.cursus.id,
      renouvelable: true,
    })),
  ]

  const actifs = acces.filter((a) => a.actif)
  const prochaineEcheance = actifs.length > 0 ? Math.min(...actifs.map((a) => joursRestants(a.expiresAt))) : null

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-6 sm:py-10">
      <section className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <Sparkles aria-hidden className="pointer-events-none absolute -bottom-6 -right-4 hidden size-44 rotate-[-12deg] text-primary/[0.07] sm:block" />
        <div className="relative">
          <p className="mb-2 font-display text-sm italic text-primary">Abonnement</p>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">Mes accès</h1>
          <p className="mt-2 max-w-xl text-muted-foreground">
            Ce que ton compte débloque aujourd'hui, examen par examen, et jusqu'à quand.
          </p>

          {charge && actifs.length > 0 && (
            <dl className="mt-5 grid grid-cols-2 gap-2 sm:gap-3">
              <Resume valeur={String(actifs.length)} libelle={actifs.length > 1 ? "accès actifs" : "accès actif"} />
              <Resume valeur={prochaineEcheance !== null ? `${prochaineEcheance} j` : "-"} libelle="avant la prochaine échéance" />
            </dl>
          )}
        </div>
      </section>

      {!charge ? (
        <div className="flex flex-col gap-4" aria-busy="true" aria-label="Chargement des accès">
          <Skeleton className="h-32 w-full rounded-3xl" />
          <Skeleton className="h-32 w-full rounded-3xl" />
        </div>
      ) : acces.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-card/60 px-6 py-12 text-center">
          <span className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Sparkles className="size-6" />
          </span>
          <p className="font-display text-lg font-semibold">Aucun accès actif pour le moment</p>
          <p className="max-w-sm text-sm text-muted-foreground">
            Choisis ton examen pour débloquer les corrigés, les cours et ta séance du jour.
          </p>
          <Button asChild className="mt-1 rounded-full">
            <Link to="/tarifs">
              Voir les formules
              <ArrowRight className="size-3.5" />
            </Link>
          </Button>
        </div>
      ) : (
        <ul className="flex flex-col gap-3">
          {acces.map(({ key, ...props }, index) => (
            <LigneAcces key={key} {...props} style={{ animationDelay: `${Math.min(index, 6) * 60}ms` }} />
          ))}
        </ul>
      )}
    </div>
  )
}

function Resume({ valeur, libelle }: { valeur: string; libelle: string }) {
  return (
    <div className="rounded-2xl border border-border/70 bg-background/70 px-3 py-3 text-center backdrop-blur-sm">
      <dd className="font-display text-2xl font-semibold tabular-nums leading-none sm:text-3xl">{valeur}</dd>
      <dt className="mt-1.5 text-xs leading-tight text-muted-foreground">{libelle}</dt>
    </div>
  )
}
