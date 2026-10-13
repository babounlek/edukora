import { Link } from "react-router-dom"
import { ArrowRight, BookOpen, History, RotateCcw, Sparkles, TrendingUp } from "lucide-react"

import type { Accueil, DepuisLaDerniereVisite } from "@/api/types"
import { Ecrin } from "@/components/Progression"
import { formatDepuis } from "@/lib/formatDepuis"
import { epreuveReaderPath } from "@/lib/countryPath"
import { langueCourante, t, tn, useI18n } from "@/lib/i18n"

/**
 * "Depuis la dernière fois" : ce qui a BOUGÉ, pas où l'on en est.
 *
 * Le niveau ("12 savoirs maîtrisés") décrit un état, il ne donne aucune raison de
 * revenir. Le mouvement ("deux de plus depuis mardi, et la Chimie qui décolle") en
 * donne une : c'est ce que montrent Strava ou Duolingo à l'ouverture, et ce que cette
 * page ne disait jamais. Tout vient du serveur (voir quiz.accueil.delta_depuis), qui
 * ne raconte que ce qui est vrai - le bloc disparaît quand rien n'a bougé.
 *
 * Dessous, ce qu'il y a à REPRENDRE : deux révisions dues au plus (la direction, pas
 * la liste des corvées - le reste vit dans Ma progression) et une lecture ouverte
 * cette semaine.
 */
export function DepuisLaDerniereFois({
  depuis, revisions, lecture,
}: {
  depuis: DepuisLaDerniereVisite | null
  revisions: Accueil["revisions"]
  lecture: Accueil["lecture"]
}) {
  useI18n()
  const aDuMouvement = depuis !== null
  const aReprendre = revisions.length > 0 || lecture !== null
  if (!aDuMouvement && !aReprendre) return null

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("depuis.aria")}>
      <Ecrin variante="sobre" className="sm:p-6">
        {depuis && (
          <div>
            <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
              <History className="size-3.5" />
              {t("depuis.titre", { quand: formatDepuis(depuis.depuis) })}
            </p>
            <ul className="mt-3 flex flex-col gap-2 text-sm">
              {(depuis.seances > 0 || depuis.questions > 0) && (
                <li className="flex items-start gap-2.5">
                  <Sparkles className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
                  <span>
                    {depuis.seances > 0 && (
                      <>
                        <strong className="font-semibold tabular-nums">{depuis.seances}</strong> {tn("depuis.seances", depuis.seances)}
                      </>
                    )}
                    {depuis.seances > 0 && depuis.questions > 0 && " · "}
                    {depuis.questions > 0 && (
                      <>
                        <strong className="font-semibold tabular-nums">{depuis.questions}</strong> {tn("depuis.questions", depuis.questions)}
                      </>
                    )}
                  </span>
                </li>
              )}
              {depuis.themes_consolides.length > 0 && (
                <li className="flex items-start gap-2.5">
                  <TrendingUp className="mt-0.5 size-4 shrink-0 text-success" aria-hidden="true" />
                  <span>
                    {tn("depuis.solide", depuis.themes_consolides_total > 1 ? 2 : 1)}{" "}
                    {depuis.themes_consolides.map((t, i) => (
                      <span key={`${t.theme}-${i}`}>
                        {i > 0 && ", "}
                        <strong className="font-semibold">{majuscule(t.theme)}</strong>
                        <span className="text-muted-foreground"> ({t.subject_label})</span>
                      </span>
                    ))}
                    {depuis.themes_consolides_total > depuis.themes_consolides.length && (
                      <span className="text-muted-foreground">
                        {" "}{tn("depuis.autres", depuis.themes_consolides_total - depuis.themes_consolides.length)}
                      </span>
                    )}
                  </span>
                </li>
              )}
              {depuis.matiere_en_hausse && (
                <li className="flex items-start gap-2.5">
                  <TrendingUp className="mt-0.5 size-4 shrink-0 text-success" aria-hidden="true" />
                  <span>
                    <strong className="font-semibold">{depuis.matiere_en_hausse.subject_label}</strong> {t("depuis.monte_de")}{" "}
                    <strong className="font-semibold tabular-nums">{depuis.matiere_en_hausse.gain}</strong> {t("depuis.points")}
                  </span>
                </li>
              )}
              {depuis.revisions_tenues > 0 && (
                <li className="flex items-start gap-2.5">
                  <RotateCcw className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
                  <span>
                    <strong className="font-semibold tabular-nums">{depuis.revisions_tenues}</strong> {tn("depuis.revisions", depuis.revisions_tenues)}
                  </span>
                </li>
              )}
            </ul>
          </div>
        )}

        {aReprendre && (
          <div className={depuis ? "mt-5 border-t border-border/60 pt-4" : undefined}>
            <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              <RotateCcw className="size-3.5" />
              {t("depuis.a_reprendre")}
            </p>
            <ul className="mt-3 flex flex-col gap-1.5">
              {revisions.map((revision) => (
                <li key={revision.id}>
                  <Link
                    to={`/quiz?cursus=${revision.cursus}&theme=${revision.theme_id}`}
                    className="group flex items-center gap-2.5 rounded-lg border border-border bg-background px-3 py-2.5 text-sm transition-colors hover:border-primary/40"
                  >
                    <span className="min-w-0 flex-1 truncate font-medium">{majuscule(revision.theme)}</span>
                    <span className="shrink-0 text-xs text-muted-foreground">{revision.subject_label}</span>
                    {/* Un retard se dit, il ne se reproche pas : gris, jamais rouge. */}
                    {revision.jours_retard > 0 && (
                      <span className="shrink-0 text-xs text-muted-foreground">{t("depuis.jours_retard", { n: revision.jours_retard })}</span>
                    )}
                    <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
                  </Link>
                </li>
              ))}
              {lecture && (
                <li>
                  <Link
                    to={epreuveReaderPath(lecture.country, lecture.slug)}
                    className="group flex items-center gap-2.5 rounded-lg border border-border bg-background px-3 py-2.5 text-sm transition-colors hover:border-primary/40"
                  >
                    <BookOpen className="size-4 shrink-0 text-primary" aria-hidden="true" />
                    <span className="min-w-0 flex-1 truncate font-medium">{lecture.title}</span>
                    <span className="shrink-0 text-xs text-muted-foreground">{t("depuis.lecture_en_cours")}</span>
                    <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
                  </Link>
                </li>
              )}
            </ul>
          </div>
        )}
      </Ecrin>
    </section>
  )
}

function majuscule(texte: string): string {
  return texte.charAt(0).toLocaleUpperCase(langueCourante()) + texte.slice(1)
}
