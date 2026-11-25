import { useEffect, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"

import { ConnexionRequise } from "@/components/ConnexionRequise"
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowLeft, ArrowRight, BadgeCheck, Bookmark, Brain, CheckCircle2, NotebookPen, Pin, Plus, Printer, Search } from "lucide-react"
import { toast } from "sonner"

import {
  creerNoteLibre, epinglerNote, getCarnetDossiers, getCarnetPage, getNotesARevoir, saveMarqueEtude, supprimerNoteLibre,
} from "@/api/endpoints"
import type { CarnetEntree } from "@/api/types"
import { AjouterNoteDialog } from "@/components/AjouterNoteDialog"
import { ApercuFiches, useApercuFiches } from "@/components/ApercuFiches"
import { ErreurChargement } from "@/components/ErreurChargement"
import { NoteTexte } from "@/components/NoteTexte"
import { CarteDossier } from "@/components/notes/CarteDossier"
import { CarteNote } from "@/components/notes/CarteNote"
import { NotesImprimees } from "@/components/notes/NotesImprimees"
import { RevisionNotes } from "@/components/RevisionNotes"
import { ReviserTabs } from "@/components/ReviserTabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { libelleCursus } from "@/lib/cursus"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

type Filtre = "tout" | "notes" | "signets" | "epinglees"

/**
 * « Mes notes » : le classeur de l'élève. En haut, ce qu'il y a à relire aujourd'hui (la raison de revenir) ; puis ses
 * notes épinglées, à portée de main ; puis un dossier par matière, à la couleur de la matière. Un dossier ouvert montre
 * ses notes comme des feuilles de cahier, vingt à la fois.
 *
 * C'est ce qui donne un sens aux notes : une remarque écrite au fond d'un cours qu'on ne rouvrira jamais ne sert à
 * personne. Regroupées ici, elles deviennent la fiche de révision que l'élève s'est écrite lui-même.
 */
