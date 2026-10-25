import { useCallback, useEffect, useRef, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import { ArrowLeft, ArrowRight, BookOpenText, Check, FileText, Flame, Lightbulb, Loader2, Sparkles, Swords, Target, X, Zap } from "lucide-react"

import {
  answerQuizEssai, answerQuizQuestion, completeQuizSession, getQuizSession, revealQuizCorrige, revealQuizEssaiCorrige,
} from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizCorrige, QuizSession } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { BoutonPartager } from "@/components/BoutonPartager"
import { BoutonSon } from "@/components/BoutonSon"
import { lireDefiMemorise } from "@/lib/defiEssai"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { ObjectifXp } from "@/components/ObjectifXp"
import { QuizFichePdfButtons } from "@/components/QuizFichePdfButtons"
import { useCountry } from "@/context/CountryContext"
import { themeExercicesPath } from "@/lib/countryPath"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { jouerRetour } from "@/lib/retours"
import { subjectIcon } from "@/lib/subjectIcon"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { libellePoints } from "@/lib/notation"
import { nomAccessibleDuChoix } from "@/lib/markdown"
import { avecQuestionCorrigee, cheminEssai, lireEssai, memoriserEssai, texteDePartageEssai } from "@/lib/quizEssai"
import { capitaliserTheme, cn } from "@/lib/utils"
import { cheminDansLangue, langueCourante, t, tn, useI18n, type CleI18n } from "@/lib/i18n"
import { traduireLibelleSerie } from "@/lib/cursus"

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

const RESULTAT_OPTIONS: { value: "REUSSI" | "PARTIEL" | "ECHEC"; label: CleI18n }[] = [
  { value: "REUSSI", label: "qs.reussi" },
  { value: "PARTIEL", label: "qs.partiel" },
  { value: "ECHEC", label: "qs.echec" },
]

const MESSAGES_BONNE: CleI18n[] = ["qs.bonne1", "qs.bonne2", "qs.bonne3", "qs.bonne4", "qs.bonne5"]
const MESSAGES_MAUVAISE: CleI18n[] = ["qs.mauvaise1", "qs.mauvaise2", "qs.mauvaise3"]

