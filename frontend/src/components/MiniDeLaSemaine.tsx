import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, CheckCircle2, Timer } from "lucide-react"

import { listEpreuves } from "@/api/endpoints"
import type { Epreuve } from "@/api/types"
import { epreuveInediteDetailPath, epreuvesListPath } from "@/lib/countryPath"
import { maintenantServeur } from "@/lib/horlogeServeur"
import { t } from "@/lib/i18n"

const MS_PAR_JOUR = 86_400_000

/** Numéro de semaine (du lundi au dimanche) depuis 1970 : le 1er janvier 1970 était un jeudi, d'où le décalage de 3 jours. */
export function numeroDeSemaine(maintenant: number): number {
  return Math.floor((Math.floor(maintenant / MS_PAR_JOUR) + 3) / 7)
}

/**
 * La mini-inédite de la semaine : une seule, la même pour tous les élèves du cursus, qui change le lundi. Tirée dans les
 * minis OUVERTES à l'élève (une mini fermée n'est pas une invitation), triées par id pour que le tirage ne bouge pas
 * quand une mini s'ajoute en fin de liste. Déjà faite : on le dit, et on propose la prochaine pas encore faite.
 */
export function choisirMiniDeLaSemaine(
  minis: Epreuve[], semaine: number,
): { mini: Epreuve; autre: Epreuve | null } | null {
  const ouvertes = minis.filter((e) => e.has_access).sort((a, b) => a.id - b.id)
  if (ouvertes.length === 0) return null
  const rang = semaine % ouvertes.length
  const mini = ouvertes[rang]
  if (!mini.is_read) return { mini, autre: null }
  const reste = [...ouvertes.slice(rang + 1), ...ouvertes.slice(0, rang)]
  return { mini, autre: reste.find((e) => !e.is_read) ?? null }
}

export function MiniDeLaSemaine({ country, cursusId }: { country: string; cursusId: number | null | undefined }) {
  const { data } = useQuery({
    queryKey: ["mini-inedites", country, cursusId],
    queryFn: ({ signal }) => listEpreuves({ country, origine: "INEDITE", mini: true, cursus: cursusId ?? undefined }, signal),
    enabled: Boolean(country) && cursusId !== undefined,
  })
  if (!data) return null
  const choix = choisirMiniDeLaSemaine(data.results, numeroDeSemaine(maintenantServeur()))
  if (!choix) return null
  const { mini, autre } = choix
  const faite = mini.is_read
  const cible = faite && autre ? autre : mini
  const fiche = epreuveInediteDetailPath(country, cible.slug ?? cible.id)
  const liste = `${epreuvesListPath(country)}?origine=INEDITE&mini=true${cursusId ? `&cursus=${cursusId}` : ""}`
  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
      <div className="flex items-center gap-3 rounded-2xl border border-gold/30 bg-gold/5 px-5 py-3.5 transition-colors hover:border-gold/60">
        <Link to={fiche} className="group flex min-w-0 flex-1 items-center gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
            {faite ? <CheckCircle2 className="size-4" /> : <Timer className="size-4" />}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {faite ? t("abonne.mini_faite") : t("abonne.mini_semaine")}
              {mini.duree_minutes ? ` · ${t("abonne.mini_duree", { n: mini.duree_minutes })}` : ""}
            </span>
            <span className="block truncate text-sm font-medium">
              {faite && autre ? t("abonne.mini_une_autre", { titre: autre.title }) : mini.title}
            </span>
          </span>
          <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" />
        </Link>
        <Link to={liste} className="shrink-0 text-xs font-medium text-gold-text underline-offset-2 hover:underline">
          {t("abonne.mini_toutes", { n: data.results.length })}
        </Link>
      </div>
    </section>
  )
}
