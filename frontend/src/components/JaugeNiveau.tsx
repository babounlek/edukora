import type { NiveauTheme } from "@/api/types"
import { t, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/** Les quatre crans d'un thème, dans l'ordre où l'élève les franchit (voir quiz.services.niveau_theme côté serveur). */
export const NIVEAUX: NiveauTheme[] = ["decouvert", "en_cours", "solide", "maitrise"]

const TEINTE: Record<NiveauTheme, string> = {
  decouvert: "bg-muted-foreground/60",
  en_cours: "bg-gold",
  solide: "bg-success",
  maitrise: "bg-primary",
}

export function libelleNiveau(niveau: NiveauTheme): string {
  return t(`jauge.${niveau}`)
}

/** Une jauge à quatre crans : les crans atteints sont pleins, le texte dit le cran, pas seulement la couleur. */
export function JaugeNiveau({ niveau, className }: { niveau: NiveauTheme | null | undefined; className?: string }) {
  useI18n()
  if (!niveau) return null
  const atteint = NIVEAUX.indexOf(niveau)
  return (
    <span className={cn("inline-flex items-center gap-1.5 text-xs text-muted-foreground", className)}>
      <span className="inline-flex gap-0.5" aria-hidden="true">
        {NIVEAUX.map((n, i) => (
          <span key={n} className={cn("h-1.5 w-3.5 rounded-full", i <= atteint ? TEINTE[niveau] : "bg-muted")} />
        ))}
      </span>
      {libelleNiveau(niveau)}
    </span>
  )
}

/** « En cours → Solide » : ce que ce quiz a fait avancer. Rien si le cran n'a pas bougé. */
export function ProgressionNiveau({ avant, apres }: { avant: NiveauTheme | null | undefined; apres: NiveauTheme | null | undefined }) {
  useI18n()
  if (!apres) return null
  const monte = avant == null || NIVEAUX.indexOf(apres) > NIVEAUX.indexOf(avant)
  if (!monte) return <JaugeNiveau niveau={apres} />
  return (
    <span className="inline-flex flex-wrap items-center gap-1.5 text-xs font-medium text-success">
      {avant ? `${libelleNiveau(avant)} → ${libelleNiveau(apres)}` : t("jauge.nouveau", { niveau: libelleNiveau(apres) })}
    </span>
  )
}
