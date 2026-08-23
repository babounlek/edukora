import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Crown, TrendingUp } from "lucide-react"

import { getThemesFrequents } from "@/api/endpoints"
import { epreuvesListPath } from "@/lib/countryPath"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface ThemesFrequentsProps {
  country: string
  cursusId: number
  subjectCode: string
}

/**
 * Classement des thèmes les plus fréquents aux épreuves officielles d'une matière/série
 * - argument de vente propre au palier Jusqu'à l'Examen (voir
 * access.services.has_access_jusqua_examen côté backend). Disparaît silencieusement si
 * le corpus est trop mince pour un classement fiable (`disponible=false`) - même patron
 * que le rail "Corrigés populaires" sous son propre seuil (voir EpreuvesListPage).
 */
export function ThemesFrequents({ country, cursusId, subjectCode }: ThemesFrequentsProps) {
  const { data } = useQuery({
    queryKey: ["themes-frequents", cursusId, subjectCode],
    queryFn: ({ signal }) => getThemesFrequents(cursusId, subjectCode, signal),
  })

  if (!data || !data.disponible || data.themes.length === 0) return null

  return (
    <Card className="mb-5 overflow-hidden border-primary/15 bg-primary/[0.02]">
      <CardContent className="flex flex-col gap-3 p-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="size-4 shrink-0 text-primary" />
          <h2 className="font-display text-sm font-semibold">Les thèmes qui reviennent le plus</h2>
        </div>
        <p className="-mt-1.5 text-xs text-muted-foreground">
          Sur les {data.nb_sessions_disponibles} sessions officielles disponibles dans notre base.
        </p>

        <div className="flex flex-col gap-1.5">
          {data.themes.map((theme) => (
            <Link
              key={theme.tag}
              to={`${epreuvesListPath(country)}?subject=${subjectCode}&cursus=${cursusId}&theme=${encodeURIComponent(theme.tag)}`}
              className="group flex items-center gap-3 rounded-md px-2 py-1.5 text-sm transition-colors hover:bg-primary/5"
            >
              <span className="min-w-0 flex-1 truncate font-medium group-hover:text-primary">{theme.tag}</span>
              <span className="h-1.5 w-16 shrink-0 overflow-hidden rounded-full bg-primary/10">
                <span
                  className="block h-full rounded-full bg-primary/60"
                  style={{ width: `${theme.frequence_pct}%` }}
                />
              </span>
              <span className="w-28 shrink-0 text-right text-xs tabular-nums text-muted-foreground">
                {theme.nb_epreuves}/{data.nb_sessions_disponibles} sessions
              </span>
            </Link>
          ))}
        </div>

        {!data.has_access && data.nb_themes_verrouilles > 0 && (
          <div className="flex flex-col gap-3 rounded-lg border border-dashed border-gold/40 bg-gold/[0.04] p-3.5">
            <p className="flex items-center gap-1.5 text-sm font-medium">
              <Crown className="size-4 shrink-0 text-gold" />
              {data.nb_themes_verrouilles} thème{data.nb_themes_verrouilles > 1 ? "s" : ""} de plus, réservé
              {data.nb_themes_verrouilles > 1 ? "s" : ""} à l'abonnement Jusqu'à l'Examen.
            </p>
            <Button asChild size="sm" className="w-fit">
              <Link to={`/abonnement?cursus=${cursusId}`}>Débloquer avec Jusqu'à l'Examen</Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
