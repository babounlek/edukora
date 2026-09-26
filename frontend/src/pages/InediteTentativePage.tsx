import { useCallback, useEffect, useRef, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import { toast } from "sonner"
import { ArrowLeft, Check, Eye, EyeOff, FileDown, Flag, Info, Timer, X } from "lucide-react"

import {
  answerTentativeQuestion,
  completeTentative,
  downloadSujetPdf,
  getTentativeInedite,
  noterTentativeQuestion,
  startExamMode,
  toggleQuestionMarquee,
} from "@/api/endpoints"
import type { NoterTentativeQuestionParams } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { NotationResume, TentativeInedite, TentativeInediteQuestion } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { BandeauNotation } from "@/components/inedit/BandeauNotation"
import { BoutonTraitee } from "@/components/inedit/BoutonTraitee"
import { DialogueModeExamen, DialogueTerminer } from "@/components/inedit/DialoguesEpreuve"
import { GrilleNotation } from "@/components/inedit/GrilleNotation"
import { formatDuration } from "@/lib/duration"
import { estANoter, formatNote, formatPoints } from "@/lib/notation"
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
  points_exercice: string
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
      points_exercice: exercice.points,
      groupes: exercice.groupes,
      exercice_intro_markdown: exercice.enonce_intro_markdown,
    })),
  )
}

function repere(question: FlatQuestion) {
  return { id: question.id, label: `Ex. ${question.numero_exercice} · Q${question.numero}` }
}

function scrollToQuestion(questionId: number) {
  const cible = document.getElementById(`question-${questionId}`)
  if (!cible) return
  const reduit = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
  cible.scrollIntoView({ behavior: reduit ? "auto" : "smooth", block: "start" })
}

const REPONSE_VIDE = { reponse_choisie: "", resultat_declare: "" }

