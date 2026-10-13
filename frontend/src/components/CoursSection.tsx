import type { ReactNode } from "react"
import { Link } from "react-router-dom"

import type { CoursSectionData, CoursSectionExerciceItem } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { SolutionToggle } from "@/components/SolutionToggle"
import { CoursRegleBox } from "@/components/CoursRegleBox"
import { CoursExempleResoluSteps } from "@/components/CoursExempleResoluSteps"
import { CoursErreurCard } from "@/components/CoursErreurCard"
import { Badge } from "@/components/ui/badge"
import { t } from "@/lib/i18n"

/** Libellés partagés entre le sommaire (CoursSommaire) et les titres de section ci-dessous - "short" pour une pastille compacte, "full" pour le titre en page. Jamais d'entrée pour "accroche" : ce n'est pas une section navigable, juste le texte d'ouverture. */
export const COURS_SECTION_LABELS: Partial<Record<CoursSectionData["type"], { short: string; full: string }>> = {
  // Des accesseurs plutôt que des chaînes : le libellé suit la langue au moment où il est lu.
  prerequis: { get short() { return t("cs.prerequis") }, get full() { return t("cs.prerequis") } },
  regle: { get short() { return t("cs.regle") }, get full() { return t("cs.regle") } },
  exemple_resolu: { get short() { return t("cs.exemple_resolu") }, get full() { return t("cs.exemple_resolu") } },
  erreurs_classiques: { get short() { return t("cs.erreurs_classiques") }, get full() { return t("cs.erreurs_classiques") } },
  exercices_application: { get short() { return t("cs.exercices_court") }, get full() { return t("cs.exercices_long") } },
  synthese: { get short() { return t("cs.synthese_court") }, get full() { return t("cs.synthese_long") } },
}

function CoursExerciceApplicationItem({ item, index }: { item: CoursSectionExerciceItem; index: number }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <p className="font-medium">{t("ed.exercice_n", { n: item.numero ?? index + 1 })}</p>
        {item.difficulte && <Badge variant="outline" className="capitalize">{item.difficulte}</Badge>}
      </div>
      <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
        <EpreuveMarkdown markdown={item.enonce_markdown} />
      </div>
      {item.solution_markdown && (
        <SolutionToggle>
          <EpreuveMarkdown markdown={item.solution_markdown} />
        </SolutionToggle>
      )}
    </div>
  )
}

/**
 * Rend une section de Cours.sections_breakdown() avec l'habillage propre à son type -
 * contrairement à l'ancien pipeline (content_markdown aplati passé tel quel à
 * EpreuveMarkdown), où règle/exemple résolu/erreurs classiques n'avaient pas plus de
 * poids visuel qu'un paragraphe. `id={section.type}` sert d'ancre au sommaire
 * (CoursSommaire) - un Cours ne porte jamais deux sections du même type.
 *
 * `pied` : ce que le lecteur ajoute en bas de section (outils d'étude : compris, signet,
 * note) - jamais rendu pour l'accroche, qui n'est pas une section navigable.
 */
export function CoursSection({ section, pied }: { section: CoursSectionData; pied?: ReactNode }) {
  if (section.type === "accroche") {
    return (
      <div className="font-display text-xl italic leading-relaxed text-justify text-foreground">
        <EpreuveMarkdown markdown={section.body_markdown} />
      </div>
    )
  }

  const label = COURS_SECTION_LABELS[section.type]

  return (
    // scroll-mt-36 sous `lg` : l'ancre doit passer sous le Header (72 px) ET la barre de pastilles
    // du sommaire (≈ 57 px, voir SommaireNav) ; au-delà, seule la sidebar existe, 24 suffit.
    <section id={section.type} className="scroll-mt-36 lg:scroll-mt-24">
      {label && <h2 className="mb-3 font-display text-xl font-semibold">{label.full}</h2>}

      {section.type === "prerequis" && (
        <ul className="not-prose flex flex-col gap-1.5">
          {section.items.map((item, index) => (
            <li key={index} className="flex items-center gap-1.5 text-sm">
              <span className="text-muted-foreground" aria-hidden="true">•</span>
              {item.cours_slug ? (
                <Link to={`/cours/${item.cours_slug}`} className="font-medium text-primary hover:underline">
                  <EpreuveMarkdown markdown={item.label} />
                </Link>
              ) : (
                <EpreuveMarkdown markdown={item.label} />
              )}
            </li>
          ))}
        </ul>
      )}

      {section.type === "regle" && <CoursRegleBox {...section} />}
      {section.type === "exemple_resolu" && <CoursExempleResoluSteps {...section} />}

      {section.type === "erreurs_classiques" && (
        <div className="flex flex-col gap-3">
          {section.items.map((item, index) => (
            <CoursErreurCard key={index} {...item} />
          ))}
        </div>
      )}

      {section.type === "exercices_application" && (
        <div className="flex flex-col gap-6">
          {section.items.map((item, index) => (
            <CoursExerciceApplicationItem key={index} item={item} index={index} />
          ))}
        </div>
      )}

      {/* Pas de `not-prose` sur la carte : il désactiverait la typographie pour tout le
          sous-arbre, y compris le `prose` juste en dessous, qu'un `prose` imbriqué ne
          réactive jamais (voir l'explication détaillée dans CoursRegleBox) - or "Ce
          qu'il faut retenir" est justement une liste à puces, qui perdait retrait et
          puces. Le `not-prose` du <ul> des prérequis plus haut reste légitime, lui :
          rien sous cet élément ne réclame la typographie de prose. */}
      {section.type === "synthese" && (
        <div className="rounded-lg border border-border bg-muted/40 p-4">
          <div className="prose prose-neutral max-w-none dark:prose-invert">
            <EpreuveMarkdown markdown={section.body_markdown} />
          </div>
        </div>
      )}

      {pied}
    </section>
  )
}
