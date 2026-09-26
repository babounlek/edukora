import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { ArrowRight, BookOpen, CalendarCheck, CheckCircle2, Flame, RotateCcw } from "lucide-react"

import { completeQuizSession, refaireLesRatees } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizResult } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
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
  const couleur = pourcentage >= 70 ? "text-success" : pourcentage >= 40 ? "text-gold" : "text-primary"
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
    <div className={cn("mx-auto animate-fade-up px-4 py-10", diagnostic ? "max-w-3xl" : "max-w-xl")}>
      <div className="relative mb-8 text-center">
        {pourcentage >= 70 && !diagnostic && <Confettis />}
        <AnneauScore pourcentage={pourcentage} score={result.score} total={result.questions_repondues} />
        <h1 className="mt-5 font-display text-3xl font-semibold">{message.titre}</h1>
        <p className="mx-auto mt-2 max-w-sm text-muted-foreground">{message.texte}</p>
      </div>

      {/* Le diagnostic ouvre sur ses priorités : c'est ce que l'élève venait chercher. */}
      {diagnostic && <PrioritesExamen cursusId={result.cursus} className="mb-6" />}

      {!diagnostic && (
      <div className="mb-6 grid grid-cols-2 gap-3">
        <div className="flex items-center gap-3 rounded-xl border bg-card p-3.5">
          <Flame className="size-6 shrink-0 text-warning" />
          <div>
            <p className="font-display text-xl font-semibold tabular-nums">{result.meilleure_serie}</p>
            <p className="text-xs text-muted-foreground">
              {result.meilleure_serie > 1 ? "bonnes réponses d'affilée" : "meilleure série"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-xl border bg-card p-3.5">
          <CalendarCheck className="size-6 shrink-0 text-primary" />
          <div>
            <p className="font-display text-xl font-semibold tabular-nums">{result.seances_cette_semaine}</p>
            <p className="text-xs text-muted-foreground">
              séance{result.seances_cette_semaine > 1 ? "s" : ""} cette semaine
            </p>
          </div>
        </div>
      </div>
      )}

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

      {result.par_theme.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">Résultat par thème</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-3">
              {result.par_theme.map((theme) => (
                <li key={theme.theme} className="text-sm">
                  <div className="flex items-center justify-between">
                    <span>{capitaliserTheme(theme.theme)}</span>
                    <span className="text-muted-foreground">
                      {theme.reussies} / {theme.total}
                    </span>
                  </div>
                  {theme.cours && (
                    <Link
                      to={`/cours/${theme.cours.slug}`}
                      className="mt-1.5 flex items-center gap-2 rounded-md bg-muted/60 px-3 py-2 text-muted-foreground hover:text-foreground"
                    >
                      <BookOpen className="size-4 shrink-0 text-primary" />
                      <span className="min-w-0 flex-1 truncate">À revoir : {theme.cours.titre}</span>
                      <ArrowRight className="size-4 shrink-0" />
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
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
