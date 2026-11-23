import { useEffect, useMemo, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"

import { ConnexionRequise } from "@/components/ConnexionRequise"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, Bookmark, BookOpen, FileText, Brain, NotebookPen, Pencil, Plus, Printer, Search, StickyNote, Trash2 } from "lucide-react"
import { toast } from "sonner"

import { getCarnet, getNotesARevoir, saveMarqueEtude, supprimerNoteLibre } from "@/api/endpoints"
import type { CarnetEntree } from "@/api/types"
import { COURS_SECTION_LABELS } from "@/components/CoursSection"
import { AjouterNoteDialog } from "@/components/AjouterNoteDialog"
import { ErreurChargement } from "@/components/ErreurChargement"
import { NoteTexte } from "@/components/NoteTexte"
import { RevisionNotes } from "@/components/RevisionNotes"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { coursReaderPath, epreuveReaderPath } from "@/lib/countryPath"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/** "regle" → "La règle", "exercice-3" → "Exercice 3" : le nom de la section, pas son ancre. */
function libelleSection(entree: CarnetEntree): string {
  if (entree.type === "libre") return t("ca.type_libre")
  if (entree.type === "cours") {
    const label = COURS_SECTION_LABELS[entree.cle as keyof typeof COURS_SECTION_LABELS]
    if (label) return label.full
  }
  const exercice = /^exercice-(.+)$/.exec(entree.cle)
  if (exercice) return t("ed.exercice_n", { n: exercice[1].toUpperCase() })
  return capitaliserTheme(entree.cle.replace(/-/g, " "))
}

function sansAccent(s: string): string {
  return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
}

function lienSection(entree: CarnetEntree): string {
  if (entree.type === "libre") return ""
  const base = entree.type === "cours" ? coursReaderPath(entree.slug) : epreuveReaderPath(entree.country, entree.slug)
  return `${base}#${entree.cle}`
}

/**
 * Le carnet de l'élève : ses signets et ses notes, tous documents confondus, du plus
 * récent au plus ancien - chaque entrée rouvre la section exacte.
 *
 * C'est ce qui donne un sens aux notes : une remarque écrite au fond d'un cours qu'on ne
 * rouvrira jamais ne sert à personne. Regroupées ici, elles deviennent la fiche de
 * révision que l'élève s'est écrite lui-même.
 */
