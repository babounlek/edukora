import { BookMarked } from "lucide-react"

import type { CoursSectionRegle } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"

type CoursRegleBoxProps = Omit<CoursSectionRegle, "type">

/**
 * Encadré fort pour la section "La règle" d'un Cours - le cœur du cours, distinct de
 * Callout (bandeau plein plutôt que bordure gauche fine, pour ne pas se confondre avec
 * un simple "Conseil").
 *
 * Pas de `not-prose` sur le conteneur, et ce n'est pas un oubli : les sélecteurs de
 * @tailwindcss/typography se terminent tous par
 * `:not(:where([class~="not-prose"], [class~="not-prose"] *))`, donc un `prose`
 * imbriqué sous un `not-prose` NE réactive PAS la typographie - tout le sous-arbre
 * reste sans marges ni puces (constaté : `<p>` à `margin: 0px` dans cet encadré). Cet
 * habillage n'est jamais rendu sous un ancêtre `.prose` (CoursReaderPage et
 * CoursDetailPage rendent CoursSection sous un `<article>`/`<div>` nu), le `not-prose`
 * n'était donc que défensif : il ne protégeait rien et cassait tout.
 */
export function CoursRegleBox({ titre, body_markdown, formule_markdown, variantes }: CoursRegleBoxProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-primary/30">
      <div className="flex items-center gap-2 bg-primary px-4 py-2.5 text-primary-foreground">
        <BookMarked className="size-4 shrink-0" aria-hidden="true" />
        <h2 className="font-display text-base font-semibold">{titre}</h2>
      </div>
      <div className="flex flex-col gap-4 bg-primary/5 px-4 py-4">
        {body_markdown && (
          <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
            <EpreuveMarkdown markdown={body_markdown} />
          </div>
        )}
        {formule_markdown && (
          <div className="prose prose-neutral max-w-none overflow-x-auto rounded-lg border border-primary/20 bg-card px-4 py-3 text-center dark:prose-invert">
            <EpreuveMarkdown markdown={formule_markdown} />
          </div>
        )}
        {variantes.length > 0 && (
          <div className="flex flex-col gap-3">
            {variantes.map((variante, index) => (
              <div key={index} className="border-l-2 border-primary/30 pl-3">
                {variante.nom && <p className="text-sm font-semibold">{variante.nom}</p>}
                {variante.quand_utiliser && (
                  <p className="text-sm italic text-muted-foreground">Quand l'utiliser : {variante.quand_utiliser}</p>
                )}
                {/* prose-sm : une variante est un aparté, son corps doit rester à la même taille
                    que le nom et le "Quand l'utiliser" ci-dessus (text-sm), pas repasser au corps
                    de texte plein de la règle. */}
                <div className="prose prose-sm prose-neutral max-w-none text-justify dark:prose-invert">
                  <EpreuveMarkdown markdown={variante.body_markdown} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
