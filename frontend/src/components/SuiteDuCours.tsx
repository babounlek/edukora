import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, FileText, ListChecks } from "lucide-react"

import { getThemesFrequents } from "@/api/endpoints"
import type { Cours } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { usePositionDansLaSeance } from "@/components/BarreSeance"
import { Button } from "@/components/ui/button"
import { themeExercicesPath } from "@/lib/countryPath"
import { capitaliserTheme } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * En bas d'un cours lu HORS séance du jour : où aller maintenant. Le cours finissait sur « Faire ma séance », le
 * bandeau de pied de page qui renvoie à l'accueil, sans lien vers les exercices ni le quiz du thème (test élève
 * 2026-10-24). Dans une séance, EtapeSuivante prend déjà la place : ce bloc s'efface.
 *
 * Le thème est celui du cours qui figure au classement des thèmes de sa matière et de son examen : c'est ce qui garantit
 * qu'il a des exercices, et dit si un quiz existe. Sans thème classé, rien n'est proposé plutôt qu'un lien vers une
 * page vide.
 */
export function SuiteDuCours({ cours }: { cours: Cours }) {
  useI18n()
  const { country } = useCountry()
  const position = usePositionDansLaSeance()
  const { user } = useAuth()
  // La plupart des cours n'ont aucun examen rattaché (voir catalog.models.q_cours_du_cursus) : on prend alors celui que
  // l'élève prépare. Un visiteur sans examen déclaré n'a pas de classement à consulter : rien n'est proposé.
  const cursusId = cours.cursus[0]?.id ?? user?.cursus_prepare?.id
  const subjectCode = cours.subject.code

  const { data: classement } = useQuery({
    queryKey: ["themes-frequents", cursusId, subjectCode],
    queryFn: ({ signal }) => getThemesFrequents(cursusId as number, subjectCode, signal),
    enabled: Boolean(cursusId),
  })

  if (position?.suivante || !cursusId || !classement?.disponible) return null
  const idsDuCours = new Set(cours.tags.map((tag) => tag.id))
  const theme = classement.themes.find((candidat) => idsDuCours.has(candidat.id))
  if (!theme) return null

  const lienExercices = `${themeExercicesPath(country, theme.id)}?subject=${subjectCode}&cursus=${cursusId}`
  return (
    <section aria-label={t("sc.titre")} className="mx-auto mt-10 max-w-3xl rounded-2xl border border-primary/30 bg-primary/5 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">{t("sc.titre")}</p>
      <p className="mt-1 font-display text-lg font-semibold">{capitaliserTheme(theme.tag)}</p>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <Button asChild size="lg" className="rounded-full">
          <Link to={lienExercices}>
            <FileText />
            {t("sc.exercices")}
            <ArrowRight />
          </Link>
        </Button>
        {theme.quiz_disponible && (
          <Button asChild size="lg" variant="outline" className="rounded-full">
            <Link to={`/quiz?cursus=${cursusId}&theme=${theme.id}`}>
              <ListChecks />
              {t("sc.quiz")}
            </Link>
          </Button>
        )}
      </div>
    </section>
  )
}
