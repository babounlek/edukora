import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import { ArrowLeft, Check, FileDown, Flag, Timer, X } from "lucide-react"

import {
  answerTentativeQuestion,
  completeTentative,
  downloadSujetPdf,
  getTentativeInedite,
  startExamMode,
  toggleQuestionMarquee,
} from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { TentativeInedite, TentativeInediteQuestion } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { formatDuration } from "@/lib/duration"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"
import { catalogueHomePath } from "@/lib/countryPath"

/** Rendu inline (pas de <p> bloc) pour le texte d'un choix QCM, qui peut contenir du LaTeX. */
function ChoixText({ texte }: { texte: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
      components={{ p: ({ children }) => <>{children}</> }}
    >
      {texte}
    </ReactMarkdown>
  )
}

interface FlatQuestion extends TentativeInediteQuestion {
  numero_exercice: string
  points: string
}

function flattenQuestions(tentative: TentativeInedite): FlatQuestion[] {
  return tentative.exercices.flatMap((exercice) =>
    exercice.questions.map((question) => ({
      ...question,
      numero_exercice: exercice.numero_exercice,
      points: exercice.points,
    })),
  )
}

const RESULTAT_OPTIONS: { value: "REUSSI" | "PARTIEL" | "ECHEC"; label: string }[] = [
  { value: "REUSSI", label: "Réussi" },
  { value: "PARTIEL", label: "Partiel" },
  { value: "ECHEC", label: "Échec" },
]

