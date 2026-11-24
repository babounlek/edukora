import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { NotebookPen } from "lucide-react"

import { getNotesParTheme } from "@/api/endpoints"
import { ImageNote } from "@/components/ImageNote"
import { NoteTexte } from "@/components/NoteTexte"
import { useAuth } from "@/context/AuthContext"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * « Tu as N notes sur ce thème » : les notes que l'élève a déjà écrites sur le thème qu'il retravaille, remises sous ses yeux
 * au moment où elles servent (après une erreur de quiz, en tête des exercices du thème). Repliée : une ligne, qui s'ouvre
 * d'un toucher. Rien tant que l'élève n'a pas de note sur ce thème, ou n'est pas connecté.
 */
export function NotesDuTheme({ themeId, className }: { themeId?: number | null; className?: string }) {
  useI18n()
  const { isAuthenticated } = useAuth()
  const { data } = useQuery({
    queryKey: ["notes-theme", themeId],
    queryFn: ({ signal }) => getNotesParTheme(themeId as number, signal),
    enabled: isAuthenticated && Boolean(themeId),
  })
  if (!data || data.total === 0) return null
  return (
    <details className={cn("group rounded-xl border border-gold/40 bg-gold/[0.06] px-4 py-3", className)}>
      <summary className="flex cursor-pointer list-none items-center gap-2 text-sm font-medium">
        <NotebookPen className="size-4 shrink-0 text-gold-text" aria-hidden="true" />
        {tn("ca.theme_notes", data.total)}
      </summary>
      <ul className="mt-3 flex flex-col gap-3">
        {data.notes.map((n) => (
          <li key={n.id} className="rounded-lg border border-border bg-card px-3 py-2.5">
            {n.citation && <NoteTexte texte={n.citation} className="mb-1 italic text-muted-foreground" />}
            {n.note && <NoteTexte texte={n.note} />}
            {n.a_image && (
              <div className="mt-2">
                <ImageNote noteId={n.id} version={n.updated_at ?? undefined} className="max-h-40 w-full object-contain" />
              </div>
            )}
          </li>
        ))}
      </ul>
      {data.total > data.notes.length && (
        <Link to={`/carnet?dossier=${data.notes[0]?.matiere_id}`} className="mt-3 inline-block text-xs font-medium text-primary hover:underline">
          {t("ca.theme_voir_tout")}
        </Link>
      )}
    </details>
  )
}
