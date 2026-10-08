import { Check, Zap } from "lucide-react"

import type { EtatXp } from "@/api/types"
import { cn } from "@/lib/utils"

/**
 * Où en est l'objectif d'XP du jour : une barre qui se remplit, "12 / 20 XP", et une coche
 * une fois atteint. `compact` pour l'en-tête d'un quiz (une seule ligne), sinon la version
 * posée sur l'écran de fin de séance et l'accueil.
 */
/** Points d'un QCM réussi (voir quiz.xp.XP_QCM_JUSTE) : sert à dire l'objectif en bonnes réponses. */
const POINTS_PAR_BONNE_REPONSE = 10

export function ObjectifXp({ etat, compact = false, className }: { etat: EtatXp; compact?: boolean; className?: string }) {
  const part = etat.objectif > 0 ? Math.min(100, Math.round((100 * etat.xp) / etat.objectif)) : 0
  const reponsesRestantes = Math.max(1, Math.ceil((etat.objectif - etat.xp) / POINTS_PAR_BONNE_REPONSE))

  return (
    <div className={cn(compact ? "flex items-center gap-2" : "w-full", className)}>
      <div className={cn("flex items-center justify-between gap-2 text-sm", compact && "shrink-0")}>
        <span className="flex items-center gap-1.5 font-semibold">
          {etat.atteint ? <Check className="size-4 text-success" aria-hidden="true" /> : <Zap className="size-4 text-gold-text" aria-hidden="true" />}
          {compact ? "" : "Objectif du jour"}
        </span>
        <span className={cn("tabular-nums", etat.atteint ? "font-semibold text-success" : "text-muted-foreground")}>
          {etat.xp} / {etat.objectif} points
        </span>
      </div>
      <div
        className={cn("h-2 overflow-hidden rounded-full bg-secondary", compact ? "w-16 sm:w-24" : "mt-2")}
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
      {/* Les points dits en réponses : « 20 points » ne parle à personne, « 2 bonnes réponses »
          si. Un ordre de grandeur (une bonne réponse à un QCM = POINTS_PAR_BONNE_REPONSE, les
          questions ouvertes rapportent moins), d'où « environ ». Pas dans l'en-tête d'un quiz. */}
      {!compact && !etat.atteint && etat.objectif > etat.xp && (
        <p className="mt-1.5 text-xs text-muted-foreground">
          Encore environ {reponsesRestantes} bonne{reponsesRestantes > 1 ? "s" : ""} réponse
          {reponsesRestantes > 1 ? "s" : ""} pour atteindre ton objectif.
        </p>
      )}
    </div>
  )
}
