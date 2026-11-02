import { useState } from "react"
import { Eye, EyeOff, Timer } from "lucide-react"

import { chronoEstMasque, memoriserChronoMasque } from "@/lib/quizChrono"
import { formatDuration } from "@/lib/duration"
import { t } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/**
 * Le compte à rebours d'un quiz chronométré. Se cache d'un clic sans s'arrêter (le serveur garde
 * l'échéance, voir quiz.chrono). Le lecteur d'écran n'entend que deux repères - « une minute » et
 * « temps écoulé » - jamais chaque seconde.
 */
export function ChronoQuiz({ restant, duree }: { restant: number; duree: number }) {
  const [masque, setMasque] = useState(chronoEstMasque)
  const urgent = restant <= 60 && restant > 0
  const fini = restant === 0

  function basculer() {
    const suivant = !masque
    setMasque(suivant)
    memoriserChronoMasque(suivant)
  }

  const annonce = fini ? t("chrono.ecoule_titre") : restant <= 60 && duree > 60 ? t("chrono.une_minute") : ""

  return (
    <div className="flex items-center gap-1.5">
      <span
        role="timer"
        aria-label={t("chrono.restant")}
        className={cn(
          "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-sm font-semibold tabular-nums transition-colors",
          fini
            ? "border-destructive/40 bg-destructive/10 text-destructive"
            : urgent
              ? "animate-pulse border-warning/50 bg-warning/10 text-warning"
              : "border-border bg-muted/40 text-foreground",
        )}
      >
        <Timer className="size-3.5" aria-hidden="true" />
        {masque && !fini ? <span aria-hidden="true">--:--</span> : formatDuration(restant)}
      </span>
      <button
        type="button"
        onClick={basculer}
        aria-pressed={masque}
        aria-label={masque ? t("chrono.afficher") : t("chrono.masquer")}
        title={masque ? t("chrono.afficher") : t("chrono.masquer")}
        className="rounded-full p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
      >
        {masque ? <Eye className="size-4" aria-hidden="true" /> : <EyeOff className="size-4" aria-hidden="true" />}
      </button>
      <span role="status" aria-live="polite" className="sr-only">
        {annonce}
      </span>
    </div>
  )
}
