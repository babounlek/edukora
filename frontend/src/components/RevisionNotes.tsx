import { useEffect, useRef, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { CheckCircle2, Eye, RotateCcw, Trophy } from "lucide-react"

import { getNotesARevoir, noterRevueNote } from "@/api/endpoints"
import type { CarnetEntree } from "@/api/types"
import { CLE_NOTES_DUES } from "@/lib/notesDues"
import { ImageNote } from "@/components/ImageNote"
import { NoteTexte } from "@/components/NoteTexte"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * « Réviser mes notes » : une note après l'autre, à la répétition espacée. Le recto est le contexte (matière, citation ou
 * titre du cours), le verso la note ; l'élève dit s'il s'en souvenait. Ce qu'il sait revient plus tard, ce qu'il a oublié
 * revient demain (voir access.etude.noter_revue). Aucun point : réviser ses notes n'est pas une mesure de maîtrise.
 *
 * Une carte à la fois, grande, à la couleur de sa matière ; une barre à segments dit où l'on en est. Au clavier : Espace
 * retourne la carte, 1 et 2 répondent.
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
  const [sues, setSues] = useState<boolean[]>([])

  useEffect(() => {
    if (open) {
      setPosition(0)
      setRetournee(false)
      setVues(0)
      setSues([])
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
    setSues((s) => [...s, savais])
    setRetournee(false)
    setPosition((p) => p + 1)
  }

  // Au clavier : Espace ou Entrée retourne la carte, 1 = à revoir, 2 = je m'en souviens.
  const gestes = useRef({ retournee, repondre, carte })
  gestes.current = { retournee, repondre, carte }
  useEffect(() => {
    if (!open) return
    function touche(e: KeyboardEvent) {
      const g = gestes.current
      if (!g.carte || e.ctrlKey || e.metaKey || e.altKey) return
      if (!g.retournee && (e.key === " " || e.key === "Enter")) {
        e.preventDefault()
        setRetournee(true)
      } else if (g.retournee && e.key === "1") void g.repondre(false)
      else if (g.retournee && e.key === "2") void g.repondre(true)
    }
    window.addEventListener("keydown", touche)
    return () => window.removeEventListener("keydown", touche)
  }, [open])

  function fermer(ouvert: boolean) {
    if (!ouvert) {
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      queryClient.invalidateQueries({ queryKey: ["notes-a-revoir"] })
      queryClient.invalidateQueries({ queryKey: CLE_NOTES_DUES })
    }
    onOpenChange(ouvert)
  }

  const contexte = carte ? (carte.citation || carte.titre || "") : ""
  const couleur = couleurMatiere(carte?.matiere_code)
  const Icone = subjectIcon(carte?.matiere_code ?? "")
  const nbSues = sues.filter(Boolean).length

  return (
    <Dialog open={open} onOpenChange={fermer}>
      <DialogContent className="max-h-[92vh] overflow-y-auto sm:max-w-xl">
        <DialogTitle className="font-display">{t("ca.reviser_titre")}</DialogTitle>
        <DialogDescription>
          {data && notes.length > 0 && position < notes.length
            ? t("ca.reviser_progression", { n: position + 1, total: notes.length })
            : t("ca.reviser_texte")}
        </DialogDescription>

        {/* Où l'on en est : un segment par note, vert quand on s'en souvenait, orangé quand elle reviendra demain. */}
        {notes.length > 0 && (
          <div className="mt-3 flex gap-1" aria-hidden="true">
            {notes.map((n, i) => (
              <span
                key={`${n.genre}-${n.id}`}
                className={cn(
                  "h-1.5 flex-1 rounded-full transition-colors duration-300",
                  i < sues.length ? (sues[i] ? "bg-success" : "bg-warning") : i === position ? "bg-primary/50" : "bg-muted",
                )}
              />
            ))}
          </div>
        )}

        {isLoading ? (
          <Skeleton className="mt-5 h-48 w-full rounded-2xl" />
        ) : !carte ? (
          <div className="mt-6 flex animate-fade-up flex-col items-center gap-2 pb-2 text-center">
            <span className={cn("flex size-16 items-center justify-center rounded-full", vues > 0 ? "bg-gold/20 text-gold-text" : "bg-success/15 text-success")}>
              {vues > 0 ? <Trophy className="size-8" /> : <CheckCircle2 className="size-8" />}
            </span>
            <p className="mt-2 font-display text-xl font-semibold">{vues > 0 ? tn("ca.reviser_fini", vues) : t("ca.reviser_rien")}</p>
            {vues > 0 && (
              <p className="text-sm tabular-nums text-muted-foreground">
                {nbSues} / {vues} · {t("ca.reviser_sais").toLowerCase()}
              </p>
            )}
            <Button className="mt-3 rounded-full px-6" onClick={() => fermer(false)}>
              {t("ca.fermer")}
            </Button>
          </div>
        ) : (
          <div key={`${carte.genre}-${carte.id}`} className="mt-4 animate-fade-up">
            <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-lg shadow-primary/5">
              <span aria-hidden="true" className={cn("absolute inset-y-0 left-0 w-1.5", couleur.barre)} />
              <div className="p-5 pl-6 sm:p-6 sm:pl-8">
                <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  <span className={cn("flex size-6 items-center justify-center rounded-full", couleur.puce)}>
                    <Icone className="size-3.5" aria-hidden="true" />
                  </span>
                  {carte.matiere}
                </p>
                {contexte ? (
                  <blockquote className="mt-3 border-l-2 border-gold/60 pl-3">
                    <NoteTexte texte={contexte} className="text-[0.95rem] italic text-muted-foreground" />
                  </blockquote>
                ) : (
                  !retournee && <p className="mt-4 font-display text-xl font-semibold leading-snug">{t("ca.reviser_recto")}</p>
                )}
                {retournee ? (
                  <div className="mt-4 animate-fade-up border-t border-dashed border-border pt-4">
                    <NoteTexte texte={carte.note} className="text-base leading-relaxed" />
                    {carte.genre === "libre" && carte.a_image && (
                      <div className="mt-3">
                        <ImageNote noteId={carte.id} version={carte.updated_at ?? undefined} />
                      </div>
                    )}
                  </div>
                ) : (
                  <Button className="mt-5 w-full rounded-full" size="lg" variant="outline" onClick={() => setRetournee(true)}>
                    <Eye />
                    {t("ca.reviser_voir")}
                  </Button>
                )}
              </div>
            </div>
            {retournee && (
              <div className="mt-4 grid animate-fade-up grid-cols-2 gap-2">
                <Button variant="outline" size="lg" className="rounded-full" onClick={() => repondre(false)}>
                  <RotateCcw />
                  {t("ca.reviser_a_revoir")}
                </Button>
                <Button size="lg" className="rounded-full" onClick={() => repondre(true)}>
                  <CheckCircle2 />
                  {t("ca.reviser_sais")}
                </Button>
              </div>
            )}
            <p className="mt-3 hidden text-center text-xs text-muted-foreground/70 lg:block">{t("ca.reviser_touches")}</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
