import { Link } from "react-router-dom"
import {
  ArrowUpRight, BadgeCheck, Bookmark, BookOpen, Brain, FileText, ListChecks, MoreHorizontal, Pencil, Pin, Quote, StickyNote, Trash2,
} from "lucide-react"

import type { CarnetEntree } from "@/api/types"
import { BoutonPartager } from "@/components/BoutonPartager"
import { COURS_SECTION_LABELS } from "@/components/CoursSection"
import { ImageNote } from "@/components/ImageNote"
import { NoteTexte } from "@/components/NoteTexte"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { coursReaderPath, epreuveReaderPath } from "@/lib/countryPath"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { cheminPublicDeLaSource, texteDeNotePartagee } from "@/lib/partageNote"
import { capitaliserTheme, cn } from "@/lib/utils"
import { localeCourante, t, useI18n, type CleI18n } from "@/lib/i18n"

/** "regle" → "La règle", "exercice-3" → "Exercice 3" : le nom de la section, pas son ancre. */
export function libelleSection(entree: CarnetEntree): string {
  if (entree.type === "libre") return t("ca.type_libre")
  if (entree.type === "cours") {
    const label = COURS_SECTION_LABELS[entree.cle as keyof typeof COURS_SECTION_LABELS]
    if (label) return label.full
  }
  const exercice = /^exercice-(.+)$/.exec(entree.cle)
  if (exercice) return t("ed.exercice_n", { n: exercice[1].toUpperCase() })
  return capitaliserTheme(entree.cle.replace(/-/g, " "))
}

export function lienSection(entree: CarnetEntree): string {
  if (entree.type === "libre") return ""
  const base = entree.type === "cours" ? coursReaderPath(entree.slug) : epreuveReaderPath(entree.country, entree.slug)
  return `${base}#${entree.cle}`
}

/** « il y a 3 jours », « hier », « à l'instant » : la date d'une note se lit comme on la dirait. */
export function ilYA(iso: string | null | undefined, maintenant = Date.now()): string {
  if (!iso) return ""
  const ecart = (new Date(iso).getTime() - maintenant) / 1000
  const dit = new Intl.RelativeTimeFormat(localeCourante(), { numeric: "auto" })
  const abs = Math.abs(ecart)
  if (abs < 3600) return dit.format(Math.round(ecart / 60), "minute")
  if (abs < 86400) return dit.format(Math.round(ecart / 3600), "hour")
  if (abs < 86400 * 30) return dit.format(Math.round(ecart / 86400), "day")
  if (abs < 86400 * 365) return dit.format(Math.round(ecart / (86400 * 30)), "month")
  return dit.format(Math.round(ecart / (86400 * 365)), "year")
}

function genreDeLaNote(entree: CarnetEntree): { cle: CleI18n; Icone: typeof StickyNote } {
  if (entree.type === "cours") return { cle: "ca.type_cours", Icone: BookOpen }
  if (entree.type === "epreuve") return { cle: "ca.type_corrige", Icone: FileText }
  if (entree.origine === "quiz") return { cle: "ca.type_quiz", Icone: ListChecks }
  if (entree.origine === "fiche") return { cle: "ca.type_fiche", Icone: BadgeCheck }
  if (!entree.note && entree.citation) return { cle: "ca.type_passage", Icone: Quote }
  return { cle: "ca.type_libre", Icone: StickyNote }
}

/**
 * Une note, comme une feuille de cahier : un filet à la couleur de sa matière (doré quand elle est épinglée), d'où elle
 * vient, quand elle a été écrite, et où elle en est dans la révision. Les gestes rares (modifier, supprimer) sont rangés
 * derrière « ⋯ » ; épingler reste sous le pouce.
 */
