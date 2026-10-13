import { WifiOff } from "lucide-react"

import { useEnLigne } from "@/lib/pwa"
import { t, useI18n } from "@/lib/i18n"

/** Bandeau fin sous l'en-tête quand le réseau tombe. Dit ce qui marche encore (ce qui a
 * déjà été lu) plutôt que de laisser l'élève découvrir page par page des chargements qui
 * échouent. Aucun bruit tant que le réseau est là. */
export function BandeauHorsLigne() {
  useI18n()
  const enLigne = useEnLigne()
  if (enLigne) return null
  return (
    <div role="status" className="flex items-center justify-center gap-2 bg-warning/15 px-4 py-2 text-center text-sm">
      <WifiOff className="size-4 shrink-0" aria-hidden="true" />
      <span>{t("gl.hors_ligne")}</span>
    </div>
  )
}
