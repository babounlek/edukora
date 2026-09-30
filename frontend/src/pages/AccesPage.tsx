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
import { EnteteCompte, EtatVide, Section } from "@/components/CompteSection"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
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
  titre, sous_titre, expiresAt, actif, cursusId, renouvelable = true, inclutInedit = false,
}: {
  titre: string
  sous_titre?: string
  expiresAt: string
  actif: boolean
  cursusId: number
  renouvelable?: boolean
  inclutInedit?: boolean
}) {
  const jours = joursRestants(expiresAt)
  const bientot = actif && jours <= JOURS_AVANT_RENOUVELLEMENT
  return (
    <li className="rounded-xl border border-border bg-background/60 p-3.5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold leading-snug">{titre}</p>
          {sous_titre && <p className="text-xs text-muted-foreground">{sous_titre}</p>}
          {inclutInedit && (
            <p className="mt-0.5 flex items-center gap-1 text-xs font-medium text-gold-text">
              <Sparkles className="size-3" />
              Épreuves inédites incluses
            </p>
          )}
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
        <div className="mt-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-0.5 text-xs">
          <span className={cn("inline-flex items-center gap-1.5 whitespace-nowrap", bientot ? "font-medium text-warning-foreground dark:text-warning" : "text-muted-foreground")}>
            <CalendarClock className="size-3.5" aria-hidden="true" />
            {jours > 1 ? `${jours} jours restants` : jours === 1 ? "Dernier jour" : "Expire aujourd'hui"}
          </span>
          <span className="text-muted-foreground">jusqu'au {dateFr(expiresAt)}</span>
        </div>
      ) : (
        <p className="mt-2 text-xs text-muted-foreground">Expiré le {dateFr(expiresAt)}.</p>
      )}

      {renouvelable && (!actif || bientot) && (
        <Button asChild size="sm" variant={actif ? "default" : "outline"} className="mt-3 h-8 rounded-full text-xs">
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

  // L'add-on Épreuves Inédites n'est plus achetable séparément (retiré le 2026-09-30) :
  // il est désormais TOUJOURS activé pour la même durée que l'abonnement qui l'inclut
  // (voir payments.models._activer_acces, Plan.inclut_inedit). Une ligne séparée avec
  // sa propre échéance ne ferait donc que dupliquer celle de l'abonnement - inutile et
  // source de confusion ("deux abonnements actifs ?"). On s'en sert seulement pour
  // savoir SUR QUEL cursus l'afficher comme un simple badge sur la ligne d'abonnement.
  const cursusAvecInedit = new Set(
    (inscriptionsInedites ?? []).filter((i) => i.is_active).map((i) => i.cursus.id),
  )

  // Les deux sources d'accès restantes (abonnement, add-on répétiteur) partagent la même
  // forme (cursus/expires_at/is_active) : une seule liste plutôt que deux blocs distincts qui
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
      inclutInedit: cursusAvecInedit.has(sub.cursus.id),
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

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:py-10 sm:px-6">
      <EnteteCompte
        icone={Sparkles}
        titre="Mes accès"
        sousTitre="Ce que ton compte débloque aujourd'hui, examen par examen."
      />

      <Section icone={Sparkles} titre="Abonnements et accès">
        {acces.length > 0 ? (
          <ul className="flex flex-col gap-2.5">
            {acces.map(({ key, ...props }) => <LigneAcces key={key} {...props} />)}
          </ul>
        ) : charge ? (
          <EtatVide
            texte="Aucun accès actif pour le moment. Choisis ton examen pour débloquer les corrigés, les cours et ta séance du jour."
            lien="/tarifs"
            libelleLien="Voir les formules"
          />
        ) : (
          <p className="text-sm text-muted-foreground">Chargement…</p>
        )}
      </Section>
    </div>
  )
}
