import { AlertTriangle, CircleCheck, CircleHelp } from "lucide-react"

import type { CoursSectionErreurItem } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"

/**
 * Carte triptyque erreur -> pourquoi c'est faux -> correction, un rendu par item de la
 * section "Erreurs classiques" - regroupe visuellement les 3 volets, séparés en simples
 * "###" successifs dans le Markdown aplati.
 *
 * Pas de `not-prose` sur le conteneur : il désactiverait la typographie pour tout le
 * sous-arbre, y compris les `prose` imbriqués ci-dessous, qu'un `prose` ne réactive
 * jamais (voir l'explication détaillée dans CoursRegleBox). Chaque volet est en
 * `prose-sm` pour rester à la taille du `text-sm` de sa ligne.
 *
 * Volontairement AUCUN `prose-p:my-*` pour resserrer davantage : un tel override écrase
 * les règles `> :first-child { margin-top: 0 }` / `> :last-child { margin-bottom: 0 }`
 * du plugin, et vient donc s'ajouter au padding du volet. Sans lui, un volet d'un seul
 * paragraphe - le cas courant - calcule `0px / 0px`, exactement comme avant, et seul un
 * volet réellement multi-paragraphe s'aère.
 *
 * `min-w-0` parce que le volet est un enfant flex : sans lui, un tableau large déborde
 * de la carte au lieu de défiler dans son propre conteneur.
 */
export function CoursErreurCard({ erreur_markdown, pourquoi_faux, correction_markdown }: CoursSectionErreurItem) {
  return (
    <div className="flex flex-col divide-y divide-border overflow-hidden rounded-lg border border-destructive/30">
      <div className="flex items-start gap-2 bg-destructive/10 px-3.5 py-2.5 text-sm">
        <AlertTriangle className="mt-0.5 size-4 shrink-0 text-destructive" aria-hidden="true" />
        <div className="prose prose-sm prose-neutral min-w-0 max-w-none dark:prose-invert">
          <EpreuveMarkdown markdown={erreur_markdown} />
        </div>
      </div>
      {pourquoi_faux && (
        <div className="flex items-start gap-2 bg-warning/10 px-3.5 py-2.5 text-sm">
          <CircleHelp className="mt-0.5 size-4 shrink-0 text-warning" aria-hidden="true" />
          <div className="prose prose-sm prose-neutral min-w-0 max-w-none dark:prose-invert">
            <EpreuveMarkdown markdown={pourquoi_faux} />
          </div>
        </div>
      )}
      {correction_markdown && (
        <div className="flex items-start gap-2 bg-success/10 px-3.5 py-2.5 text-sm">
          <CircleCheck className="mt-0.5 size-4 shrink-0 text-success" aria-hidden="true" />
          <div className="prose prose-sm prose-neutral min-w-0 max-w-none dark:prose-invert">
            <EpreuveMarkdown markdown={correction_markdown} />
          </div>
        </div>
      )}
    </div>
  )
}
