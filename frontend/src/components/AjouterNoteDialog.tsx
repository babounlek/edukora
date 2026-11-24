import { useEffect, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { creerNoteLibre, listSubjects, modifierNoteLibre } from "@/api/endpoints"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { useCountry } from "@/context/CountryContext"
import { CLE_NOTES_DUES } from "@/lib/notesDues"
import { useCursusAbonne } from "@/lib/abonneActif"
import { t, useI18n } from "@/lib/i18n"

const NOTE_MAX = 2000
const CLE_DERNIERE_MATIERE = "edukora_note_derniere_matiere"

/** La matière de la dernière note écrite : on écrit souvent plusieurs notes de suite dans la même. */
function derniereMatiere(): number | null {
  try {
    const v = Number(window.localStorage.getItem(CLE_DERNIERE_MATIERE))
    return v > 0 ? v : null
  } catch {
    return null
  }
}

/**
 * Écrire une note libre, rangée dans le dossier d'une matière. Deux entrées : le bouton « Nouvelle note » de Mes notes
 * (l'élève choisit la matière) et « Ajouter à mes notes » depuis la correction d'un quiz (la matière est connue, la
 * question est jointe en citation).
 */
export function AjouterNoteDialog({
  open, onOpenChange, subjectId, citation, texteInitial, edition,
}: {
  open: boolean
  onOpenChange: (ouvert: boolean) => void
  /** Modifier une note libre existante : la matière et la citation ne changent pas, seul le texte. */
  edition?: { id: number; note: string; citation?: string }
  /** Matière imposée (depuis un quiz) ; sinon l'élève la choisit. */
  subjectId?: number | null
  citation?: string
  texteInitial?: string
}) {
  useI18n()
  const queryClient = useQueryClient()
  const { country } = useCountry()
  const cursus = useCursusAbonne()
  const [texte, setTexte] = useState(edition?.note ?? texteInitial ?? "")
  const [choix, setChoix] = useState<number | null>(derniereMatiere)

  useEffect(() => {
    if (open) setTexte(edition?.note ?? texteInitial ?? "")
  }, [open, texteInitial, edition?.note])

  const { data: matieres } = useQuery({
    queryKey: ["matieres-notes", country, cursus],
    // Les matières de l'examen préparé quand on le connaît : sinon la liste mêlait BEPC et GCE.
    queryFn: ({ signal }) => listSubjects(country, signal, cursus ?? undefined),
    enabled: open && !subjectId && !edition,
  })
  // La dernière matière n'est reprise que si elle fait partie de la liste proposée (examen changé depuis).
  const choixValide = choix !== null && matieres?.some((m) => m.id === choix) ? choix : null
  const matiere = subjectId ?? choixValide ?? matieres?.[0]?.id ?? null

  const creer = useMutation({
    mutationFn: () =>
      edition ? modifierNoteLibre(edition.id, texte) : creerNoteLibre(matiere as number, texte, citation ?? ""),
    onSuccess: () => {
      if (!edition && matiere !== null) {
        try {
          window.localStorage.setItem(CLE_DERNIERE_MATIERE, String(matiere))
        } catch {
          /* stockage indisponible : la matière ne sera simplement pas retenue */
        }
      }
      toast.success(t(edition ? "ca.note_modifiee" : "ca.note_ajoutee"))
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      queryClient.invalidateQueries({ queryKey: ["notes-a-revoir"] })
      queryClient.invalidateQueries({ queryKey: CLE_NOTES_DUES })
      setTexte("")
      onOpenChange(false)
    },
    onError: () => toast.error(t("ca.note_erreur")),
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogTitle>{t(edition ? "ca.modifier_note" : "ca.nouvelle_note")}</DialogTitle>
        <DialogDescription>{t("ca.nouvelle_note_texte")}</DialogDescription>
        {(edition?.citation ?? citation) && (
          <blockquote className="mt-3 rounded-xl border-l-4 border-gold/60 bg-gold/[0.06] px-3 py-2 text-sm text-muted-foreground">
            {(edition?.citation ?? citation ?? "").slice(0, 280)}
          </blockquote>
        )}
        {!subjectId && !edition && matieres && matieres.length > 0 && (
          <select
            aria-label={t("ca.matiere")}
            value={matiere ?? ""}
            onChange={(e) => setChoix(Number(e.target.value))}
            className="mt-3 w-full rounded-xl border border-input bg-background px-3 py-2.5 text-sm"
          >
            {matieres.map((m) => (
              <option key={m.id} value={m.id}>
                {m.label}
              </option>
            ))}
          </select>
        )}
        <textarea
          value={texte}
          onChange={(e) => setTexte(e.target.value)}
          onKeyDown={(e) => {
            // Ctrl/Cmd + Entrée enregistre, comme dans une messagerie.
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && texte.trim() && !creer.isPending && (edition || matiere !== null)) creer.mutate()
          }}
          maxLength={NOTE_MAX}
          rows={5}
          autoFocus
          aria-label={t("ed.note_label")}
          placeholder={t("ed.note_placeholder")}
          className="mt-3 w-full resize-y rounded-xl border border-input bg-background px-3.5 py-2.5 text-sm leading-relaxed outline-none focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring/40"
        />
        <div className="mt-3 flex items-center justify-end gap-2">
          <span className="mr-auto text-xs tabular-nums text-muted-foreground">
            {texte.length} / {NOTE_MAX}
          </span>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("seance.annuler")}
          </Button>
          <Button disabled={!texte.trim() || (!edition && matiere === null) || creer.isPending} onClick={() => creer.mutate()}>
            {t("matieres.enregistrer")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
