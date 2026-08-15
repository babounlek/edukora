import { AlertTriangle, CircleCheck, CircleHelp } from "lucide-react"

import type { CoursSectionErreurItem } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"

/** Carte triptyque erreur -> pourquoi c'est faux -> correction, un rendu par item de la section "Erreurs classiques" - regroupe visuellement les 3 volets, séparés en simples "###" successifs dans le Markdown aplati. */
export function CoursErreurCard({ erreur_markdown, pourquoi_faux, correction_markdown }: CoursSectionErreurItem) {
  return (
    <div className="not-prose flex flex-col divide-y divide-border overflow-hidden rounded-lg border border-destructive/30">
      <div className="flex items-start gap-2 bg-destructive/10 px-3.5 py-2.5 text-sm">
        <AlertTriangle className="mt-0.5 size-4 shrink-0 text-destructive" aria-hidden="true" />
        <div className="prose prose-neutral max-w-none dark:prose-invert">
          <EpreuveMarkdown markdown={erreur_markdown} />
        </div>
      </div>
      {pourquoi_faux && (
        <div className="flex items-start gap-2 bg-warning/10 px-3.5 py-2.5 text-sm">
          <CircleHelp className="mt-0.5 size-4 shrink-0 text-warning" aria-hidden="true" />
          <div className="prose prose-neutral max-w-none dark:prose-invert">
            <EpreuveMarkdown markdown={pourquoi_faux} />
          </div>
        </div>
      )}
      {correction_markdown && (
        <div className="flex items-start gap-2 bg-success/10 px-3.5 py-2.5 text-sm">
          <CircleCheck className="mt-0.5 size-4 shrink-0 text-success" aria-hidden="true" />
          <div className="prose prose-neutral max-w-none dark:prose-invert">
            <EpreuveMarkdown markdown={correction_markdown} />
          </div>
        </div>
      )}
    </div>
  )
}
