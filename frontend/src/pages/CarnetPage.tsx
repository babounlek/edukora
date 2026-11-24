import { useEffect, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"

import { ConnexionRequise } from "@/components/ConnexionRequise"
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowLeft, ArrowRight, Bookmark, BookOpen, FileText, Brain, Folder, NotebookPen, Pencil, Pin, Plus, Printer, Search, StickyNote, Trash2 } from "lucide-react"
import { toast } from "sonner"

import { creerNoteLibre, epinglerNote, getCarnetDossiers, getCarnetPage, getNotesARevoir, saveMarqueEtude, supprimerNoteLibre } from "@/api/endpoints"
import type { CarnetEntree } from "@/api/types"
import { COURS_SECTION_LABELS } from "@/components/CoursSection"
import { AjouterNoteDialog } from "@/components/AjouterNoteDialog"
import { ErreurChargement } from "@/components/ErreurChargement"
import { BoutonPartager } from "@/components/BoutonPartager"
import { ImageNote } from "@/components/ImageNote"
import { NoteTexte } from "@/components/NoteTexte"
import { RevisionNotes } from "@/components/RevisionNotes"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { coursReaderPath, epreuveReaderPath } from "@/lib/countryPath"
import { useSeo } from "@/lib/seo"
import { cheminPublicDeLaSource, texteDeNotePartagee } from "@/lib/partageNote"
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

  // Deux niveaux : la grille des dossiers (un résumé par matière), puis les notes d'un dossier, 20 à la fois. Une
  // recherche sort des dossiers et fouille toutes les matières.
  const { data: resume, isLoading, isError, refetch } = useQuery({
    queryKey: ["carnet", "dossiers"],
    queryFn: ({ signal }) => getCarnetDossiers(signal),
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
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      queryClient.invalidateQueries({ queryKey: ["notes-a-revoir"] })
      // Pas de fenêtre de confirmation : on supprime, et un message permet de revenir en arrière quelques secondes.
      toast(t("ca.note_supprimee"), { duration: 7000, action: { label: t("seance.annuler"), onClick: () => void restaurer(entree) } })
      if (entree.genre === "libre") return
      // La page du lecteur garde son propre cache de marques pour ce document.
      queryClient.invalidateQueries({ queryKey: ["etude", entree.type === "cours" ? "cours" : "lesson", entree.slug] })
    },
  })

  /** « Annuler » après une suppression : la note revient avec son texte, sa citation et son épingle (pas son calendrier de révision). */
  async function restaurer(entree: CarnetEntree) {
    try {
      if (entree.genre === "libre") {
        const neuve = await creerNoteLibre(entree.matiere_id, entree.note, entree.citation, entree.origine ?? "", entree.source ?? "")
        if (entree.epingle) await epinglerNote("libre", neuve.id, true)
      } else {
        await saveMarqueEtude(
          { type: entree.type === "cours" ? "cours" : "lesson", slug: entree.slug },
          entree.cle,
          { signet: entree.signet, note: entree.note },
        )
        queryClient.invalidateQueries({ queryKey: ["etude", entree.type === "cours" ? "cours" : "lesson", entree.slug] })
      }
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      queryClient.invalidateQueries({ queryKey: ["notes-a-revoir"] })
    } catch {
      toast.error(t("ca.note_erreur"))
    }
  }
  const demanderRetrait = (entree: CarnetEntree) => retirer.mutate(entree)

  const [recherche, setRecherche] = useState("")
  const [aiguille, setAiguille] = useState("")
  // La recherche part au serveur : on attend une courte pause de frappe plutôt qu'une requête par lettre.
  useEffect(() => {
    const m = window.setTimeout(() => setAiguille(recherche.trim()), 250)
    return () => window.clearTimeout(m)
  }, [recherche])
  const [filtre, setFiltre] = useState<"tout" | "notes" | "signets" | "epinglees">("tout")
  const [tri, setTri] = useState<"recent" | "a_reviser">("recent")
  // Le dossier ouvert vit dans l'adresse (?dossier=<matière>) : le bouton Retour du téléphone revient à la grille.
  const dossierId = Number(params.get("dossier")) || null
  function ouvrirDossier(id: number | null) {
    const p = new URLSearchParams(params)
    if (id === null) p.delete("dossier")
    else p.set("dossier", String(id))
    setParams(p)
    setFiltre("tout")
    setTri("recent")
  }
  const dossiers = resume?.dossiers ?? []
  const dossier = dossiers.find((d) => d.matiere_id === dossierId) ?? null
  // Un dossier qui n'existe plus (dernière note retirée) ramène à la grille.
  useEffect(() => {
    if (resume && dossierId !== null && !dossier) {
      const p = new URLSearchParams(params)
      p.delete("dossier")
      setParams(p, { replace: true })
    }
  }, [resume, dossierId, dossier, params, setParams])
  const enListe = dossierId !== null || aiguille !== ""

  const pages = useInfiniteQuery({
    queryKey: ["carnet", "page", { dossierId, filtre, tri, aiguille }],
    queryFn: ({ pageParam, signal }) => getCarnetPage({ matiere: dossierId, filtre, q: aiguille, tri, page: pageParam }, signal),
    initialPageParam: 1,
    getNextPageParam: (derniere) => (derniere.page * derniere.page_size < derniere.count ? derniere.page + 1 : undefined),
    enabled: isAuthenticated && enListe,
  })
  const entrees = pages.data?.pages.flatMap((p) => p.results) ?? []
  const nombre = pages.data?.pages[0]?.count ?? 0

  // Imprimer un dossier : on charge d'abord toutes ses pages, sinon seules les 20 premières notes sortiraient.
  const [impression, setImpression] = useState(false)
  async function imprimerDossier() {
    setImpression(true)
    try {
      let suite = pages.hasNextPage
      while (suite) suite = (await pages.fetchNextPage()).hasNextPage
      window.setTimeout(() => window.print(), 150)
    } finally {
      setImpression(false)
    }
  }
  const epingler = useMutation({
    mutationFn: (entree: CarnetEntree) => epinglerNote(entree.genre, entree.id, !entree.epingle),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["carnet"] }),
    onError: () => toast.error(t("ca.note_erreur")),
  })
  const aDesEpinglees = dossier ? dossier.epingles > 0 : dossiers.some((d) => d.epingles > 0)
  const aDesDues = dossier ? dossier.a_reviser > 0 : dossiers.some((d) => d.a_reviser > 0)

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
      ) : (resume?.total ?? 0) === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Bookmark className="size-6" />
          </span>
          <p className="mt-4 font-display text-lg font-semibold">{t("ca.vide")}</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">{t("ca.vide_texte")}</p>
          <ol className="mx-auto mt-4 flex max-w-sm list-none flex-col gap-2.5 text-left text-sm">
            {(["ca.vide_1", "ca.vide_2", "ca.vide_3"] as const).map((cle, i) => (
              <li key={cle} className="flex items-start gap-3">
                <span className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                  {i + 1}
                </span>
                <span>{t(cle)}</span>
              </li>
            ))}
          </ol>
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
          {enListe && (
            <div className="flex flex-wrap items-center gap-2">
              {(["tout", "notes", "signets", "epinglees"] as const)
                .filter((f) => f !== "epinglees" || aDesEpinglees || filtre === "epinglees")
                .map((f) => (
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
              {aDesDues && (
                <button
                  type="button"
                  aria-pressed={tri === "a_reviser"}
                  onClick={() => setTri(tri === "a_reviser" ? "recent" : "a_reviser")}
                  className={`ml-auto rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors ${
                    tri === "a_reviser" ? "border-primary bg-primary text-primary-foreground" : "border-border bg-card text-muted-foreground hover:border-primary/40"
                  }`}
                >
                  {t("ca.tri_a_reviser")}
                </button>
              )}
            </div>
          )}
        </div>

        {!enListe && (
          <ul className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {dossiers.map((d) => (
              <li key={d.matiere_id}>
                <button
                  type="button"
                  onClick={() => ouvrirDossier(d.matiere_id)}
                  className="flex h-full w-full items-start gap-3 rounded-2xl border border-border bg-card p-4 text-left transition-colors hover:border-primary/40 sm:p-5"
                >
                  <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Folder className="size-5" aria-hidden="true" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block font-display text-base font-semibold leading-snug">{d.matiere}</span>
                    <span className="mt-0.5 block text-xs text-muted-foreground">
                      {t(d.total === 1 ? "ca.compteur_un" : "ca.compteur_n", { n: d.total })}
                    </span>
                    {(d.a_reviser > 0 || d.epingles > 0) && (
                      <span className="mt-2 flex flex-wrap gap-1.5">
                        {d.a_reviser > 0 && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                            <Brain className="size-3" aria-hidden="true" />
                            {t("ca.dossier_a_reviser", { n: d.a_reviser })}
                          </span>
                        )}
                        {d.epingles > 0 && (
                          <span className="inline-flex items-center gap-1 rounded-full bg-gold/15 px-2 py-0.5 text-xs font-medium text-gold-text">
                            <Pin className="size-3 fill-current" aria-hidden="true" />
                            {d.epingles}
                          </span>
                        )}
                      </span>
                    )}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}

        {enListe && (
        <section className="mt-6">
        {dossierId !== null && dossiers.length > 1 && (
          // Passer d'une matière à l'autre sans repasser par la grille ; la pastille active se centre d'elle-même.
          <nav aria-label={t("ca.dossiers_aria")} className="relative -mx-4 mb-4 flex gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:px-0 print:hidden">
            {dossiers.map((d) => {
              const actif = d.matiere_id === dossierId
              return (
                <button
                  key={d.matiere_id}
                  type="button"
                  aria-current={actif ? "true" : undefined}
                  ref={(el) => {
                    // Défilement de la rangée seule : scrollIntoView aurait aussi fait bouger la page.
                    const rangee = el?.parentElement
                    if (actif && el && rangee) rangee.scrollLeft = el.offsetLeft - (rangee.clientWidth - el.offsetWidth) / 2
                  }}
                  onClick={() => !actif && ouvrirDossier(d.matiere_id)}
                  className={`inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors ${
                    actif ? "border-primary bg-primary text-primary-foreground" : "border-border bg-card text-muted-foreground hover:border-primary/40"
                  }`}
                >
                  {d.matiere}
                  <span className={actif ? "text-primary-foreground/80" : "text-muted-foreground/70"}>{d.total}</span>
                  {d.a_reviser > 0 && (
                    <span className="size-1.5 rounded-full bg-gold" role="img" aria-label={t("ca.dossier_a_reviser", { n: d.a_reviser })} />
                  )}
                </button>
              )
            })}
          </nav>
        )}
        <div className="flex flex-wrap items-center justify-between gap-2 print:hidden">
          {dossierId !== null ? (
            <button
              type="button"
              onClick={() => ouvrirDossier(null)}
              className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
            >
              <ArrowLeft className="size-4" aria-hidden="true" />
              {t("ca.tous_dossiers")}
            </button>
          ) : (
            <span />
          )}
          {dossier && (
            <div className="flex items-center gap-3">
              {dossier.avec_note > 0 && (
                <button
                  type="button"
                  className="inline-flex shrink-0 items-center gap-1 text-xs font-medium text-primary hover:underline"
                  onClick={() => {
                    setMatiereRevision(dossier.matiere_id)
                    setRevision(true)
                  }}
                >
                  <Brain className="size-3.5" aria-hidden="true" />
                  {t("ca.reviser_matiere")}
                </button>
              )}
              <button
                type="button"
                aria-label={t("ca.imprimer_dossier")}
                title={t("ca.imprimer_dossier")}
                disabled={impression}
                className="inline-flex shrink-0 items-center text-muted-foreground hover:text-primary"
                onClick={imprimerDossier}
              >
                <Printer className="size-3.5" aria-hidden="true" />
              </button>
            </div>
          )}
        </div>
        <h2 className="mt-2 flex items-baseline gap-2 font-display text-lg font-semibold">
          {dossier ? dossier.matiere : t("ca.resultats")}
          {pages.data && (
            <span className="text-xs font-normal text-muted-foreground">
              {t(nombre === 1 ? "ca.compteur_un" : "ca.compteur_n", { n: nombre })}
            </span>
          )}
        </h2>
        {pages.isError ? (
          <ErreurChargement objet={t("ca.objet")} message={t("ca.message_erreur")} onRetry={() => pages.refetch()} className="mt-4" />
        ) : pages.isLoading ? (
          <div className="mt-4 flex flex-col gap-3">
            <Skeleton className="h-28 w-full rounded-2xl" />
            <Skeleton className="h-28 w-full rounded-2xl" />
          </div>
        ) : entrees.length === 0 ? (
          <p className="mt-8 text-center text-sm text-muted-foreground">{t("ca.aucun_resultat")}</p>
        ) : null}
        <ul className="mt-3 flex flex-col gap-3">
          {entrees.map((entree) => (
            <li
              key={`${entree.genre}-${entree.id}`}
              className="group break-inside-avoid rounded-2xl border border-border bg-card p-4 transition-colors hover:border-primary/40 sm:p-5"
            >
              <div className="flex items-start gap-3">
                <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary print:hidden">
                  {entree.type === "cours" ? <BookOpen className="size-4" /> : entree.type === "libre" ? <StickyNote className="size-4" /> : <FileText className="size-4" />}
                </span>
                <div className="min-w-0 flex-1">
                  {dossierId === null && <p className="text-xs font-medium text-primary">{entree.matiere}</p>}
                  {entree.origine === "quiz" && (
                    <p className="text-xs text-muted-foreground">{t("ca.origine_quiz")}</p>
                  )}
                  {entree.type === "libre" ? (
                    entree.citation && <NoteTexte texte={entree.citation} className="italic text-muted-foreground" />
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
                {(entree.note || entree.genre === "libre") && (
                  <Button
                    type="button"
                    size="icon"
                    variant="ghost"
                    aria-pressed={entree.epingle}
                    className={`shrink-0 print:hidden ${entree.epingle ? "text-gold-text" : "text-muted-foreground"}`}
                    aria-label={t(entree.epingle ? "ca.desepingler" : "ca.epingler")}
                    disabled={epingler.isPending}
                    onClick={() => epingler.mutate(entree)}
                  >
                    <Pin className={`size-4 ${entree.epingle ? "fill-current" : ""}`} />
                  </Button>
                )}
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
              {entree.genre === "libre" && entree.a_image && (
                <div className="mt-3">
                  <ImageNote noteId={entree.id} version={entree.updated_at ?? undefined} />
                </div>
              )}
              {entree.genre === "libre" && entree.source && (
                <Link
                  to={entree.source}
                  className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline print:hidden"
                >
                  {t("ca.rouvrir_source")}
                  <ArrowRight className="size-3" />
                </Link>
              )}
              {(entree.note || entree.citation) && (
                <BoutonPartager
                  chemin={cheminPublicDeLaSource(entree.type === "libre" ? entree.source : lienSection(entree))}
                  texte={texteDeNotePartagee({ matiere: entree.matiere, note: entree.note, citation: entree.citation }, t("ca.partage_entete"))}
                  type="note"
                  variant="ghost"
                  className="-ml-2 mt-2 text-muted-foreground print:hidden"
                />
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
        {pages.hasNextPage && (
          <div className="mt-5 flex justify-center print:hidden">
            <Button type="button" variant="outline" className="rounded-full" disabled={pages.isFetchingNextPage} onClick={() => pages.fetchNextPage()}>
              {t("ca.voir_suite")}
              <span className="text-muted-foreground">({nombre - entrees.length})</span>
            </Button>
          </div>
        )}
        </section>
        )}
        </>
      )}

      <AjouterNoteDialog open={nouvelle} onOpenChange={setNouvelle} matiereParDefaut={dossier ? { id: dossier.matiere_id, label: dossier.matiere } : null} />
      <RevisionNotes open={revision} onOpenChange={setRevision} matiereId={matiereRevision} />
      <AjouterNoteDialog
        open={aModifier !== null}
        onOpenChange={(ouvert) => !ouvert && setAModifier(null)}
        edition={
          aModifier
            ? { id: aModifier.id, note: aModifier.note, citation: aModifier.citation, aImage: aModifier.a_image, version: aModifier.updated_at ?? undefined }
            : undefined
        }
      />
    </div>
  )
}