export function InediteTentativePage() {
  useSeo({ title: "Épreuve inédite" })

  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()

  const [tentative, setTentative] = useState<TentativeInedite | null>(null)
  const [questions, setQuestions] = useState<FlatQuestion[]>([])
  const [notation, setNotation] = useState<NotationResume | null>(null)
  const [loadError, setLoadError] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [remainingSeconds, setRemainingSeconds] = useState<number | null>(null)
  const [showCorrection, setShowCorrection] = useState(false)
  const [flaggedIds, setFlaggedIds] = useState<Set<number>>(new Set())
  const [startingExam, setStartingExam] = useState(false)
  const [downloadingSujet, setDownloadingSujet] = useState(false)
  const [finishing, setFinishing] = useState(false)
  const [terminerOuvert, setTerminerOuvert] = useState(false)
  const [examenOuvert, setExamenOuvert] = useState(false)
  const [rendueAutomatiquement, setRendueAutomatiquement] = useState(false)

  // Dernière requête d'écriture émise par question : deux clics rapprochés sur « + »
  // produisent deux requêtes, et une réponse tardive ne doit jamais écraser la plus récente.
  const sequences = useRef(new Map<number, number>())
  const defilementInitial = useRef(false)
  // Un seul refetch de verrouillage à la fois : si l'horloge du serveur retarde sur celle du
  // navigateur, la tentative n'est pas encore verrouillée à 00:00 - sans ce garde, chaque
  // réponse relancerait l'effet ci-dessous et martèlerait l'API.
  const verrouillageDemande = useRef(false)

  const charger = useCallback((data: TentativeInedite) => {
    setTentative(data)
    setQuestions(flattenQuestions(data))
    setNotation(data.notation)
  }, [])

  useEffect(() => {
    if (!id) return
    getTentativeInedite(Number(id))
      .then((data) => {
        charger(data)
        setFlaggedIds(new Set(data.questions_marquees))
        setShowCorrection(data.submitted_at !== null)
      })
      .catch((err) => {
        setLoadError(err instanceof ApiError ? err.message : "Impossible de charger cette épreuve.")
      })
  }, [id, charger])

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
    if (remainingSeconds !== 0 || !tentative || tentative.submitted_at || verrouillageDemande.current) return
    verrouillageDemande.current = true
    getTentativeInedite(tentative.id)
      .then((data) => {
        charger(data)
        if (data.submitted_at) {
          setShowCorrection(true)
          setRendueAutomatiquement(true)
          window.scrollTo({ top: 0 })
        }
      })
      .finally(() => {
        window.setTimeout(() => {
          verrouillageDemande.current = false
        }, 3000)
      })
  }, [remainingSeconds, tentative, charger])

  // Arrivée depuis « Terminer ma notation » (page de résultat) : on amène l'élève droit
  // sur la première question à noter, pas en haut d'une longue épreuve.
  useEffect(() => {
    if (defilementInitial.current || searchParams.get("noter") !== "1" || !tentative?.submitted_at) return
    const premiere = questions.find(estANoter)
    defilementInitial.current = true
    if (premiere) window.requestAnimationFrame(() => scrollToQuestion(premiere.id))
  }, [searchParams, tentative?.submitted_at, questions])

  if (loadError) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{loadError}</p>
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

  const rendue = tentative.submitted_at !== null
  const enExamen = tentative.exam_mode_started_at !== null && !rendue
  const traiteesCount = questions.filter((q) => q.traitee).length
  const nonTraitees = questions.filter((q) => !q.traitee).map(repere)
  const aRevoir = questions.filter((q) => flaggedIds.has(q.id)).map(repere)
  const pourcentageTraitees = questions.length ? (traiteesCount / questions.length) * 100 : 0

  /** Fusionne une question renvoyée par le serveur dans l'état, `reponse` compris : une
   * question dé-traitée n'a plus de `reponse` dans le payload, et un simple spread
   * garderait l'ancienne. */
  function appliquer(mise_a_jour: TentativeInediteQuestion) {
    const { notation: nouvelle, ...question } = mise_a_jour
    setQuestions((prev) =>
      prev.map((q) => (q.id === question.id ? { ...q, ...question, reponse: question.reponse } : q)),
    )
    if (nouvelle !== undefined) setNotation(nouvelle)
  }

  function remplacer(questionId: number, fabrique: (q: FlatQuestion) => FlatQuestion) {
    setQuestions((prev) => prev.map((q) => (q.id === questionId ? fabrique(q) : q)))
  }

  async function refetchAfterLock(autoLocked: boolean) {
    const data = await getTentativeInedite(tentative!.id)
    charger(data)
    setShowCorrection(true)
    setRendueAutomatiquement(autoLocked)
    window.scrollTo({ top: 0, behavior: "smooth" })
    trackEvent("inedit_tentative_completed", { epreuve_id: data.epreuve, auto_locked: autoLocked })
  }

  /** Écriture sur une question ouverte avec mise à jour optimiste : le geste de l'élève
   * (cocher, ajuster) répond instantanément, même sur une connexion lente ; en cas
   * d'échec on rétablit l'état d'avant et on le lui dit, sans casser la page. */
  async function ecrire(
    question: FlatQuestion,
    corps: NoterTentativeQuestionParams,
    optimiste: (q: FlatQuestion) => FlatQuestion,
    messageErreur: string,
  ) {
    const numero = (sequences.current.get(question.id) ?? 0) + 1
    sequences.current.set(question.id, numero)
    remplacer(question.id, optimiste)
    try {
      const mise_a_jour = await noterTentativeQuestion(tentative!.id, question.id, corps)
      if (sequences.current.get(question.id) === numero) appliquer(mise_a_jour)
    } catch (err) {
      if (sequences.current.get(question.id) !== numero) return
      remplacer(question.id, () => question)
      if (err instanceof ApiError && err.status === 409) {
        // Verrouillée entre-temps (chrono écoulé) : recharger l'état réel plutôt que d'insister.
        await refetchAfterLock(true)
      } else {
        toast.error(messageErreur)
      }
    }
  }

  function handleToggleTraitee(question: FlatQuestion) {
    const traitee = !question.traitee
    ecrire(
      question,
      { traitee },
      (q) => ({ ...q, traitee, reponse: traitee ? (q.reponse ?? REPONSE_VIDE) : undefined }),
      "Impossible d'enregistrer cette question. Réessaie.",
    )
  }

  function handleCriteres(question: FlatQuestion, indices: number[]) {
    const total = indices.reduce((somme, i) => somme + (question.criteres_notation?.[i]?.points ?? 0), 0)
    ecrire(
      question,
      { criteres_valides: indices },
      (q) => ({
        ...q,
        traitee: true,
        reponse: { ...(q.reponse ?? REPONSE_VIDE), notee: true, criteres_valides: indices, points_obtenus: total },
      }),
      "Impossible d'enregistrer ta note. Réessaie.",
    )
  }

  function handlePoints(question: FlatQuestion, points: number) {
    ecrire(
      question,
      { points_obtenus: points },
      (q) => ({ ...q, traitee: true, reponse: { ...(q.reponse ?? REPONSE_VIDE), notee: true, points_obtenus: points } }),
      "Impossible d'enregistrer ta note. Réessaie.",
    )
  }

  async function handleAnswerQcm(question: FlatQuestion, lettre: string) {
    if (submitting || showCorrection) return
    setSubmitting(true)
    try {
      const updated = await answerTentativeQuestion(tentative!.id, question.id, { reponse_choisie: lettre })
      appliquer(updated)
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        await refetchAfterLock(true)
      } else {
        toast.error("Impossible d'enregistrer ta réponse. Réessaie.")
      }
    } finally {
      setSubmitting(false)
    }
  }

  async function handleToggleFlag(question: FlatQuestion) {
    try {
      const result = await toggleQuestionMarquee(tentative!.id, question.id)
      setFlaggedIds(new Set(result.questions_marquees))
    } catch {
      toast.error("Impossible de marquer cette question. Réessaie.")
    }
  }

  async function handleStartExamMode() {
    setStartingExam(true)
    try {
      const updated = await startExamMode(tentative!.id)
      charger(updated)
      setExamenOuvert(false)
    } catch (err) {
      setExamenOuvert(false)
      toast.error(err instanceof ApiError ? err.message : "Impossible d'activer le mode examen.")
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
      toast.error("Impossible d'ouvrir l'épreuve pour le moment. Réessaie.")
    } finally {
      setDownloadingSujet(false)
    }
  }

  async function handleFinish() {
    setFinishing(true)
    try {
      await completeTentative(tentative!.id)
      setTerminerOuvert(false)
      await refetchAfterLock(false)
    } catch {
      toast.error("Impossible de terminer l'épreuve. Réessaie.")
    } finally {
      setFinishing(false)
    }
  }

  // Sauter la confirmation quand il n'y a rien à perdre : tout est traité, pas de chrono.
  function handleTerminerClick() {
    if (enExamen || nonTraitees.length > 0) setTerminerOuvert(true)
    else handleFinish()
  }

  function allerALaProchaineANoter() {
    const prochaine = questions.find(estANoter)
    if (prochaine) scrollToQuestion(prochaine.id)
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
          hiérarchie visuelle. Sur mobile les libellés secondaires disparaissent (icône
          seule) pour que la rangée du haut tienne sur une ligne à 375 px. */}
      <div className="sticky top-[72px] z-10 mb-6 rounded-xl border border-border bg-background/95 px-3 py-3 shadow-sm backdrop-blur-sm sm:px-5">
        <div className="flex items-center justify-between gap-2">
          <div className="flex min-w-0 items-center gap-1 sm:gap-2">
            <Badge variant="secondary" className="hidden max-w-[16rem] truncate md:inline-flex">
              {tentative.cursus_display}
            </Badge>
            {tentative.sujet_pdf_disponible && (
              <Button
                size="sm"
                variant="ghost"
                disabled={downloadingSujet}
                onClick={handleDownloadSujet}
                title="Ouvrir l'épreuve en PDF"
                aria-label="Ouvrir l'épreuve en PDF"
              >
                <FileDown className="size-3.5" />
                <span className="hidden sm:inline">{downloadingSujet ? "Ouverture..." : "PDF"}</span>
              </Button>
            )}
            {tentative.correction_disponible && (
              <Button
                size="sm"
                variant="ghost"
                aria-pressed={showCorrection}
                onClick={() => setShowCorrection((v) => !v)}
                title={showCorrection ? "Masquer la correction" : "Afficher la correction"}
              >
                {showCorrection ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                <span className="hidden sm:inline">{showCorrection ? "Masquer la correction" : "Afficher la correction"}</span>
                <span className="sm:hidden">Correction</span>
              </Button>
            )}
          </div>

          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            {!tentative.exam_mode_started_at && !rendue && tentative.duree_minutes && (
              <Button
                size="sm"
                variant="outline"
                disabled={traiteesCount > 0}
                onClick={() => setExamenOuvert(true)}
                title={traiteesCount > 0 ? "Disponible avant ta première réponse" : "Passer l'épreuve en conditions réelles"}
              >
                <Timer className="size-3.5" />
                <span className="hidden sm:inline">Mode examen ({tentative.duree_minutes} min)</span>
                <span className="sm:hidden">Examen</span>
              </Button>
            )}

            {remainingSeconds !== null && (
              <Badge
                role="timer"
                aria-label="Temps restant"
                variant={remainingSeconds <= 300 ? "warning" : "outline"}
                className={cn(
                  "flex items-center gap-1 tabular-nums",
                  remainingSeconds <= 60 && "motion-safe:animate-pulse",
                )}
              >
                <Timer className="size-3" />
                {formatDuration(remainingSeconds)}
              </Badge>
            )}

            {!rendue ? (
              <Button size="sm" disabled={finishing} onClick={handleTerminerClick}>
                Terminer<span className="hidden sm:inline">&nbsp;l'épreuve</span>
              </Button>
            ) : (
              <Button asChild size="sm">
                <Link to={`/inedit/tentative/${tentative.id}/resultat`}>Voir mon résultat</Link>
              </Button>
            )}
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2.5">
          <div
            role="progressbar"
            aria-label="Questions traitées"
            aria-valuemin={0}
            aria-valuemax={questions.length}
            aria-valuenow={traiteesCount}
            className="h-1.5 min-w-12 flex-1 overflow-hidden rounded-full bg-secondary"
          >
            <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${pourcentageTraitees}%` }} />
          </div>
          <span className="shrink-0 text-xs font-medium tabular-nums text-muted-foreground">
            {traiteesCount} / {questions.length} traitées
          </span>
          {notation && (
            <span
              aria-live="polite"
              title={notation.definitive ? "Note définitive" : "Note provisoire : elle évolue à mesure que tu notes tes questions"}
              className="shrink-0 rounded-md bg-secondary px-2 py-0.5 text-xs font-semibold tabular-nums"
            >
              {notation.definitive ? "Note" : "Provisoire"} {formatNote(notation.note, notation.bareme)}
            </span>
          )}
        </div>
      </div>

      {rendue && notation && (
        <BandeauNotation
          notation={notation}
          tentativeId={tentative.id}
          rendueAutomatiquement={rendueAutomatiquement}
          onProchaine={allerALaProchaineANoter}
        />
      )}

      {tentative.bareme_estime && (
        <p className="mb-6 flex items-start gap-2 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" />
          Barème estimé : les points de chaque exercice sont répartis à parts égales entre ses questions
          (total : {formatPoints(tentative.bareme)} points).
        </p>
      )}

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
        const corrigeVisible = showCorrection && !!question.corrige_markdown
        return (
          <div
            key={question.id}
            id={`question-${question.id}`}
            className={cn("scroll-mt-44", !isNewExercice && !isNewGroupeLocal && "mt-8")}
          >
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
                  {question.points_exercice && <Badge variant="outline">{question.points_exercice} pts</Badge>}
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
                <span className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Question {question.numero}
                  <span
                    className="rounded bg-secondary px-1.5 py-0.5 font-medium normal-case tracking-normal tabular-nums"
                    title={question.bareme_estime ? "Barème estimé" : undefined}
                  >
                    {question.bareme_estime ? "≈ " : ""}
                    {formatPoints(question.points)} pt{question.points >= 2 ? "s" : ""}
                  </span>
                </span>
                <article className="prose prose-neutral max-w-none dark:prose-invert sm:text-justify">
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
                  "mt-1 shrink-0 rounded-md p-2 transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
                  isFlagged ? "text-gold-text" : "text-muted-foreground hover:text-foreground",
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
                        "flex min-h-11 items-center justify-between gap-2 rounded-md border px-3.5 py-2.5 text-left text-sm transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none disabled:cursor-default",
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
                {/* Question ouverte : l'élève compose sur brouillon ou papier, puis le
                    déclare ici. Le corrigé (une fois disponible) précède la grille de
                    notation, pour comparer d'abord, se noter ensuite. */}
                <div className="flex flex-wrap items-center gap-3">
                  <BoutonTraitee
                    traitee={question.traitee}
                    rendue={rendue}
                    onToggle={() => handleToggleTraitee(question)}
                  />
                  {corrigeVisible && !question.traitee && (
                    <span className="text-sm text-muted-foreground">Non traitée : cette question vaut 0 point.</span>
                  )}
                </div>

                {corrigeVisible && (
                  <article className="prose prose-neutral max-w-none border-l-2 border-border pl-4 dark:prose-invert sm:text-justify">
                    <EpreuveMarkdown markdown={question.corrige_markdown ?? ""} />
                  </article>
                )}

                {corrigeVisible && question.traitee && (
                  <GrilleNotation
                    question={question}
                    onCriteres={(indices) => handleCriteres(question, indices)}
                    onPoints={(points) => handlePoints(question, points)}
                  />
                )}
              </div>
            )}
          </div>
        )
      })}

      <DialogueTerminer
        open={terminerOuvert}
        onOpenChange={setTerminerOuvert}
        enExamen={enExamen}
        total={questions.length}
        traitees={traiteesCount}
        nonTraitees={nonTraitees}
        aRevoir={aRevoir}
        enCours={finishing}
        onAller={(questionId) => window.requestAnimationFrame(() => scrollToQuestion(questionId))}
        onConfirmer={handleFinish}
      />
      {tentative.duree_minutes && (
        <DialogueModeExamen
          open={examenOuvert}
          onOpenChange={setExamenOuvert}
          dureeMinutes={tentative.duree_minutes}
          enCours={startingExam}
          onConfirmer={handleStartExamMode}
        />
      )}
    </div>
  )
}
