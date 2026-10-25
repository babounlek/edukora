import { useState } from "react"
import { Volume2, VolumeX } from "lucide-react"

import { definirRetoursActifs, jouerRetour, retoursActifs } from "@/lib/retours"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le même réglage que « Sons et vibrations » du compte (voir InterrupteurRetours), à portée de pouce dans le quiz :
 * l'élève qui révise en classe coupe le son d'un tap, celui qui ne savait pas qu'il y en avait un l'entend dès le
 * premier essai (test élève Guyguy : « les sons sont cachés dans Mon compte »). Une préférence par appareil.
 */
export function BoutonSon({ className }: { className?: string }) {
  useI18n()
  const [actif, setActif] = useState(retoursActifs)

  function basculer() {
    const suivant = !actif
    definirRetoursActifs(suivant)
    setActif(suivant)
    // Un aperçu à l'activation : on entend tout de suite ce que fait le bouton.
    if (suivant) jouerRetour("juste")
  }

  const Icone = actif ? Volume2 : VolumeX
  return (
    <button
      type="button"
      onClick={basculer}
      aria-pressed={actif}
      aria-label={actif ? t("retours.couper") : t("retours.activer")}
      title={actif ? t("retours.couper") : t("retours.activer")}
      className={cn(
        "relative inline-flex size-9 items-center justify-center rounded-full border border-border text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary after:absolute after:-inset-1 after:content-['']",
        className,
      )}
    >
      <Icone className="size-4" aria-hidden="true" />
    </button>
  )
}
