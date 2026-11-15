import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, CheckCircle2, Swords } from "lucide-react"

import { getDefiSemaine } from "@/api/endpoints"
import { epreuveInediteDetailPath, epreuvesListPath } from "@/lib/countryPath"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * Le défi de la semaine (audit produit 2026-11-13, R17) : une mini-inédite, la même pour tous les élèves du cursus, du lundi
 * au dimanche. Le choix est fait par le serveur (voir inedit.defi) : il ne dépend ni de l'élève ni de ses accès. Une fois le
 * défi relevé, la carte le dit ; le dimanche, elle donne la bande anonyme parmi les participants chronométrés (jamais un rang,
 * jamais une note d'autrui) quand la cohorte est assez grande.
 */
export function DefiDeLaSemaine({ country, cursusId }: { country: string; cursusId: number | null | undefined }) {
  useI18n()
  const { data } = useQuery({
    queryKey: ["defi-semaine", cursusId],
    queryFn: ({ signal }) => getDefiSemaine(cursusId as number, signal),
    enabled: Boolean(country) && Boolean(cursusId),
  })
  const defi = data?.defi
  if (!defi) return null

  const fiche = epreuveInediteDetailPath(country, defi.slug || defi.epreuve_id)
  const liste = `${epreuvesListPath(country)}?origine=INEDITE&mini=true${cursusId ? `&cursus=${cursusId}` : ""}`
  const bande = defi.bande?.bande ?? null
  const precedent = defi.precedent?.bande?.bande ?? null

  const etat = defi.releve
    ? defi.resultat_ouvert
      ? bande
        ? t(`defi.bande_${bande}`)
        : t("defi.releve")
      : `${t("defi.releve")} · ${t("defi.resultat_dimanche")}`
    : defi.jours_restants === 0
      ? t("defi.dernier_jour")
      : tn("defi.jours", defi.jours_restants)

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
      <div className="flex items-center gap-3 rounded-2xl border border-gold/30 bg-gold/5 px-5 py-3.5 transition-colors hover:border-gold/60">
        <Link to={fiche} className="group flex min-w-0 flex-1 items-center gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
            {defi.releve ? <CheckCircle2 className="size-4" aria-hidden="true" /> : <Swords className="size-4" aria-hidden="true" />}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {t("defi.titre")}
              {defi.duree_minutes ? ` · ${t("defi.duree", { n: defi.duree_minutes })}` : ""}
            </span>
            <span className="block truncate text-sm font-medium">{defi.titre}</span>
            <span className="block text-xs text-muted-foreground">{etat}</span>
            {precedent && <span className="block text-xs text-muted-foreground">{t(`defi.precedent_${precedent}`)}</span>}
          </span>
          <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
        </Link>
        <Link to={liste} className="shrink-0 text-xs font-medium text-gold-text underline-offset-2 hover:underline">
          {t("defi.toutes")}
        </Link>
      </div>
    </section>
  )
}