export function CarteNote({
  entree, dansDossier, rang = 0, occupe = false, onEpingler, onModifier, onRetirer,
}: {
  entree: CarnetEntree
  /** Dans un dossier ouvert, la matière ne se répète pas sur chaque carte. */
  dansDossier: boolean
  rang?: number
  occupe?: boolean
  onEpingler: () => void
  onModifier: () => void
  onRetirer: () => void
}) {
  useI18n()
  const couleur = couleurMatiere(entree.matiere_code)
  const { cle, Icone } = genreDeLaNote(entree)
  const epinglable = Boolean(entree.note) || entree.genre === "libre"
  const aujourdhui = new Date().toISOString().slice(0, 10)
  const due = Boolean(entree.note) && Boolean(entree.revision_due) && (entree.revision_due as string) <= aujourdhui
  const prochaine =
    entree.note && entree.revision_due && !due
      ? new Date(entree.revision_due).toLocaleDateString(localeCourante(), { day: "numeric", month: "short" })
      : ""
  const source = entree.type === "libre" ? entree.source : lienSection(entree)

  return (
    <li
      style={{ animationDelay: `${Math.min(rang, 10) * 35}ms` }}
      className={cn(
        "group relative animate-fade-up break-inside-avoid overflow-hidden rounded-2xl border bg-card shadow-sm transition-shadow duration-300 hover:shadow-lg hover:shadow-primary/5 print:shadow-none",
        entree.epingle ? "border-gold/50" : "border-border",
      )}
    >
      <span aria-hidden="true" className={cn("absolute inset-y-0 left-0 w-1", entree.epingle ? "bg-gold" : couleur.barre)} />
      <div className="p-4 pl-5 sm:p-5 sm:pl-6">
        <div className="flex items-center gap-2">
          <span className={cn("inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[0.7rem] font-semibold uppercase tracking-wide", couleur.puce)}>
            <Icone className="size-3" aria-hidden="true" />
            {t(cle)}
          </span>
          <span className="min-w-0 flex-1 truncate text-xs text-muted-foreground">
            {!dansDossier && <span className="font-medium text-foreground/80">{entree.matiere} · </span>}
            {ilYA(entree.updated_at)}
          </span>
          {epinglable && (
            <Button
              type="button"
              size="icon"
              variant="ghost"
              aria-pressed={entree.epingle}
              className={cn("-my-1 size-8 shrink-0 print:hidden", entree.epingle ? "text-gold-text" : "text-muted-foreground/60 hover:text-foreground")}
              aria-label={t(entree.epingle ? "ca.desepingler" : "ca.epingler")}
              disabled={occupe}
              onClick={onEpingler}
            >
              <Pin className={cn("size-4 transition-transform", entree.epingle && "-rotate-45 fill-current")} />
            </Button>
          )}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button type="button" size="icon" variant="ghost" className="-my-1 -mr-1.5 size-8 shrink-0 text-muted-foreground/60 hover:text-foreground print:hidden" aria-label={t("ca.actions")}>
                <MoreHorizontal className="size-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {/* Toute note se modifie ici, y compris celle d'une section : il fallait sinon rouvrir la source, et on
                  croyait la note figée. */}
              <DropdownMenuItem onSelect={onModifier}>
                <Pencil aria-hidden="true" />
                {t(entree.genre === "marque" && !entree.note ? "ed.ajouter_note" : "ca.modifier_aria")}
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={onRetirer} disabled={occupe} className="text-destructive focus:text-destructive">
                <Trash2 aria-hidden="true" />
                {t("ca.retirer_aria")}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {entree.type !== "libre" && (
          <div className="mt-2.5">
            <Link to={lienSection(entree)} className="block font-display text-base font-semibold leading-snug tracking-tight hover:text-primary">
              {entree.titre}
            </Link>
            <p className="mt-0.5 flex items-center gap-1.5 text-xs text-muted-foreground">
              {entree.signet && <Bookmark className="size-3 shrink-0 fill-current text-gold-text" aria-label={t("ca.garde")} />}
              {libelleSection(entree)}
            </p>
          </div>
        )}

        {entree.type === "libre" && entree.citation && (
          <blockquote className="mt-3 border-l-2 border-gold/60 pl-3">
            <NoteTexte texte={entree.citation} className="italic text-muted-foreground" />
          </blockquote>
        )}

        {entree.note && <NoteTexte texte={entree.note} className="mt-3 text-[0.95rem] leading-relaxed" />}

        {entree.genre === "libre" && entree.a_image && (
          <div className="mt-3">
            <ImageNote noteId={entree.id} version={entree.updated_at ?? undefined} />
          </div>
        )}

        {(due || prochaine || source || entree.note || entree.citation) && (
          // Deux zones qui ne se touchent jamais : l'état et la source à gauche (elles passent à la ligne au besoin), le
          // partage à droite, à largeur fixe. En une seule rangée, « Rouvrir la source » et « Partager » se chevauchaient.
          <div className="mt-3.5 flex items-center justify-between gap-4 border-t border-dashed border-border pt-3 print:hidden">
            <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1.5">
              {due && (
                <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                  <Brain className="size-3" aria-hidden="true" />
                  {t("ca.a_relire")}
                </span>
              )}
              {prochaine && <span className="text-xs text-muted-foreground">{t("ca.revue_le", { date: prochaine })}</span>}
              {source && (
                <Link to={source} className="inline-flex shrink-0 items-center gap-0.5 whitespace-nowrap text-xs font-medium text-primary hover:underline">
                  {t(entree.type === "libre" ? "ca.rouvrir_source" : "ca.rouvrir")}
                  <ArrowUpRight className="size-3" aria-hidden="true" />
                </Link>
              )}
            </div>
            {(entree.note || entree.citation) && (
              <BoutonPartager
                chemin={cheminPublicDeLaSource(source)}
                texte={texteDeNotePartagee({ matiere: entree.matiere, note: entree.note, citation: entree.citation }, t("ca.partage_entete"))}
                type="note"
                variant="ghost"
                className="h-8 shrink-0 px-2.5 text-xs text-muted-foreground"
              />
            )}
          </div>
        )}
      </div>
    </li>
  )
}
