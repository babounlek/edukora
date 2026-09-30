import { useEffect, useRef, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import { ArrowLeft, ArrowRight, BookOpenText, Check, FileText, Flame, Lightbulb, Sparkles, Target, X } from "lucide-react"

import { answerQuizQuestion, completeQuizSession, getQuizSession, revealQuizCorrige } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizCorrige, QuizSession } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { QuizFichePdfButtons } from "@/components/QuizFichePdfButtons"
import { useCountry } from "@/context/CountryContext"
import { themeExercicesPath } from "@/lib/countryPath"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn } from "@/lib/utils"

/** Rendu inline (pas de <p> bloc) pour le texte d'un choix QCM, qui peut contenir du LaTeX. */
function ChoixText({ texte }: { texte: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeRaw, rehypeKatex]}
      components={{ p: ({ children }) => <>{children}</> }}
    >
      {texte}
    </ReactMarkdown>
  )
}

const RESULTAT_OPTIONS: { value: "REUSSI" | "PARTIEL" | "ECHEC"; label: string }[] = [
  { value: "REUSSI", label: "Réussi" },
  { value: "PARTIEL", label: "Partiel" },
  { value: "ECHEC", label: "Échec" },
]

const MESSAGES_BONNE = ["Bravo !", "Excellent !", "Exactement !", "Bien vu !", "Tu maîtrises !"]
const MESSAGES_MAUVAISE = [
  "Pas tout à fait, mais c'est comme ça qu'on retient.",
  "Raté de peu : lis la correction, elle vaut de l'or.",
  "Une erreur comprise, c'est un point gagné pour l'examen.",
]

function pick(messages: string[], seed: number) {
  return messages[seed % messages.length]
}

/** Couleur du segment de progression d'une question, selon ce que l'élève en a fait. */
function segmentClass(q: QuizSession["questions"][number], isCurrent: boolean) {
  if (q.reponse) {
    if (q.reponse.est_correcte) return "bg-success"
    if (q.reponse.resultat_declare === "PARTIEL") return "bg-gold"
    return "bg-destructive"
  }
  return isCurrent ? "bg-primary" : "bg-secondary"
}

