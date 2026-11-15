import { CalendarDays } from "lucide-react"

import type { PlanDate as PlanDateType } from "@/api/types"
import { pourcent } from "@/lib/maitrise"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"

function jourCourt(iso: string): string {
  return new Date(`${iso}T12:00:00`).toLocaleDateString(localeCourante(), { day: "numeric", month: "long" })
}

/**
 * Le plan daté de la préparation (audit produit 2026-11-13, R16) : la trajectoire rendue concrète. « Cette semaine : 2 sur 4
 * thèmes », les étapes jusqu'au jour J, et ce que changerait une séance de plus par semaine. Replié par défaut : l'accueil
 * garde sa phrase, le plan s'ouvre à la demande.
 */
export function PlanDate({ plan }: { plan: PlanDateType }) {
  useI18n()
  if (plan.themes_a_consolider === 0) {
    return <p className="mt-3 text-sm text-muted-foreground">{t("plan.deja_atteint")}</p>
  }
  const { cette_semaine: semaine } = plan
  const avancement = semaine.cible > 0 ? Math.min(100, Math.round((100 * semaine.faits) / semaine.cible)) : 0
  const fait = semaine.faits >= semaine.cible

  return (
    <details className="group mt-3 rounded-xl border border-border/70 bg-card px-3 py-2.5">
      <summary className="flex cursor-pointer list-none items-center gap-2 text-sm font-medium">
        <CalendarDays className="size-4 shrink-0 text-primary" aria-hidden="true" />
        {t("plan.titre", { date: jourCourt(plan.jour_j) })}
      </summary>

      <div className="mt-3">
        <p className="text-sm">
          {fait
            ? t("plan.semaine_faite", { n: semaine.faits })
            : t("plan.semaine", { faits: semaine.faits, cible: semaine.cible })}
        </p>
        <span className="mt-1.5 block h-1.5 overflow-hidden rounded-full bg-muted" aria-hidden="true">
          <span className="block h-full rounded-full bg-primary" style={{ width: `${Math.max(avancement, 3)}%` }} />
        </span>
      </div>

      <ol className="mt-4 flex flex-col gap-1.5 border-l-2 border-primary/20 pl-3 text-sm">
        {plan.etapes.map((etape, i) => {
          const dernier = i === plan.etapes.length - 1
          return (
            <li key={etape.date} className={dernier ? "font-medium" : "text-muted-foreground"}>
              <span className="block text-xs">{dernier ? t("plan.jour_j", { date: jourCourt(etape.date) }) : t("plan.dici", { date: jourCourt(etape.date) })}</span>
              {tn("plan.themes_a_consolider", etape.themes)}
            </li>
          )
        })}
      </ol>

      {plan.une_seance_de_plus && (
        <p className="mt-4 rounded-lg bg-primary/5 px-3 py-2 text-sm">
          {t("plan.une_de_plus", { pct: pourcent(plan.une_seance_de_plus.couverture_projetee) })}
        </p>
      )}
      <p className="mt-3 text-xs text-muted-foreground">{t("plan.estimation")}</p>
    </details>
  )
}
