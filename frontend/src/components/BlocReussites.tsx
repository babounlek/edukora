import { useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { Award, Check, Flame } from "lucide-react"

import { getReussites } from "@/api/endpoints"
import type { Jalon } from "@/api/types"
import { ErreurChargement } from "@/components/ErreurChargement"
import { useAuth } from "@/context/AuthContext"
import { marquerJalonsVus } from "@/lib/jalonsVus"
import { NiveauXp } from "@/components/NiveauXp"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"
import { t, tn, useI18n, type CleI18n } from "@/lib/i18n"

const FAMILLES = ["quiz", "themes", "cartes", "examens", "defis", "serie"] as const

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
 * Le niveau (15 rangs jusqu'à l'examen), le record de série et les jalons d'étude atteints, en tête de « Ma progression » :
 * c'est là que l'élève les cherche (passe élève du 2026-11-17 : « Mes réussites » n'avait de lien que dans « Mon compte »).
 * Chaque jalon repose sur un fait d'étude durable : il ne se perd pas. Les jalons se déplient : seize lignes d'un coup
 * repoussaient la progression sous le pli.
 */
export function BlocReussites({ className }: { className?: string }) {
  useI18n()
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["reussites"],
    queryFn: ({ signal }) => getReussites(signal),
  })
  // Tous les jalons sont montrés ici : aucun n'est à fêter plus tard comme une nouveauté (voir JalonsAtteints).
  const profilId = useAuth().user?.profil_actif?.id
  useEffect(() => {
    if (data && profilId != null) marquerJalonsVus(profilId, data.jalons.filter((j) => j.obtenu).map((j) => j.code))
  }, [data, profilId])

  if (isLoading) return <Skeleton className={cn("h-32 w-full rounded-2xl", className)} />
  if (isError || !data) return <ErreurChargement objet={t("reussites.objet")} onRetry={() => refetch()} className={className} />

  const prochain = data.jalons.find((j) => j.code === data.prochain)

  return (
    <section aria-label={t("reussites.titre")} className={cn("flex flex-col gap-3", className)}>
      <div className="rounded-2xl border border-border bg-card p-5">
        <NiveauXp niveau={data.niveau} />
      </div>
      <div className="flex items-center gap-3 rounded-2xl border border-border bg-card p-5">
        <Flame className="size-6 shrink-0 text-gold-text" aria-hidden="true" />
        <div>
          <p className="font-display text-xl font-semibold tabular-nums">{tn("reussites.record", data.serie.record)}</p>
          <p className="text-xs text-muted-foreground">
            {tn("reussites.serie_actuelle", data.serie.actuelle)}
            {data.serie.repos_pris ? ` · ${t("reussites.repos")}` : ""}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">{t("reussites.repos_regle")}</p>
        </div>
      </div>
      {prochain && !prochain.obtenu && <ul><LigneJalon jalon={prochain} prochain /></ul>}
      <details className="group rounded-2xl border border-border bg-card">
        <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-2 px-5 text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
          <span className="flex items-center gap-2">
            <Award className="size-4" aria-hidden="true" />
            {t("reussites.tous_jalons")}
          </span>
        </summary>
        <div className="border-t border-border px-4 pb-4">
          {FAMILLES.map((famille) => (
            <div key={famille} className="mt-5">
              <h3 className="font-display text-base font-semibold">{t(`reussites.famille_${famille}` as CleI18n)}</h3>
              <ul className="mt-2 flex flex-col gap-2">
                {data.jalons
                  .filter((j) => j.famille === famille)
                  .map((j) => (
                    <LigneJalon key={j.code} jalon={j} prochain={data.prochain === j.code} />
                  ))}
              </ul>
            </div>
          ))}
        </div>
      </details>
    </section>
  )
}
