import { Check, Flame, Zap } from "lucide-react"

import type { EtatXp, SerieDeJours } from "@/api/types"
import { cn } from "@/lib/utils"

const INITIALES = ["L", "M", "M", "J", "V", "S", "D"]

/**
 * L'objectif d'XP du jour, la série et la semaine sur UNE ligne fine : de quoi se situer d'un
 * coup d'œil sans repousser le bouton principal sous le pli. Les versions détaillées
 * (ObjectifXp, SemaineDeSerie) servent l'écran de fin de quiz, où l'élève a le temps de lire.
 *
 * Objectif atteint : « Objectif atteint » plutôt que « 35 / 20 XP », qui ressemble à une erreur.
 */
export function LigneJour({ etat, serie }: { etat: EtatXp; serie: SerieDeJours }) {
  const semaine = serie.semaine
  const part = etat.objectif > 0 ? Math.min(100, Math.round((100 * etat.xp) / etat.objectif)) : 0

  return (
    <div className="mb-5 flex flex-wrap items-center justify-between gap-x-6 gap-y-2.5 rounded-2xl border border-border/70 bg-muted/30 px-4 py-2.5">
      <div className="flex items-center gap-2.5 text-sm">
        {etat.atteint ? (
          <Check className="size-4 text-success" aria-hidden="true" />
        ) : (
          <Zap className="size-4 text-gold-text" aria-hidden="true" />
        )}
        <span className={cn("font-semibold", etat.atteint && "text-success")}>
          {etat.atteint ? "Objectif atteint" : `${etat.xp} / ${etat.objectif} points`}
        </span>
        <div
          className="h-1.5 w-16 overflow-hidden rounded-full bg-secondary sm:w-24"
          role="progressbar"
          aria-label="Objectif de points du jour"
          aria-valuemin={0}
          aria-valuemax={etat.objectif}
          aria-valuenow={Math.min(etat.xp, etat.objectif)}
        >
          <div
            className={cn("h-full rounded-full transition-all duration-700", etat.atteint ? "bg-success" : "bg-gold")}
            style={{ width: `${part}%` }}
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* La série ne s'affiche qu'à partir de deux jours (un seul n'est pas encore une
            habitude) et ne culpabilise jamais ; un repos pardonné reste signalé en infobulle. */}
        {serie.jours >= 2 && (
          <span
            className="flex items-center gap-1 whitespace-nowrap text-sm font-semibold"
            title={serie.repos_pris ? "Un jour de repos a été pardonné cette semaine" : undefined}
          >
            <Flame className="size-4 text-warning" aria-hidden="true" />
            {serie.jours} jours de suite
          </span>
        )}
        {semaine && semaine.length === 7 && (
          <ol className="flex gap-1" aria-label="Jours travaillés cette semaine">
            {semaine.map((jour, i) => (
              <li
                key={jour.date}
                role="img"
                aria-label={jour.fait ? "Travaillé" : jour.aujourdhui ? "Aujourd'hui, pas encore" : "Non travaillé"}
                className={cn(
                  "flex size-5 items-center justify-center rounded-full border text-[0.6rem] font-semibold",
                  jour.fait ? "border-gold/50 bg-gold/20 text-gold-text" : "border-border bg-card text-muted-foreground",
                  jour.aujourdhui && !jour.fait && "border-dashed border-primary/60",
                )}
              >
                {jour.fait ? <Check className="size-3" aria-hidden="true" /> : INITIALES[i]}
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  )
}
