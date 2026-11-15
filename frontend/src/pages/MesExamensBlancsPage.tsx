import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Timer, Trophy } from "lucide-react"

import { listMySimulations, listMyTentativesInedites } from "@/api/endpoints"
import type { SimulationListItem, TentativeInediteListItem } from "@/api/types"
import { ConnexionRequise } from "@/components/ConnexionRequise"
import { ErreurChargement } from "@/components/ErreurChargement"
import { PointsPerdus } from "@/components/PointsPerdus"
import { ReviserTabs } from "@/components/ReviserTabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { epreuvesListPath } from "@/lib/countryPath"
import { formatNote } from "@/lib/notation"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

type Genre = "annale" | "inedite" | "mini" | "defi"

/** Une copie passée en conditions d'examen, quelle que soit son origine : annale, inédite, mini-inédite ou défi de la semaine. */
interface Copie {
  cle: string
  genre: Genre
  titre: string
  matiere: string
  started_at: string
  submitted_at: string | null
  note_obtenue: number | null
  bareme_snapshot: number | null
  enCours: boolean
  lienCopie: string
  lienResultat: string
}

function depuisAnnale(s: SimulationListItem): Copie {
  return {
    cle: `a${s.id}`, genre: "annale", titre: s.epreuve_titre, matiere: s.matiere ?? "", started_at: s.started_at,
    submitted_at: s.submitted_at, note_obtenue: s.note_obtenue, bareme_snapshot: s.bareme_snapshot,
    enCours: Boolean(s.chrono_en_cours), lienCopie: `/simulation/${s.id}`, lienResultat: `/simulation/${s.id}/resultat`,
  }
}

function depuisInedite(s: TentativeInediteListItem): Copie {
  return {
    cle: `i${s.id}`, genre: s.genre ?? "inedite", titre: s.epreuve_titre, matiere: s.subject_label, started_at: s.started_at,
    submitted_at: s.submitted_at, note_obtenue: s.note_obtenue, bareme_snapshot: s.bareme_snapshot,
    // Une copie libre entamée n'est pas un examen blanc : seule celle dont le chrono tourne est « en cours » ici.
    enCours: s.submitted_at === null && s.exam_mode_started_at !== null,
    lienCopie: `/inedit/tentative/${s.id}`, lienResultat: `/inedit/tentative/${s.id}/resultat`,
  }
}

/** La note d'une copie rendue, en % du barème : la seule mesure comparable d'une épreuve à l'autre. */
function pourcentage(s: Copie): number | null {
  if (s.submitted_at === null || s.note_obtenue === null || !s.bareme_snapshot) return null
  return Math.round((100 * s.note_obtenue) / s.bareme_snapshot)
}

function jour(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "long" })
}

/**
 * « Mes examens blancs » : les annales passées en conditions d'examen. Avant cette page, une simulation
 * interrompue ou terminée ne se retrouvait que par l'historique du navigateur (audit produit du 2026-11-13) : la
 * liste existait côté serveur, aucun écran ne l'appelait.
 *
 * Trois choses, dans l'ordre où elles servent : la copie dont le chrono tourne encore (à reprendre tout de suite),
 * les notes déjà obtenues (avec la meilleure et la tendance), puis la porte pour en passer une autre.
 */
