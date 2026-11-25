import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ListChecks } from "lucide-react"

import { getEpreuveQuizThemes } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { capitaliserTheme, cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Quiz sur ces thèmes », sous une épreuve : se vérifier sur ce qu'elle mobilise. Ni la fiche, ni le lecteur, ni la page
 * d'un thème ne menaient au quiz (audit du 2026-11-25). Seuls les thèmes qui ont des questions pour l'examen sont proposés.
 */
export function QuizSurCesThemes({ slug, className }: { slug: string; className?: string }) {
  useI18n()
  const { user } = useAuth()
  const prepare = user?.cursus_prepare?.id
  const { data } = useQuery({
    queryKey: ["epreuve-themes-quiz", slug, prepare ?? null],
    queryFn: ({ signal }) => getEpreuveQuizThemes(slug, prepare, signal),
  })
  if (!data || data.cursus_id === null || data.themes.length === 0) return null
  return (
    <section aria-label={t("qct.titre")} className={cn("rounded-2xl border border-primary/30 bg-primary/5 p-5", className)}>
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
        <ListChecks className="size-3.5" aria-hidden="true" />
        {t("qct.titre")}
      </p>
      <p className="mt-1 text-sm text-muted-foreground">{t("qct.texte")}</p>
      <ul className="mt-3 flex flex-wrap gap-2">
        {data.themes.map((theme) => (
          <li key={theme.theme_id} className="max-w-full">
            <Link
              to={`/quiz?cursus=${data.cursus_id}&theme=${theme.theme_id}`}
              className="inline-flex min-h-9 max-w-full items-center rounded-full border border-primary/30 bg-card px-3.5 py-1.5 text-sm font-medium text-primary hover:border-primary"
            >
              <span className="truncate">{capitaliserTheme(theme.theme)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