function pick(messages: CleI18n[], seed: number) {
  return t(messages[seed % messages.length])
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

/**
 * Le lecteur de quiz. `essai` : l'essai gratuit d'un visiteur sans compte (route /quiz/essai) -
 * même écran, mais le quiz vient du navigateur (voir lib/quizEssai.ts) et chaque réponse est
 * corrigée par les routes publiques /quiz/essais/*, sans XP, série ni PDF (rien n'est enregistré).
 */
export function QuizSessionPage({ essai = false }: { essai?: boolean } = {}) {
  useI18n()
  useSeo({ title: essai ? t("qs.seo_essai") : t("qs.seo") })

  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { country } = useCountry()

  const [session, setSession] = useState<QuizSession | null>(null)
  // Le score à battre d'un défi reçu par lien (essai gratuit seulement, voir lib/defiEssai).
  const [defi] = useState(() => (essai ? lireDefiMemorise() : null))
  // Deux erreurs distinctes : un échec de CHARGEMENT remplace la page, mais un échec d'ACTION
  // (réponse, correction, fin du quiz) ne doit jamais effacer un quiz en cours - l'élève
  // garde ses réponses sous les yeux et peut simplement réessayer.
  const [error, setError] = useState("")
  const [actionError, setActionError] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)
  const [revealed, setRevealed] = useState<Record<number, QuizCorrige>>({})
  const [submitting, setSubmitting] = useState(false)
  // Le choix tapé, tant que le serveur n'a pas répondu : sur une connexion lente, la case doit
  // réagir tout de suite (sans connaître encore le verdict, que seul le serveur donne).
  const [choixEnCours, setChoixEnCours] = useState<string | null>(null)
  // Toujours la dernière version des gestionnaires, pour un écouteur clavier posé une seule fois.
  const keyHandlerRef = useRef<(e: KeyboardEvent) => void>(() => {})
  // Posé quand une réponse vient d'être enregistrée : le retour qui apparaît alors est amené à l'écran (voir
  // amenerLeRetour). Jamais pour une question déjà répondue qu'on rouvre : la page ne doit pas sauter à l'ouverture.
  const retourARegarderRef = useRef(false)
  // Callback de ref (identité stable) : appelé une seule fois, au moment où le message de retour apparaît. Sur mobile, une
  // longue correction repliée sous la barre fixe « Question suivante » le laissait hors de l'écran, sans autre signe que
  // des boutons qui disparaissaient. `nearest` : ne bouge pas s'il est déjà visible ; la marge basse laisse la place à la barre.
  const amenerLeRetour = useCallback((el: HTMLElement | null) => {
    if (!el || !retourARegarderRef.current) return
    retourARegarderRef.current = false
    const reduit = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true
    el.scrollIntoView({ block: "nearest", behavior: reduit ? "auto" : "smooth" })
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => keyHandlerRef.current(e)
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [])

  useEffect(() => {
    if (essai) {
      const enCours = lireEssai()
      if (!enCours) {
        navigate("/quiz", { replace: true })
        return
      }
      setSession(enCours)
      const premiere = enCours.questions.findIndex((q) => !q.reponse)
      setCurrentIndex(premiere === -1 ? Math.max(0, enCours.questions.length - 1) : premiere)
      return
    }
    if (!id) return
    getQuizSession(Number(id))
      .then((data) => {
        if (data.completed_at) {
          navigate(`/quiz/session/${data.id}/resultat`, { replace: true })
          return
        }
        setSession(data)
        const firstUnanswered = data.questions.findIndex((q) => !q.reponse)
        // Tout répondu mais pas rendu (reprise après coup) : on arrive sur la dernière question,
        // d'où « Voir mon résultat » est à portée, plutôt qu'au début d'un quiz fini.
        setCurrentIndex(firstUnanswered === -1 ? Math.max(0, data.questions.length - 1) : firstUnanswered)
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : t("qs.charger_erreur"))
      })
  }, [id, navigate, essai])

  if (error) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link to="/quiz" className="mt-3 inline-block text-sm text-primary hover:underline">
          {t("qs.retour")}
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
    retourARegarderRef.current = true
    // Essai : la réponse corrigée est réécrite dans le navigateur, seule mémoire de ce quiz.
    if (essai) memoriserEssai(avecQuestionCorrigee(session!, updated))
    setSession((prev) => {
      if (!prev) return prev
      const questions = prev.questions.map((q) => (q.id === updated.id ? updated : q))
      return { ...prev, questions, xp_jour: updated.xp_jour ?? prev.xp_jour }
    })
    // Le retour sensoriel part avec la réponse : un son et une vibration courts, une fête à
    // part quand c'est cette réponse qui a fait franchir l'objectif du jour. Une réponse
    // partielle qui a rapporté des points sonne "juste" : ce n'est pas une erreur.
    jouerRetour(
      updated.objectif_atteint_maintenant
        ? "objectif"
        : updated.reponse?.est_correcte || (updated.reponse?.xp_gagne ?? 0) > 0
          ? "juste"
          : "faux",
    )
  }

  async function handleAnswerQcm(lettre: string) {
    if (submitting || question.reponse) return
    setActionError("")
    setSubmitting(true)
    setChoixEnCours(lettre)
    try {
      const params = { reponse_choisie: lettre }
      const updated = essai
        ? await answerQuizEssai(session!.cursus, question.id, params)
        : await answerQuizQuestion(session!.id, question.id, params)
      updateQuestion(updated)
    } catch {
      setActionError(t("qs.reponse_erreur"))
    } finally {
      setSubmitting(false)
      setChoixEnCours(null)
    }
  }

  async function handleReveal() {
    if (submitting) return
    setActionError("")
    setSubmitting(true)
    try {
      const corrige = essai
        ? await revealQuizEssaiCorrige(session!.cursus, question.id)
        : await revealQuizCorrige(session!.id, question.id)
      setRevealed((prev) => ({ ...prev, [question.id]: corrige }))
    } catch {
      setActionError(t("qs.correction_erreur"))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDeclare(resultat: "REUSSI" | "PARTIEL" | "ECHEC") {
    if (submitting || question.reponse) return
    setActionError("")
    setSubmitting(true)
    try {
      const params = { resultat_declare: resultat }
      const updated = essai
        ? await answerQuizEssai(session!.cursus, question.id, params)
        : await answerQuizQuestion(session!.id, question.id, params)
      updateQuestion(updated)
    } catch {
      setActionError(t("qs.reponse_erreur"))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleNext() {
    setActionError("")
    if (!isLast) {
      setCurrentIndex((i) => i + 1)
      // Après avoir lu une longue correction, la question suivante s'afficherait à mi-page.
      window.scrollTo({ top: 0 })
      return
    }
    if (essai) {
      // Rien à clore côté serveur : le score se calcule depuis les réponses gardées dans le navigateur.
      trackEvent("quiz_completed", { cursus_id: session!.cursus, mode: session!.mode, source: "essai_anonyme" })
      navigate("/quiz/essai/resultat")
      return
    }
    setSubmitting(true)
    try {
      await completeQuizSession(session!.id)
      trackEvent("quiz_completed", { cursus_id: session!.cursus, mode: session!.mode })
      navigate(`/quiz/session/${session!.id}/resultat`)
    } catch {
      setActionError(t("qs.terminer_erreur"))
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
          to={session.subject && !essai ? `/parcours/${session.subject}?cursus=${session.cursus}` : "/quiz"}
          onClick={() => {
            // Quitter avant la dernière réponse : le contre-indicateur de la boucle de séance.
            if (answeredCount < total) trackEvent("quiz_abandonne", { cursus_id: session.cursus, mode: session.mode, repondues: answeredCount, total, ...(essai && { source: "essai_anonyme" }) })
          }}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-primary"
        >
          <ArrowLeft className="size-4" />
          {t("qs.quitter")}
        </Link>
        <div className="flex items-center gap-2">
          <BoutonSon />
          {essai ? (
            // Le quiz gratuit se partage : le lien relance CE quiz chez l'ami, sans compte ni liste à parcourir.
            cheminEssai(session) && (
              <BoutonPartager chemin={cheminEssai(session)!} texte={texteDePartageEssai(session)} type="quiz" libelle={t("qs.partager")} />
            )
          ) : (
            <QuizFichePdfButtons sessionId={session.id} />
          )}
        </div>
      </div>

      {defi && (
        <p className="mb-4 flex items-center gap-2 rounded-xl bg-gold/15 px-3 py-2 text-sm font-medium">
          <Swords className="size-4 shrink-0 text-gold-text" aria-hidden="true" />
          {t("defi.en_cours", { a: defi.reussies, b: defi.total })}
        </p>
      )}

      {/* Progression : un segment par question, coloré selon le résultat - on voit d'un
          coup d'œil où l'on en est et comment ça se passe. Un segment déjà répondu se
          clique pour relire sa correction. */}
      <div className="mb-2 flex gap-1" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={answeredCount}>
        {session.questions.map((q, i) => (
          <button
            key={q.id}
            type="button"
            disabled={!accessible(i)}
            onClick={() => {
              setCurrentIndex(i)
              window.scrollTo({ top: 0 })
            }}
            aria-label={t("qs.question_n", { n: i + 1 })}
            title={accessible(i) ? t("qs.question_n", { n: i + 1 }) : undefined}
            className={cn(
              "relative h-2.5 flex-1 rounded-full transition-all duration-500 after:absolute after:-inset-y-3 after:inset-x-0 after:content-[''] enabled:cursor-pointer enabled:hover:scale-y-150 disabled:cursor-default",
              segmentClass(q, i === currentIndex),
              i === currentIndex && "ring-2 ring-primary/30 ring-offset-1 ring-offset-background",
            )}
          />
        ))}
      </div>
      <div className="mb-5 flex items-center justify-between text-sm">
        <p className="font-medium text-muted-foreground">
          {t("qs.question_sur", { n: currentIndex + 1, total })}
        </p>
        <div className="flex items-center gap-3">
          {session.xp_jour && <ObjectifXp etat={session.xp_jour} compact />}
          {streak >= 2 && (
            <span className="inline-flex items-center gap-1 rounded-full bg-gold/15 px-2.5 py-0.5 font-semibold">
              <Flame className="animate-quiz-flame size-4 text-warning" />
              {t("qs.daffilee", { n: streak })}
            </span>
          )}
          <span className="font-semibold tabular-nums text-foreground">
            {score} <span className="font-normal text-muted-foreground">/ {answeredCount} {tn("qs.justes", score)}</span>
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
          <Badge variant="secondary">{traduireLibelleSerie(session.cursus_display)}</Badge>
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
            href={cheminDansLangue(`/epreuves/${question.lesson_id}`, langueCourante())}
            target="_blank"
            rel="noopener noreferrer"
            className="mb-4 flex w-fit items-center gap-1.5 rounded-md border border-dashed border-border px-3 py-1.5 text-sm font-medium text-primary hover:underline"
          >
            <BookOpenText className="size-3.5" />
            {t("qs.voir_epreuve")}
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
              const enCours = choixEnCours === choix.lettre
              return (
                <button
                  key={choix.lettre}
                  type="button"
                  aria-label={nomAccessibleDuChoix(choix.lettre, choix.texte)}
                  aria-busy={enCours || undefined}
                  disabled={submitting || answered}
                  onClick={() => handleAnswerQcm(choix.lettre)}
                  className={cn(
                    "group flex items-center gap-3 rounded-xl border-2 px-3.5 py-3 text-left text-[0.95rem] transition-all duration-200 disabled:cursor-default",
                    !answered &&
                      "border-border hover:-translate-y-0.5 hover:border-primary/60 hover:bg-accent/40 hover:shadow-sm active:translate-y-0",
                    isCorrectChoice && "animate-quiz-pop border-success bg-success/10",
                    isSelected && !isCorrectChoice && "animate-quiz-shake border-destructive bg-destructive/10",
                    answered && !isSelected && !isCorrectChoice && "border-border opacity-50",
                    enCours && "border-primary bg-primary/5",
                    choixEnCours !== null && !enCours && "opacity-50",
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
                    {enCours ? (
                      <Loader2 className="size-4 animate-spin" aria-hidden="true" />
                    ) : isCorrectChoice ? (
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
                {t("qs.astuce", { lettres: question.choix.map((c) => c.lettre.toUpperCase()).join(", ") })}
              </p>
            )}
          </div>
        ) : (
          <div className="mt-6 flex flex-col gap-4">
            {!answered && !questionCorrige && (
              <div className="flex flex-col gap-3 rounded-2xl border border-dashed border-primary/30 bg-primary/[0.03] p-4 sm:flex-row sm:items-center sm:justify-between">
                <p className="flex items-start gap-2 text-sm text-muted-foreground">
                  <Lightbulb className="mt-0.5 size-4 shrink-0 text-gold-text" />
                  {t("qs.brouillon")}
                </p>
                <Button size="lg" onClick={handleReveal} disabled={submitting} className="shrink-0">
                  <Sparkles />
                  {t("qs.voir_correction")}
                </Button>
              </div>
            )}

            {(questionCorrige || answered) && (
              <article className="prose prose-neutral max-w-none rounded-xl border-l-4 border-primary/50 bg-muted/40 py-3 pl-4 pr-3 dark:prose-invert">
                <EpreuveMarkdown markdown={question.corrige_markdown ?? questionCorrige?.corrige_markdown ?? ""} solutionsOuvertes />
              </article>
            )}

            {questionCorrige && !answered && (
              <div className="flex flex-col gap-2">
                <p className="text-sm font-medium">{t("qs.honnete")}</p>
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
                      {t(option.label)}
                    </Button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Le retour immédiat : dit tout de suite si c'est bon, encourage dans les deux cas. Le
            conteneur `status` est TOUJOURS présent : un lecteur d'écran n'annonce que les
            changements d'une région déjà montée, pas une région qui apparaît avec son contenu. */}
        <div role="status" aria-live="polite">
        {answered && (
          <div
            ref={amenerLeRetour}
            className={cn(
              "mt-5 flex scroll-mb-28 items-start gap-3 rounded-xl border px-4 py-3",
              // Une bonne réponse se FÊTE (rebond du bandeau, message en grand) : « le Bravo, c'est tout petit » (test élève Guyguy).
              correct ? "animate-quiz-bravo border-success/40 bg-success/10" : "animate-fade-up border-border bg-muted/50",
            )}
          >
            {correct ? (
              <Sparkles className="mt-0.5 size-6 shrink-0 text-success" />
            ) : (
              <BookOpenText className="mt-0.5 size-5 shrink-0 text-muted-foreground" />
            )}
            <div className="text-sm">
              <p className={cn("font-display font-semibold", correct && "text-lg")}>
                {correct
                  ? pick(MESSAGES_BONNE, question.id)
                  : question.reponse?.resultat_declare === "PARTIEL"
                    ? t("qs.presque")
                    : pick(MESSAGES_MAUVAISE, question.id)}
              </p>
              {correct && streak >= 3 && (
                <p className="text-muted-foreground">{t("qs.en_feu", { n: streak })}</p>
              )}
              {question.objectif_atteint_maintenant && (
                <p className="font-semibold text-success">{t("qs.objectif_atteint")}</p>
              )}
              {isQcm && !correct && question.reponse_correcte && (
                <p className="text-muted-foreground">
                  {t("qs.bonne_reponse")} <strong>{question.reponse_correcte.toUpperCase()}</strong>.
                </p>
              )}
            </div>
            {(question.reponse?.xp_gagne ?? 0) > 0 && (
              <span
                key={question.id}
                className="animate-xp-pop ml-auto inline-flex shrink-0 items-center gap-1 rounded-full bg-gold/20 px-3 py-1 text-sm font-bold tabular-nums text-gold-text"
              >
                <Zap className="size-4" aria-hidden="true" />
                +{libellePoints(question.reponse?.xp_gagne ?? 0)}
              </span>
            )}
          </div>
        )}
        </div>

        {isQcm && answered && question.corrige_markdown && (
          <details className="mt-4 rounded-xl border bg-muted/30 px-4 py-3" open={!correct}>
            <summary className="cursor-pointer text-sm font-medium">{t("qs.comprendre")}</summary>
            <article className="prose prose-neutral mt-3 max-w-none dark:prose-invert">
              <EpreuveMarkdown markdown={question.corrige_markdown} solutionsOuvertes />
            </article>
          </details>
        )}

        {/* Pour aller plus loin : un vrai sujet d'examen sur la même notion. Dans le MÊME onglet : la séance est enregistrée et
            se rouvre par son adresse, donc « Retour » la retrouve ; un onglet de plus, sans signe visible, déroutait sur
            téléphone (test élève Gogo). */}
        {answered && lienExercicesTheme && (
          <Link
            to={lienExercicesTheme}
            className="mt-4 flex items-center gap-3 rounded-xl border border-border px-4 py-3 text-sm transition-colors hover:border-primary/40 hover:bg-accent/40"
          >
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <FileText className="size-4" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block font-medium">{t("essai.exercices_theme")}</span>
              <span className="block text-muted-foreground">
                {t("qs.sujets_reels", { theme: capitaliserTheme(question.theme ?? "") })}
              </span>
            </span>
            <ArrowRight className="size-4 shrink-0 text-primary" />
          </Link>
        )}

        {actionError && (
          <p role="alert" className="mt-4 text-sm text-destructive">
            {actionError}
          </p>
        )}
      </div>

      {/* Sur téléphone, "Question suivante" reste sous le pouce, sans remonter. */}
      {answered && (
        <div className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-background/95 px-4 py-3 backdrop-blur sm:static sm:mt-5 sm:flex sm:justify-end sm:border-0 sm:bg-transparent sm:p-0 sm:backdrop-blur-none">
          <Button onClick={handleNext} disabled={submitting} className="animate-fade-up w-full sm:w-auto" size="lg">
            {isLast ? t("qs.voir_resultat") : t("qs.suivante")}
            <ArrowRight />
          </Button>
        </div>
      )}
    </div>
  )
}
