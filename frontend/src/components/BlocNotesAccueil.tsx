import { useState } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, Brain, NotebookPen, Plus } from "lucide-react"

import { AjouterNoteDialog } from "@/components/AjouterNoteDialog"
import { NoteTexte } from "@/components/NoteTexte"
import { Button } from "@/components/ui/button"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

export interface ResumeNotesAccueil {
  total: number
  derniere: { texte: string; matiere: string; matiere_code: string; matiere_id: number; epingle: boolean } | null
}

/**
 * « Mes notes » sur l'accueil de l'abonné : sans ce bloc, l'accueil ne disait rien des notes tant qu'aucune n'était à
 * relire, et un élève qui n'en avait jamais écrit ne savait pas qu'elles existaient. Toujours là : ce qu'il y a à relire
 * (la raison d'ouvrir), la dernière note épinglée ou écrite, et le geste pour en écrire une sans quitter l'accueil.
 */
export function BlocNotesAccueil({ resume, dues }: { resume: ResumeNotesAccueil; dues: number }) {
  useI18n()
  const [nouvelle, setNouvelle] = useState(false)
  const derniere = resume.derniere
  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-labelledby="accueil-notes-titre">
      <div className="overflow-hidden rounded-2xl border border-border bg-card">
        <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 px-5 pt-4">
          <h2 id="accueil-notes-titre" className="flex items-center gap-2 font-sans text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <NotebookPen className="size-3.5" aria-hidden="true" />
            {t("cpt.carnet")}
          </h2>
          {resume.total > 0 && (
            <Link to="/carnet" className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline">
              {tn("ca.stat_notes", resume.total)}
              <ArrowRight className="size-3" aria-hidden="true" />
            </Link>
          )}
        </div>

        {resume.total === 0 ? (
          <p className="px-5 pt-2 text-sm text-muted-foreground">{t("ca.accueil_vide")}</p>
        ) : (
          derniere && (
            <Link
              to={`/carnet?dossier=${derniere.matiere_id}`}
              className="relative mx-5 mt-3 block overflow-hidden rounded-xl border border-border bg-background/60 py-3 pl-5 pr-4 transition-colors hover:border-primary/40"
            >
              <span aria-hidden="true" className={cn("absolute inset-y-0 left-0 w-1", derniere.epingle ? "bg-gold" : couleurMatiere(derniere.matiere_code).barre)} />
              <span className="block text-xs font-medium text-muted-foreground">{derniere.matiere}</span>
              <span className="mt-1 block max-h-[4.4rem] overflow-hidden [mask-image:linear-gradient(to_bottom,black_60%,transparent)]">
                <NoteTexte texte={derniere.texte} />
              </span>
            </Link>
          )
        )}

        <div className="flex flex-wrap items-center gap-2 px-5 pb-4 pt-3.5">
          {dues > 0 && (
            <Button asChild className="min-h-10 rounded-full">
              <Link to="/carnet?reviser=1">
                <Brain />
                {tn("ca.notes_dues", dues)}
              </Link>
            </Button>
          )}
          <Button type="button" variant={dues > 0 ? "outline" : "default"} className="min-h-10 rounded-full" onClick={() => setNouvelle(true)}>
            <Plus />
            {t("ca.nouvelle_note")}
          </Button>
        </div>
      </div>
      <AjouterNoteDialog open={nouvelle} onOpenChange={setNouvelle} />
    </section>
  )
}
