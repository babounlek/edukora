import { BookMarked } from "lucide-react"

import type { CoursSectionRegle } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"

type CoursRegleBoxProps = Omit<CoursSectionRegle, "type">

/** Encadré fort pour la section "La règle" d'un Cours - le cœur du cours, distinct de Callout (bandeau plein plutôt que bordure gauche fine, pour ne pas se confondre avec un simple "Conseil"). */
export function CoursRegleBox({ titre, body_markdown, formule_markdown, variantes }: CoursRegleBoxProps) {
  return (
    <div className="not-prose overflow-hidden rounded-xl border border-primary/30">
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
                <div className="prose prose-neutral max-w-none text-justify dark:prose-invert">
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
