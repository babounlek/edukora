import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowLeft, Check, Info, ListChecks, RotateCcw, X } from "lucide-react"

import { getQuizHistoriqueDetail, rejouerQuiz } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizHistoriqueQuestion } from "@/api/types"
import { EnteteCompte } from "@/components/CompteSection"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { ErreurChargement } from "@/components/ErreurChargement"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { traduireLibelleSerie } from "@/lib/cursus"
import { formatDureeEcoulee } from "@/lib/duration"
import { localeCourante, t, useI18n } from "@/lib/i18n"
import { nomAccessibleDuChoix } from "@/lib/markdown"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn } from "@/lib/utils"

const SEUIL_REUSSITE = 70

const DECLARE: Record<string, "hq.declare_reussi" | "hq.declare_partiel" | "hq.declare_echec"> = {
  REUSSI: "hq.declare_reussi",
  PARTIEL: "hq.declare_partiel",
  ECHEC: "hq.declare_echec",
}

/** Une question de la tentative, en lecture seule : ce qui a été présenté, répondu, et la correction. */
function QuestionHistorique({ question }: { question: QuizHistoriqueQuestion }) {
  useI18n()
  const reponse = question.reponse
  const qcm = question.type_reponse === "QCM"
  return (
    <li className="rounded-2xl border border-border bg-card p-4 sm:p-5">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="font-display text-sm font-semibold">{t("hq.question_n", { n: question.ordre })}</span>
        {question.theme && <Badge variant="outline">{capitaliserTheme(question.theme)}</Badge>}
        {reponse === null ? (
          <Badge variant="outline">{t("hq.sans_reponse")}</Badge>
        ) : (
          <Badge variant={reponse.est_correcte ? "success" : "warning"}>
            {reponse.est_correcte ? <Check className="mr-1 size-3" aria-hidden="true" /> : <X className="mr-1 size-3" aria-hidden="true" />}
            {qcm ? (reponse.est_correcte ? t("hq.bonne_reponse") : t("hq.ta_reponse")) : t(DECLARE[reponse.resultat_declare] ?? "hq.declare_echec")}
          </Badge>
        )}
      </div>

      <article className="prose prose-neutral max-w-none dark:prose-invert">
        {question.enonce_intro_markdown && <EpreuveMarkdown markdown={question.enonce_intro_markdown} />}
        <EpreuveMarkdown markdown={question.enonce_markdown} />
      </article>

      {qcm && (
        <ul className="mt-4 flex flex-col gap-2">
          {question.choix.map((choix) => {
            const choisi = reponse?.reponse_choisie === choix.lettre
            const juste = question.reponse_correcte === choix.lettre
            return (
              <li
                key={choix.lettre}
                aria-label={nomAccessibleDuChoix(choix.lettre, choix.texte)}
                className={cn(
                  "flex items-center gap-3 rounded-xl border-2 px-3.5 py-2.5 text-[0.95rem]",
                  juste && "border-success/60 bg-success/10",
                  choisi && !juste && "border-destructive/50 bg-destructive/10",
                  !juste && !choisi && "border-border",
                )}
              >
                <span className="flex size-6 shrink-0 items-center justify-center rounded-full border border-border bg-background text-xs font-semibold uppercase">
                  {choix.lettre}
                </span>
                <span className="min-w-0 flex-1">
                  <EpreuveMarkdown markdown={choix.texte} />
                </span>
                {juste && <Check className="size-4 shrink-0 text-success" aria-label={t("hq.bonne_reponse")} />}
                {choisi && !juste && <X className="size-4 shrink-0 text-destructive" aria-label={t("hq.ta_reponse")} />}
              </li>
            )
          })}
        </ul>
      )}

      {question.cle_modifiee && (
        <p className="mt-3 flex items-start gap-1.5 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
          {t("hq.cle_modifiee")}
        </p>
      )}
      {!question.contenu_disponible && (
        <p className="mt-3 flex items-start gap-1.5 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
          {t("hq.contenu_retire")}
        </p>
      )}

      <details className="group mt-4 rounded-xl border border-border bg-muted/30 px-3.5 py-2.5">
        <summary className="cursor-pointer text-sm font-semibold text-primary">{t("hq.correction")}</summary>
        <article className="prose prose-neutral mt-3 max-w-none dark:prose-invert">
          <EpreuveMarkdown markdown={question.corrige_markdown} solutionsOuvertes />
        </article>
      </details>
    </li>
  )
}

