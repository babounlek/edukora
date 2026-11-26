import { useEffect, useMemo, useRef, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, BadgeCheck, Check, Crown, GraduationCap, Layers, Lock, NotebookPen, Printer, Search } from "lucide-react"
import { toast } from "sonner"

import { garderFiche, getFiches, getFichesMatieres, situerFiche } from "@/api/endpoints"
import type { FicheEdukora } from "@/api/types"
import { ApercuFiches } from "@/components/ApercuFiches"
import { ErreurChargement } from "@/components/ErreurChargement"
import { BlocsFiche, Sessions } from "@/components/fiches/BlocsFiche"
import { FichesImprimees } from "@/components/fiches/FichesImprimees"
import { NoteTexte } from "@/components/NoteTexte"
import { ReviserTabs } from "@/components/ReviserTabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { trackEvent } from "@/lib/analytics"
import { coursListPath, epreuveDetailPath } from "@/lib/countryPath"
import { useCursusDeclare } from "@/lib/cursusAccueil"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { useImpression } from "@/lib/useImpression"
import { grouperParRubrique } from "@/lib/rubriquesFiches"
import { CLE_NOTES_DUES } from "@/lib/notesDues"
import { subjectIcon } from "@/lib/subjectIcon"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

function sansAccent(s: string): string {
  return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
}

/**
 * D'une fiche vers le quiz de sa notion, son cours et les sujets dont elle est tirée. Les fiches formaient une île : on y
 * entrait, on n'en sortait nulle part (audit du 2026-11-25). Un lien n'est montré que s'il mène à quelque chose.
 */
function PassagesDeLaFiche({ fiche, cursus, pays }: { fiche: FicheEdukora; cursus: number; pays: string }) {
  const theme = fiche.theme
  const sources = (fiche.sources ?? []).slice(0, 4)
  const lien = "inline-flex min-h-9 items-center font-medium text-primary underline-offset-4 hover:underline"
  if (!theme?.a_quiz && !theme?.a_cours && sources.length === 0) return null
  return (
    <div className="mt-1 flex flex-wrap items-center gap-x-4 text-xs">
      {theme?.a_quiz && (
        <Link to={`/quiz?cursus=${cursus}&theme=${theme.id}`} className={lien}>
          {t("fe.quiz")}
        </Link>
      )}
      {theme?.a_cours && (
        <Link to={`${coursListPath(pays)}?theme=${theme.id}`} className={lien}>
          {t("fe.cours")}
        </Link>
      )}
      {sources.length > 0 && (
        <span className="flex flex-wrap items-center gap-x-2 text-muted-foreground">
          {t("fe.sujets")}
          {sources.map((s) => (
            <Link
              key={s.slug}
              to={epreuveDetailPath(pays, s.slug)}
              className={lien}
              title={s.titre}
              aria-label={t("fe.voir_sujet", { annee: s.annee ?? s.titre })}
            >
              {s.annee ?? s.titre}
            </Link>
          ))}
        </span>
      )}
    </div>
  )
}

/**
 * « Fiches EduKora » : des fiches de révision toutes faites, à côté des notes que l'élève écrit lui-même. Une notion par
 * fiche (une définition d'éducation civique, par exemple), dite en quelques lignes, avec les sessions où elle est tombée.
 * « Garder dans mes notes » la copie dans le dossier de sa matière : elle entre alors dans la révision espacée.
 *
 * Quelques fiches par matière se lisent sans abonnement ; les autres montrent leur terme et leurs sessions, pas leur
 * définition. En développement, une fiche pas encore relue par un enseignant s'affiche avec la mention « à relire ».
 */