export function MesExamensBlancsPage() {
  useI18n()
  useSeo({ title: t("blancs.titre") })
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["mes-simulations"],
    queryFn: listMySimulations,
    enabled: isAuthenticated,
  })
  const { data: inedites, isLoading: inedChargent } = useQuery({
    queryKey: ["mes-tentatives-inedites"],
    queryFn: listMyTentativesInedites,
    enabled: isAuthenticated,
    retry: false,
  })

  if (!authLoading && !isAuthenticated) {
    return <ConnexionRequise from="/examens-blancs" titre={t("blancs.h1")} explication={t("blancs.intent")} />
  }

  // Les inédites ne sont pas la panne de la page : sans l'option, leur liste est vide ou refusée, les annales restent.
  const copies: Copie[] = [...(data ?? []).map(depuisAnnale), ...(inedites ?? []).map(depuisInedite)]
  const enCours = copies.filter((s) => s.enCours)
  // Rendues : notées, ou à noter par l'élève (la note arrive quand il a tout noté).
  const rendues = copies
    .filter((s) => s.submitted_at !== null)
    .sort((a, b) => (b.submitted_at as string).localeCompare(a.submitted_at as string))
  const notees = rendues.filter((s) => pourcentage(s) !== null)
  const pourcents = notees.map((s) => pourcentage(s) as number)
  const meilleure = pourcents.length ? Math.max(...pourcents) : null
  // De la plus ancienne à la plus récente : de quoi dire si les notes montent.
  const chrono = [...notees].reverse()
  const tendance =
    chrono.length >= 2 ? (pourcentage(chrono[chrono.length - 1]) as number) - (pourcentage(chrono[0]) as number) : null

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <ReviserTabs />
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        <Timer className="size-3.5" />
        {t("blancs.titre")}
      </p>
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("blancs.h1")}</h1>
      <p className="mt-2 text-sm text-muted-foreground">{t("blancs.texte")}</p>

      {authLoading || isLoading || inedChargent ? (
        <div className="mt-8 flex flex-col gap-3">
          <Skeleton className="h-24 w-full rounded-2xl" />
          <Skeleton className="h-24 w-full rounded-2xl" />
        </div>
      ) : isError ? (
        <ErreurChargement objet={t("blancs.objet")} onRetry={() => refetch()} className="mt-8" />
      ) : (
        <>
          {enCours.length > 0 && (
            <section aria-label={t("blancs.en_cours")} className="mt-8 flex flex-col gap-3">
              {enCours.map((s) => (
                <Link
                  key={s.cle}
                  to={s.lienCopie}
                  className="group flex items-center gap-3 rounded-2xl border border-gold/50 bg-gold/10 px-5 py-4 transition-colors hover:border-gold"
                >
                  <span className="min-w-0 flex-1">
                    <span className="block text-xs font-semibold uppercase tracking-wide text-gold-text">
                      {t("blancs.en_cours")} · {t(`blancs.genre_${s.genre}`)}
                    </span>
                    <span className="block truncate font-display text-base font-semibold">{s.titre}</span>
                  </span>
                  <span className="shrink-0 text-sm font-medium text-primary">{t("blancs.reprendre")}</span>
                  <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
                </Link>
              ))}
            </section>
          )}

          {rendues.length > 0 ? (
            <section className="mt-8">
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-2xl border border-border bg-card p-4">
                  <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Trophy className="size-3.5 text-gold-text" aria-hidden="true" />
                    {t("blancs.meilleure")}
                  </p>
                  <p className="mt-1 font-display text-3xl font-semibold tabular-nums">{meilleure === null ? "–" : `${meilleure} %`}</p>
                </div>
                <div className="rounded-2xl border border-border bg-card p-4">
                  <p className="text-xs text-muted-foreground">{tn("blancs.passes", rendues.length)}</p>
                  <p className="mt-1 font-display text-3xl font-semibold tabular-nums">
                    {tendance === null ? "–" : tendance > 0 ? `+${tendance}` : tendance}{" "}
                    <span className="text-base font-medium text-muted-foreground">{t("blancs.points")}</span>
                  </p>
                  <p className="mt-0.5 text-xs text-muted-foreground">{t("blancs.depuis_premier")}</p>
                </div>
              </div>
              <PointsPerdus />
              <ul className="mt-4 flex flex-col gap-2">
                {rendues.map((s) => {
                  const p = pourcentage(s)
                  return (
                    <li key={s.cle}>
                      <Link
                        to={s.lienResultat}
                        className="group flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3 transition-colors hover:border-primary/40"
                      >
                        <span className="min-w-0 flex-1">
                          <span className="block truncate text-sm font-semibold">{s.titre}</span>
                          <span className="block text-xs text-muted-foreground">
                            <span className="mr-1.5 rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-foreground/80">
                              {t(`blancs.genre_${s.genre}`)}
                            </span>
                            {s.matiere} · {jour(s.submitted_at as string)}
                            {p !== null && ` · ${formatNote(s.note_obtenue, s.bareme_snapshot)}`}
                          </span>
                        </span>
                        {p === null ? (
                          <span className="shrink-0 text-sm font-medium text-gold-text">{t("blancs.a_noter")}</span>
                        ) : (
                          <span
                            className={cn(
                              "shrink-0 font-display text-xl font-semibold tabular-nums",
                              p >= 70 ? "text-success" : p >= 40 ? "text-foreground" : "text-muted-foreground",
                            )}
                          >
                            {p} %
                          </span>
                        )}
                        <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
                      </Link>
                    </li>
                  )
                })}
              </ul>
            </section>
          ) : (
            enCours.length === 0 && (
              <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
                <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                  <Timer className="size-6" />
                </span>
                <p className="mt-4 font-display text-lg font-semibold">{t("blancs.vide")}</p>
                <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">{t("blancs.vide_texte")}</p>
              </div>
            )
          )}

          <Button asChild size="lg" className="mt-8 h-12 w-full rounded-full sm:w-auto sm:px-7">
            <Link to={epreuvesListPath(country)}>
              {t("blancs.choisir")}
              <ArrowRight />
            </Link>
          </Button>
          <p className="mt-3 text-xs text-muted-foreground">{t("blancs.serie")}</p>
        </>
      )}
    </div>
  )
}
