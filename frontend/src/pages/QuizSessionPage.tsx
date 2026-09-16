import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import { ArrowLeft, BookOpenText, Check, X } from "lucide-react"

import { answerQuizQuestion, completeQuizSession, getQuizSession, revealQuizCorrige } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizCorrige, QuizSession } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { QuizFichePdfButtons } from "@/components/QuizFichePdfButtons"
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

export function QuizSessionPage() {
  useSeo({ title: "Quiz" })

  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [session, setSession] = useState<QuizSession | null>(null)
  const [error, setError] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)
  const [revealed, setRevealed] = useState<Record<number, QuizCorrige>>({})
  const [submitting, setSubmitting] = useState(false)

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

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-8 sm:px-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <Link
          to={session.subject ? `/parcours/${session.subject}?cursus=${session.cursus}` : "/quiz"}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary"
        >
          <ArrowLeft className="size-4" />
          Quitter le quiz
        </Link>
        <QuizFichePdfButtons sessionId={session.id} />
      </div>

      <div className="mb-3 flex flex-wrap items-center gap-1.5">
        <Badge variant="secondary">{session.cursus_display}</Badge>
        <Badge variant="outline">{question.subject_label}</Badge>
        {question.theme && <Badge variant="outline">{capitaliserTheme(question.theme)}</Badge>}
      </div>

      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">
          Question {currentIndex + 1} / {session.questions.length}
        </p>
        <div className="h-1.5 w-32 overflow-hidden rounded-full bg-secondary">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${((currentIndex + 1) / session.questions.length) * 100}%` }}
          />
        </div>
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

      <article className="prose prose-neutral max-w-none text-justify dark:prose-invert">
        <EpreuveMarkdown markdown={enonce} />
      </article>

      {question.type_reponse === "QCM" ? (
        <div className="mt-5 flex flex-col gap-2">
          {question.choix.map((choix) => {
            const isSelected = question.reponse?.reponse_choisie === choix.lettre
            const isCorrectChoice = question.reponse && question.reponse_correcte === choix.lettre
            return (
              <button
                key={choix.lettre}
                type="button"
                disabled={submitting || Boolean(question.reponse)}
                onClick={() => handleAnswerQcm(choix.lettre)}
                className={cn(
                  "flex items-center justify-between gap-2 rounded-md border px-3.5 py-2.5 text-left text-sm transition-colors disabled:cursor-default",
                  isCorrectChoice && "border-success bg-success/10",
                  isSelected && !isCorrectChoice && "border-destructive bg-destructive/10",
                  !question.reponse && "border-border hover:bg-accent/40",
                  question.reponse && !isSelected && !isCorrectChoice && "border-border opacity-60",
                )}
              >
                <span>
                  <span className="font-medium">{choix.lettre.toUpperCase()}.</span> <ChoixText texte={choix.texte} />
                </span>
                {isCorrectChoice && <Check className="size-4 shrink-0 text-success" />}
                {isSelected && !isCorrectChoice && <X className="size-4 shrink-0 text-destructive" />}
              </button>
            )
          })}
        </div>
      ) : (
        <div className="mt-5 flex flex-col gap-4">
          {!question.reponse && !questionCorrige && (
            <Button variant="outline" onClick={handleReveal} disabled={submitting}>
              Voir la correction
            </Button>
          )}

          {(questionCorrige || question.reponse) && (
            <article className="prose prose-neutral max-w-none border-l-2 border-border pl-4 text-justify dark:prose-invert">
              <EpreuveMarkdown markdown={question.corrige_markdown ?? questionCorrige?.corrige_markdown ?? ""} />
            </article>
          )}

          {questionCorrige && !question.reponse && (
            <div className="flex flex-col gap-2">
              <p className="text-sm text-muted-foreground">As-tu réussi cette question ?</p>
              <div className="flex gap-2">
                {RESULTAT_OPTIONS.map((option) => (
                  <Button
                    key={option.value}
                    variant="outline"
                    size="sm"
                    disabled={submitting}
                    onClick={() => handleDeclare(option.value)}
                  >
                    {option.label}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {question.reponse && (
            <Badge variant={question.reponse.est_correcte ? "success" : "outline"} className="w-fit">
              {question.reponse.est_correcte ? "Réussi" : question.reponse.resultat_declare === "PARTIEL" ? "Partiel" : "Échec"}
            </Badge>
          )}
        </div>
      )}

      {error && <p className="mt-4 text-sm text-destructive">{error}</p>}

      {question.reponse && (
        <Button onClick={handleNext} disabled={submitting} className="mt-6" size="lg">
          {isLast ? "Voir mon résultat" : "Question suivante"}
        </Button>
      )}
    </div>
  )
}