export function FichesEdukoraPage() {
  useI18n()
  useSeo({ title: t("fe.seo_titre"), description: t("fe.seo_description", { site: SITE_NAME }) })
  const queryClient = useQueryClient()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()
  const declare = useCursusDeclare()
  const [params, setParams] = useSearchParams()
  const [recherche, setRecherche] = useState("")
  // « Rouvrir la source » d'une note gardée mène ici avec la seule fiche (?fiche=<id>) : on demande où elle se trouve,
  // sinon la page ouvrait l'examen déclaré et la première matière, où la fiche n'est pas forcément.
  const ficheVisee = Number(params.get("fiche")) || null
  const aSituer = ficheVisee !== null && !params.get("matiere")
  const situationQ = useQuery({
    queryKey: ["fiches-edukora", "situer", ficheVisee],
    queryFn: ({ signal }) => situerFiche(ficheVisee as number, signal),
    enabled: aSituer && !authLoading,
    retry: false,
  })
  const situation = aSituer ? situationQ.data : undefined
  const enSituation = aSituer && situationQ.isLoading
  const cursusDeLaFiche = situation
    ? (declare !== null && situation.cursus_ids.includes(declare) ? declare : (situation.cursus_ids[0] ?? null))
    : null
  const cursus = Number(params.get("cursus")) || cursusDeLaFiche || declare

  const matieresQ = useQuery({
    queryKey: ["fiches-edukora", "matieres", cursus, isAuthenticated],
    queryFn: ({ signal }) => getFichesMatieres(cursus as number, signal),
    enabled: !authLoading && !enSituation && cursus !== null,
  })
  const matieres = matieresQ.data?.matieres ?? []
  const matiereId = Number(params.get("matiere")) || situation?.matiere_id || matieres[0]?.matiere_id || null
  const matiere = matieres.find((m) => m.matiere_id === matiereId) ?? null
  const fichesQ = useQuery({
    queryKey: ["fiches-edukora", "fiches", cursus, matiereId, isAuthenticated],
    queryFn: ({ signal }) => getFiches(cursus as number, matiereId as number, signal),
    enabled: !authLoading && !enSituation && cursus !== null && matiereId !== null,
  })
  const abonne = fichesQ.data?.abonne ?? matieresQ.data?.abonne ?? false
  const trouvees = useMemo(() => {
    const toutes = fichesQ.data?.fiches ?? []
    const aiguille = sansAccent(recherche.trim())
    return aiguille ? toutes.filter((f) => sansAccent(`${f.terme} ${f.definition ?? ""}`).includes(aiguille)) : toutes
  }, [fichesQ.data, recherche])
  // Les rubriques se lisent sur toutes les fiches de la matière : une recherche ne doit pas faire disparaître un filtre.
  const rubriques = useMemo(
    () => grouperParRubrique(fichesQ.data?.fiches ?? []).filter((g) => g.rubrique),
    [fichesQ.data],
  )
  const [rubriqueChoisie, setRubriqueChoisie] = useState("")
  // Le choix d'une autre matière, ou une rubrique disparue, ramène à « Toutes ».
  const rubriqueActive = rubriques.some((g) => g.rubrique === rubriqueChoisie) ? rubriqueChoisie : ""
  const fiches = useMemo(
    () => (rubriqueActive ? trouvees.filter((f) => f.rubrique === rubriqueActive) : trouvees),
    [trouvees, rubriqueActive],
  )
  const parRubrique = rubriques.length > 1
  const groupes = parRubrique ? grouperParRubrique(fiches) : [{ rubrique: "", fiches }]

  // La fiche visée est mise sous les yeux.
  const viseeRef = useRef<HTMLLIElement>(null)
  useEffect(() => {
    if (ficheVisee && fiches.some((f) => f.id === ficheVisee)) viseeRef.current?.scrollIntoView({ block: "center" })
  }, [ficheVisee, fiches])

  // Une matière ouverte, une fois par passage : de quoi savoir si les fiches sont lues.
  const matieresLues = useRef(new Set<number>())
  const nbFiches = fichesQ.data?.fiches.length ?? 0
  useEffect(() => {
    if (!matiereId || !cursus || nbFiches === 0 || matieresLues.current.has(matiereId)) return
    matieresLues.current.add(matiereId)
    trackEvent("fiche_lue", { matiere_id: matiereId, cursus_id: cursus })
  }, [matiereId, cursus, nbFiches])

  const garder = useMutation({
    mutationFn: (fiche: FicheEdukora) => garderFiche(fiche.id),
    onSuccess: () => {
      toast.success(t("fe.gardee_toast"))
      queryClient.invalidateQueries({ queryKey: ["fiches-edukora", "fiches"] })
      queryClient.invalidateQueries({ queryKey: ["carnet"] })
      queryClient.invalidateQueries({ queryKey: ["notes-a-revoir"] })
      queryClient.invalidateQueries({ queryKey: CLE_NOTES_DUES })
    },
    onError: () => toast.error(t("ca.note_erreur")),
  })

  const Icone = matiere ? subjectIcon(matiere.matiere_code) : Layers
  const verrouillees = fiches.filter((f) => f.verrouillee).length
  // Sur papier sortent les fiches affichées (matière, rubrique, recherche) que l'élève peut lire.
  const imprimables = fiches.length - verrouillees
  const impression = useImpression()
  const feuille = impression && imprimables > 0

  return (
    <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-10 print:max-w-none print:p-0">
      {feuille && <FichesImprimees titre={[matiere?.matiere, rubriqueActive].filter(Boolean).join(" · ")} fiches={fiches} />}
      <div className={feuille ? "print:hidden" : undefined}>
      <ReviserTabs />

      <header className="relative animate-fade-up overflow-hidden rounded-3xl border border-gold/40 bg-gradient-to-br from-gold/[0.16] via-card to-primary/[0.06] px-5 py-6 sm:px-9 sm:py-8">
        <div aria-hidden="true" className="absolute -right-10 -top-16 size-56 rounded-full bg-gold/25 blur-3xl" />
        <div className="relative">
          <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-gold-text">
            <BadgeCheck className="size-3.5" aria-hidden="true" />
            {t("fe.surtitre")}
          </p>
          <h1 className="mt-2 font-display text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl">{t("fe.titre")}</h1>
          <p className="mt-3 max-w-xl text-sm text-muted-foreground">{t("fe.texte")}</p>
        </div>
      </header>

      {cursus === null ? (
        <>
        <ApercuFiches country={country} className="mt-8" />
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <GraduationCap className="mx-auto size-8 text-primary" aria-hidden="true" />
          <p className="mt-3 font-display text-xl font-semibold">{t("fe.choisir_examen")}</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">{t("fe.choisir_examen_texte")}</p>
          <Button asChild className="mt-5 rounded-full">
            <Link to={`/${country}`}>
              {t("fe.choisir_examen_bouton")}
              <ArrowRight />
            </Link>
          </Button>
        </div>
        </>
      ) : matieresQ.isLoading || authLoading ? (
        <div className="mt-8 flex flex-col gap-3">
          <Skeleton className="h-10 w-64 rounded-full" />
          <Skeleton className="h-32 w-full rounded-2xl" />
          <Skeleton className="h-32 w-full rounded-2xl" />
        </div>
      ) : matieresQ.isError ? (
        <ErreurChargement objet={t("fe.objet")} onRetry={() => matieresQ.refetch()} className="mt-8" />
      ) : matieres.length === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <Layers className="mx-auto size-8 text-primary" aria-hidden="true" />
          <p className="mt-3 font-display text-xl font-semibold">{t("fe.vide")}</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">{t("fe.vide_texte")}</p>
        </div>
      ) : (
        <>
          {/* Les matières qui ont des fiches. */}
          <nav aria-label={t("fe.matieres_aria")} className="no-scrollbar -mx-4 mt-6 flex gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:flex-wrap sm:overflow-visible sm:px-0">
            {matieres.map((m) => {
              const actif = m.matiere_id === matiereId
              return (
                <button
                  key={m.matiere_id}
                  type="button"
                  aria-current={actif ? "true" : undefined}
                  onClick={() => {
                    const p = new URLSearchParams(params)
                    p.set("matiere", String(m.matiere_id))
                    p.set("cursus", String(cursus))
                    p.delete("fiche")
                    setParams(p, { replace: true })
                  }}
                  className={cn(
                    "inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors",
                    actif ? "border-primary bg-primary text-primary-foreground" : "border-border bg-card text-muted-foreground hover:border-primary/40",
                  )}
                >
                  <span className={cn("size-2 rounded-full", actif ? "bg-primary-foreground" : couleurMatiere(m.matiere_code).barre)} aria-hidden="true" />
                  {m.matiere}
                  <span className={actif ? "text-primary-foreground/80" : "text-muted-foreground/70"}>{m.total}</span>
                </button>
              )
            })}
          </nav>

          <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-3">
            <span className={cn("flex size-14 shrink-0 items-center justify-center rounded-2xl", couleurMatiere(matiere?.matiere_code).puce)}>
              <Icone className="size-7" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <h2 className="font-display text-2xl font-semibold leading-tight tracking-tight sm:text-3xl">{matiere?.matiere}</h2>
              <p className="text-xs text-muted-foreground">{tn("fe.nombre", matiere?.total ?? 0)}</p>
            </div>
            {imprimables > 0 && (
              <Button type="button" variant="outline" className="rounded-full print:hidden" onClick={() => window.print()}>
                <Printer />
                {t("ca.imprimer")}
              </Button>
            )}
            <div className="relative w-full sm:w-64">
              <Search className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <input
                type="search"
                value={recherche}
                onChange={(e) => setRecherche(e.target.value)}
                placeholder={t("fe.recherche")}
                aria-label={t("fe.recherche")}
                className="w-full rounded-full border border-input bg-card py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring/40"
              />
            </div>
          </div>

          {parRubrique && (
            <div role="group" aria-label={t("fe.rubriques_aria")} className="mt-4 flex flex-wrap gap-2">
              {[{ rubrique: "", fiches: fichesQ.data?.fiches ?? [] }, ...rubriques].map((g) => {
                const actif = g.rubrique === rubriqueActive
                return (
                  <button
                    key={g.rubrique || "toutes"}
                    type="button"
                    aria-pressed={actif}
                    onClick={() => setRubriqueChoisie(g.rubrique)}
                    className={cn(
                      "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3.5 text-xs font-medium transition-colors",
                      actif ? "border-primary bg-primary/10 text-primary" : "border-border bg-card text-muted-foreground hover:border-primary/40",
                    )}
                  >
                    {g.rubrique || t("fe.toutes")}
                    <span className="tabular-nums opacity-70">{g.fiches.length}</span>
                  </button>
                )
              })}
            </div>
          )}

          {!abonne && verrouillees > 0 && (
            <div className="mt-5 flex flex-col gap-3 rounded-2xl border border-gold/40 bg-gradient-to-br from-gold/[0.10] via-gold/[0.03] to-transparent p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
              <p className="flex items-start gap-3 text-sm">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-gold text-gold-foreground">
                  <Crown className="size-4" aria-hidden="true" />
                </span>
                <span>
                  <span className="block font-display text-base font-semibold">{tn("fe.verrou_titre", verrouillees)}</span>
                  <span className="text-muted-foreground">{t("fe.verrou_texte")}</span>
                </span>
              </p>
              <Button asChild className="shrink-0 rounded-full">
                <Link to={`/abonnement?cursus=${cursus}`}>
                  {t("qd.debloquer")}
                  <ArrowRight />
                </Link>
              </Button>
            </div>
          )}

          {fichesQ.isLoading ? (
            <div className="mt-5 grid items-start gap-4 lg:grid-cols-2">
              <Skeleton className="h-36 w-full rounded-2xl" />
              <Skeleton className="h-36 w-full rounded-2xl" />
            </div>
          ) : fichesQ.isError ? (
            <ErreurChargement objet={t("fe.objet")} onRetry={() => fichesQ.refetch()} className="mt-5" />
          ) : fiches.length === 0 ? (
            <p className="mt-10 text-center text-sm text-muted-foreground">{t("fe.aucun_resultat")}</p>
          ) : (
            groupes.map((groupe) => (
            <section key={groupe.rubrique || "sans"} aria-label={groupe.rubrique || undefined}>
              {groupe.rubrique && (
                <h3 className="mt-8 font-display text-lg font-semibold tracking-tight text-muted-foreground">{groupe.rubrique}</h3>
              )}
                <ul className={cn("grid items-start gap-4 lg:grid-cols-2", groupe.rubrique ? "mt-3" : "mt-5")}>
                  {groupe.fiches.map((fiche, i) => (
                    <li
                      key={fiche.id}
                      ref={fiche.id === ficheVisee ? viseeRef : undefined}
                      style={{ animationDelay: `${Math.min(i, 10) * 35}ms` }}
                      className={cn(
                        "relative animate-fade-up overflow-hidden rounded-2xl border bg-card shadow-sm transition-shadow duration-300 hover:shadow-lg hover:shadow-primary/5",
                        fiche.id === ficheVisee ? "border-primary ring-2 ring-primary/20" : "border-border",
                      )}
                    >
                      <span aria-hidden="true" className={cn("absolute inset-y-0 left-0 w-1", couleurMatiere(matiere?.matiere_code).barre)} />
                      <div className="p-4 pl-5 sm:p-5 sm:pl-6">
                        <div className="flex items-start justify-between gap-3">
                          <h3 className="font-display text-xl font-semibold leading-tight tracking-tight">{fiche.terme}</h3>
                          {fiche.a_relire && (
                            <span className="shrink-0 rounded-full bg-warning/15 px-2 py-0.5 text-[0.7rem] font-semibold uppercase tracking-wide text-warning-foreground dark:text-warning">
                              {t("fe.a_relire")}
                            </span>
                          )}
                        </div>
                        <div className="mt-2">
                          <Sessions fiche={fiche} />
                        </div>
                        <PassagesDeLaFiche fiche={fiche} cursus={cursus as number} pays={country} />
                        {fiche.verrouillee ? (
                          <p className="mt-3 flex items-center gap-2 rounded-xl bg-muted/50 px-3 py-2.5 text-sm text-muted-foreground">
                            <Lock className="size-3.5 shrink-0" aria-hidden="true" />
                            {t("fe.verrouillee")}
                          </p>
                        ) : (
                          <>
                            <NoteTexte texte={fiche.definition ?? ""} className="mt-3 text-[0.95rem] leading-relaxed" />
                            <BlocsFiche fiche={fiche} />
                            <div className="mt-3.5 flex items-center justify-end border-t border-dashed border-border pt-3">
                              {fiche.gardee ? (
                                <Link to={`/carnet?dossier=${fiche.matiere_id}`} className="inline-flex items-center gap-1.5 text-xs font-medium text-primary hover:underline">
                                  <Check className="size-3.5" aria-hidden="true" />
                                  {t("fe.gardee")}
                                </Link>
                              ) : isAuthenticated ? (
                                <Button type="button" size="sm" variant="outline" className="rounded-full" disabled={garder.isPending} onClick={() => garder.mutate(fiche)}>
                                  <NotebookPen />
                                  {t("fe.garder")}
                                </Button>
                              ) : (
                                <Link to="/connexion" state={{ from: "/fiches-edukora" }} className="text-xs font-medium text-primary hover:underline">
                                  {t("fe.connecte_toi")}
                                </Link>
                              )}
                            </div>
                          </>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
            </section>
            ))
          )}
        </>
      )}
      </div>
    </div>
  )
}
