import type { CoursSectionExempleResolu } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"

type CoursExempleResoluStepsProps = Omit<CoursSectionExempleResolu, "type">

/**
 * Étapes de la section "Exemple résolu" en stepper numéroté, plutôt qu'en "**Étape N**"
 * en gras plat (habillage précédent, hérité du Markdown aplati).
 *
 * Pas de `not-prose` sur le conteneur : il désactiverait la typographie pour tout le
 * sous-arbre, y compris les `prose` imbriqués ci-dessous, qu'un `prose` ne réactive
 * jamais (voir l'explication détaillée dans CoursRegleBox).
 */
export function CoursExempleResoluSteps({ enonce_markdown, etapes, conclusion_markdown }: CoursExempleResoluStepsProps) {
  return (
    <div className="flex flex-col gap-5">
      {enonce_markdown && (
        <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
          <EpreuveMarkdown markdown={enonce_markdown} />
        </div>
      )}
      {etapes.length > 0 && (
        <ol className="flex flex-col gap-4">
          {etapes.map((etape, index) => (
            <li key={index} className="relative flex gap-3">
              {index < etapes.length - 1 && (
                <span className="absolute left-3.5 top-8 h-[calc(100%-0.5rem)] w-px bg-border" aria-hidden="true" />
              )}
              <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                {index + 1}
              </span>
              <div className="flex flex-1 flex-col gap-1.5 pb-2 pt-0.5">
                {etape.action && (
                  <div className="font-medium [&_p]:m-0">
                    <EpreuveMarkdown markdown={etape.action} />
                  </div>
                )}
                {etape.justification && (
                  <div className="text-sm italic text-muted-foreground [&_p]:m-0">
                    <EpreuveMarkdown markdown={etape.justification} />
                  </div>
                )}
                {/* Taille de corps pleine (pas prose-sm) : c'est le résultat de l'étape, souvent
                    une formule, qu'on ne veut pas rapetisser. Pas de `prose-p:my-*` non plus
                    pour compenser le padding serré (px-3 py-2) - cf. CoursErreurCard : un tel
                    override écraserait le reset first/last-child du plugin et ajouterait au
                    contraire de la marge au cas courant (un seul bloc, qui calcule 0). */}
                {etape.resultat_markdown && (
                  <div className="prose prose-neutral max-w-none rounded-md border border-border bg-muted/40 px-3 py-2 dark:prose-invert">
                    <EpreuveMarkdown markdown={etape.resultat_markdown} />
                  </div>
                )}
                {etape.body_markdown && (
                  <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
                    <EpreuveMarkdown markdown={etape.body_markdown} />
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}
      {conclusion_markdown && (
        <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
          <EpreuveMarkdown markdown={conclusion_markdown} />
        </div>
      )}
    </div>
  )
}
