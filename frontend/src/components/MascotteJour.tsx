import { useEffect, useState } from "react"

import type { EtatXp, SerieDeJours } from "@/api/types"
import { MascotteDessin } from "@/components/MascotteDessin"
import { MASCOTTE_ACTIVE, phraseJourMascotte, situationJourMascotte } from "@/lib/mascotte"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/** Combien de temps sa bouche bouge après un toucher (ms) : le temps de « dire » la phrase. */
const MS_PAROLE = 1400

/**
 * La mascotte de l'accueil, dans la ligne de l'objectif du jour : un petit personnage qui respire et cligne des yeux.
 * Rien ne s'écrit de lui-même (la tête de l'accueil porte déjà la phrase du coach, et le bouton « Commencer » doit
 * rester au-dessus du pli) : un toucher la fait parler, avec un rappel simple tiré de l'objectif et de la série.
 * Le rappel apparaît sur sa propre ligne, sous la ligne du jour (voir LigneJour). Ne rend rien si MASCOTTE_ACTIVE est faux.
 */
export function MascotteJour({
  etat, serie, rappel, onRappel,
}: {
  etat: EtatXp
  serie: SerieDeJours
  /** Le rappel affiché (null tant que l'élève n'a pas touché la mascotte) : l'état vit dans LigneJour pour qu'elle le range sur sa ligne. */
  rappel: string | null
  onRappel: (phrase: string | null) => void
}) {
  useI18n()
  const [touches, setTouches] = useState(0)
  const [parle, setParle] = useState(false)
  useEffect(() => {
    if (!parle) return
    const minuteur = setTimeout(() => setParle(false), MS_PAROLE)
    return () => clearTimeout(minuteur)
  }, [parle])
  if (!MASCOTTE_ACTIVE) return null
  const situation = situationJourMascotte(etat, serie)

  function toucher() {
    setTouches((n) => n + 1)
    setParle(true)
    onRappel(phraseJourMascotte(situation, etat, serie, (touches % 2) / 2 + 0.01))
  }

  return (
    <button
      type="button"
      onClick={toucher}
      aria-label={t("mascotte.toucher_jour")}
      aria-expanded={rappel !== null}
      data-situation={situation}
      className={cn(
        "-my-2 shrink-0 cursor-pointer rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring",
      )}
    >
      <MascotteDessin humeur={situation === "reste" || situation === "debut" ? "content" : "fete"} parle={parle} saut={touches} taille={40} />
    </button>
  )
}
