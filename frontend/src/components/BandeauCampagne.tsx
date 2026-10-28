import { Tag } from "lucide-react"

import type { Campagne } from "@/api/types"
import { dateLimiteCampagne, nomCampagne, urgenceCampagne } from "@/lib/campagne"
import { t } from "@/lib/i18n"
import { cn, formatAmount } from "@/lib/utils"

interface Props {
  campagne: Campagne
  /** Prix payé par le premier enfant pendant la campagne. */
  prix: number
  /** Prix normal (barré à côté dans la carte de prix, rappelé ici en toutes lettres). */
  prixReference: number
  className?: string
}

/**
 * Bandeau d'une campagne promotionnelle : le nom, la remise, le prix avant/après et la date
 * limite. Composant d'affichage pur - la campagne vient de `useCampagne()` ou de `plan.campagne`,
 * jamais calculée ici (le serveur facture ce qu'il a lui-même calculé).
 */
export function BandeauCampagne({ campagne, prix, prixReference, className }: Props) {
  const urgence = urgenceCampagne(campagne.fin)
  return (
    <div
      role="status"
      className={cn(
        "flex flex-wrap items-center gap-x-3 gap-y-1 rounded-xl border border-gold/40 bg-gold/[0.08] px-4 py-3 text-sm",
        className,
      )}
    >
      <Tag className="size-4 shrink-0 text-gold-text" aria-hidden="true" />
      <p className="font-display font-semibold text-gold-text">
        {t("camp.bandeau_titre", { nom: nomCampagne(campagne), pct: campagne.pourcentage })}
      </p>
      <p className="text-foreground">
        {t("camp.bandeau_prix", {
          prix: formatAmount(prix),
          ref: formatAmount(prixReference),
          date: dateLimiteCampagne(campagne.fin),
        })}
      </p>
      {urgence && <p className="font-medium text-destructive">{urgence}</p>}
    </div>
  )
}
