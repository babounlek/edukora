import { useEffect, useMemo, useRef, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, BadgeCheck, Check, Crown, GraduationCap, Layers, Lock, NotebookPen, Search } from "lucide-react"
import { toast } from "sonner"

import { garderFiche, getFiches, getFichesMatieres } from "@/api/endpoints"
import type { FicheEdukora } from "@/api/types"
import { ApercuFiches } from "@/components/ApercuFiches"
import { ErreurChargement } from "@/components/ErreurChargement"
import { NoteTexte } from "@/components/NoteTexte"
import { ReviserTabs } from "@/components/ReviserTabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { useCursusDeclare } from "@/lib/cursusAccueil"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { CLE_NOTES_DUES } from "@/lib/notesDues"
import { subjectIcon } from "@/lib/subjectIcon"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

function sansAccent(s: string): string {
  return s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
}

/** « Tombé au BEPC 2018, 2019 » et, à part, les examens blancs : seules les sessions officielles font foi. */
function Sessions({ fiche }: { fiche: FicheEdukora }) {
  const officielles = fiche.sessions.filter((s) => s.origine === "OFFICIEL").map((s) => s.annee)
  const autres = fiche.sessions.filter((s) => s.origine !== "OFFICIEL").map((s) => s.annee)
  if (officielles.length === 0 && autres.length === 0) return null
  return (
    <p className="flex flex-wrap items-center gap-1.5 text-xs">
      {officielles.length > 0 && (
        <>
          <span className="font-medium text-gold-text">{tn("fe.tombe", officielles.length)}</span>
          {officielles.map((a) => (
            <span key={a} className="rounded-full bg-gold/15 px-2 py-0.5 font-semibold tabular-nums text-gold-text">
              {a}
            </span>
          ))}
        </>
      )}
      {autres.length > 0 && (
        <span className="text-muted-foreground">
          {t("fe.blanc", { annees: [...new Set(autres)].join(", ") })}
        </span>
      )}
    </p>
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
  useSeo({ title: t("fe.titre"), description: t("fe.texte") })
  const queryClient = useQueryClient()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()
  const declare = useCursusDeclare()
  const [params, setParams] = useSearchParams()
  const cursus = Number(params.get("cursus")) || declare
  const [recherche, setRecherche] = useState("")

  const matieresQ = useQuery({
    queryKey: ["fiches-edukora", "matieres", cursus, isAuthenticated],
    queryFn: ({ signal }) => getFichesMatieres(cursus as number, signal),
    enabled: !authLoading && cursus !== null,
  })
  const matieres = matieresQ.data?.matieres ?? []
  const matiereId = Number(params.get("matiere")) || matieres[0]?.matiere_id || null
  const matiere = matieres.find((m) => m.matiere_id === matiereId) ?? null
  const fichesQ = useQuery({
    queryKey: ["fiches-edukora", "fiches", cursus, matiereId, isAuthenticated],
    queryFn: ({ signal }) => getFiches(cursus as number, matiereId as number, signal),
    enabled: !authLoading && cursus !== null && matiereId !== null,
  })
  const abonne = fichesQ.data?.abonne ?? matieresQ.data?.abonne ?? false
  const fiches = useMemo(() => {
    const toutes = fichesQ.data?.fiches ?? []
    const aiguille = sansAccent(recherche.trim())
    return aiguille ? toutes.filter((f) => sansAccent(`${f.terme} ${f.definition ?? ""}`).includes(aiguille)) : toutes
  }, [fichesQ.data, recherche])

  // « Rouvrir la source » d'une note gardée mène ici, sur sa fiche (?fiche=<id>) : on la met sous les yeux.
  const ficheVisee = Number(params.get("fiche")) || null
  const viseeRef = useRef<HTMLLIElement>(null)
  useEffect(() => {
    if (ficheVisee && fiches.some((f) => f.id === ficheVisee)) viseeRef.current?.scrollIntoView({ block: "center" })
  }, [ficheVisee, fiches])

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

  return (
    <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-10">
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
          <nav aria-label={t("fe.matieres_aria")} className="-mx-4 mt-6 flex gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:px-0">
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
            <ul className="mt-5 grid items-start gap-4 lg:grid-cols-2">
              {fiches.map((fiche, i) => (
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
                    {fiche.verrouillee ? (
                      <p className="mt-3 flex items-center gap-2 rounded-xl bg-muted/50 px-3 py-2.5 text-sm text-muted-foreground">
                        <Lock className="size-3.5 shrink-0" aria-hidden="true" />
                        {t("fe.verrouillee")}
                      </p>
                    ) : (
                      <>
                        <NoteTexte texte={fiche.definition ?? ""} className="mt-3 text-[0.95rem] leading-relaxed" />
                        {fiche.exemple && (
                          <blockquote className="mt-3 border-l-2 border-gold/60 pl-3">
                            <NoteTexte texte={fiche.exemple} className="italic text-muted-foreground" />
                          </blockquote>
                        )}
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
          )}
        </>
      )}
    </div>
  )
}