export function CarnetPage() {
  useI18n()
  useSeo({ title: t("cpt.carnet") })
  const queryClient = useQueryClient()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["carnet"],
    queryFn: ({ signal }) => getCarnet(signal),
    enabled: isAuthenticated,
  })

  const [nouvelle, setNouvelle] = useState(false)
  const [revision, setRevision] = useState(false)
  const [matiereRevision, setMatiereRevision] = useState<number | null>(null)
  const [aModifier, setAModifier] = useState<CarnetEntree | null>(null)
  // Le lien « notes à réviser » de l'accueil ouvre directement la révision.
  const [params, setParams] = useSearchParams()
  useEffect(() => {
    if (params.get("reviser") === "1") {
      setRevision(true)
      params.delete("reviser")
      setParams(params, { replace: true })
    }
  }, [params, setParams])
  const { data: aRevoir } = useQuery({
    queryKey: ["notes-a-revoir"],
    queryFn: ({ signal }) => getNotesARevoir(signal),
    enabled: isAuthenticated,
  })

  const retirer = useMutation({
    mutationFn: async (entree: CarnetEntree): Promise<unknown> =>
      entree.genre === "libre"
        ? supprimerNoteLibre(entree.id)
        : saveMarqueEtude(
        { type: entree.type === "cours" ? "cours" : "lesson", slug: entree.slug },
        entree.cle,
        { signet: false, note: "" },
      ),
    onError: () => {
      toast.error(t("ca.erreur_retrait"))
    },
    onSuccess: (_reponse, entree) => {
      setAConfirmer(null)
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      queryClient.invalidateQueries({ queryKey: ["notes-a-revoir"] })
      if (entree.genre === "libre") return
      // La page du lecteur garde son propre cache de marques pour ce document.
      queryClient.invalidateQueries({ queryKey: ["etude", entree.type === "cours" ? "cours" : "lesson", entree.slug] })
    },
  })

  // La corbeille supprime le signet ET la note : une note écrite à la main ne se récupère pas,
  // on demande donc confirmation quand l'entrée en porte une (un simple signet se refait en un clic).
  const [aConfirmer, setAConfirmer] = useState<CarnetEntree | null>(null)
  function demanderRetrait(entree: CarnetEntree) {
    if (entree.note || entree.genre === "libre") setAConfirmer(entree)
    else retirer.mutate(entree)
  }

  const [recherche, setRecherche] = useState("")
  const [filtre, setFiltre] = useState<"tout" | "notes" | "signets">("tout")
  const toutes = useMemo(() => data ?? [], [data])

  // Un dossier par matière : calculé à partir de ce que l'entrée sait déjà (sa matière), sans rangement à la main.
  const { entrees, groupes } = useMemo(() => {
    const aiguille = sansAccent(recherche.trim())
    const gardees = toutes.filter((e) => {
      if (filtre === "notes" && !e.note) return false
      if (filtre === "signets" && !e.signet) return false
      if (!aiguille) return true
      return sansAccent(`${e.note} ${e.titre} ${e.matiere} ${libelleSection(e)}`).includes(aiguille)
    })
    const parMatiere = new Map<string, CarnetEntree[]>()
    for (const e of gardees) parMatiere.set(e.matiere, [...(parMatiere.get(e.matiere) ?? []), e])
    return {
      entrees: gardees,
      groupes: [...parMatiere.entries()].sort((a, b) => a[0].localeCompare(b[0])),
    }
  }, [toutes, recherche, filtre])

  if (!authLoading && !isAuthenticated) {
    return <ConnexionRequise from="/carnet" titre={t("cpt.carnet")} explication={t("carnet.intent")} />
  }

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        <NotebookPen className="size-3.5" />
        {t("cpt.carnet")}
      </p>
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("ca.titre")}</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        {t("ca.texte")}
      </p>

      {!authLoading && (
        <div className="mt-5 flex flex-wrap gap-2 print:hidden">
          <Button type="button" className="rounded-full" onClick={() => setNouvelle(true)}>
            <Plus />
            {t("ca.nouvelle_note")}
          </Button>
          {(aRevoir?.total ?? 0) > 0 && (
            <Button type="button" variant="outline" className="rounded-full" onClick={() => { setMatiereRevision(null); setRevision(true) }}>
              <Brain />
              {t("ca.reviser_bouton", { n: aRevoir?.total ?? 0 })}
            </Button>
          )}
          {toutes.length > 0 && (
            <Button type="button" variant="ghost" className="rounded-full text-muted-foreground" onClick={() => window.print()}>
              <Printer />
              {t("ca.imprimer")}
            </Button>
          )}
        </div>
      )}

      {isLoading || authLoading ? (
        <div className="mt-8 flex flex-col gap-3">
          <Skeleton className="h-28 w-full rounded-2xl" />
          <Skeleton className="h-28 w-full rounded-2xl" />
        </div>
      ) : isError ? (
        // Une panne n'est pas un carnet vide : sans ce cas, l'élève croyait avoir perdu ses notes.
        <ErreurChargement
          objet={t("ca.objet")}
          message={t("ca.message_erreur")}
          onRetry={() => refetch()}
          className="mt-8"
        />
      ) : toutes.length === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Bookmark className="size-6" />
          </span>
          <p className="mt-4 font-display text-lg font-semibold">{t("ca.vide")}</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
            {t("ca.vide_texte")}
          </p>
          <Button asChild className="mt-5 rounded-full">
            <Link to={`/${country}`}>
              {t("ca.aller_reviser")}
              <ArrowRight />
            </Link>
          </Button>
        </div>
      ) : (
        <>
        <div className="mt-6 flex flex-col gap-3 print:hidden">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
              placeholder={t("ca.recherche")}
              aria-label={t("ca.recherche")}
              className="w-full rounded-full border border-input bg-background py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring/40"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {(["tout", "notes", "signets"] as const).map((f) => (
              <button
                key={f}
                type="button"
                aria-pressed={filtre === f}
                onClick={() => setFiltre(f)}
                className={`rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors ${
                  filtre === f ? "border-primary bg-primary text-primary-foreground" : "border-border bg-card text-muted-foreground hover:border-primary/40"
                }`}
              >
                {t(`ca.filtre_${f}`)}
              </button>
            ))}
          </div>
        </div>
        {entrees.length === 0 && <p className="mt-8 text-center text-sm text-muted-foreground">{t("ca.aucun_resultat")}</p>}
        {groupes.map(([matiere, liste]) => (
        <section key={matiere} className="mt-8">
        <div className="flex items-baseline justify-between gap-2">
          <h2 className="flex items-baseline gap-2 font-display text-lg font-semibold">
            {matiere}
            <span className="text-xs font-normal text-muted-foreground">
              {t(liste.length === 1 ? "ca.compteur_un" : "ca.compteur_n", { n: liste.length })}
            </span>
          </h2>
          {liste.some((e) => e.note) && (
            <button
              type="button"
              className="inline-flex shrink-0 items-center gap-1 text-xs font-medium text-primary hover:underline print:hidden"
              onClick={() => {
                setMatiereRevision(liste[0].matiere_id)
                setRevision(true)
              }}
            >
              <Brain className="size-3.5" aria-hidden="true" />
              {t("ca.reviser_matiere")}
            </button>
          )}
        </div>
        <ul className="mt-3 flex flex-col gap-3">
          {liste.map((entree) => (
            <li
              key={`${entree.genre}-${entree.id}`}
              className="group break-inside-avoid rounded-2xl border border-border bg-card p-4 transition-colors hover:border-primary/40 sm:p-5"
            >
              <div className="flex items-start gap-3">
                <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary print:hidden">
                  {entree.type === "cours" ? <BookOpen className="size-4" /> : entree.type === "libre" ? <StickyNote className="size-4" /> : <FileText className="size-4" />}
                </span>
                <div className="min-w-0 flex-1">
                  {entree.type === "libre" ? (
                    entree.citation && <p className="text-sm italic text-muted-foreground">{entree.citation}</p>
                  ) : (
                    <>
                      <p className="text-xs text-muted-foreground">
                        {entree.type === "cours" ? t("ca.type_cours") : t("ca.type_corrige")}
                      </p>
                      <Link to={lienSection(entree)} className="mt-0.5 block font-display text-base font-semibold leading-snug hover:text-primary">
                        {entree.titre}
                      </Link>
                      <p className="mt-0.5 flex items-center gap-1.5 text-sm text-muted-foreground">
                        {entree.signet && <Bookmark className="size-3.5 shrink-0 fill-current text-gold-text" aria-label={t("ca.garde")} />}
                        {libelleSection(entree)}
                      </p>
                    </>
                  )}
                </div>
                {entree.genre === "libre" && (
                  <Button
                    type="button"
                    size="icon"
                    variant="ghost"
                    className="shrink-0 text-muted-foreground print:hidden"
                    aria-label={t("ca.modifier_aria")}
                    onClick={() => setAModifier(entree)}
                  >
                    <Pencil className="size-4" />
                  </Button>
                )}
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  className="shrink-0 text-muted-foreground hover:text-destructive print:hidden"
                  aria-label={t("ca.retirer_aria")}
                  disabled={retirer.isPending}
                  onClick={() => demanderRetrait(entree)}
                >
                  <Trash2 className="size-4" />
                </Button>
              </div>
              {entree.note && (
                <div className="mt-3 rounded-xl border border-gold/30 bg-gold/[0.06] px-4 py-3">
                  <NoteTexte texte={entree.note} />
                </div>
              )}
              {entree.type !== "libre" && (
                <Link
                  to={lienSection(entree)}
                  className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline print:hidden"
                >
                  {t("ca.rouvrir")}
                  <ArrowRight className="size-3" />
                </Link>
              )}
            </li>
          ))}
        </ul>
        </section>
        ))}
        </>
      )}

      <AjouterNoteDialog open={nouvelle} onOpenChange={setNouvelle} />
      <RevisionNotes open={revision} onOpenChange={setRevision} matiereId={matiereRevision} />
      <AjouterNoteDialog
        open={aModifier !== null}
        onOpenChange={(ouvert) => !ouvert && setAModifier(null)}
        edition={aModifier ? { id: aModifier.id, note: aModifier.note, citation: aModifier.citation } : undefined}
      />

      <Dialog open={aConfirmer !== null} onOpenChange={(ouvert) => !ouvert && setAConfirmer(null)}>
        <DialogContent>
          <DialogTitle>{t("ca.dialogue_titre")}</DialogTitle>
          <DialogDescription>
            {t("ca.dialogue_texte")}
          </DialogDescription>
          <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button variant="outline" onClick={() => setAConfirmer(null)}>
              {t("ca.garder")}
            </Button>
            <Button
              variant="destructive"
              disabled={retirer.isPending}
              onClick={() => aConfirmer && retirer.mutate(aConfirmer)}
            >
              {retirer.isPending ? t("ca.suppression") : t("ca.retirer")}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
