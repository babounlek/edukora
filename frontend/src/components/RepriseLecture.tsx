import { useEffect, useState, type RefObject } from "react"
import { BookOpenCheck, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { lireReprise, oublierReprise, PART_MIN, retenirReprise, type Reprise } from "@/lib/repriseLecture"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/** Les sections du cours sous `article`, dans l'ordre : ce sont elles qui portent une ancre (voir CoursSection). */
function sectionsDe(article: HTMLElement): HTMLElement[] {
  return Array.from(article.querySelectorAll<HTMLElement>("section[id]"))
}

/**
 * « Tu en étais à "Exemple résolu" » : en rouvrant un cours commencé, l'élève retrouve sa section d'un toucher au lieu de
 * tout redéfiler. Le même composant RETIENT la position pendant la lecture (la section sous le point de lecture, le même
 * que BarreLecture : un tiers de la hauteur de l'écran) et la PROPOSE à l'ouverture. Proposée, jamais imposée : sauter tout
 * seul au milieu d'une page désoriente, et l'élève peut vouloir relire depuis le début.
 *
 * `cle` : le slug du cours. `pret` : le contenu est affiché (il arrive en asynchrone). `actif` : faux quand la page s'ouvre
 * sur une ancre (lien du carnet) - elle dit déjà où aller.
 */
export function RepriseLecture({
  cibleRef, cle, pret, actif = true, className,
}: {
  cibleRef: RefObject<HTMLElement | null>
  cle: string | undefined
  pret: boolean
  actif?: boolean
  className?: string
}) {
  useI18n()
  const [reprise, setReprise] = useState<(Reprise & { titre: string }) | null>(null)

  // À l'ouverture : y a-t-il une position à proposer, et sa section existe-t-elle encore (un cours peut être réécrit) ?
  useEffect(() => {
    setReprise(null)
    if (!cle || !pret || !actif) return
    const retenue = lireReprise(cle)
    const section = retenue && cibleRef.current ? sectionsDe(cibleRef.current).find((s) => s.id === retenue.section) : null
    if (!retenue || !section) return
    setReprise({ ...retenue, titre: section.querySelector("h2")?.textContent?.trim() ?? "" })
  }, [cle, pret, actif, cibleRef])

  // Pendant la lecture : retenir la section en cours. Écrit seulement quand elle change ou que la lecture a avancé de 5 %.
  useEffect(() => {
    if (!cle || !pret) return
    let image = 0
    let derniere = { section: "", part: -1 }
    function relever() {
      image = 0
      const article = cibleRef.current
      if (!article) return
      const rect = article.getBoundingClientRect()
      if (rect.height <= 0) return
      const ligne = window.innerHeight * 0.35
      const part = Math.min(1, Math.max(0, (ligne - rect.top) / rect.height))
      // Tant que l'élève n'a pas dépassé le tout début, on ne touche à rien : ouvrir un cours ne doit pas effacer la
      // position de la dernière fois avant qu'il ait pu la reprendre.
      if (part < PART_MIN) return
      const courante = sectionsDe(article).filter((s) => s.getBoundingClientRect().top <= ligne).pop()
      if (!courante) return
      if (courante.id === derniere.section && Math.abs(part - derniere.part) < 0.05) return
      derniere = { section: courante.id, part }
      retenirReprise(cle!, courante.id, part)
    }
    function planifier() {
      if (!image) image = requestAnimationFrame(relever)
    }
    window.addEventListener("scroll", planifier, { passive: true })
    return () => {
      window.removeEventListener("scroll", planifier)
      if (image) cancelAnimationFrame(image)
    }
  }, [cle, pret, cibleRef])

  if (!reprise || !cle) return null

  function reprendre() {
    const id = reprise!.section
    setReprise(null)
    // Après le retrait du bandeau, pas avant : sa disparition remonte toute la page de sa hauteur, et la section visée
    // finissait sous l'en-tête. Deux images : une pour le rendu, une pour la mise en page.
    requestAnimationFrame(() => {
      requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ block: "start", behavior: "smooth" }))
    })
  }

  function recommencer() {
    oublierReprise(cle!)
    setReprise(null)
  }

  return (
    <div className={cn("flex flex-wrap items-center gap-x-3 gap-y-2 rounded-2xl border border-primary/30 bg-primary/5 px-4 py-3", className)}>
      <BookOpenCheck className="size-5 shrink-0 text-primary" aria-hidden="true" />
      <p className="min-w-0 flex-1 text-sm">
        {reprise.titre
          ? t("reprise.texte", { section: reprise.titre, pct: Math.round(reprise.part * 100) })
          : t("reprise.texte_sans_titre", { pct: Math.round(reprise.part * 100) })}
      </p>
      <Button type="button" size="sm" className="min-h-11 rounded-full" onClick={reprendre}>
        {t("reprise.reprendre")}
      </Button>
      <button
        type="button"
        onClick={recommencer}
        aria-label={t("reprise.fermer")}
        className="flex size-11 shrink-0 items-center justify-center rounded-full text-muted-foreground hover:text-foreground"
      >
        <X className="size-4" aria-hidden="true" />
      </button>
    </div>
  )
}
