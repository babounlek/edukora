import { Link } from "react-router-dom"

import type { CoursSectionData, CoursSectionExerciceItem } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { SolutionToggle } from "@/components/SolutionToggle"
import { CoursRegleBox } from "@/components/CoursRegleBox"
import { CoursExempleResoluSteps } from "@/components/CoursExempleResoluSteps"
import { CoursErreurCard } from "@/components/CoursErreurCard"
import { Badge } from "@/components/ui/badge"

/** Libellés partagés entre le sommaire (CoursSommaire) et les titres de section ci-dessous - "short" pour une pastille compacte, "full" pour le titre en page. Jamais d'entrée pour "accroche" : ce n'est pas une section navigable, juste le texte d'ouverture. */
export const COURS_SECTION_LABELS: Partial<Record<CoursSectionData["type"], { short: string; full: string }>> = {
  prerequis: { short: "Prérequis", full: "Prérequis" },
  regle: { short: "La règle", full: "La règle" },
  exemple_resolu: { short: "Exemple résolu", full: "Exemple résolu" },
  erreurs_classiques: { short: "Erreurs classiques", full: "Erreurs classiques" },
  exercices_application: { short: "Exercices", full: "Exercices d'application" },
  synthese: { short: "À retenir", full: "Ce qu'il faut retenir" },
}

function CoursExerciceApplicationItem({ item, index }: { item: CoursSectionExerciceItem; index: number }) {
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <p className="font-medium">Exercice {item.numero ?? index + 1}</p>
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
 */
export function CoursSection({ section }: { section: CoursSectionData }) {
  if (section.type === "accroche") {
    return (
      <div className="font-display text-xl italic leading-relaxed text-foreground">
        <EpreuveMarkdown markdown={section.body_markdown} />
      </div>
    )
  }

  const label = COURS_SECTION_LABELS[section.type]

  return (
    <section id={section.type} className="scroll-mt-24">
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

      {section.type === "synthese" && (
        <div className="not-prose rounded-lg border border-border bg-muted/40 p-4">
          <div className="prose prose-neutral max-w-none dark:prose-invert">
            <EpreuveMarkdown markdown={section.body_markdown} />
          </div>
        </div>
      )}
    </section>
  )
}
