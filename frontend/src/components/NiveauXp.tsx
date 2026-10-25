import { Medal } from "lucide-react"

import type { NiveauXp as NiveauXpDonnees } from "@/api/types"
import { libelleNiveau, nomNiveau, partVersSuivant, pointsRestants } from "@/lib/niveau"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le niveau de l’élève et ce qui reste jusqu’au suivant. `compact` : une pastille d’une ligne pour la ligne du jour de
 * l’accueil ; sinon la barre et la phrase, pour l’écran de fin de quiz où l’élève a le temps de lire.
 * Un niveau ne se perd jamais (voir quiz.xp.niveau_du_profil) : rien ici ne parle de baisse.
 */
export function NiveauXp({ niveau, compact = false, className }: { niveau: NiveauXpDonnees; compact?: boolean; className?: string }) {
  useI18n()
  const restants = pointsRestants(niveau)

  if (compact) {
    return (
      <span
        className={cn("inline-flex items-center gap-1 whitespace-nowrap rounded-full bg-gold/15 px-2.5 py-0.5 text-xs font-semibold text-gold-text", className)}
        title={restants === null ? t("niveau.sommet", { nom: nomNiveau(niveau.rang) }) : t("niveau.reste", { n: restants, nom: nomNiveau(niveau.rang + 1) })}
      >
        <Medal className="size-3.5" aria-hidden="true" />
        {libelleNiveau(niveau)}
      </span>
    )
  }

  return (
    <div className={cn("w-full", className)}>
      <p className="flex items-center gap-1.5 text-sm font-semibold">
        <Medal className="size-4 text-gold-text" aria-hidden="true" />
        {libelleNiveau(niveau)}
      </p>
      <div
        className="mt-2 h-2 overflow-hidden rounded-full bg-secondary"
        role="progressbar"
        aria-label={t("niveau.aria")}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={partVersSuivant(niveau)}
      >
        <div className="h-full rounded-full bg-gold transition-all duration-700" style={{ width: `${partVersSuivant(niveau)}%` }} />
      </div>
      <p className="mt-1.5 text-xs text-muted-foreground">
        {restants === null ? t("niveau.sommet", { nom: nomNiveau(niveau.rang) }) : t("niveau.reste", { n: restants, nom: nomNiveau(niveau.rang + 1) })}
      </p>
    </div>
  )
}
