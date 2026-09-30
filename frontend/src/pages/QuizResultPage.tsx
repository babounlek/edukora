import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { ArrowRight, BookOpen, CalendarCheck, CheckCircle2, FileText, Flame, ListChecks, RotateCcw } from "lucide-react"

import { completeQuizSession, refaireLesRatees, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizResult, QuizThemeScore } from "@/api/types"
import { themeExercicesPath } from "@/lib/countryPath"
import { Button } from "@/components/ui/button"
import { PrioritesExamen } from "@/components/PrioritesExamen"
import { QuizFichePdfButtons } from "@/components/QuizFichePdfButtons"
import { Skeleton } from "@/components/ui/skeleton"
import { useCountry } from "@/context/CountryContext"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn } from "@/lib/utils"

const CONFETTI_COULEURS = ["bg-gold", "bg-primary", "bg-success", "bg-info", "bg-warning"]

/** Pluie de confettis pour un beau score - décorative, coupée si mouvement réduit (voir index.css). */
function Confettis() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-x-0 top-0 h-0 overflow-visible">
      {Array.from({ length: 28 }).map((_, i) => (
        <span
          key={i}
          className={"quiz-confetti-piece " + CONFETTI_COULEURS[i % CONFETTI_COULEURS.length]}
          style={
            {
              left: (i * 37) % 100 + "%",
              animationDelay: (i % 7) * 0.12 + "s",
              "--dx": ((i % 5) - 2) * 26 + "px",
              "--rot": 360 + (i % 4) * 180 + "deg",
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  )
}

/** Anneau de score : se remplit au montage, la couleur suit le niveau atteint. */
function AnneauScore({ pourcentage, score, total }: { pourcentage: number; score: number; total: number }) {
  const [rempli, setRempli] = useState(false)
  useEffect(() => {
    const t = setTimeout(() => setRempli(true), 100)
    return () => clearTimeout(t)
  }, [])
  const rayon = 52
  const circonference = 2 * Math.PI * rayon
  const couleur = pourcentage >= 70 ? "text-success" : pourcentage >= 40 ? "text-gold-text" : "text-primary"
  return (
    <div className="relative mx-auto size-40">
      <svg viewBox="0 0 120 120" className="size-full -rotate-90">
        <circle cx="60" cy="60" r={rayon} fill="none" strokeWidth="10" className="stroke-secondary" />
        <circle
          cx="60"
          cy="60"
          r={rayon}
          fill="none"
          strokeWidth="10"
          strokeLinecap="round"
          className={"stroke-current transition-all duration-[1400ms] ease-out " + couleur}
          strokeDasharray={circonference}
          strokeDashoffset={rempli ? circonference * (1 - pourcentage / 100) : circonference}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-4xl font-semibold tabular-nums">{pourcentage}%</span>
        <span className="text-xs text-muted-foreground">
          {score} / {total}
        </span>
      </div>
    </div>
  )
}

/**
 * Un thème du quiz, avec ses suites possibles : exercices corrigés du thème (vrais
 * sujets d'examen), cours à relire s'il y en a un, et un quiz ciblé pour le retravailler
 * tout de suite - le même trio que sur /themes-frequents.
 */
function LigneTheme({
  theme, cursusId, country, onQuiz, lancement,
}: {
  theme: QuizThemeScore
  cursusId: number
  country: string
  onQuiz: () => void
  lancement: boolean
}) {
  const taux = theme.total > 0 ? Math.round((100 * theme.reussies) / theme.total) : 0
  const tonalite = taux >= 70 ? "bg-success" : taux >= 40 ? "bg-gold" : "bg-destructive/70"
  return (
    <li className="flex flex-col gap-3 px-4 py-3.5 sm:flex-row sm:items-center sm:gap-4 sm:px-5">
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-3">
          <span className="min-w-0 flex-1 truncate font-medium">{capitaliserTheme(theme.theme)}</span>
          <span className="shrink-0 text-sm font-semibold tabular-nums">
            {theme.reussies}
            <span className="font-normal text-muted-foreground"> / {theme.total}</span>
          </span>
        </div>
        <span className="mt-2 block h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <span className={cn("block h-full rounded-full transition-[width] duration-700", tonalite)} style={{ width: `${Math.max(taux, 4)}%` }} />
        </span>
      </div>
      <div className="flex shrink-0 flex-wrap gap-1.5">
        {theme.subject_code && (
          <Button asChild size="sm" variant="outline" className="h-8 px-2.5 text-xs">
            <Link to={`${themeExercicesPath(country, theme.theme_id)}?subject=${theme.subject_code}&cursus=${cursusId}`}>
              <FileText className="size-3.5" />
              Exercices
            </Link>
          </Button>
        )}
        {theme.cours && (
          <Button asChild size="sm" variant="outline" className="h-8 px-2.5 text-xs">
            <Link to={`/cours/${theme.cours.slug}`}>
              <BookOpen className="size-3.5" />
              Cours
            </Link>
          </Button>
        )}
        {theme.subject_code && (
          <Button size="sm" variant={taux < 70 ? "default" : "outline"} className="h-8 px-2.5 text-xs" onClick={onQuiz} disabled={lancement}>
            <ListChecks className="size-3.5" />
            {lancement ? "Préparation..." : "Quiz ciblé"}
          </Button>
        )}
      </div>
    </li>
  )
}

function messageDeFin(pourcentage: number, diagnostic: boolean) {
  // Un diagnostic n'est pas une note : un 30 % n'y est pas un échec, c'est un point
  // de départ. Le message ne doit ni féliciter ni consoler.
  if (diagnostic) return { titre: "Voilà ton point de départ", texte: "Ce n'est pas une note : c'est ce qui permet de te proposer les bonnes séances." }
  if (pourcentage >= 90) return { titre: "Sans faute, ou presque !", texte: "Tu maîtrises ce sujet. Continue sur cette lancée." }
  if (pourcentage >= 70) return { titre: "Très beau score !", texte: "Encore un petit effort sur les points ratés et ce sera parfait." }
  if (pourcentage >= 40) return { titre: "Bon travail, tu progresses !", texte: "Les cours à revoir ci-dessous te feront gagner des points au prochain essai." }
  return { titre: "Chaque quiz te rapproche de l'examen", texte: "Relis les cours proposés puis refais un quiz : tu verras la différence." }
}

export function QuizResultPage() {
  const queryClient = useQueryClient()
  useSeo({ title: "Résultat du quiz" })

  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { country } = useCountry()
  const [result, setResult] = useState<QuizResult | null>(null)
  const [error, setError] = useState("")
  const [refaisant, setRefaisant] = useState(false)
  const [erreurRefaire, setErreurRefaire] = useState("")
  const [themeEnLancement, setThemeEnLancement] = useState<number | null>(null)
  const [erreurQuizCible, setErreurQuizCible] = useState("")

  async function quizCible(themeId: number) {
    if (!result || themeEnLancement !== null) return
    setThemeEnLancement(themeId)
    setErreurQuizCible("")
    try {
      const session = await startQuizSession({ cursus: result.cursus, theme: themeId, mode: "PRATIQUE", n: 10 })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setErreurQuizCible(err instanceof ApiError ? err.message : "Impossible de lancer ce quiz.")
      setThemeEnLancement(null)
    }
  }

  async function refaireLesRatees_() {
    if (refaisant) return
    setRefaisant(true)
    setErreurRefaire("")
    try {
      const session = await refaireLesRatees(Number(id))
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setErreurRefaire(err instanceof ApiError ? err.message : "Impossible de relancer ces questions.")
      setRefaisant(false)
    }
  }

  useEffect(() => {
    if (!id) return
    // Endpoint idempotent : si la session est déjà terminée, il se contente de
    // retourner le résultat déjà calculé (voir quiz.views.complete_session).
    completeQuizSession(Number(id))
      .then((resultat) => {
        setResult(resultat)
        // Terminer un quiz change TOUT ce qui se calcule à partir des réponses :
        // le taux de maîtrise d'un thème dans le parcours, l'histogramme par matière,
        // la file de révision espacée, et la séance du jour - que ce quiz vient
        // peut-être de clôturer (voir quiz.views.complete_session).
        //
        // Sans cette invalidation, l'élève revenait sur son parcours et retrouvait
        // ses chiffres d'avant : `staleTime` est à 60 s et `refetchOnWindowFocus` est
        // désactivé (voir main.tsx, choix assumé pour un catalogue qui ne bouge pas),
        // donc rien ne déclenchait de rafraîchissement. Le travail était bien
        // enregistré côté serveur - il ne se voyait simplement pas, ce qui est pire
        // qu'une erreur : l'élève croit que son quiz n'a servi à rien.
        for (const cle of ["parcours", "parcours-resume", "maitrise", "revisions-dues", "plan-du-jour", "priorites", "bilan-periode"]) {
          queryClient.invalidateQueries({ queryKey: [cle] })
        }
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger ce résultat.")
      })
  }, [id, queryClient])

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link to="/quiz" className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour au quiz
        </Link>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="mx-auto max-w-xl px-4 py-10">
        <Skeleton className="mb-4 h-8 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    )
  }

  const pourcentage = result.questions_repondues > 0 ? Math.round((result.score / result.questions_repondues) * 100) : 0
  const diagnostic = result.mode === "DIAGNOSTIC"
  // Le thème le plus faible qui a un cours à relire : c'est LE cours à recommander en premier.
  const aRevoir = result.par_theme
    .filter((theme) => theme.cours && 100 * theme.reussies / theme.total < 70)
    .sort((a, b) => a.reussies / a.total - b.reussies / b.total)[0]
  const message = messageDeFin(pourcentage, diagnostic)

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      {/* En-tête : même gabarit que les autres pages - l'anneau de score à gauche, le
          message et les chiffres de la séance à droite. */}
      <div className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        {pourcentage >= 70 && !diagnostic && <Confettis />}
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative flex flex-col items-center gap-6 text-center sm:flex-row sm:gap-10 sm:text-left">
          <div className="shrink-0">
            <AnneauScore pourcentage={pourcentage} score={result.score} total={result.questions_repondues} />
          </div>
          <div className="min-w-0">
            <p className="mb-2 font-display text-sm italic text-primary">
              {diagnostic ? "Test de niveau terminé" : "Quiz terminé"}
            </p>
            <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight sm:text-4xl">{message.titre}</h1>
            <p className="mt-2 max-w-md text-muted-foreground">{message.texte}</p>
            {!diagnostic && (
              <div className="mt-4 flex flex-wrap justify-center gap-2 sm:justify-start">
                <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm shadow-xs">
                  <Flame className="size-4 text-warning" />
                  <span className="font-medium tabular-nums">{result.meilleure_serie}</span>
                  <span className="text-muted-foreground">
                    {result.meilleure_serie > 1 ? "bonnes réponses d'affilée" : "meilleure série"}
                  </span>
                </span>
                <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm shadow-xs">
                  <CalendarCheck className="size-4 text-primary" />
                  <span className="font-medium tabular-nums">{result.seances_cette_semaine}</span>
                  <span className="text-muted-foreground">
                    séance{result.seances_cette_semaine > 1 ? "s" : ""} cette semaine
                  </span>
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Le diagnostic ouvre sur ses priorités : c'est ce que l'élève venait chercher. */}
      {diagnostic && <PrioritesExamen cursusId={result.cursus} className="mb-6" />}

      {/* Le moment qui donne envie de revenir demain : on dit que la séance est faite
          et on ramène à "Aujourd'hui", d'où l'élève pourra en demander une autre. */}
      {result.seance_validee && (
        <div className="mb-6 flex flex-col gap-3 rounded-xl border border-primary/30 bg-primary/5 p-4 sm:flex-row sm:items-center">
          <CheckCircle2 className="size-6 shrink-0 text-primary" />
          <div className="min-w-0 flex-1">
            <p className="font-display font-semibold">Séance du jour validée</p>
            <p className="text-sm text-muted-foreground">Bien joué : tu as fait ce qu'il fallait pour aujourd'hui.</p>
          </div>
          <Button asChild>
            <Link to={`/${country}`}>
              Revenir à Aujourd'hui
              <ArrowRight />
            </Link>
          </Button>
        </div>
      )}

      {/* Par thème, du plus fragile au plus solide : c'est là que se décide la suite. */}
      {result.par_theme.length > 0 && (
        <section aria-labelledby="par-theme-titre" className="mb-6">
          <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
            <h2 id="par-theme-titre" className="font-display text-xl font-semibold">Résultat par thème</h2>
            <p className="text-sm text-muted-foreground">Du plus fragile au plus solide</p>
          </div>
          <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            {[...result.par_theme]
              .sort((a, b) => a.reussies / a.total - b.reussies / b.total)
              .map((theme) => (
                <LigneTheme
                  key={theme.theme}
                  theme={theme}
                  cursusId={result.cursus}
                  country={country}
                  onQuiz={() => quizCible(theme.theme_id)}
                  lancement={themeEnLancement === theme.theme_id}
                />
              ))}
          </ul>
          {erreurQuizCible && <p role="alert" className="mt-2 text-sm text-destructive">{erreurQuizCible}</p>}
        </section>
      )}

      <div className="mb-6">
        <QuizFichePdfButtons sessionId={Number(id)} />
      </div>

      {/* La suite, dans l'ordre où elle sert : comprendre ce qui a été raté, PUIS le refaire.
          Quatre boutons de même poids laissaient l'élève choisir seul au moment où il a
          le plus besoin qu'on le guide. Pas pour un diagnostic, dont la suite est la
          première séance (voir PrioritesExamen). */}
      {!diagnostic && (aRevoir || result.nb_ratees > 0) && (
        <section className="mb-6 rounded-2xl border border-primary/25 bg-primary/[0.04] p-4 sm:p-5">
          <h2 className="font-display text-lg font-semibold">Pour progresser</h2>
          <ol className="mt-3 flex flex-col gap-2.5">
            {aRevoir?.cours && (
              <li>
                <Link
                  to={`/cours/${aRevoir.cours.slug}`}
                  className="group flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 transition-colors hover:border-primary/50"
                >
                  <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary font-display text-sm font-semibold text-primary-foreground">1</span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-semibold">Revoir le cours</span>
                    <span className="block truncate text-sm text-muted-foreground">{aRevoir.cours.titre}</span>
                  </span>
                  <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
                </Link>
              </li>
            )}
            {result.nb_ratees > 0 && (
              <li>
                <button
                  type="button"
                  onClick={refaireLesRatees_}
                  disabled={refaisant}
                  className="group flex w-full items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 text-left transition-colors hover:border-primary/50 disabled:opacity-60"
                >
                  <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary font-display text-sm font-semibold text-primary-foreground">
                    {aRevoir?.cours ? 2 : 1}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-semibold">
                      {refaisant ? "Je prépare tes questions…" : `Refaire ${result.nb_ratees === 1 ? "la question ratée" : `les ${result.nb_ratees} questions ratées`}`}
                    </span>
                    <span className="block text-sm text-muted-foreground">Seulement celles-là, pour vérifier que c'est acquis.</span>
                  </span>
                  <RotateCcw className="size-4 shrink-0 text-primary" />
                </button>
                {erreurRefaire && <p role="alert" className="mt-2 text-sm text-destructive">{erreurRefaire}</p>}
              </li>
            )}
          </ol>
        </section>
      )}

      <div className="flex flex-col gap-2 sm:flex-row">
        <Button
          onClick={() => navigate("/quiz")}
          className="flex-1"
          size="lg"
          variant={!diagnostic && (aRevoir || result.nb_ratees > 0) ? "outline" : "default"}
        >
          {!diagnostic && (aRevoir || result.nb_ratees > 0) ? "Un autre quiz" : "Refaire un quiz"}
        </Button>
        {result.subject && (
          <Button asChild variant="outline" className="flex-1" size="lg">
            <Link to={`/parcours/${result.subject}?cursus=${result.cursus}`}>Retour au parcours</Link>
          </Button>
        )}
        <Button asChild variant="outline" className="flex-1" size="lg">
          <Link to="/compte">Mon compte</Link>
        </Button>
      </div>
    </div>
  )
}
