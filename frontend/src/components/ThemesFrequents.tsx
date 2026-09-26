import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Crown, FileText, ListChecks, TrendingUp } from "lucide-react"

import { getThemesFrequents } from "@/api/endpoints"
import { themeExercicesPath, themesFrequentsPath } from "@/lib/countryPath"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { capitaliserTheme, cn } from "@/lib/utils"

interface ThemesFrequentsProps {
  country: string
  cursusId: number
  subjectCode: string
  // "preview" : aperçu tronqué embarqué sur /epreuves (voir EpreuvesListPage) - le
  // classement complet reste à une page de là (ThemesFrequentsPage), qui rend ce
  // même composant en variant "full" (défaut). Le calcul complet (max 20, voir
  // MAX_THEMES_FREQUENTS côté backend) est toujours renvoyé par l'API ; seul
  // l'affichage se tronque ici, jamais un second appel réseau allégé.
  variant?: "preview" | "full"
}

const PREVIEW_LIMIT = 4

/**
 * Classement des thèmes les plus fréquents aux épreuves officielles d'une matière/série
 * - argument de vente propre au palier Jusqu'à l'Examen (voir
 * access.services.has_access_jusqua_examen côté backend). Disparaît silencieusement si
 * le corpus est trop mince pour un classement fiable (`disponible=false`) - même patron
 * que le rail "Corrigés populaires" sous son propre seuil (voir EpreuvesListPage).
 */
export function ThemesFrequents({ country, cursusId, subjectCode, variant = "full" }: ThemesFrequentsProps) {
  const { data } = useQuery({
    queryKey: ["themes-frequents", cursusId, subjectCode],
    queryFn: ({ signal }) => getThemesFrequents(cursusId, subjectCode, signal),
  })

  if (!data || !data.disponible || data.themes.length === 0) return null

  const themesAffiches = variant === "preview" ? data.themes.slice(0, PREVIEW_LIMIT) : data.themes

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

        <div className="flex flex-col gap-2">
          {themesAffiches.map((theme, index) => {
            const rang = index + 1
            const enTete = rang === 1
            return (
            <div
              key={theme.id}
              className={cn(
                "flex flex-col gap-2.5 rounded-xl border px-3 py-2.5 transition-colors sm:flex-row sm:items-center sm:gap-3",
                enTete
                  ? "border-gold/30 bg-gold/[0.05]"
                  : "border-transparent hover:border-border hover:bg-accent/40",
              )}
            >
              <div className="flex min-w-0 flex-1 items-center gap-3 text-sm">
                <span
                  className={cn(
                    "flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-bold tabular-nums",
                    enTete ? "bg-gold text-gold-foreground" : "bg-muted text-muted-foreground",
                  )}
                >
                  {enTete ? <Crown className="size-3.5" /> : rang}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="min-w-0 flex-1 truncate font-medium">{capitaliserTheme(theme.tag)}</span>
                    <span className={cn("shrink-0 text-xs font-semibold tabular-nums", enTete ? "text-gold" : "text-primary")}>
                      {theme.frequence_pct}%
                    </span>
                  </div>
                  <span className="mt-1.5 block h-1.5 w-full overflow-hidden rounded-full bg-primary/10">
                    <span
                      className={cn("block h-full rounded-full transition-[width] duration-500", enTete ? "bg-gold" : "bg-primary/60")}
                      style={{ width: `${theme.frequence_pct}%` }}
                    />
                  </span>
                </div>
                <span className="hidden w-20 shrink-0 text-right text-xs tabular-nums text-muted-foreground sm:block">
                  {theme.nb_epreuves}/{data.nb_sessions_disponibles}
                </span>
              </div>
              {/* Deux destinations distinctes plutôt qu'un choix unique imposé (retour
                  produit) : "Exercices" pour qui veut lire le corrigé complet en
                  contexte, "Quiz" pour qui veut s'entraîner directement sur des items
                  autonomes - jamais fusionnées, le bon choix dépend de l'élève, pas de
                  nous. */}
              <div className="flex shrink-0 gap-1.5 pl-9 sm:pl-0">
                <Button asChild size="sm" variant="outline" className="h-7 px-2.5 text-xs">
                  <Link
                    to={`${themeExercicesPath(country, theme.id)}?subject=${subjectCode}&cursus=${cursusId}&pct=${theme.frequence_pct}&nb=${theme.nb_epreuves}&total=${data.nb_sessions_disponibles}`}
                  >
                    <FileText className="size-3.5" />
                    Exercices
                  </Link>
                </Button>
                {theme.quiz_disponible ? (
                  <Button asChild size="sm" variant="outline" className="h-7 px-2.5 text-xs">
                    <Link to={`/quiz?cursus=${cursusId}&theme=${theme.id}`}>
                      <ListChecks className="size-3.5" />
                      Quiz
                    </Link>
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled
                    title="Pas encore de question de quiz sur ce thème précis"
                    className="h-7 px-2.5 text-xs"
                  >
                    <ListChecks className="size-3.5" />
                    Quiz
                  </Button>
                )}
              </div>
            </div>
            )
          })}
        </div>

        {variant === "preview" && (
          <Link
            to={`${themesFrequentsPath(country)}?subject=${subjectCode}&cursus=${cursusId}`}
            className="flex items-center gap-1 self-start text-xs font-medium text-primary hover:underline"
          >
            Voir le classement complet
            <ArrowRight className="size-3.5" />
          </Link>
        )}

        {variant === "full" && !data.has_access && data.nb_themes_verrouilles > 0 && (
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
