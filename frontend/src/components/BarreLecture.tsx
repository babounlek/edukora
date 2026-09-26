import { useEffect, useState, type RefObject } from "react"

// Vitesse de lecture d'un contenu scolaire - formules, exemples à suivre au crayon : bien
// en dessous des 230 mots/min d'un texte courant. Un temps annoncé trop court serait
// pire que pas de temps du tout : l'élève se croirait lent.
const MOTS_PAR_MINUTE = 150
// Sous ce volume, "il reste 1 min" n'apprend rien.
const MOTS_MIN_POUR_AFFICHER_LE_TEMPS = 350

/**
 * Le fil de la lecture : une barre fine tout en haut de l'écran, et - seulement sur un
 * contenu assez long pour que ça serve - le temps qu'il reste.
 *
 * La progression se mesure sur `cibleRef` (l'article), pas sur la page : le pied de page,
 * les cours liés et l'étape suivante ne sont pas de la lecture. Le "point de lecture" est à
 * un tiers de la hauteur de l'écran, là où l'œil est vraiment posé, plutôt qu'au bord
 * bas - sinon la barre annonçait 100 % alors que la fin de l'article n'était même pas
 * entrée dans le champ de vision.
 *
 * Aucun état persisté ici : c'est un repère de confort, pas un suivi. Ce que l'élève a
 * réellement compris se déclare, section par section (voir MarquesSection).
 */
export function BarreLecture({
  cibleRef, contenuKey,
}: { cibleRef: RefObject<HTMLElement | null>; contenuKey?: unknown }) {
  const [progression, setProgression] = useState(0)
  const [mots, setMots] = useState(0)

  // Le contenu arrive en asynchrone : on compte les mots une fois rendu, jamais au montage.
  useEffect(() => {
    const t = setTimeout(() => {
      const texte = cibleRef.current?.textContent?.trim() ?? ""
      setMots(texte ? texte.split(/\s+/).length : 0)
    }, 400)
    return () => clearTimeout(t)
  }, [cibleRef, contenuKey])

  useEffect(() => {
    let image = 0
    function calculer() {
      image = 0
      const element = cibleRef.current
      if (!element) return
      const rect = element.getBoundingClientRect()
      if (rect.height <= 0) return
      const ligne = window.innerHeight * 0.35
      const finDePage = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2
      setProgression(finDePage ? 1 : Math.min(1, Math.max(0, (ligne - rect.top) / rect.height)))
    }
    function planifier() {
      if (!image) image = requestAnimationFrame(calculer)
    }
    calculer()
    window.addEventListener("scroll", planifier, { passive: true })
    window.addEventListener("resize", planifier)
    return () => {
      window.removeEventListener("scroll", planifier)
      window.removeEventListener("resize", planifier)
      if (image) cancelAnimationFrame(image)
    }
  }, [cibleRef, contenuKey, mots])

  const pourcent = Math.round(progression * 100)
  const minutes = Math.max(1, Math.ceil((mots * (1 - progression)) / MOTS_PAR_MINUTE))
  const afficherTemps = mots >= MOTS_MIN_POUR_AFFICHER_LE_TEMPS && progression > 0.03 && progression < 0.97

  return (
    <>
      <div
        role="progressbar"
        aria-label="Progression de la lecture"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pourcent}
        className="fixed inset-x-0 top-0 z-50 h-[3px] bg-transparent"
      >
        <div
          className="h-full bg-gradient-to-r from-primary via-primary to-gold transition-[width] duration-150 ease-out motion-reduce:transition-none"
          style={{ width: `${pourcent}%` }}
        />
      </div>
      {afficherTemps && (
        <p
          aria-hidden="true"
          className="pointer-events-none fixed bottom-28 right-4 z-40 rounded-full border border-border bg-background/90 px-3 py-1.5 text-xs font-medium tabular-nums text-muted-foreground shadow-md backdrop-blur-sm lg:bottom-6"
        >
          ≈ {minutes} min restante{minutes > 1 ? "s" : ""} · {pourcent} %
        </p>
      )}
    </>
  )
}