export function CarnetPage() {
  useI18n()
  useSeo({ title: t("cpt.carnet") })
  const queryClient = useQueryClient()
  const { isAuthenticated, isLoading: authLoading, user } = useAuth()
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

  const [recherche, setRecherche] = useState("")
  const [aiguille, setAiguille] = useState("")
  // La recherche part au serveur : on attend une courte pause de frappe plutôt qu'une requête par lettre.
  useEffect(() => {
    const m = window.setTimeout(() => setAiguille(recherche.trim()), 250)
    return () => window.clearTimeout(m)
  }, [recherche])
  const [filtre, setFiltre] = useState<Filtre>("tout")
  const [tri, setTri] = useState<"recent" | "a_reviser">("recent")
  // Le dossier ouvert vit dans l'adresse (?dossier=<matière>) : le bouton Retour du téléphone revient à la grille.
  const dossierId = Number(params.get("dossier")) || null
  function ouvrirDossier(id: number | null, filtreInitial: Filtre = "tout") {
    const p = new URLSearchParams(params)
    if (id === null) p.delete("dossier")
    else p.set("dossier", String(id))
    setParams(p)
    setFiltre(filtreInitial)
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

  const totalEpingles = dossiers.reduce((s, d) => s + d.epingles, 0)
  // L'étagère des épinglées, sur la grille : les notes que l'élève veut garder sous la main, toutes matières confondues.
  const { data: epinglees } = useQuery({
    queryKey: ["carnet", "page", "etagere-epinglees"],
    queryFn: ({ signal }) => getCarnetPage({ matiere: null, filtre: "epinglees", q: "", tri: "recent", page: 1 }, signal),
    enabled: isAuthenticated && !enListe && totalEpingles > 0,
  })

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
  const nonAbonne = !authLoading && !user?.a_un_abonnement_actif
  const apercu = useApercuFiches(country)
  const apercuMontre = nonAbonne && (apercu?.fiches.length ?? 0) > 0
  const aDesEpinglees = dossier ? dossier.epingles > 0 : totalEpingles > 0
  const aDesDues = dossier ? dossier.a_reviser > 0 : dossiers.some((d) => d.a_reviser > 0)

  if (!authLoading && !isAuthenticated) {
    // Le visiteur ne bute pas sur un mur : sous l'invitation à se connecter, les fiches gratuites se lisent tout de suite.
    return (
      <>
        <ConnexionRequise from="/carnet" titre={t("cpt.carnet")} explication={t("carnet.intent")} />
        <ApercuFiches country={country} className="mx-auto max-w-5xl px-4 pb-12 sm:px-6" />
      </>
    )
  }

  const total = resume?.total ?? 0
  const dues = aRevoir?.total ?? 0
  const reviserTout = () => {
    setMatiereRevision(null)
    setRevision(true)
  }
  const pastille = (actif: boolean) =>
    cn(
      "rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors",
      actif ? "border-primary bg-primary text-primary-foreground" : "border-border bg-card text-muted-foreground hover:border-primary/40",
    )
  const IconeDossier = dossier ? subjectIcon(dossier.matiere_code ?? "") : null

  return (
    <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-10 print:max-w-none print:p-0">
      {/* Sur papier, seule cette feuille sort : la page de l'écran, faite pour le doigt, est masquée en entier. */}
      {enListe && (
        <NotesImprimees
          titre={dossier ? dossier.matiere : t("ca.resultats")}
          entrees={entrees}
          eleve={user?.profil_actif?.prenom || user?.full_name || undefined}
          examen={user?.cursus_prepare ? libelleCursus(user.cursus_prepare) : undefined}
        />
      )}
      {/* Sur la grille des dossiers il n'y a pas de feuille : la page s'imprime telle quelle (sans ses boutons). */}
      <div className={enListe ? "print:hidden" : undefined}>
      <div className="print:hidden">
        <ReviserTabs />
      </div>

      {/* Le bandeau : ce que l'élève a gardé, et surtout ce qu'il a à relire aujourd'hui. Réduit à une ligne dès qu'on entre
          dans un dossier ou une recherche : la place est alors aux notes. */}
      {enListe ? (
        <div className="flex items-center justify-between gap-3 print:hidden">
          <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <NotebookPen className="size-3.5" aria-hidden="true" />
            {t("cpt.carnet")}
          </p>
          <div className="flex items-center gap-2">
            {dues > 0 && (
              <Button type="button" size="sm" variant="outline" className="rounded-full" onClick={reviserTout}>
                <Brain />
                {dues}
              </Button>
            )}
            <Button type="button" size="sm" className="rounded-full" onClick={() => setNouvelle(true)}>
              <Plus />
              {t("ca.nouvelle_note")}
            </Button>
          </div>
        </div>
      ) : (
        <header className="relative animate-fade-up overflow-hidden rounded-3xl bg-primary px-5 py-6 text-primary-foreground shadow-xl shadow-primary/20 sm:px-9 sm:py-9 print:hidden">
          <div
            aria-hidden="true"
            className="absolute inset-0 opacity-[0.08]"
            style={{ backgroundImage: "repeating-linear-gradient(to bottom, transparent 0 27px, currentColor 27px 28px)" }}
          />
          <div aria-hidden="true" className="absolute -right-16 -top-24 size-72 rounded-full bg-gold/30 blur-3xl" />
          <div aria-hidden="true" className="absolute inset-y-0 left-[4.5rem] hidden w-px bg-gold/40 sm:block" />
          <div className="relative grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
            <div className="sm:pl-16">
              <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-primary-foreground/70">
                <NotebookPen className="size-3.5" aria-hidden="true" />
                {t("cpt.carnet")}
              </p>
              <h1 className="mt-2 font-display text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl">{t("ca.titre")}</h1>
              <p className="mt-3 max-w-md text-sm text-primary-foreground/75">{t("ca.texte")}</p>
              <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-3">
                <Button
                  type="button"
                  className="rounded-full bg-gold text-gold-foreground shadow-lg shadow-black/10 hover:bg-gold/90"
                  onClick={() => setNouvelle(true)}
                >
                  <Plus />
                  {t("ca.nouvelle_note")}
                </Button>
                {total > 0 && (
                  <p className="text-sm tabular-nums text-primary-foreground/75">
                    {tn("ca.stat_notes", total)} · {tn("ca.stat_dossiers", dossiers.length)}
                  </p>
                )}
              </div>
            </div>
            {total > 0 && (
              <div className="rounded-2xl bg-primary-foreground/10 p-4 ring-1 ring-primary-foreground/15 backdrop-blur-sm sm:p-5 lg:w-72">
                {dues > 0 ? (
                  <>
                    <p className="flex items-baseline gap-2.5">
                      <span className="font-display text-5xl font-semibold leading-none tabular-nums">{dues}</span>
                      <span className="text-sm leading-snug text-primary-foreground/80">{tn("ca.hero_dues", dues)}</span>
                    </p>
                    <Button
                      type="button"
                      className="mt-4 w-full rounded-full bg-primary-foreground text-primary hover:bg-primary-foreground/90"
                      onClick={reviserTout}
                    >
                      <Brain />
                      {t("ca.hero_reviser")}
                    </Button>
                  </>
                ) : (
                  <p className="flex items-start gap-3 text-sm leading-snug">
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-gold" aria-hidden="true" />
                    <span>
                      <span className="block font-display text-lg font-semibold">{t("ca.hero_a_jour")}</span>
                      <span className="text-primary-foreground/75">{t("ca.hero_a_jour_texte")}</span>
                    </span>
                  </p>
                )}
              </div>
            )}
          </div>
        </header>
      )}

      {isLoading || authLoading ? (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-36 w-full rounded-2xl" />
          ))}
        </div>
      ) : isError ? (
        // Une panne n'est pas un carnet vide : sans ce cas, l'élève croyait avoir perdu ses notes.
        <ErreurChargement objet={t("ca.objet")} message={t("ca.message_erreur")} onRetry={() => refetch()} className="mt-8" />
      ) : total === 0 ? (
        <>
        <div className="mt-8 animate-fade-up rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Bookmark className="size-6" />
          </span>
          <p className="mt-4 font-display text-xl font-semibold">{t("ca.vide")}</p>
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
        {nonAbonne && <ApercuFiches country={country} className="mt-10 print:hidden" />}
        </>
      ) : (
        <>
          <div className="relative mt-5 print:hidden">
            <Search className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
              placeholder={t("ca.recherche")}
              aria-label={t("ca.recherche")}
              className="w-full rounded-full border border-input bg-card py-3 pl-11 pr-4 text-sm shadow-sm outline-none transition-colors focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring/40"
            />
          </div>

          {!enListe && (
            <>
              {epinglees && epinglees.results.length > 0 && (
                <section className="mt-8 print:hidden" aria-label={t("ca.epinglees_titre")}>
                  <h2 className="flex items-center gap-2 font-sans text-xs font-semibold uppercase tracking-[0.18em] text-gold-text">
                    <Pin className="size-3.5 -rotate-45 fill-current" aria-hidden="true" />
                    {t("ca.epinglees_titre")}
                  </h2>
                  <ul className="-mx-4 mt-3 flex snap-x gap-3 overflow-x-auto overflow-y-hidden px-4 pb-2 pt-1 sm:mx-0 sm:px-0">
                    {epinglees.results.map((e, i) => (
                      <li key={`${e.genre}-${e.id}`} className="w-64 shrink-0 snap-start">
                        <button
                          type="button"
                          onClick={() => ouvrirDossier(e.matiere_id, "epinglees")}
                          style={{ animationDelay: `${i * 50}ms` }}
                          className="relative flex h-full w-full animate-fade-up flex-col overflow-hidden rounded-2xl border border-gold/40 bg-gradient-to-br from-gold/[0.14] to-gold/[0.04] p-4 text-left transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-gold/15"
                        >
                          <span className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                            <span className={cn("size-2 rounded-full", couleurMatiere(e.matiere_code).barre)} aria-hidden="true" />
                            {e.matiere}
                          </span>
                          <span className="relative mt-2 block max-h-[5.2rem] overflow-hidden [mask-image:linear-gradient(to_bottom,black_65%,transparent)]">
                            <NoteTexte texte={e.note || e.citation || e.titre} />
                          </span>
                        </button>
                      </li>
                    ))}
                  </ul>
                </section>
              )}

              {/* Les fiches toutes faites d'EduKora : à garder dans ses notes d'un toucher. Sans abonnement, quelques-unes se
                  lisent ici même. */}
              {apercuMontre && <ApercuFiches country={country} className="mt-8 print:hidden" />}
              {!apercuMontre && <Link
                to="/fiches-edukora"
                className="group mt-8 flex items-center gap-4 rounded-2xl border border-gold/40 bg-gradient-to-r from-gold/[0.14] to-transparent p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-gold/15 sm:p-5 print:hidden"
              >
                <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-gold text-gold-foreground">
                  <BadgeCheck className="size-5" aria-hidden="true" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block font-display text-lg font-semibold leading-tight">{t("fe.titre")}</span>
                  <span className="mt-0.5 block text-sm text-muted-foreground">{t("fe.accroche")}</span>
                </span>
                <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
              </Link>}

              <section className="mt-8" aria-label={t("ca.dossiers_titre")}>
                <h2 className="font-sans text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground print:hidden">{t("ca.dossiers_titre")}</h2>
                <ul className="mt-2 grid gap-x-4 gap-y-3 sm:grid-cols-2 lg:grid-cols-3">
                  {dossiers.map((d, i) => (
                    <li key={d.matiere_id}>
                      <CarteDossier dossier={d} rang={i} onOuvrir={() => ouvrirDossier(d.matiere_id)} />
                    </li>
                  ))}
                </ul>
              </section>
            </>
          )}

          {enListe && (
            <section className="mt-5">
              {dossierId !== null && dossiers.length > 1 && (
                // Passer d'une matière à l'autre sans repasser par la grille ; la pastille active se centre d'elle-même.
                <nav aria-label={t("ca.dossiers_aria")} className="relative -mx-4 mb-5 flex gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:px-0 print:hidden">
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
                        className={cn("inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap", pastille(actif))}
                      >
                        <span className={cn("size-2 rounded-full", actif ? "bg-primary-foreground" : couleurMatiere(d.matiere_code).barre)} aria-hidden="true" />
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

              {/* Sur sa propre ligne : à côté du titre, il se coupait en deux sur téléphone. */}
              {dossierId !== null && (
                <button
                  type="button"
                  onClick={() => ouvrirDossier(null)}
                  className="mb-3 inline-flex items-center gap-1 whitespace-nowrap text-xs font-medium text-primary hover:underline print:hidden"
                >
                  <ArrowLeft className="size-3.5" aria-hidden="true" />
                  {t("ca.tous_dossiers")}
                </button>
              )}
              <div className="flex flex-wrap items-center gap-x-4 gap-y-3">
                {dossier && IconeDossier && (
                  <span className={cn("flex size-14 shrink-0 items-center justify-center rounded-2xl print:hidden", couleurMatiere(dossier.matiere_code).puce)}>
                    <IconeDossier className="size-7" aria-hidden="true" />
                  </span>
                )}
                <div className="min-w-0 flex-1">
                  <h2 className="font-display text-2xl font-semibold leading-tight tracking-tight sm:text-3xl print:text-xl">
                    {dossier ? dossier.matiere : t("ca.resultats")}
                  </h2>
                  {pages.data && (
                    <p className="text-xs text-muted-foreground">{t(nombre === 1 ? "ca.compteur_un" : "ca.compteur_n", { n: nombre })}</p>
                  )}
                </div>
                {dossier && (
                  <div className="flex items-center gap-1.5 print:hidden">
                    {dossier.avec_note > 0 && (
                      <Button
                        type="button"
                        variant={dossier.a_reviser > 0 ? "default" : "outline"}
                        size="sm"
                        className="rounded-full"
                        onClick={() => {
                          setMatiereRevision(dossier.matiere_id)
                          setRevision(true)
                        }}
                      >
                        <Brain />
                        {t("ca.reviser_matiere")}
                      </Button>
                    )}
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      aria-label={t("ca.imprimer_dossier")}
                      title={t("ca.imprimer_dossier")}
                      disabled={impression}
                      className="text-muted-foreground"
                      onClick={imprimerDossier}
                    >
                      <Printer />
                    </Button>
                  </div>
                )}
              </div>

              <div className="mt-4 flex flex-wrap items-center gap-2 print:hidden">
                {(["tout", "notes", "signets", "epinglees"] as const)
                  .filter((f) => f !== "epinglees" || aDesEpinglees || filtre === "epinglees")
                  .map((f) => (
                    <button key={f} type="button" aria-pressed={filtre === f} onClick={() => setFiltre(f)} className={pastille(filtre === f)}>
                      {t(`ca.filtre_${f}`)}
                    </button>
                  ))}
                {aDesDues && (
                  <button
                    type="button"
                    aria-pressed={tri === "a_reviser"}
                    onClick={() => setTri(tri === "a_reviser" ? "recent" : "a_reviser")}
                    className={cn("ml-auto", pastille(tri === "a_reviser"))}
                  >
                    {t("ca.tri_a_reviser")}
                  </button>
                )}
              </div>

              {pages.isError ? (
                <ErreurChargement objet={t("ca.objet")} message={t("ca.message_erreur")} onRetry={() => pages.refetch()} className="mt-4" />
              ) : pages.isLoading ? (
                <div className="mt-4 grid items-start gap-4 lg:grid-cols-2">
                  <Skeleton className="h-36 w-full rounded-2xl" />
                  <Skeleton className="h-28 w-full rounded-2xl" />
                </div>
              ) : entrees.length === 0 ? (
                <p className="mt-10 text-center text-sm text-muted-foreground">{t("ca.aucun_resultat")}</p>
              ) : null}

              {/* Deux colonnes sur grand écran, chaque feuille à sa hauteur : on embrasse plus de notes d'un regard. */}
              <ul className="mt-4 grid items-start gap-4 lg:grid-cols-2 print:block print:[&>li]:mb-3">
                {entrees.map((entree, i) => (
                  <CarteNote
                    key={`${entree.genre}-${entree.id}`}
                    entree={entree}
                    dansDossier={dossierId !== null}
                    rang={i % 20}
                    occupe={epingler.isPending || retirer.isPending}
                    onEpingler={() => epingler.mutate(entree)}
                    onModifier={() => setAModifier(entree)}
                    onRetirer={() => retirer.mutate(entree)}
                  />
                ))}
              </ul>
              {pages.hasNextPage && (
                <div className="mt-6 flex justify-center print:hidden">
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

      </div>

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
