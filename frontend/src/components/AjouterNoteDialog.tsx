import { useEffect, useRef, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { Bold, Eye, ImagePlus, Italic, List, Sigma, X } from "lucide-react"

import { creerNoteLibre, envoyerImageNote, listSubjects, modifierNoteLibre, retirerImageNote, supprimerNoteLibre } from "@/api/endpoints"
import { Button } from "@/components/ui/button"
import { ImageNote } from "@/components/ImageNote"
import { NoteTexte } from "@/components/NoteTexte"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { useCountry } from "@/context/CountryContext"
import { CLE_NOTES_DUES } from "@/lib/notesDues"
import { useCursusAbonne } from "@/lib/abonneActif"
import { t, useI18n } from "@/lib/i18n"
import { appliquerFormat, type Format } from "@/lib/miseEnForme"
import { reduireImage } from "@/lib/reduireImage"
import { cn } from "@/lib/utils"

const NOTE_MAX = 2000
const CLE_DERNIERE_MATIERE = "edukora_note_derniere_matiere"
const CLE_BROUILLON = "edukora_note_brouillon"

/** Le brouillon d'une note non enregistrée : fermer la fenêtre par erreur ne doit pas faire perdre ce qui était écrit. */
function lireBrouillon(citation: string): string {
  try {
    const b = JSON.parse(window.localStorage.getItem(CLE_BROUILLON) ?? "null")
    return b && b.c === citation && typeof b.t === "string" ? b.t : ""
  } catch {
    return ""
  }
}
function ecrireBrouillon(citation: string, texte: string) {
  try {
    if (texte.trim()) window.localStorage.setItem(CLE_BROUILLON, JSON.stringify({ c: citation, t: texte }))
    else window.localStorage.removeItem(CLE_BROUILLON)
  } catch {
    /* stockage indisponible : pas de brouillon, la note s'écrit normalement */
  }
}

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
  open, onOpenChange, subjectId, matiereParDefaut, citation, texteInitial, edition, origine, source, joignables, joindreParDefaut = false,
}: {
  open: boolean
  onOpenChange: (ouvert: boolean) => void
  /** Modifier une note libre existante : la matière et la citation ne changent pas, seul le texte. */
  edition?: { id: number; note: string; citation?: string; aImage?: boolean; version?: string }
  /** Adresse interne d'où vient la note (« Rouvrir la source » sur sa carte). */
  source?: string
  /** Matière imposée (depuis un quiz) ; sinon l'élève la choisit. */
  subjectId?: number | null
  /** Matière proposée d'office (le dossier ouvert) : l'élève peut encore en changer. */
  matiereParDefaut?: { id: number; label: string } | null
  citation?: string
  texteInitial?: string
  /**
   * Depuis la correction d'un quiz : la question et la bonne réponse ne sont jamais imposées, l'élève coche ce qu'il veut joindre
   * à sa note (rien de coché : une note libre dans la matière).
   */
  joignables?: { question: string; bonneReponse?: string }
  /** Cases cochées d'office à l'ouverture (après une erreur : la question et la bonne réponse). */
  joindreParDefaut?: boolean
  /** « quiz » : la note vient de la correction d'un quiz (rappelé sur sa carte). */
  origine?: string
}) {
  useI18n()
  const queryClient = useQueryClient()
  const { country } = useCountry()
  const cursus = useCursusAbonne()
  const [texte, setTexte] = useState(edition?.note ?? texteInitial ?? "")
  const [choix, setChoix] = useState<number | null>(matiereParDefaut?.id ?? derniereMatiere())
  const [avecQuestion, setAvecQuestion] = useState(joindreParDefaut)
  const [avecReponse, setAvecReponse] = useState(joindreParDefaut)
  const citationEffective = joignables ? (avecQuestion ? joignables.question : "") : (citation ?? "")
  const reponseJointe = joignables?.bonneReponse && avecReponse ? t("ca.bonne_reponse_note", { reponse: joignables.bonneReponse }) : ""
  const aCitation = Boolean(edition?.citation ?? citationEffective) || reponseJointe !== ""
  // Le brouillon ne sert qu'aux notes écrites hors quiz : une note de quiz se fait en quelques secondes, dans la page.
  const brouillon = !edition && !joignables
  const zoneTexte = useRef<HTMLTextAreaElement>(null)
  const texteVide = texte === ""
  const [apercu, setApercu] = useState(false)
  // La photo : choisie dans cette fenêtre (image), ou déjà jointe à la note qu'on modifie (edition.aImage).
  const [image, setImage] = useState<File | null>(null)
  const [imageRetiree, setImageRetiree] = useState(false)
  const choixImage = useRef<HTMLInputElement>(null)
  const [adresseImage, setAdresseImage] = useState<string | null>(null)
  useEffect(() => {
    if (!image) {
      setAdresseImage(null)
      return
    }
    const a = URL.createObjectURL(image)
    setAdresseImage(a)
    return () => URL.revokeObjectURL(a)
  }, [image])
  const imageDejaJointe = Boolean(edition?.aImage) && !imageRetiree
  const aUneImage = image !== null || imageDejaJointe

  useEffect(() => {
    if (!open) return
    setTexte(edition?.note ?? texteInitial ?? (brouillon ? lireBrouillon(citation ?? "") : ""))
    setChoix(matiereParDefaut?.id ?? derniereMatiere())
    setAvecQuestion(joindreParDefaut)
    setAvecReponse(joindreParDefaut)
    setApercu(false)
    setImage(null)
    setImageRetiree(false)
  }, [open, texteInitial, edition?.note, matiereParDefaut?.id, citation, brouillon, joindreParDefaut])

  // Le curseur se pose À LA FIN d'un texte déjà écrit (la bonne réponse d'un quiz, un brouillon) : on écrit à la suite.
  useEffect(() => {
    if (!open) return
    const m = window.setTimeout(() => {
      const z = zoneTexte.current
      if (z) z.setSelectionRange(z.value.length, z.value.length)
    }, 60)
    return () => window.clearTimeout(m)
  }, [open, texteVide])

  function ecrire(valeur: string) {
    setTexte(valeur)
    if (brouillon) ecrireBrouillon(citation ?? "", valeur)
  }
  // Un passage gardé tel quel est déjà une note : le texte peut rester vide quand il y a une citation.
  const enregistrable = Boolean(texte.trim()) || aCitation || aUneImage

  /** Gras, italique, liste, formule : les signes Markdown posés autour de la sélection (la sélection reste choisie après). */
  function formater(format: Format) {
    const z = zoneTexte.current
    if (!z) return
    const r = appliquerFormat(texte, z.selectionStart, z.selectionEnd, format)
    ecrire(r.texte.slice(0, NOTE_MAX))
    window.setTimeout(() => {
      z.focus()
      z.setSelectionRange(r.debut, r.fin)
    }, 0)
  }

  const { data: liste } = useQuery({
    queryKey: ["matieres-notes", country, cursus],
    // Les matières de l'examen préparé quand on le connaît : sinon la liste mêlait BEPC et GCE.
    queryFn: ({ signal }) => listSubjects(country, signal, cursus ?? undefined),
    enabled: open && !subjectId && !edition,
  })
  // Le dossier ouvert est toujours proposé, même si sa matière n'est plus dans la liste de l'examen préparé.
  const matieres =
    liste && matiereParDefaut && !liste.some((m) => m.id === matiereParDefaut.id)
      ? [{ id: matiereParDefaut.id, label: matiereParDefaut.label }, ...liste]
      : liste
  // La dernière matière n'est reprise que si elle fait partie de la liste proposée (examen changé depuis).
  const choixValide = choix !== null && matieres?.some((m) => m.id === choix) ? choix : null
  const matiere = subjectId ?? choixValide ?? matieres?.[0]?.id ?? null

  const creer = useMutation({
    mutationFn: async () => {
      if (edition) {
        await modifierNoteLibre(edition.id, texte, image !== null || imageDejaJointe)
        if (image) await envoyerImageNote(edition.id, await reduireImage(image))
        else if (edition.aImage && imageRetiree) await retirerImageNote(edition.id)
        return
      }
      const note = await creerNoteLibre(matiere as number, reponseJointe + texte, citationEffective, origine ?? "", source ?? "", image !== null)
      if (image) {
        try {
          await envoyerImageNote(note.id, await reduireImage(image))
        } catch {
          // La note ne doit pas rester vide par la faute de la photo : sans texte ni passage, on la retire.
          if (!(reponseJointe + texte).trim() && !citationEffective) await supprimerNoteLibre(note.id).catch(() => undefined)
          toast.error(t("ca.image_erreur_envoi"))
        }
      }
    },
    onSuccess: () => {
      if (!edition && matiere !== null) {
        try {
          window.localStorage.setItem(CLE_DERNIERE_MATIERE, String(matiere))
        } catch {
          /* stockage indisponible : la matière ne sera simplement pas retenue */
        }
      }
      if (brouillon) ecrireBrouillon("", "")
      toast.success(t(edition ? "ca.note_modifiee" : "ca.note_ajoutee"))
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      queryClient.invalidateQueries({ queryKey: ["notes-a-revoir"] })
      queryClient.invalidateQueries({ queryKey: CLE_NOTES_DUES })
      setTexte("")
      setImage(null)
      onOpenChange(false)
    },
    onError: () => toast.error(t("ca.note_erreur")),
  })

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[92vh] overflow-y-auto">
        <DialogTitle>{t(edition ? "ca.modifier_note" : "ca.nouvelle_note")}</DialogTitle>
        <DialogDescription>{t("ca.nouvelle_note_texte")}</DialogDescription>
        {joignables && (
          <fieldset className="mt-3 flex flex-col gap-1.5 text-sm">
            <label className="flex items-center gap-2">
              <input type="checkbox" className="size-4 accent-primary" checked={avecQuestion} onChange={(e) => setAvecQuestion(e.target.checked)} />
              {t("ca.joindre_question")}
            </label>
            {joignables.bonneReponse && (
              <label className="flex items-center gap-2">
                <input type="checkbox" className="size-4 accent-primary" checked={avecReponse} onChange={(e) => setAvecReponse(e.target.checked)} />
                {t("ca.joindre_reponse")}
              </label>
            )}
          </fieldset>
        )}
        {(edition?.citation ?? citationEffective) && (
          <blockquote className="mt-3 max-h-40 overflow-y-auto rounded-xl border-l-4 border-gold/60 bg-gold/[0.06] px-3 py-2 text-muted-foreground">
            <NoteTexte texte={edition?.citation ?? citationEffective} />
          </blockquote>
        )}
        {reponseJointe && (
          <div className="mt-2 rounded-xl border border-gold/30 bg-gold/[0.06] px-3 py-2">
            <NoteTexte texte={reponseJointe.trim()} />
          </div>
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
        <div className="mt-3 flex flex-wrap items-center gap-1" role="toolbar" aria-label={t("ca.mise_en_forme")}>
          {(
            [
              ["gras", Bold, "ca.format_gras"],
              ["italique", Italic, "ca.format_italique"],
              ["liste", List, "ca.format_liste"],
              ["formule", Sigma, "ca.format_formule"],
            ] as const
          ).map(([format, Icone, cle]) => (
            <Button key={format} type="button" variant="ghost" size="icon" className="size-9" aria-label={t(cle)} title={t(cle)} onClick={() => formater(format)}>
              <Icone className="size-4" aria-hidden="true" />
            </Button>
          ))}
          <Button
            type="button"
            variant="ghost"
            size="sm"
            aria-pressed={apercu}
            className={cn("ml-auto gap-1.5", apercu && "bg-accent")}
            onClick={() => setApercu(!apercu)}
          >
            <Eye className="size-4" aria-hidden="true" />
            {t("ca.apercu")}
          </Button>
        </div>
        <textarea
          ref={zoneTexte}
          value={texte}
          onChange={(e) => ecrire(e.target.value)}
          onKeyDown={(e) => {
            // Ctrl/Cmd + Entrée enregistre, comme dans une messagerie.
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey) && enregistrable && !creer.isPending && (edition || matiere !== null)) creer.mutate()
          }}
          maxLength={NOTE_MAX}
          rows={5}
          autoFocus
          aria-label={t("ed.note_label")}
          placeholder={t("ed.note_placeholder")}
          className="mt-1.5 w-full resize-y rounded-xl border border-input bg-background px-3.5 py-2.5 text-sm leading-relaxed outline-none focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring/40"
        />
        {apercu && (
          <div className="mt-2 rounded-xl border border-gold/30 bg-gold/[0.06] px-4 py-3" aria-label={t("ca.apercu")}>
            {texte.trim() ? <NoteTexte texte={texte} /> : <p className="text-sm text-muted-foreground">{t("ca.apercu_vide")}</p>}
          </div>
        )}
        <div className="mt-3">
          <input
            ref={choixImage}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="sr-only"
            tabIndex={-1}
            aria-label={t("ca.ajouter_photo")}
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) {
                setImage(f)
                setImageRetiree(false)
              }
              e.target.value = ""
            }}
          />
          {image && adresseImage && (
            <div className="relative mb-2 overflow-hidden rounded-xl border border-border bg-muted/30">
              <img src={adresseImage} alt={t("ca.image_alt")} className="max-h-48 w-full object-contain" />
            </div>
          )}
          {!image && imageDejaJointe && edition && (
            <div className="mb-2">
              <ImageNote noteId={edition.id} version={edition.version} className="max-h-48 w-full object-contain" />
            </div>
          )}
          <div className="flex flex-wrap items-center gap-2">
            <Button type="button" variant="outline" size="sm" className="gap-1.5 rounded-full" onClick={() => choixImage.current?.click()}>
              <ImagePlus className="size-4" aria-hidden="true" />
              {t(aUneImage ? "ca.remplacer_photo" : "ca.ajouter_photo")}
            </Button>
            {aUneImage && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="gap-1.5 text-muted-foreground"
                onClick={() => {
                  setImage(null)
                  if (edition?.aImage) setImageRetiree(true)
                }}
              >
                <X className="size-4" aria-hidden="true" />
                {t("ca.retirer_photo")}
              </Button>
            )}
          </div>
        </div>
        <div className="mt-3 flex items-center justify-end gap-2">
          <span className="mr-auto text-xs tabular-nums text-muted-foreground">
            {texte.length} / {NOTE_MAX}
          </span>
          <Button variant="outline" onClick={() => { if (brouillon) ecrireBrouillon("", ""); onOpenChange(false) }}>
            {t("seance.annuler")}
          </Button>
          <Button disabled={!enregistrable || (!edition && matiere === null) || creer.isPending} onClick={() => creer.mutate()}>
            {t("matieres.enregistrer")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
