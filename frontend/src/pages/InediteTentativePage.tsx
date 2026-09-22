import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
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
import { epreuvesListPath } from "@/lib/countryPath"

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

interface FlatQuestion extends TentativeInediteQuestion {
  numero_exercice: string
  points: string
  // Pile de repères de groupe de l'exercice parent (voir TentativeInediteExercice.
  // groupes) - un seul en-tête par exercice, affiché quand isNewExercice (voir plus
  // bas). Distinct de `groupe_local` (hérité de TentativeInediteQuestion via le spread
  // ci-dessous) : celui-ci peut changer PLUSIEURS fois au sein d'un même exercice, pour
  // scinder ses questions en sous-sections successives (ex. "Vérification des savoirs"
  // puis "Vérification des savoir-faire") - voir isNewGroupeLocal plus bas.
  groupes: string[]
  // Renommé (et non `enonce_intro_markdown`) une fois aplati sur la question : à ce
  // niveau, plus rien ne rappelle qu'il appartient à l'exercice, et le confondre avec
  // l'énoncé de la question elle-même le ferait afficher autant de fois qu'il y a de
  // questions - voir le rendu conditionné par isNewExercice plus bas.
  exercice_intro_markdown: string
}

function flattenQuestions(tentative: TentativeInedite): FlatQuestion[] {
  return tentative.exercices.flatMap((exercice) =>
    exercice.questions.map((question) => ({
      ...question,
      numero_exercice: exercice.numero_exercice,
      points: exercice.points,
      groupes: exercice.groupes,
      exercice_intro_markdown: exercice.enonce_intro_markdown,
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
          to={tentative ? `${epreuvesListPath(tentative.country.toLowerCase())}?origine=INEDITE` : "/"}
          className="mt-3 inline-block text-sm text-primary hover:underline"
        >
          Retour au catalogue
        </Link>
      </div>
    )
  }

  if (!tentative || questions.length === 0) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10">
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
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-8 sm:px-6">
      <Link
        to={`${epreuvesListPath(tentative.country.toLowerCase())}?origine=INEDITE`}
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Quitter l'épreuve
      </Link>

      {/* Barre d'actions "flottante" : carte sticky arrondie plutôt qu'un bandeau
          plein-bleed - deux rangées (identité/utilitaires en haut, progression en bas)
          au lieu d'un unique flex-wrap où badges et boutons se mélangeaient sans
          hiérarchie visuelle. */}
      <div className="sticky top-[72px] z-10 mb-6 rounded-xl border border-border bg-background/95 px-4 py-3 shadow-sm backdrop-blur-sm sm:px-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary">{tentative.cursus_display}</Badge>
            {tentative.sujet_pdf_disponible && (
              <Button
                size="sm"
                variant="ghost"
                disabled={downloadingSujet}
                onClick={handleDownloadSujet}
                title="Ouvrir l'épreuve en PDF"
              >
                <FileDown className="size-3.5" />
                {downloadingSujet ? "Ouverture..." : "PDF"}
              </Button>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {!tentative.exam_mode_started_at && !tentative.submitted_at && tentative.duree_minutes && (
              <Button
                size="sm"
                variant="outline"
                disabled={startingExam || answeredCount > 0}
                onClick={handleStartExamMode}
                title={answeredCount > 0 ? "Disponible avant ta première réponse" : undefined}
              >
                <Timer className="size-3.5" />
                Mode examen ({tentative.duree_minutes} min)
              </Button>
            )}

            {remainingSeconds !== null && (
              <Badge
                variant={remainingSeconds <= 300 ? "warning" : "outline"}
                className="flex items-center gap-1 tabular-nums"
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
        </div>

        <div className="mt-3 flex items-center gap-2.5">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${questions.length ? (answeredCount / questions.length) * 100 : 0}%` }}
            />
          </div>
          <span className="shrink-0 text-xs font-medium tabular-nums text-muted-foreground">
            {answeredCount} / {questions.length} répondues
          </span>
        </div>
      </div>

      {error && <p className="mb-4 text-sm text-destructive">{error}</p>}

      {questions.map((question, index) => {
        const isNewExercice = index === 0 || question.numero_exercice !== questions[index - 1].numero_exercice
        // Sous-partie locale (voir QuestionInedite.groupe_local côté backend) - peut
        // changer PLUSIEURS fois au sein d'un même exercice, contrairement à `groupes`
        // ci-dessous (un seul en-tête par exercice). Comparée à la question précédente,
        // pas seulement à isNewExercice : sans ça un exercice scindé en deux sous-parties
        // ("Vérification des savoirs" puis "des savoir-faire") afficherait les deux
        // repères d'un coup en tête, avant sa toute première question.
        const isNewGroupeLocal =
          !!question.groupe_local && (isNewExercice || question.groupe_local !== questions[index - 1].groupe_local)
        const isFlagged = flaggedIds.has(question.id)
        return (
          <div key={question.id}>
            {isNewExercice && (
              <>
                {/* En-tête de groupe (Partie/section/matière) - affiché uniquement quand
                    l'épreuve est structurée en groupes (voir ExerciceInedite.groupes,
                    [] pour la grande majorité des épreuves). Purement informatif : pas de
                    lien ni d'ancre, contrairement à EpreuveSommaire côté épreuves
                    classiques - on ne laisse pas l'élève sauter en avant pendant un examen
                    chronométré, seulement situer où il en est dans l'énoncé qu'il lit. */}
                {question.groupes.length > 0 && (
                  <p className={cn("text-xs font-semibold uppercase tracking-wide text-muted-foreground", index > 0 && "mt-8")}>
                    {question.groupes.join(" · ")}
                  </p>
                )}
                <div className={cn("mb-3 flex items-center gap-1.5", index > 0 && "mt-8 border-t border-border pt-6", index > 0 && question.groupes.length > 0 && "mt-3 border-t-0 pt-0")}>
                  <Badge variant="outline">Exercice {question.numero_exercice}</Badge>
                  {question.points && <Badge variant="outline">{question.points} pts</Badge>}
                </div>
                {/* Support commun aux questions de l'exercice - rendu une seule fois,
                    ici et pas dans chaque question (voir ExerciceInedite.enonce_intro_markdown).
                    Encadré : l'élève doit pouvoir le distinguer d'un énoncé de question au
                    premier coup d'œil, et y revenir en remontant pendant qu'il répond. */}
                {question.exercice_intro_markdown && (
                  <article className="mb-5 rounded-md border border-border bg-muted/40 px-4 py-3 prose prose-neutral max-w-none text-justify prose-sm dark:prose-invert">
                    <EpreuveMarkdown markdown={question.exercice_intro_markdown} />
                  </article>
                )}
              </>
            )}

            {isNewGroupeLocal && (
              <p
                className={cn(
                  "mb-3 text-sm font-semibold text-foreground",
                  isNewExercice ? "mt-0" : "mt-8 border-t border-dashed border-border pt-6",
                )}
              >
                {question.groupe_local}
              </p>
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
