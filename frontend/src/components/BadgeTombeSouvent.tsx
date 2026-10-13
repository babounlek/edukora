import { Star } from "lucide-react"

import type { CoursTombeSouvent } from "@/api/types"
import { capitaliserTheme } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Tombé dans 8 épreuves sur 10 » : le repère des cours qui reviennent le plus à l'examen (voir
 * catalog.FrequenceCours). Le fait, pas un ordre : le chiffre se vérifie, « à lire absolument »
 * serait une promesse. Même teinte dorée que l'étoile du parcours. Le thème dont le cours hérite la
 * fréquence est en infobulle - c'est lui, pas le cours, que les épreuves ont réellement posé.
 */
export function BadgeTombeSouvent({ tombeSouvent }: { tombeSouvent: CoursTombeSouvent }) {
  useI18n()
  return (
    <span
      title={t("co.theme_titre", { theme: capitaliserTheme(tombeSouvent.theme) })}
      className="inline-flex items-center gap-1 rounded-md bg-gold/15 px-2 py-0.5 text-xs font-medium text-gold-text"
    >
      <Star className="size-3" fill="currentColor" aria-hidden="true" />
      {t("seance.frequence", { n: tombeSouvent.nb_epreuves, total: tombeSouvent.nb_sessions })}
    </span>
  )
}
