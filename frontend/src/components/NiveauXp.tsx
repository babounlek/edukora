import { Medal } from "lucide-react"

import type { NiveauXp as NiveauXpDonnees } from "@/api/types"
import { libelleNiveau, partVersSuivant, phraseNiveau } from "@/lib/niveau"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

const PASTILLE = "inline-flex items-center gap-1 whitespace-nowrap rounded-full bg-gold/15 px-2.5 py-0.5 text-xs font-semibold text-gold-text"

/**
 * Le niveau de l’élève et ce qui reste jusqu’au suivant. `compact` : une pastille d’une ligne pour la ligne du jour de
 * l’accueil ; sinon la barre et la phrase, pour l’écran de fin de quiz où l’élève a le temps de lire.
 * Un niveau ne se perd jamais (voir quiz.xp.niveau_du_profil) : rien ici ne parle de baisse.
 *
 * `onDetail` (pastille seulement) : la pastille devient un bouton, et l'appelant affiche la phrase « Encore n points
 * pour devenir X ». Elle n'existait qu'en infobulle (`title`), donc jamais sur un téléphone.
 */
export function NiveauXp({
  niveau, compact = false, onDetail, className,
}: { niveau: NiveauXpDonnees; compact?: boolean; onDetail?: (phrase: string) => void; className?: string }) {
  useI18n()
  const phrase = phraseNiveau(niveau)

  if (compact) {
    const contenu = (
      <>
        <Medal className="size-3.5" aria-hidden="true" />
        {libelleNiveau(niveau)}
      </>
    )
    if (onDetail) {
      return (
        // -my-1.5 py-1.5 + min-h-9 : une cible tactile de 36 px sans épaissir la ligne (même recette que RythmeRapide).
        <button type="button" onClick={() => onDetail(phrase)} title={phrase} className={cn("-my-1.5 flex min-h-9 items-center py-1.5", className)}>
          <span className={PASTILLE}>{contenu}</span>
        </button>
      )
    }
    return (
      <span className={cn(PASTILLE, className)} title={phrase}>
        {contenu}
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
      <p className="mt-1.5 text-xs text-muted-foreground">{phrase}</p>
    </div>
  )
}
