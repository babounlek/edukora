import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, NotebookPen } from "lucide-react"

import { getNotesARevoir } from "@/api/endpoints"
import { CLE_NOTES_DUES } from "@/lib/notesDues"
import { t, tn, useI18n } from "@/lib/i18n"

/** Les notes à réviser aujourd'hui : le nombre seulement. Même cache que l'accueil, qui le remplit avec sa réponse. */
export function useNotesDues(actif = true) {
  return useQuery({
    queryKey: CLE_NOTES_DUES,
    queryFn: ({ signal }) => getNotesARevoir(signal).then((d) => ({ total: d.total })),
    enabled: actif,
  }).data
}

/**
 * Une ligne du bloc « À continuer » de l'accueil : « 3 notes à réviser », qui ouvre la révision sur Mes notes. Rien tant
 * qu'aucune note n'est due : l'élève qui n'écrit pas de notes ne voit jamais cette ligne.
 */
export function RangeeNotes({ total }: { total: number }) {
  useI18n()
  return (
    <Link to="/carnet?reviser=1" className="group flex items-center gap-3 px-5 py-3.5 transition-colors hover:bg-muted/40">
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
        <NotebookPen className="size-4" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">{t("ca.notes_titre")}</span>
        <span className="line-clamp-2 text-sm font-medium">{tn("ca.notes_dues", total)}</span>
      </span>
      <span className="shrink-0 text-sm font-medium text-primary">{t("ca.reviser_matiere")}</span>
      <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
    </Link>
  )
}
