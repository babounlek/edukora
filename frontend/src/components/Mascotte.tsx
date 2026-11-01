import { useEffect, useMemo, useState } from "react"

import { cn } from "@/lib/utils"
import { trackEvent } from "@/lib/analytics"
import { MascotteDessin } from "@/components/MascotteDessin"
import {
  humeurMascotte, MASCOTTE_ACTIVE, phraseMascotte, situationMascotte, VARIANTES_MASCOTTE, type ContexteMascotte,
} from "@/lib/mascotte"
import { t, useI18n } from "@/lib/i18n"
import { lireSouvenir, memoriserPresentee, memoriserSouvenir, pasEncorePresentee } from "@/lib/memoireMascotte"
import { useMediaQuery } from "@/lib/useMediaQuery"

/** Vitesse à laquelle la phrase « sort de sa bouche » : une lettre toutes les 28 ms, une phrase en moins de 2 s. */
const MS_PAR_LETTRE = 28

/**
 * La mascotte de l'écran de résultat : le livre du logo devient un petit personnage coiffé de la toque. Il respire,
 * cligne des yeux, saute de joie ou encourage selon le résultat, et dit une phrase courte ; un toucher le fait
 * sauter et passe à une autre variante. Du SVG animé en CSS (voir .mascotte-* dans index.css) : aucune image, aucune
 * bibliothèque, aucun son - rien de plus à télécharger. Le dessin est décoratif pour les lecteurs d'écran, qui lisent
 * la phrase. Ne rend rien quand MASCOTTE_ACTIVE est faux.
 */
export function Mascotte({ contexte: contexteBrut, className }: { contexte: ContexteMascotte; className?: string }) {
  useI18n()
  // Ce que Kora savait AVANT ce quiz : lu une fois au montage, avant que l'effet plus bas n'écrive le nouveau résultat.
  const [souvenir] = useState(() => lireSouvenir())
  const [premiereFois] = useState(pasEncorePresentee)
  const contexte = useMemo(() => ({ souvenir, ...contexteBrut }), [souvenir, contexteBrut])
  const situation = situationMascotte(contexte)
  // Le tirage est fait une fois au montage : un re-rendu ne doit pas changer la phrase sous les yeux de l'élève.
  const [depart] = useState(() => Math.floor(Math.random() * VARIANTES_MASCOTTE))
  const [touches, setTouches] = useState(0)
  const mouvementReduit = useMediaQuery("(prefers-reduced-motion: reduce)")
  const [lettres, setLettres] = useState(0)
  const humeur = humeurMascotte(situation)
  const rang = (depart + touches) % VARIANTES_MASCOTTE
  // Au milieu de la tranche [rang/N, (rang+1)/N[ : le tirage de phraseMascotte retombe sur la variante `rang`.
  const phrase = phraseMascotte(situation, contexte, (rang + 0.5) / VARIANTES_MASCOTTE)
  // La première fois, Kora se présente (une seule fois par navigateur) avant sa phrase.
  const dite = premiereFois && touches === 0 ? `${t("mascotte.intro")} ${phrase}` : phrase

  useEffect(() => {
    if (!MASCOTTE_ACTIVE) return
    memoriserPresentee()
    memoriserSouvenir(contexteBrut.pourcentage)
    // Une seule écriture, au montage : le résultat de ce quiz devient le « dernier » du suivant.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // La voix, sans son : la phrase s'écrit pendant que la bouche bouge, comme si elle la disait. Mouvement réduit : tout d'un coup.
  useEffect(() => {
    if (!MASCOTTE_ACTIVE || mouvementReduit) return
    setLettres(0)
    const minuteur = setInterval(() => setLettres((n) => n + 1), MS_PAR_LETTRE)
    return () => clearInterval(minuteur)
  }, [dite, mouvementReduit])
  useEffect(() => {
    if (lettres >= dite.length) setLettres(dite.length)
  }, [lettres, dite])
  const parle = !mouvementReduit && lettres < dite.length
  const visible = mouvementReduit ? dite : dite.slice(0, lettres)
  if (!MASCOTTE_ACTIVE) return null

  return (
    <div
      data-testid="mascotte"
      data-situation={situation}
      className={cn("flex items-center gap-3 rounded-2xl border border-border bg-card p-3 shadow-xs", className)}
    >
      <button
        type="button"
        onClick={() => {
          setTouches((n) => n + 1)
          trackEvent("mascotte_touchee", { surface: "resultat", situation })
        }}
        aria-label={t("mascotte.toucher")}
        className="shrink-0 cursor-pointer rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
      >
        <MascotteDessin humeur={humeur} parle={parle} saut={touches} />
      </button>
      {/* La bulle : une queue vers la mascotte. Le texte entier est lu tel quel par les lecteurs d'écran ; le texte qui s'écrit est décoratif. */}
      <p className="relative min-w-0 flex-1 rounded-2xl bg-muted/60 px-3 py-2 text-sm font-medium leading-snug before:absolute before:-left-1.5 before:top-1/2 before:size-3 before:-translate-y-1/2 before:rotate-45 before:rounded-sm before:bg-muted/60 before:content-['']">
        <span className="sr-only">{dite}</span>
        <span aria-hidden="true" className="relative block min-h-[2.75rem] sm:min-h-0">
          {visible}
          {parle && <span className="mascotte-curseur" />}
        </span>
      </p>
    </div>
  )
}
