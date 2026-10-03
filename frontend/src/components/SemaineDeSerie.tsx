import { Check, Flame } from "lucide-react"

import type { SerieDeJours } from "@/api/types"
import { cn } from "@/lib/utils"

const INITIALES = ["L", "M", "M", "J", "V", "S", "D"]

/**
 * La semaine en cours, lundi à dimanche : une case par jour, cochée si l'élève a travaillé
 * (séance terminée ou objectif d'XP atteint, voir quiz.serie). Montre la régularité d'un coup
 * d'œil sans la transformer en compteur qui punit : un jour sans case n'efface rien.
 */
export function SemaineDeSerie({ serie, className }: { serie: SerieDeJours; className?: string }) {
  const semaine = serie.semaine
  if (!semaine || semaine.length !== 7) return null

  return (
    <div className={cn("w-full", className)}>
      <p
        className="flex flex-wrap items-center gap-x-1.5 text-sm font-semibold"
        title={serie.repos_pris ? "Un jour de repos a été pardonné cette semaine" : undefined}
      >
        <Flame className="size-4 shrink-0 text-warning" aria-hidden="true" />
        {/* La série ne s'affiche qu'à partir de deux jours (un seul n'est pas encore une
            habitude) et ne culpabilise jamais. */}
        {serie.jours >= 2 ? `Série de ${serie.jours} jours` : "Ta semaine"}
        {serie.jours >= 2 && !serie.actif_aujourdhui && (
          <span className="text-xs font-normal text-muted-foreground">· ton objectif du jour la prolonge</span>
        )}
      </p>
      <ol className="mt-2 grid grid-cols-7 gap-1.5" aria-label="Jours travaillés cette semaine">
        {semaine.map((jour, i) => (
          <li key={jour.date} className="flex flex-col items-center gap-1 text-[0.7rem] text-muted-foreground">
            <span className={cn(jour.aujourdhui && "font-semibold text-foreground")}>{INITIALES[i]}</span>
            <span
              className={cn(
                "flex size-8 items-center justify-center rounded-full border",
                jour.fait ? "border-gold/50 bg-gold/20 text-gold-text" : "border-border bg-muted/40",
                jour.aujourdhui && !jour.fait && "border-dashed border-primary/60",
              )}
              role="img"
              aria-label={`${jour.fait ? "Travaillé" : jour.aujourdhui ? "Aujourd'hui, pas encore" : "Non travaillé"}`}
            >
              {jour.fait && <Check className="size-4" aria-hidden="true" />}
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}
