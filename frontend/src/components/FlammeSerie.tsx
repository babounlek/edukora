import { useQuery } from "@tanstack/react-query"
import { Flame } from "lucide-react"
import { Link } from "react-router-dom"

import { getPlanDuJour } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath } from "@/lib/countryPath"
import { t, useI18n } from "@/lib/i18n"

/**
 * La série de jours dans l'en-tête, sur toutes les pages : la flamme est ce qui donne envie de revenir demain, elle ne
 * doit pas dépendre d'un détour par l'accueil (test élève Guyguy : « pas de vraie série visible »). Rien à 0 jour : une
 * flamme éteinte à côté du nom ne ferait que culpabiliser. Lit le même plan du jour que l'accueil (même clé de cache) ;
 * il n'est relu qu'au bout de cinq minutes.
 */
export function FlammeSerie() {
  useI18n()
  const { isAuthenticated, user } = useAuth()
  const { country } = useCountry()
  const actif = isAuthenticated && Boolean(user?.cursus_prepare)
  const { data: plan } = useQuery({
    queryKey: ["plan-du-jour"],
    queryFn: ({ signal }) => getPlanDuJour(signal),
    enabled: actif,
    staleTime: 5 * 60_000,
  })
  const jours = plan?.serie?.jours ?? 0
  if (!actif || jours < 1) return null

  const libelle = jours === 1 ? t("serie.premier_jour") : t("serie.jours_de_suite", { n: jours })
  return (
    <Link
      to={catalogueHomePath(country)}
      aria-label={libelle}
      title={libelle}
      className="flex h-9 items-center gap-1 rounded-full px-2 text-sm font-semibold tabular-nums transition-colors hover:bg-muted"
    >
      <Flame className="size-4 text-warning" aria-hidden="true" />
      {jours}
    </Link>
  )
}
