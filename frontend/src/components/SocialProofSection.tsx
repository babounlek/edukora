import { useEffect, useState } from "react"
import { Star } from "lucide-react"

import { listTemoignages } from "@/api/endpoints"
import type { Temoignage } from "@/api/types"
import { t, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/** En dessous, la section ne s'affiche pas : un avis seul sur la page fait plus douter qu'aucun. */
export const SEUIL_AVIS_AFFICHES = 3

const NOTE_MAX = 5

/**
 * Preuve sociale publique (page d'accueil catalogue, /tarifs) - voir l'audit UX, reco 8.3.
 * Disparaît silencieusement tant que SEUIL_AVIS_AFFICHES avis ne sont pas publiés depuis l'admin
 * (jamais générés ni fabriqués - voir catalog.models.Temoignage et catalog.avis).
 *
 * Chaque avis a la même forme : la note sur cinq étoiles (les étoiles non obtenues restent visibles, en creux, pour que
 * trois avis de notes différentes s'alignent), le texte, puis l'auteur avec son initiale dans une pastille. Sans
 * visage ni repère, trois cartes de texte se lisaient comme du remplissage (audit visuel de l'accueil, 2026-11-23).
 */
export function SocialProofSection({ fournis, bande = false }: {
  /** Les témoignages déjà reçus par la page (l'accueil les a avec ses chiffres, voir getAccueilVitrine) : la section ne les
   * redemande pas. `null` tant que la page les attend. Sans cette prop, la section les charge elle-même (/tarifs). */
  fournis?: Temoignage[] | null
  /** Sur l'accueil : la section occupe une bande blanche pleine largeur, et ses cartes prennent le fond de la page. */
  bande?: boolean
} = {}) {
  const { langue } = useI18n()
  const [charges, setCharges] = useState<Temoignage[]>([])
  const autonome = fournis === undefined

  useEffect(() => {
    if (!autonome) return
    listTemoignages(langue).then(setCharges).catch(() => {})
  }, [autonome, langue])

  const temoignages = autonome ? charges : (fournis ?? [])

  if (temoignages.length < SEUIL_AVIS_AFFICHES) return null

  const section = (
    <section aria-labelledby="avis-publies-titre" className={cn("mx-auto max-w-5xl px-4 sm:px-6", bande ? "py-12 sm:py-14" : "animate-fade-up py-10")}>
      <h2 id="avis-publies-titre" className={cn("font-display font-semibold", bande ? "mb-6 text-2xl" : "mb-4 text-xl")}>
        {t("avis.section_titre")}
      </h2>
      {/* Sur un téléphone, les trois avis défilent côte à côte (le suivant dépasse du bord, pour qu'on le devine) :
          empilés, ils faisaient un écran et quart à eux seuls. À partir de `sm`, trois colonnes. */}
      <div className="-mx-4 flex snap-x snap-mandatory gap-3 overflow-x-auto px-4 pb-1 [scrollbar-width:none] sm:mx-0 sm:grid sm:grid-cols-3 sm:gap-4 sm:overflow-visible sm:px-0 sm:pb-0 [&::-webkit-scrollbar]:hidden">
        {temoignages.slice(0, 3).map((temoignage) => (
          <figure
            key={temoignage.id}
            className={cn(
              "flex w-[85%] shrink-0 snap-start flex-col rounded-2xl border border-border/70 p-5 sm:w-auto",
              bande ? "bg-background" : "bg-card",
            )}
          >
            {temoignage.note !== null && (
              <div className="mb-3 flex items-center gap-0.5" role="img" aria-label={t("temoignage.note", { n: temoignage.note })}>
                {Array.from({ length: NOTE_MAX }).map((_, index) => (
                  <Star
                    key={index}
                    aria-hidden="true"
                    className={cn("size-4", index < (temoignage.note ?? 0) ? "fill-gold text-gold-text" : "text-border")}
                  />
                ))}
              </div>
            )}
            <blockquote className="text-sm leading-relaxed text-foreground">{temoignage.contenu}</blockquote>
            <figcaption className="mt-auto flex items-center gap-3 pt-4">
              <span
                aria-hidden="true"
                className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary/10 font-display text-base font-semibold text-primary"
              >
                {initiale(temoignage.auteur_nom)}
              </span>
              <span className="min-w-0">
                <span className="block text-sm font-semibold">{temoignage.auteur_nom}</span>
                {temoignage.auteur_description && (
                  <span className="block text-xs text-muted-foreground">{temoignage.auteur_description}</span>
                )}
              </span>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  )

  return bande ? <div className="border-y border-border bg-card">{section}</div> : section
}

/** « Mme Ngono » donne N, « Aïcha M. » donne A : la première lettre du nom, sans la civilité. */
export function initiale(nom: string): string {
  const mots = nom.trim().split(/\s+/).filter(Boolean)
  const sansCivilite = mots.length > 1 && /^(m|mme|mlle|mr|mrs|ms|dr|pr)\.?$/i.test(mots[0]) ? mots.slice(1) : mots
  return (sansCivilite[0]?.[0] ?? "").toLocaleUpperCase()
}
