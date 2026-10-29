import { Crown, Timer } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { t } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/**
 * Le badge d'une épreuve inédite, identique dans les listes (carte, ligne) et sur la fiche.
 *
 * Doré pour la famille « inédite ». La mini-inédite s'en distingue par la forme et non par une autre couleur : contour
 * doré plutôt que fond plein, et un chronomètre à la place de la couronne (c'est une version courte). Elle n'est jamais
 * verte : le vert est celui de « Gratuite », et une mini est réservée aux abonnés du cursus.
 */
export function BadgeInedite({ mini = false, className }: { mini?: boolean; className?: string }) {
  if (mini) {
    return (
      <Badge
        variant="outline"
        title={t("ine.mini_aide")}
        className={cn("gap-1 border-gold bg-gold/10 text-gold-text", className)}
      >
        <Timer className="size-3" aria-hidden="true" />
        {t("ine.mini")}
      </Badge>
    )
  }
  return (
    <Badge variant="gold" className={cn("gap-1", className)}>
      <Crown className="size-3" aria-hidden="true" />
      {t("ep.origine_INEDITE")}
    </Badge>
  )
}