export function InediteTentativePage() {
  useSeo({ title: "Épreuve inédite" })

  const { id } = useParams<{ id: string }>()

  const [tentative, setTentative] = useState<TentativeInedite | null>(null)
  const [questions, setQuestions] = useState<FlatQuestion[]>([])
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null)
  const [showCorrection, setShowCorrection] = useState(false)
  const [flaggedIds, setFlaggedIds] = useState<Set<number>>(new Set())
  const [startingExam, setStartingExam] = useState(false)
  const [downloadingSujet, setDownloadingSujet] = useState(false)

  useEffect(() => {
    if (!id) return
    getTentativeInedite(Number(id))
      .then((data) => {
        setTentative(data)
        setQuestions(flattenQuestions(data))
        setFlaggedIds(new Set(data.questions_marquees))
        setShowCorrection(data.submitted_at !== null)
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger cette épreuve.")
      })
  }, [id])

  // Chrono du mode examen - recalcule depuis un timestamp fixe (deadline) à chaque
  // tick plutôt que de décrémenter un compteur : robuste au throttling d'un onglet en
  // arrière-plan (même technique que LoginPage.tsx pour le cooldown de renvoi d'OTP).
  // Reclé sur exam_mode_started_at (pas started_at) : un chrono n'existe que si
  // l'élève a explicitement activé le mode examen.
  useEffect(() => {
    if (!tentative?.exam_mode_started_at || tentative.submitted_at || !tentative.duree_minutes) {
      setRemainingSeconds(null)
      return
    }
    const deadline = new Date(tentative.exam_mode_started_at).getTime() + tentative.duree_minutes * 60_000
    const tick = () => setRemainingSeconds(Math.max(0, Math.round((deadline - Date.now()) / 1000)))
    tick()
    const interval = window.setInterval(tick, 1000)
    return () => window.clearInterval(interval)
  }, [tentative?.exam_mode_started_at, tentative?.duree_minutes, tentative?.submitted_at])

  // À zéro, le serveur a déjà (ou va) verrouiller la tentative dès la prochaine
  // requête qui la touche (voir inedit.views._auto_complete_if_expired) - un simple
  // refetch suffit à faire apparaître submitted_at et le corrigé désormais disponible,
  // sans action explicite de l'élève.
  useEffect(() => {
    if (remainingSeconds !== 0 || !tentative || tentative.submitted_at) return
    getTentativeInedite(tentative.id).then((data) => {
      setTentative(data)
      setQuestions(flattenQuestions(data))
      setShowCorrection(true)
    })
  }, [remainingSeconds, tentative])

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link
          to={tentative ? `${catalogueHomePath(tentative.country.toLowerCase())}?origine=INEDITE#catalogue` : "/"}
          className="mt-3 inline-block text-sm text-primary hover:underline"
        >
          Retour au catalogue
        </Link>
      </div>
    )
  }

  if (!tentative || questions.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <Skeleton className="mb-6 h-4 w-32" />
        <Skeleton className="mb-3 h-6 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    )
  }

  const answeredCount = questions.filter((q) => q.reponse).length

  function updateQuestion(updated: TentativeInediteQuestion) {
    setQuestions((prev) => prev.map((q) => (q.id === updated.id ? { ...q, ...updated } : q)))
  }

  async function refetchAfterLock(autoLocked: boolean) {
    const data = await getTentativeInedite(tentative!.id)
    setTentative(data)
    setQuestions(flattenQuestions(data))
    setShowCorrection(true)
    trackEvent("inedit_tentative_completed", { epreuve_id: data.epreuve, auto_locked: autoLocked })
  }

  async function handleAnswerQcm(question: FlatQuestion, lettre: string) {
    if (submitting || showCorrection) return
    setSubmitting(true)
    try {
      const updated = await answerTentativeQuestion(tentative!.id, question.id, { reponse_choisie: lettre })
      updateQuestion(updated)
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        await refetchAfterLock(true)
      } else {
        setError("Impossible d'enregistrer ta réponse. Réessaie.")
      }
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDeclare(question: FlatQuestion, resultat: "REUSSI" | "PARTIEL" | "ECHEC") {
    if (submitting || question.reponse) return
    setSubmitting(true)
    try {
      const updated = await answerTentativeQuestion(tentative!.id, question.id, { resultat_declare: resultat })
      updateQuestion(updated)
    } catch {
      setError("Impossible d'enregistrer ta réponse. Réessaie.")
    } finally {
      setSubmitting(false)
    }
  }

  async function handleToggleFlag(question: FlatQuestion) {
    try {
      const result = await toggleQuestionMarquee(tentative!.id, question.id)
      setFlaggedIds(new Set(result.questions_marquees))
    } catch {
      setError("Impossible de marquer cette question. Réessaie.")
    }
  }

  async function handleStartExamMode() {
    setStartingExam(true)
    try {
      const updated = await startExamMode(tentative!.id)
      setTentative(updated)
      setQuestions(flattenQuestions(updated))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible d'activer le mode examen.")
    } finally {
      setStartingExam(false)
    }
  }

  async function handleDownloadSujet() {
    if (!tentative || downloadingSujet) return
    setDownloadingSujet(true)
    try {
      await downloadSujetPdf(tentative.epreuve)
    } catch {
      setError("Impossible d'ouvrir l'épreuve pour le moment. Réessaie.")
    } finally {
      setDownloadingSujet(false)
    }
  }

  async function handleFinish() {
    setSubmitting(true)
    try {
      await completeTentative(tentative!.id)
      await refetchAfterLock(false)
    } catch {
      setError("Impossible de terminer l'épreuve. Réessaie.")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl animate-fade-up px-4 py-8 sm:px-6">
      <Link
        to={`${catalogueHomePath(tentative.country.toLowerCase())}?origine=INEDITE#catalogue`}
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Quitter l'épreuve
      </Link>

      <div className="sticky top-0 z-10 -mx-4 mb-5 flex flex-wrap items-center gap-2 border-b border-border bg-background/95 px-4 py-3 backdrop-blur-sm sm:-mx-6 sm:px-6">
        <Badge variant="secondary">{tentative.cursus_display}</Badge>
        <Badge variant="outline">
          {answeredCount} / {questions.length} répondues
        </Badge>

        {tentative.sujet_pdf_disponible && (
          <Button
            size="sm"
            variant="outline"
            disabled={downloadingSujet}
            onClick={handleDownloadSujet}
            title="Ouvrir l'épreuve en PDF"
          >
            <FileDown className="size-3.5" />
            {downloadingSujet ? "Ouverture..." : "PDF"}
          </Button>
        )}

        {!tentative.exam_mode_started_at && !tentative.submitted_at && tentative.duree_minutes && (
          <div className="ml-auto flex items-center gap-2">
            {answeredCount > 0 && (
              <span className="text-xs text-muted-foreground">Disponible avant ta première réponse</span>
            )}
            <Button size="sm" variant="outline" disabled={startingExam || answeredCount > 0} onClick={handleStartExamMode}>
              <Timer className="size-3.5" />
              Mode examen ({tentative.duree_minutes} min)
            </Button>
          </div>
        )}

        {remainingSeconds !== null && (
          <Badge
            variant={remainingSeconds <= 300 ? "warning" : "outline"}
            className="ml-auto flex items-center gap-1 tabular-nums"
          >
            <Timer className="size-3" />
            {formatDuration(remainingSeconds)}
          </Badge>
        )}

        {tentative.correction_disponible && (
          <Button size="sm" variant="ghost" onClick={() => setShowCorrection((v) => !v)}>
            {showCorrection ? "Masquer la correction" : "Afficher la correction"}
          </Button>
        )}

        {!tentative.submitted_at ? (
          <Button size="sm" disabled={submitting} onClick={handleFinish}>
            Terminer l'épreuve
          </Button>
        ) : (
          <Button asChild size="sm">
            <Link to={`/inedit/tentative/${tentative.id}/resultat`}>Voir mon résultat</Link>
          </Button>
        )}
      </div>

      {error && <p className="mb-4 text-sm text-destructive">{error}</p>}

      {questions.map((question, index) => {
        const isNewExercice = index === 0 || question.numero_exercice !== questions[index - 1].numero_exercice
        const isFlagged = flaggedIds.has(question.id)
        return (
          <div key={question.id}>
            {isNewExercice && (
              <div className={cn("mb-3 flex items-center gap-1.5", index > 0 && "mt-8 border-t border-border pt-6")}>
                <Badge variant="outline">Exercice {question.numero_exercice}</Badge>
                {question.points && <Badge variant="outline">{question.points} pts</Badge>}
              </div>
            )}

            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0 flex-1">
                <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Question {question.numero}
                </span>
                <article className="prose prose-neutral max-w-none text-justify dark:prose-invert">
                  <EpreuveMarkdown markdown={question.enonce_markdown} />
                </article>
              </div>
              <button
                type="button"
                onClick={() => handleToggleFlag(question)}
                aria-pressed={isFlagged}
                aria-label="Marquer à revoir"
                title="Marquer cette question pour y revenir plus tard"
                className={cn(
                  "mt-1 shrink-0 rounded-md p-1.5 transition-colors",
                  isFlagged ? "text-gold" : "text-muted-foreground hover:text-foreground",
                )}
              >
                <Flag className={cn("size-4", isFlagged && "fill-current")} />
              </button>
            </div>

            {question.type_reponse === "QCM" ? (
              <div className="mt-3 flex flex-col gap-2">
                {question.choix.map((choix) => {
                  const isSelected = question.reponse?.reponse_choisie === choix.lettre
                  const isCorrectChoice = showCorrection && question.reponse_correcte === choix.lettre
                  const isWrongSelected = showCorrection && isSelected && !isCorrectChoice
                  return (
                    <button
                      key={choix.lettre}
                      type="button"
                      disabled={submitting || showCorrection}
                      onClick={() => handleAnswerQcm(question, choix.lettre)}
                      className={cn(
                        "flex items-center justify-between gap-2 rounded-md border px-3.5 py-2.5 text-left text-sm transition-colors disabled:cursor-default",
                        isCorrectChoice && "border-success bg-success/10",
                        isWrongSelected && "border-destructive bg-destructive/10",
                        !showCorrection && isSelected && "border-primary bg-primary/5",
                        !showCorrection && !isSelected && "border-border hover:bg-accent/40",
                        showCorrection && !isSelected && !isCorrectChoice && "border-border opacity-60",
                      )}
                    >
                      <span>
                        <span className="font-medium">{choix.lettre.toUpperCase()}.</span> <ChoixText texte={choix.texte} />
                      </span>
                      {isCorrectChoice && <Check className="size-4 shrink-0 text-success" />}
                      {isWrongSelected && <X className="size-4 shrink-0 text-destructive" />}
                    </button>
                  )
                })}
              </div>
            ) : (
              <div className="mt-3 flex flex-col gap-3">
                {showCorrection && question.corrige_markdown && (
                  <article className="prose prose-neutral max-w-none border-l-2 border-border pl-4 text-justify dark:prose-invert">
                    <EpreuveMarkdown markdown={question.corrige_markdown} />
                  </article>
                )}

                {showCorrection && question.corrige_markdown && !question.reponse && (
                  <div className="flex flex-col gap-2">
                    <p className="text-sm text-muted-foreground">As-tu réussi cette question ?</p>
                    <div className="flex gap-2">
                      {RESULTAT_OPTIONS.map((option) => (
                        <Button
                          key={option.value}
                          variant="outline"
                          size="sm"
                          disabled={submitting}
                          onClick={() => handleDeclare(question, option.value)}
                        >
                          {option.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {question.reponse?.resultat_declare && (
                  <Badge variant={question.reponse.est_correcte ? "success" : "outline"} className="w-fit">
                    {question.reponse.est_correcte
                      ? "Réussi"
                      : question.reponse.resultat_declare === "PARTIEL"
                        ? "Partiel"
                        : "Échec"}
                  </Badge>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