export function QuizHistoriquePage() {
  useI18n()
  useSeo({ title: t("hq.detail_titre") })

  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { isAuthenticated, isLoading } = useAuth()
  const [rejeu, setRejeu] = useState(false)
  const [erreurRejeu, setErreurRejeu] = useState("")

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) navigate("/connexion", { state: { from: `/historique/quiz/${id}` } })
  }, [isLoading, isAuthenticated, navigate, id])

  const detailQuery = useQuery({
    queryKey: ["quiz-historique-detail", id],
    queryFn: ({ signal }) => getQuizHistoriqueDetail(Number(id), signal),
    enabled: !isLoading && isAuthenticated && !!id,
    // Une tentative terminée est immuable : inutile de la recharger à chaque visite.
    staleTime: 5 * 60_000,
  })

  async function rejouer() {
    if (rejeu) return
    setRejeu(true)
    setErreurRejeu("")
    try {
      const session = await rejouerQuiz(Number(id))
      // Le rejeu est une nouvelle tentative : elle apparaîtra dans l'historique une fois terminée.
      queryClient.invalidateQueries({ queryKey: ["quiz-historique"] })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setErreurRejeu(err instanceof ApiError ? err.message : t("hq.err_rejouer"))
      setRejeu(false)
    }
  }

  if (isLoading) return null

  const retour = (
    <Link to="/historique" className="mb-4 inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline">
      <ArrowLeft className="size-4" aria-hidden="true" />
      {t("hq.retour")}
    </Link>
  )

  if (detailQuery.isError) {
    const introuvable = detailQuery.error instanceof ApiError && detailQuery.error.status === 404
    return (
      <div className="mx-auto max-w-5xl px-4 py-6 sm:py-10 sm:px-6">
        {retour}
        <ErreurChargement
          objet={t("hq.objet")}
          message={introuvable ? t("hq.introuvable") : undefined}
          onRetry={introuvable ? undefined : () => detailQuery.refetch()}
          compact
        />
      </div>
    )
  }

  const detail = detailQuery.data
  if (!detail) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-6 sm:py-10 sm:px-6">
        <Skeleton className="mb-4 h-8 w-48" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  const details = [
    traduireLibelleSerie(detail.cursus_display),
    new Date(detail.completed_at).toLocaleDateString(localeCourante()),
    detail.duree_secondes !== null ? formatDureeEcoulee(detail.duree_secondes) : null,
    detail.nb_tentatives > 1 ? t("hq.tentative_n", { n: detail.numero_tentative, total: detail.nb_tentatives }) : null,
  ].filter(Boolean)

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:py-10 sm:px-6">
      {retour}
      <EnteteCompte
        icone={ListChecks}
        titre={detail.subject_label || detail.theme || t("hq.quiz_sans_titre")}
        sousTitre={details.join(" · ")}
      />

      <section className="mb-5 flex flex-col gap-3 rounded-2xl border border-border bg-card p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
        <div>
          <p className="font-display text-2xl font-semibold">
            {t("hq.score", { score: detail.score, total: detail.total_questions })}
            <Badge className="ml-2 align-middle" variant={detail.pourcentage >= SEUIL_REUSSITE ? "success" : "outline"}>
              {detail.pourcentage}%
            </Badge>
          </p>
          <p className="mt-1 text-sm text-muted-foreground">{t("hq.lecture_seule")}</p>
        </div>
        {detail.peut_rejouer && (
          <div className="sm:max-w-xs">
            <Button onClick={rejouer} disabled={rejeu} size="lg" className="w-full">
              <RotateCcw className="mr-2 size-4" aria-hidden="true" />
              {rejeu ? t("hq.rejouer_en_cours") : t("hq.rejouer")}
            </Button>
            <p className="mt-1.5 text-xs text-muted-foreground">{t("hq.rejouer_aide")}</p>
            {erreurRejeu && <p role="alert" className="mt-2 text-sm text-destructive">{erreurRejeu}</p>}
          </div>
        )}
      </section>

      {detail.snapshot_retroactif && (
        <p className="mb-4 flex items-start gap-1.5 rounded-xl border border-dashed border-border px-3.5 py-2.5 text-sm text-muted-foreground">
          <Info className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
          {t("hq.retroactif")}
        </p>
      )}

      <ol className="flex flex-col gap-4">
        {detail.questions.map((question) => (
          <QuestionHistorique key={question.id} question={question} />
        ))}
      </ol>
    </div>
  )
}
