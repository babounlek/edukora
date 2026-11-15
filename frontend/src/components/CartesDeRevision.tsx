import { useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import { Layers } from "lucide-react"

import { getCartesCours, getCartesDues, noterCarte } from "@/api/endpoints"
import type { CarteRevision } from "@/api/types"
import { PaquetDeCartes } from "@/components/PaquetDeCartes"
import { Button } from "@/components/ui/button"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"

const CLE_DUES = ["cartes-dues"] as const

/**
 * Fin d'un cours (audit produit 2026-11-13, R18) : « Réviser en cartes » ouvre les cartes du cours (la règle, puis ses erreurs
 * classiques) qui sont nouvelles ou à revoir. Rien n'est écrit pour ça : les cartes se lisent dans le cours lui-même.
 */
export function CartesDuCours({ slug }: { slug: string }) {
  useI18n()
  const client = useQueryClient()
  // Le paquet est figé à l'ouverture : un rechargement des données en cours de revue ne doit pas déplacer les cartes.
  const [paquet, setPaquet] = useState<CarteRevision[] | null>(null)
  const { data } = useQuery({ queryKey: ["cartes-cours", slug], queryFn: ({ signal }) => getCartesCours(slug, signal) })
  if (!data || data.cartes.length === 0) return null

  const aFaire = data.cartes.filter((c) => c.etat !== "planifiee")
  const prochaine = data.cartes.map((c) => c.due_at).filter((d): d is string => Boolean(d)).sort()[0]

  return (
    <section className="mx-auto mt-10 max-w-3xl rounded-2xl border border-gold/30 bg-gold/5 px-5 py-4" aria-label={t("cartes.titre")}>
      <div className="flex flex-wrap items-center gap-3">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
          <Layers className="size-4" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{t("cartes.titre")}</p>
          <p className="text-sm font-medium">
            {aFaire.length > 0
              ? tn("cartes.a_reviser", aFaire.length)
              : t("cartes.a_jour", { date: prochaine ? new Date(`${prochaine}T12:00:00`).toLocaleDateString(localeCourante(), { day: "numeric", month: "long" }) : "" })}
          </p>
        </div>
        {aFaire.length > 0 && !paquet && (
          <Button type="button" className="min-h-11 rounded-full" onClick={() => setPaquet(aFaire)}>
            {t("cartes.reviser")}
          </Button>
        )}
      </div>
      {paquet && (
        <div className="mt-4">
          <PaquetDeCartes
            cartes={paquet}
            noter={(carte, savais) => noterCarte(slug, carte.cle, savais)}
            onTermine={() => {
              client.invalidateQueries({ queryKey: ["cartes-cours", slug] })
              client.invalidateQueries({ queryKey: CLE_DUES })
              client.invalidateQueries({ queryKey: ["cartes-paquets"] })
            }}
          />
        </div>
      )}
    </section>
  )
}

/**
 * Sur l'accueil : les cartes dont l'échéance est arrivée, toutes matières. Une ligne, un geste pour les ouvrir ; rien tant
 * qu'aucune carte n'est due (une élève qui n'a jamais révisé de carte ne voit pas cette ligne : elle les découvre en fin de cours).
 */
export function LigneCartes({ integre = false }: { integre?: boolean }) {
  useI18n()
  const [paquet, setPaquet] = useState<CarteRevision[] | null>(null)
  const { data } = useQuery({ queryKey: CLE_DUES, queryFn: ({ signal }) => getCartesDues(signal) })
  if (!data || (data.total === 0 && !paquet)) return null

  return (
    <section className={integre ? undefined : "mx-auto max-w-5xl px-4 pt-6 sm:px-6"} aria-label={t("cartes.titre")}>
      <div className="rounded-2xl border border-border bg-card px-5 py-3">
        <div className="flex items-center gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
            <Layers className="size-4" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{t("cartes.titre")}</p>
            <p className="truncate text-sm font-medium">{tn("cartes.dues", data.total)}</p>
          </div>
          {!integre && !paquet && (
            <Link to="/cartes" className="shrink-0 text-xs font-medium text-primary hover:underline">{t("cartes.toutes")}</Link>
          )}
          {!paquet && (
            <Button type="button" variant="outline" className="min-h-11 shrink-0 rounded-full" onClick={() => setPaquet(data.cartes)}>
              {t("cartes.reviser")}
            </Button>
          )}
        </div>
        {paquet && (
          <div className="mt-4">
            <PaquetDeCartes
              cartes={paquet}
              noter={(carte, savais) => noterCarte(carte.cours?.slug ?? "", carte.cle, savais)}
            />
          </div>
        )}
      </div>
    </section>
  )
}
