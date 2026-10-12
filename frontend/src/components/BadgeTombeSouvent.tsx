import { Star } from "lucide-react"

import type { CoursTombeSouvent } from "@/api/types"
import { capitaliserTheme } from "@/lib/utils"

/**
 * « Tombé dans 8 épreuves sur 10 » : le repère des cours qui reviennent le plus à l'examen (voir
 * catalog.FrequenceCours). Le fait, pas un ordre : le chiffre se vérifie, « à lire absolument »
 * serait une promesse. Même teinte dorée que l'étoile du parcours. Le thème dont le cours hérite la
 * fréquence est en infobulle - c'est lui, pas le cours, que les épreuves ont réellement posé.
 */
export function BadgeTombeSouvent({ tombeSouvent }: { tombeSouvent: CoursTombeSouvent }) {
  return (
    <span
      title={`Thème : ${capitaliserTheme(tombeSouvent.theme)}`}
      className="inline-flex items-center gap-1 rounded-md bg-gold/15 px-2 py-0.5 text-xs font-medium text-gold-text"
    >
      <Star className="size-3" fill="currentColor" aria-hidden="true" />
      Tombé dans {tombeSouvent.nb_epreuves} épreuves sur {tombeSouvent.nb_sessions}
    </span>
  )
}
