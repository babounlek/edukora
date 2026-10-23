import { useEffect, useId, useRef } from "react"
import { Link } from "react-router-dom"

import { LivreOuvert } from "@/components/guides/LivreOuvert"
import { Button } from "@/components/ui/button"
import { ciblePresente, dialogueOuvert, mettreEnEvidence } from "@/lib/guides/cibles"
import { allerALEtape, fermerGuide, type GuideOuvert } from "@/lib/guides/etat"
import { etapesEffectives } from "@/lib/guides/moteur"
import type { DefinitionGuide } from "@/lib/guides/types"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le déroulé d'un guide à plusieurs étapes (le tutoriel de bienvenue), dans une carte
 * posée au bas de l'écran.
 *
 * Elle ne BLOQUE rien : pas de voile, pas de piège à focus, la page derrière reste
 * utilisable (`aria-modal="false"`). Sur téléphone, elle prend la largeur de l'écran et se
 * pose juste au-dessus de la barre d'onglets (`--bottom-tab-bar`, voir BottomTabBar) ; sur
 * grand écran, elle se met en coin. Elle se ferme à tout moment : « Passer », Échap, ou en
 * quittant la page.
 */
export function GuideRunner({ guide, ouvert }: { guide: DefinitionGuide; ouvert: GuideOuvert }) {
  useI18n()
  const titreId = useId()
  const texteId = useId()
  const carteRef = useRef<HTMLElement>(null)

  // Les étapes dont la cible obligatoire manque sont sautées (voir etapesEffectives). Relu à
  // chaque rendu : la page peut avoir changé depuis l'ouverture (données arrivées, bloc replié).
  const effectives = etapesEffectives(guide, ciblePresente)
  const trouvee = effectives.findIndex((etape) => guide.etapes.indexOf(etape) >= ouvert.etape)
  const position = trouvee === -1 ? Math.max(0, effectives.length - 1) : trouvee
  const etape = effectives[position] ?? effectives[effectives.length - 1]
  const derniere = position >= effectives.length - 1

  // Mise en évidence de la cible de l'étape, retirée au changement d'étape et à la fermeture.
  const cible = etape?.cible
  useEffect(() => mettreEnEvidence(cible), [cible])

  // Un guide demandé à la main reçoit le focus (le clavier et le lecteur d'écran y arrivent) et
  // le rend à l'endroit d'où il vient en se fermant. Un guide qui s'est montré SEUL ne le prend
  // pas : il ne doit pas arracher le focus à quelqu'un qui est en train de faire autre chose.
  useEffect(() => {
    if (!ouvert.explicite) return
    const origine = document.activeElement instanceof HTMLElement ? document.activeElement : null
    carteRef.current?.focus()
    return () => {
      if (origine?.isConnected) origine.focus()
    }
  }, [ouvert.explicite])

  // Échap ferme, sauf si une fenêtre modale (code PIN, menu) est ouverte au-dessus : c'est
  // elle qui doit recevoir la touche.
  useEffect(() => {
    function surTouche(evenement: KeyboardEvent) {
      if (evenement.key !== "Escape" || dialogueOuvert()) return
      fermerGuide(ouvert.explicite ? undefined : "ignore")
    }
    document.addEventListener("keydown", surTouche)
    return () => document.removeEventListener("keydown", surTouche)
  }, [ouvert.explicite])

  if (!etape) return null

  function suivant() {
    if (derniere) {
      fermerGuide("termine")
      return
    }
    allerALEtape(guide.etapes.indexOf(effectives[position + 1]))
  }

  function precedent() {
    if (position > 0) allerALEtape(guide.etapes.indexOf(effectives[position - 1]))
  }

  return (
    <section
      ref={carteRef}
      role="dialog"
      aria-modal="false"
      aria-labelledby={titreId}
      aria-describedby={texteId}
      tabIndex={-1}
      className="animate-fade-up fixed inset-x-0 bottom-[var(--bottom-tab-bar,0px)] z-40 p-3 outline-none sm:inset-x-auto sm:bottom-[calc(var(--bottom-tab-bar,0px)+1rem)] sm:right-4 sm:w-[25rem] sm:p-0"
    >
      <div className="rounded-2xl border border-border bg-card p-4 text-card-foreground shadow-lg">
        <div className="flex items-center gap-2 text-primary">
          <LivreOuvert />
          <p className="text-xs font-semibold uppercase tracking-wide">{t("guide.region")}</p>
          <p className="ml-auto text-xs tabular-nums text-muted-foreground">
            {t("guide.etape", { n: position + 1, total: effectives.length })}
          </p>
        </div>
        {/* Annoncé à chaque changement d'étape par les lecteurs d'écran. */}
        <div aria-live="polite" aria-atomic="true">
          <h2 id={titreId} className="mt-3 font-display text-lg font-semibold leading-snug">
            {t(etape.titre)}
          </h2>
          <p id={texteId} className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
            {t(etape.texte)}
          </p>
        </div>
        {etape.action && (
          <Button asChild variant="outline" className="mt-3 min-h-11 w-full">
            <Link to={etape.action.to} onClick={() => fermerGuide("termine")}>
              {t(etape.action.label)}
            </Link>
          </Button>
        )}
        <div className="mt-4 flex items-center gap-2">
          <Button
            type="button"
            variant="ghost"
            className="min-h-11 px-3 text-muted-foreground"
            onClick={() => fermerGuide(ouvert.explicite ? undefined : "ignore")}
          >
            {t("guide.passer")}
          </Button>
          <div className="ml-auto flex items-center gap-2">
            {position > 0 && (
              <Button type="button" variant="outline" className="min-h-11" onClick={precedent}>
                {t("guide.precedent")}
              </Button>
            )}
            <Button type="button" className="min-h-11" onClick={suivant}>
              {derniere ? t("guide.terminer") : t("guide.suivant")}
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