export function QuizSessionPage() {
  useSeo({ title: "Quiz" })

  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { country } = useCountry()

  const [session, setSession] = useState<QuizSession | null>(null)
  const [error, setError] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)
  const [revealed, setRevealed] = useState<Record<number, QuizCorrige>>({})
  const [submitting, setSubmitting] = useState(false)
  // Toujours la dernière version des gestionnaires, pour un écouteur clavier posé une seule fois.
  const keyHandlerRef = useRef<(e: KeyboardEvent) => void>(() => {})

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => keyHandlerRef.current(e)
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [])

  useEffect(() => {
    if (!id) return
    getQuizSession(Number(id))
      .then((data) => {
        if (data.completed_at) {
          navigate(`/quiz/session/${data.id}/resultat`, { replace: true })
          return
        }
        setSession(data)
        const firstUnanswered = data.questions.findIndex((q) => !q.reponse)
        setCurrentIndex(firstUnanswered === -1 ? 0 : firstUnanswered)
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger ce quiz.")
      })
  }, [id, navigate])

  if (error) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link to="/quiz" className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour au quiz
        </Link>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10">
        <Skeleton className="mb-6 h-4 w-32" />
        <Skeleton className="mb-3 h-6 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    )
  }

  const question = session.questions[currentIndex]
  const isLast = currentIndex === session.questions.length - 1
  const questionCorrige = revealed[question.id]

  function updateQuestion(updated: QuizSession["questions"][number]) {
    setSession((prev) => {
      if (!prev) return prev
      const questions = prev.questions.map((q) => (q.id === updated.id ? updated : q))
      return { ...prev, questions }
    })
  }

  async function handleAnswerQcm(lettre: string) {
    if (submitting || question.reponse) return
    setSubmitting(true)
    try {
      const updated = await answerQuizQuestion(session!.id, question.id, { reponse_choisie: lettre })
      updateQuestion(updated)
    } catch {
      setError("Impossible d'enregistrer ta réponse. Réessaie.")
    } finally {
      setSubmitting(false)
    }
  }

  async function handleReveal() {
    if (submitting) return
    setSubmitting(true)
    try {
      const corrige = await revealQuizCorrige(session!.id, question.id)
      setRevealed((prev) => ({ ...prev, [question.id]: corrige }))
    } catch {
      setError("Impossible de charger la correction. Réessaie.")
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDeclare(resultat: "REUSSI" | "PARTIEL" | "ECHEC") {
    if (submitting || question.reponse) return
    setSubmitting(true)
    try {
      const updated = await answerQuizQuestion(session!.id, question.id, { resultat_declare: resultat })
      updateQuestion(updated)
    } catch {
      setError("Impossible d'enregistrer ta réponse. Réessaie.")
    } finally {
      setSubmitting(false)
    }
  }

  async function handleNext() {
    if (!isLast) {
      setCurrentIndex((i) => i + 1)
      return
    }
    setSubmitting(true)
    try {
      await completeQuizSession(session!.id)
      trackEvent("quiz_completed", { cursus_id: session!.cursus, mode: session!.mode })
      navigate(`/quiz/session/${session!.id}/resultat`)
    } catch {
      setError("Impossible de terminer le quiz. Réessaie.")
      setSubmitting(false)
    }
  }

  const enonce = question.enonce_intro_markdown
    ? `${question.enonce_intro_markdown}\n\n${question.enonce_markdown}`
    : question.enonce_markdown

  const total = session.questions.length
  const answeredCount = session.questions.filter((q) => q.reponse).length
  const score = session.questions.filter((q) => q.reponse?.est_correcte).length
  // Série en cours : bonnes réponses consécutives jusqu'à la question affichée incluse.
  let streak = 0
  for (const q of session.questions.slice(0, currentIndex + 1)) {
    streak = q.reponse?.est_correcte ? streak + 1 : 0
  }
  // Relecture : on peut revenir sur toute question déjà répondue, et sur la première
  // restée sans réponse - jamais sauter en avant, l'ordre de la séance reste celui du quiz.
  const premiereSansReponse = session.questions.findIndex((q) => !q.reponse)
  const accessible = (i: number) => Boolean(session.questions[i].reponse) || i === premiereSansReponse
  const SubjectIcon = subjectIcon(question.subject_code ?? "")
  // Exercices corrigés du thème (/themes-frequents/<id>/exercices) : le pont entre une
  // question et un vrai sujet d'examen sur la même notion.
  const lienExercicesTheme =
    question.theme_id && question.subject_code
      ? `${themeExercicesPath(country, question.theme_id)}?subject=${question.subject_code}&cursus=${session.cursus}`
      : null
  const isQcm = question.type_reponse === "QCM"
  const answered = Boolean(question.reponse)
  const correct = question.reponse?.est_correcte

  keyHandlerRef.current = (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return
    const target = e.target as HTMLElement | null
    if (target && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return
    if (answered && (e.key === "Enter" || e.key === "ArrowRight")) {
      e.preventDefault()
      void handleNext()
      return
    }
    if (isQcm && !answered) {
      const choix = question.choix.find((c) => c.lettre.toLowerCase() === e.key.toLowerCase())
      if (choix) void handleAnswerQcm(choix.lettre)
    }
  }

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 pb-28 pt-6 sm:px-6 sm:pb-10 sm:pt-10">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <Link
          to={session.subject ? `/parcours/${session.subject}?cursus=${session.cursus}` : "/quiz"}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary"
        >
          <ArrowLeft className="size-4" />
          Quitter le quiz
        </Link>
        <QuizFichePdfButtons sessionId={session.id} />
      </div>

      {/* Progression : un segment par question, coloré selon le résultat - on voit d'un
          coup d'œil où l'on en est et comment ça se passe. Un segment déjà répondu se
          clique pour relire sa correction. */}
      <div className="mb-2 flex gap-1" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={answeredCount}>
        {session.questions.map((q, i) => (
          <button
            key={q.id}
            type="button"
            disabled={!accessible(i)}
            onClick={() => setCurrentIndex(i)}
            aria-label={`Question ${i + 1}`}
            title={accessible(i) ? `Question ${i + 1}` : undefined}
            className={cn(
              "h-2.5 flex-1 rounded-full transition-all duration-500 enabled:cursor-pointer enabled:hover:scale-y-150 disabled:cursor-default",
              segmentClass(q, i === currentIndex),
              i === currentIndex && "ring-2 ring-primary/30 ring-offset-1 ring-offset-background",
            )}
          />
        ))}
      </div>
      <div className="mb-5 flex items-center justify-between text-sm">
        <p className="font-medium text-muted-foreground">
          Question {currentIndex + 1} sur {total}
        </p>
        <div className="flex items-center gap-3">
          {streak >= 2 && (
            <span className="inline-flex items-center gap-1 rounded-full bg-gold/15 px-2.5 py-0.5 font-semibold">
              <Flame className="animate-quiz-flame size-4 text-warning" />
              {streak} d'affilée
            </span>
          )}
          <span className="font-semibold tabular-nums text-foreground">
            {score} <span className="font-normal text-muted-foreground">/ {answeredCount} juste{score > 1 ? "s" : ""}</span>
          </span>
        </div>
      </div>

      {/* key = id de la question : la carte se rejoue à chaque question, ça donne le rythme. */}
      <div key={question.id} className="animate-fade-up rounded-3xl border border-border bg-card p-5 shadow-lg shadow-primary/5 sm:p-8">
        <div className="mb-5 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/40 py-0.5 pl-0.5 pr-2.5 text-xs font-medium">
            <span className={cn("flex size-5 items-center justify-center rounded-full", couleurMatiere(question.subject_code).puce)}>
              <SubjectIcon className="size-3" aria-hidden="true" />
            </span>
            {question.subject_label}
          </span>
          <Badge variant="secondary">{session.cursus_display}</Badge>
          {question.theme && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-gold/40 bg-gold/10 px-2.5 py-0.5 text-xs font-semibold text-gold-text">
              <Target className="size-3" />
              {capitaliserTheme(question.theme)}
            </span>
          )}
        </div>

        {/* Uniquement pour l'historique pré-bascule : un CompetenceItem n'appartient à
            aucune épreuve/leçon d'origine vers laquelle renvoyer (voir QuizQuestion ci-dessus). */}
        {question.lesson_id && (
          <a
            href={`/epreuves/${question.lesson_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="mb-4 flex w-fit items-center gap-1.5 rounded-md border border-dashed border-border px-3 py-1.5 text-sm font-medium text-primary hover:underline"
          >
            <BookOpenText className="size-3.5" />
            Voir l'épreuve d'origine
          </a>
        )}

        <article className="prose prose-neutral max-w-none dark:prose-invert">
          <EpreuveMarkdown markdown={enonce} />
        </article>

        {isQcm ? (
          <div className="mt-6 flex flex-col gap-2.5">
            {question.choix.map((choix) => {
              const isSelected = question.reponse?.reponse_choisie === choix.lettre
              const isCorrectChoice = answered && question.reponse_correcte === choix.lettre
              return (
                <button
                  key={choix.lettre}
                  type="button"
                  disabled={submitting || answered}
                  onClick={() => handleAnswerQcm(choix.lettre)}
                  className={cn(
                    "group flex items-center gap-3 rounded-xl border-2 px-3.5 py-3 text-left text-[0.95rem] transition-all duration-200 disabled:cursor-default",
                    !answered &&
                      "border-border hover:-translate-y-0.5 hover:border-primary/60 hover:bg-accent/40 hover:shadow-sm active:translate-y-0",
                    isCorrectChoice && "animate-quiz-pop border-success bg-success/10",
                    isSelected && !isCorrectChoice && "animate-quiz-shake border-destructive bg-destructive/10",
                    answered && !isSelected && !isCorrectChoice && "border-border opacity-50",
                  )}
                >
                  <span
                    className={cn(
                      "flex size-8 shrink-0 items-center justify-center rounded-full border text-sm font-semibold transition-colors",
                      !answered && "bg-secondary group-hover:border-primary group-hover:bg-primary group-hover:text-primary-foreground",
                      isCorrectChoice && "border-success bg-success text-success-foreground",
                      isSelected && !isCorrectChoice && "border-destructive bg-destructive text-destructive-foreground",
                    )}
                  >
                    {isCorrectChoice ? (
                      <Check className="size-4" />
                    ) : isSelected ? (
                      <X className="size-4" />
                    ) : (
                      choix.lettre.toUpperCase()
                    )}
                  </span>
                  <span className="min-w-0 flex-1">
                    <ChoixText texte={choix.texte} />
                  </span>
                </button>
              )
            })}
            {!answered && (
              <p className="mt-1 hidden text-xs text-muted-foreground sm:block">
                Astuce : appuie sur {question.choix.map((c) => c.lettre.toUpperCase()).join(", ")} au clavier pour répondre.
              </p>
            )}
          </div>
        ) : (
          <div className="mt-6 flex flex-col gap-4">
            {!answered && !questionCorrige && (
              <div className="flex flex-col gap-3 rounded-2xl border border-dashed border-primary/30 bg-primary/[0.03] p-4 sm:flex-row sm:items-center sm:justify-between">
                <p className="flex items-start gap-2 text-sm text-muted-foreground">
                  <Lightbulb className="mt-0.5 size-4 shrink-0 text-gold-text" />
                  Essaie d'abord sur ton brouillon, puis compare avec la correction.
                </p>
                <Button size="lg" onClick={handleReveal} disabled={submitting} className="shrink-0">
                  <Sparkles />
                  Voir la correction
                </Button>
              </div>
            )}

            {(questionCorrige || answered) && (
              <article className="prose prose-neutral max-w-none rounded-xl border-l-4 border-primary/50 bg-muted/40 py-3 pl-4 pr-3 dark:prose-invert">
                <EpreuveMarkdown markdown={question.corrige_markdown ?? questionCorrige?.corrige_markdown ?? ""} />
              </article>
            )}

            {questionCorrige && !answered && (
              <div className="flex flex-col gap-2">
                <p className="text-sm font-medium">Sois honnête avec toi-même : as-tu réussi cette question ?</p>
                <div className="grid grid-cols-3 gap-2">
                  {RESULTAT_OPTIONS.map((option) => (
                    <Button
                      key={option.value}
                      variant="outline"
                      disabled={submitting}
                      onClick={() => handleDeclare(option.value)}
                      className={cn(
                        option.value === "REUSSI" && "hover:border-success hover:bg-success/10",
                        option.value === "PARTIEL" && "hover:border-gold hover:bg-gold/10",
                        option.value === "ECHEC" && "hover:border-destructive hover:bg-destructive/10",
                      )}
                    >
                      {option.label}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Le retour immédiat : dit tout de suite si c'est bon, encourage dans les deux cas. */}
        {answered && (
          <div
            role="status"
            className={cn(
              "animate-fade-up mt-5 flex items-start gap-3 rounded-xl border px-4 py-3",
              correct ? "border-success/40 bg-success/10" : "border-border bg-muted/50",
            )}
          >
            {correct ? (
              <Sparkles className="mt-0.5 size-5 shrink-0 text-success" />
            ) : (
              <BookOpenText className="mt-0.5 size-5 shrink-0 text-muted-foreground" />
            )}
            <div className="text-sm">
              <p className="font-display font-semibold">
                {correct
                  ? pick(MESSAGES_BONNE, question.id)
                  : question.reponse?.resultat_declare === "PARTIEL"
                    ? "Presque ! Tu y es presque."
                    : pick(MESSAGES_MAUVAISE, question.id)}
              </p>
              {correct && streak >= 3 && (
                <p className="text-muted-foreground">{streak} bonnes réponses d'affilée, tu es en feu.</p>
              )}
              {isQcm && !correct && question.reponse_correcte && (
                <p className="text-muted-foreground">
                  La bonne réponse était <strong>{question.reponse_correcte.toUpperCase()}</strong>.
                </p>
              )}
            </div>
          </div>
        )}

        {isQcm && answered && question.corrige_markdown && (
          <details className="mt-4 rounded-xl border bg-muted/30 px-4 py-3" open={!correct}>
            <summary className="cursor-pointer text-sm font-medium">Comprendre la correction</summary>
            <article className="prose prose-neutral mt-3 max-w-none dark:prose-invert">
              <EpreuveMarkdown markdown={question.corrige_markdown} />
            </article>
          </details>
        )}

        {/* Pour aller plus loin : un vrai sujet d'examen sur la même notion, dans un
            nouvel onglet pour ne pas perdre le fil de la séance. */}
        {answered && lienExercicesTheme && (
          <a
            href={lienExercicesTheme}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 flex items-center gap-3 rounded-xl border border-border px-4 py-3 text-sm transition-colors hover:border-primary/40 hover:bg-accent/40"
          >
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <FileText className="size-4" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block font-medium">Exercices corrigés sur ce thème</span>
              <span className="block text-muted-foreground">
                Des sujets d'examen réels sur « {capitaliserTheme(question.theme ?? "")} ».
              </span>
            </span>
            <ArrowRight className="size-4 shrink-0 text-primary" />
          </a>
        )}

        {error && <p className="mt-4 text-sm text-destructive">{error}</p>}
      </div>

      {/* Sur téléphone, "Question suivante" reste sous le pouce, sans remonter. */}
      {answered && (
        <div className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-background/95 px-4 py-3 backdrop-blur sm:static sm:mt-5 sm:flex sm:justify-end sm:border-0 sm:bg-transparent sm:p-0 sm:backdrop-blur-none">
          <Button onClick={handleNext} disabled={submitting} className="animate-fade-up w-full sm:w-auto" size="lg">
            {isLast ? "Voir mon résultat" : "Question suivante"}
            <ArrowRight />
          </Button>
        </div>
      )}
    </div>
  )
}
