import { Navigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Award, Check, Flame } from "lucide-react"

import { getReussites } from "@/api/endpoints"
import type { Jalon } from "@/api/types"
import { ErreurChargement } from "@/components/ErreurChargement"
import { NiveauXp } from "@/components/NiveauXp"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"
import { t, useI18n, type CleI18n } from "@/lib/i18n"

const FAMILLES = ["quiz", "themes", "examens", "serie"] as const

/** Une ligne de jalon : le titre, ce qu'il demande, et où l'élève en est. Un jalon atteint reste affiché, plein. */
function LigneJalon({ jalon, prochain }: { jalon: Jalon; prochain: boolean }) {
  useI18n()
  const part = Math.round((100 * jalon.valeur) / jalon.cible)
  return (
    <li
      className={cn(
        "flex items-center gap-3 rounded-2xl border px-4 py-3",
        jalon.obtenu ? "border-success/40 bg-success/5" : prochain ? "border-gold/50 bg-gold/10" : "border-border bg-card",
      )}
    >
      <span
        className={cn(
          "flex size-9 shrink-0 items-center justify-center rounded-full",
          jalon.obtenu ? "bg-success text-white" : "bg-muted text-muted-foreground",
        )}
        aria-hidden="true"
      >
        {jalon.obtenu ? <Check className="size-5" strokeWidth={3} /> : <Award className="size-5" />}
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-sm font-semibold">{t(`jalon.${jalon.code}` as CleI18n)}</span>
        <span className="block text-xs text-muted-foreground">
          {jalon.obtenu ? t("reussites.obtenu") : t("reussites.avancement", { a: jalon.valeur, b: jalon.cible })}
          {prochain && !jalon.obtenu && ` · ${t("reussites.prochain")}`}
        </span>
        {!jalon.obtenu && (
          <span className="mt-1.5 block h-1.5 overflow-hidden rounded-full bg-muted" aria-hidden="true">
            <span className="block h-full rounded-full bg-gold" style={{ width: `${Math.max(part, 3)}%` }} />
          </span>
        )}
      </span>
    </li>
  )
}

/**
 * « Mes réussites » : le niveau (15 rangs jusqu'à l'examen), le record de série et les jalons d'étude atteints (audit
 * produit du 2026-11-13, R12). Chaque jalon repose sur un fait d'étude durable : il ne se perd pas.
 */
export function MesReussitesPage() {
  useI18n()
  useSeo({ title: t("reussites.titre") })
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["reussites"],
    queryFn: ({ signal }) => getReussites(signal),
    enabled: isAuthenticated,
  })

  if (!authLoading && !isAuthenticated) return <Navigate to="/connexion" state={{ from: "/reussites" }} replace />

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        <Award className="size-3.5" />
        {t("reussites.titre")}
      </p>
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("reussites.h1")}</h1>
      <p className="mt-2 text-sm text-muted-foreground">{t("reussites.texte")}</p>

      {authLoading || isLoading ? (
        <div className="mt-8 flex flex-col gap-3">
          <Skeleton className="h-24 w-full rounded-2xl" />
          <Skeleton className="h-40 w-full rounded-2xl" />
        </div>
      ) : isError || !data ? (
        <ErreurChargement objet={t("reussites.objet")} onRetry={() => refetch()} className="mt-8" />
      ) : (
        <>
          <section className="mt-8 rounded-2xl border border-border bg-card p-5">
            <NiveauXp niveau={data.niveau} />
          </section>

          <section className="mt-4 flex items-center gap-3 rounded-2xl border border-border bg-card p-5">
            <Flame className="size-6 text-gold-text" aria-hidden="true" />
            <div>
              <p className="font-display text-xl font-semibold tabular-nums">{t("reussites.record", { n: data.serie.record })}</p>
              <p className="text-xs text-muted-foreground">
                {t("reussites.serie_actuelle", { n: data.serie.actuelle })}
                {data.serie.repos_pris ? ` · ${t("reussites.repos")}` : ""}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">{t("reussites.repos_regle")}</p>
            </div>
          </section>

          {FAMILLES.map((famille) => (
            <section key={famille} className="mt-8">
              <h2 className="font-display text-lg font-semibold">{t(`reussites.famille_${famille}` as CleI18n)}</h2>
              <ul className="mt-3 flex flex-col gap-2">
                {data.jalons
                  .filter((j) => j.famille === famille)
                  .map((j) => (
                    <LigneJalon key={j.code} jalon={j} prochain={data.prochain === j.code} />
                  ))}
              </ul>
            </section>
          ))}
        </>
      )}
    </div>
  )
}
