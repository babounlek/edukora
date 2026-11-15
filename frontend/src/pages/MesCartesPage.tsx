import { useState } from "react"
import { Link } from "react-router-dom"

import { ConnexionRequise } from "@/components/ConnexionRequise"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Layers } from "lucide-react"

import { getPaquetsCartes } from "@/api/endpoints"
import { CartesDuCours, LigneCartes } from "@/components/CartesDeRevision"
import { ErreurChargement } from "@/components/ErreurChargement"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { coursListPath, coursReaderPath } from "@/lib/countryPath"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"
import { useSeo } from "@/lib/seo"

function jour(iso: string): string {
  return new Date(`${iso}T12:00:00`).toLocaleDateString(localeCourante(), { day: "numeric", month: "long" })
}

/**
 * « Mes cartes » (audit produit 2026-11-13, R18) : les cartes à revoir aujourd'hui, toutes matières, puis un paquet par cours
 * dont l'élève a déjà revu une carte. Les cartes elles-mêmes se lisent dans le cours (rien n'est stocké) : cette page dit où
 * en est chaque paquet et laisse l'ouvrir d'un geste.
 */
export function MesCartesPage() {
  useI18n()
  useSeo({ title: t("cartes.mes") })
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { country } = useCountry()
  const [ouvert, setOuvert] = useState<string | null>(null)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["cartes-paquets"],
    queryFn: ({ signal }) => getPaquetsCartes(signal),
    enabled: isAuthenticated,
  })

  if (!authLoading && !isAuthenticated) return <ConnexionRequise from="/cartes" titre={t("cartes.titre")} explication={t("cartes.intent")} />

  const paquets = data?.paquets ?? []
  const totalDues = paquets.reduce((somme, p) => somme + p.dues, 0)

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        <Layers className="size-3.5" aria-hidden="true" />
        {t("cartes.mes")}
      </p>
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("cartes.h1")}</h1>
      <p className="mt-2 text-sm text-muted-foreground">{t("cartes.intro")}</p>

      {authLoading || isLoading ? (
        <div className="mt-8 flex flex-col gap-3">
          <Skeleton className="h-20 w-full rounded-2xl" />
          <Skeleton className="h-20 w-full rounded-2xl" />
        </div>
      ) : isError ? (
        <ErreurChargement objet={t("cartes.objet")} onRetry={() => refetch()} className="mt-8" />
      ) : paquets.length === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Layers className="size-6" aria-hidden="true" />
          </span>
          <p className="mt-4 font-display text-lg font-semibold">{t("cartes.vide")}</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">{t("cartes.vide_texte")}</p>
          <Button asChild className="mt-5 rounded-full">
            <Link to={coursListPath(country)}>
              {t("cartes.choisir_cours")}
              <ArrowRight />
            </Link>
          </Button>
        </div>
      ) : (
        <>
          <div className="mt-8">
            {totalDues > 0 ? (
              <LigneCartes integre />
            ) : (
              <p className="rounded-2xl border border-border bg-card px-5 py-4 text-sm text-muted-foreground">{t("cartes.rien_aujourdhui")}</p>
            )}
          </div>

          <h2 className="mt-8 font-display text-xl font-semibold">{t("cartes.paquets")}</h2>
          <ul className="mt-3 flex flex-col gap-3">
            {paquets.map((p) => (
              <li key={p.slug} className="rounded-2xl border border-border bg-card px-5 py-4">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold">{p.titre}</p>
                    <p className="text-xs text-muted-foreground">
                      {t("cartes.paquet_revues", { revues: p.revues, total: p.total })}
                      {p.dues === 0 && p.prochaine && ` · ${t("cartes.paquet_prochaine", { date: jour(p.prochaine) })}`}
                    </p>
                  </div>
                  <span className={p.dues > 0 ? "text-sm font-medium text-gold-text" : "text-sm text-success"}>
                    {p.dues > 0 ? tn("cartes.paquet_dues", p.dues) : t("cartes.paquet_a_jour")}
                  </span>
                  <Link to={coursReaderPath(p.slug)} className="text-xs font-medium text-primary hover:underline">
                    {t("cartes.relire")}
                  </Link>
                  <Button
                    type="button"
                    variant="outline"
                    className="min-h-11 rounded-full"
                    aria-expanded={ouvert === p.slug}
                    onClick={() => setOuvert(ouvert === p.slug ? null : p.slug)}
                  >
                    {t("cartes.reviser")}
                  </Button>
                </div>
                {ouvert === p.slug && <CartesDuCours slug={p.slug} />}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
