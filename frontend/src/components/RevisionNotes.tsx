import { useEffect, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { CheckCircle2, Eye, RotateCcw, Trophy } from "lucide-react"

import { getNotesARevoir, noterRevueNote } from "@/api/endpoints"
import type { CarnetEntree } from "@/api/types"
import { CLE_NOTES_DUES } from "@/lib/notesDues"
import { NoteTexte } from "@/components/NoteTexte"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * « Réviser mes notes » : une note après l'autre, à la répétition espacée. Le recto est le contexte (matière, citation ou
 * titre du cours), le verso la note ; l'élève dit s'il s'en souvenait. Ce qu'il sait revient plus tard, ce qu'il a oublié
 * revient demain (voir access.etude.noter_revue). Aucun point : réviser ses notes n'est pas une mesure de maîtrise.
 */
export function RevisionNotes({
  open, onOpenChange, matiereId,
}: { open: boolean; onOpenChange: (ouvert: boolean) => void; matiereId?: number | null }) {
  useI18n()
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ["notes-a-revoir", "paquet", matiereId ?? null],
    queryFn: ({ signal }) => getNotesARevoir(signal, matiereId ?? undefined),
    enabled: open,
    // Le paquet est figé à l'ouverture : le recharger à chaque réponse ferait sauter la carte sous les doigts.
    staleTime: Infinity,
    gcTime: 0,
  })
  const [position, setPosition] = useState(0)
  const [retournee, setRetournee] = useState(false)
  const [vues, setVues] = useState(0)

  useEffect(() => {
    if (open) {
      setPosition(0)
      setRetournee(false)
      setVues(0)
    }
  }, [open])

  const notes = data?.notes ?? []
  const carte: CarnetEntree | undefined = notes[position]

  async function repondre(savais: boolean) {
    if (!carte) return
    try {
      await noterRevueNote(carte.genre, carte.id, savais)
    } catch {
      /* la révision n'est pas perdue pour autant : la note reviendra à la prochaine ouverture */
    }
    setVues((v) => v + 1)
    setRetournee(false)
    setPosition((p) => p + 1)
  }

  function fermer(ouvert: boolean) {
    if (!ouvert) {
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      queryClient.invalidateQueries({ queryKey: ["notes-a-revoir"] })
      queryClient.invalidateQueries({ queryKey: CLE_NOTES_DUES })
    }
    onOpenChange(ouvert)
  }

  const contexte = carte ? (carte.citation || carte.titre || carte.matiere) : ""

  return (
    <Dialog open={open} onOpenChange={fermer}>
      <DialogContent>
        <DialogTitle>{t("ca.reviser_titre")}</DialogTitle>
        <DialogDescription>
          {data && notes.length > 0 && position < notes.length
            ? t("ca.reviser_progression", { n: position + 1, total: notes.length })
            : t("ca.reviser_texte")}
        </DialogDescription>

        {isLoading ? (
          <p className="mt-6 text-sm text-muted-foreground">…</p>
        ) : !carte ? (
          <div className="mt-6 flex flex-col items-center gap-2 text-center">
            {vues > 0 ? <Trophy className="size-8 text-gold-text" /> : <CheckCircle2 className="size-8 text-success" />}
            <p className="font-display text-lg font-semibold">{vues > 0 ? tn("ca.reviser_fini", vues) : t("ca.reviser_rien")}</p>
            <Button className="mt-2 rounded-full" onClick={() => fermer(false)}>
              {t("ca.fermer")}
            </Button>
          </div>
        ) : (
          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{carte.matiere}</p>
            {contexte !== carte.matiere && <p className="mt-1 text-sm text-muted-foreground">{contexte}</p>}
            {retournee ? (
              <div className="mt-3 rounded-xl border border-gold/30 bg-gold/[0.06] px-4 py-3">
                <NoteTexte texte={carte.note} />
              </div>
            ) : (
              <Button className="mt-4 w-full rounded-full" variant="outline" onClick={() => setRetournee(true)}>
                <Eye />
                {t("ca.reviser_voir")}
              </Button>
            )}
            {retournee && (
              <div className="mt-4 flex gap-2">
                <Button variant="outline" className="flex-1 rounded-full" onClick={() => repondre(false)}>
                  <RotateCcw />
                  {t("ca.reviser_a_revoir")}
                </Button>
                <Button className="flex-1 rounded-full" onClick={() => repondre(true)}>
                  <CheckCircle2 />
                  {t("ca.reviser_sais")}
                </Button>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
