import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, CheckCircle2, Swords } from "lucide-react"

import { getDefiSemaine } from "@/api/endpoints"
import type { DefiSemaine } from "@/api/types"
import { epreuveInediteDetailPath, epreuvesListPath } from "@/lib/countryPath"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * Le défi de la semaine (audit produit 2026-11-13, R17) : une mini-inédite, la même pour tous les élèves du cursus, du lundi
 * au dimanche. Le choix est fait par le serveur (voir inedit.defi) : il ne dépend ni de l'élève ni de ses accès. Une fois le
 * défi relevé, la carte le dit ; le dimanche, elle donne la bande anonyme parmi les participants chronométrés (jamais un rang,
 * jamais une note d'autrui) quand la cohorte est assez grande.
 */
/** Le défi de la semaine d'un examen : même clé de cache que l'accueil, qui la remplit (voir AccueilEleve). */
export function useDefiSemaine(country: string, cursusId: number | null | undefined) {
  const { data } = useQuery({
    queryKey: ["defi-semaine", cursusId],
    queryFn: ({ signal }) => getDefiSemaine(cursusId as number, signal),
    enabled: Boolean(country) && Boolean(cursusId),
  })
  return data?.defi ?? null
}

/** Ce qu'il reste pour relever le défi : « Dernier jour pour le relever », ou « Encore 3 jours, le même sujet pour tous ». */
export function echeanceDefi(defi: DefiSemaine): string {
  return defi.jours_restants === 0 ? t("defi.dernier_jour") : tn("defi.jours", defi.jours_restants)
}

/**
 * Le défi de la semaine dit sur la ligne d'une copie déjà entamée (voir AccueilEleve) : « Défi de la semaine · Encore 1
 * jour, le même sujet pour tous ». La copie et le défi sont alors la même épreuve : une ligne, pas deux.
 */
export function mentionDefi(defi: DefiSemaine): string {
  return `${t("defi.titre")} · ${echeanceDefi(defi)}`
}

export function DefiDeLaSemaine({
  country, cursusId, rangee = false,
}: { country: string; cursusId: number | null | undefined; rangee?: boolean }) {
  useI18n()
  const defi = useDefiSemaine(country, cursusId)
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
    : echeanceDefi(defi)

  // `rangee` : une ligne du bloc « À continuer » de l'accueil (voir AccueilEleve), sans cadre ni marge à elle, et sans
  // le lien « Toutes les minis » (la fiche du défi y mène).
  if (rangee) {
    return (
      <Link to={fiche} className="group flex items-center gap-3 px-5 py-3.5 transition-colors hover:bg-muted/40">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
          {defi.releve ? <CheckCircle2 className="size-4" aria-hidden="true" /> : <Swords className="size-4" aria-hidden="true" />}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {t("defi.titre")}
            {defi.duree_minutes ? ` · ${t("defi.duree", { n: defi.duree_minutes })}` : ""}
          </span>
          <span className="line-clamp-2 text-sm font-medium">{defi.titre}</span>
          <span className="block text-xs text-muted-foreground">{etat}</span>
          {precedent && <span className="block text-xs text-muted-foreground">{t(`defi.precedent_${precedent}`)}</span>}
        </span>
        <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
      </Link>
    )
  }

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("defi.titre")}>
      {/* Sur téléphone, « Toutes les minis » passe sous la carte : à côté, il ne laissait au titre que la place de
          « Mini-inédite … », sans la matière, et le libellé tenait sur trois lignes. */}
      <div className="flex flex-wrap items-center gap-x-3 rounded-2xl border border-gold/30 bg-gold/5 px-5 py-3.5 transition-colors hover:border-gold/60">
        <Link to={fiche} className="group flex min-w-0 flex-1 basis-full items-center gap-3 sm:basis-0">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
            {defi.releve ? <CheckCircle2 className="size-4" aria-hidden="true" /> : <Swords className="size-4" aria-hidden="true" />}
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
              {t("defi.titre")}
              {defi.duree_minutes ? ` · ${t("defi.duree", { n: defi.duree_minutes })}` : ""}
            </span>
            <span className="line-clamp-2 text-sm font-medium">{defi.titre}</span>
            <span className="block text-xs text-muted-foreground">{etat}</span>
            {precedent && <span className="block text-xs text-muted-foreground">{t(`defi.precedent_${precedent}`)}</span>}
          </span>
          <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
        </Link>
        <Link to={liste} className="ml-12 flex min-h-11 shrink-0 items-center text-xs font-medium text-gold-text underline-offset-2 hover:underline sm:ml-0">
          {t("defi.toutes")}
        </Link>
      </div>
    </section>
  )
}
