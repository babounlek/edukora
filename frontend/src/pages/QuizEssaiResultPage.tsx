import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, FileText, Lock, RotateCcw, Sparkles, Trophy, Zap } from "lucide-react"

import { startQuizEssai } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { BoutonPartager } from "@/components/BoutonPartager"
import { Button } from "@/components/ui/button"
import { Confettis } from "@/components/Confettis"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { themeExercicesPath } from "@/lib/countryPath"
import {
  bat, cheminEssai, lireEssai, lireRecord, memoriserEssai, memoriserRecord, oublierEssai, pointsEssai, scoreEssai,
  texteDePartageEssai,
} from "@/lib/quizEssai"
import { trackEvent } from "@/lib/analytics"
import { jouerRetour } from "@/lib/retours"
import { useCompteur } from "@/lib/useCompteur"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"
import { traduireLibelleSerie } from "@/lib/cursus"

function message(pourcentage: number) {
  if (pourcentage >= 90) return { titre: t("essai.msg1_titre"), texte: t("essai.msg1_texte") }
  if (pourcentage >= 70) return { titre: t("essai.msg2_titre"), texte: t("essai.msg2_texte") }
  if (pourcentage >= 40) return { titre: t("essai.msg3_titre"), texte: t("essai.msg3_texte") }
  return { titre: t("essai.msg4_titre"), texte: t("essai.msg4_texte") }
}

/**
 * Fin de l'essai gratuit d'un visiteur sans compte (voir lib/quizEssai.ts) : le score vient des
 * réponses gardées dans le navigateur, rien n'a été enregistré côté serveur. L'écran dit ce que
 * le visiteur a fait et ce que l'abonnement ajoute - sans rien promettre que le site ne garde
 * (pas de « ton score est sauvegardé » : il ne l'est pas).
 */
export function QuizEssaiResultPage() {
  useI18n()
  useSeo({ title: t("essai.seo_resultat") })
  const navigate = useNavigate()
  const { country } = useCountry()
  const { isAuthenticated } = useAuth()
  const [session] = useState(() => lireEssai())
  const [relance, setRelance] = useState(false)
  const [erreur, setErreur] = useState("")

  const score = useMemo(() => (session ? scoreEssai(session) : null), [session])
  const aRepondu = Boolean(score && score.repondues > 0)
  // Le record d'AVANT cet essai : lu une fois au montage, la mémorisation plus bas ne le change pas sous nos yeux.
  const [recordAvant] = useState(() => (session ? lireRecord(session) : null))
  const points = useMemo(() => (session ? pointsEssai(session) : 0), [session])
  const pointsAffiches = useCompteur(points)

  useEffect(() => {
    if (!aRepondu) navigate("/quiz", { replace: true })
  }, [aRepondu, navigate])

  useEffect(() => {
    if (!aRepondu || !session || !score) return
    jouerRetour("fin")
    memoriserRecord(session, score.reussies, score.total)
  }, [aRepondu, session, score])

  if (!session || !score || !aRepondu) return null

  const recordBattu = bat(recordAvant, score.reussies, score.total)
  const pourcentage = Math.round((100 * score.reussies) / score.total)
  const { titre, texte } = message(pourcentage)
  const premiere = session.questions[0]
  const themeId = premiere.theme_id
  const subjectCode = premiere.subject_code
  const subjectId = session.subject

  async function refaire() {
    if (relance || !subjectId || !themeId) return
    setRelance(true)
    setErreur("")
    try {
      const nouvelle = await startQuizEssai({ cursus: session!.cursus, subject: subjectId, theme: themeId })
      memoriserEssai(nouvelle)
      trackEvent("quiz_started", { cursus_id: session!.cursus, mode: "PRATIQUE", source: "essai_anonyme" })
      navigate("/quiz/essai")
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : t("essai.relance_erreur"))
      setRelance(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 pb-12 pt-6 sm:px-6 sm:pt-10">
      {pourcentage >= 70 && <Confettis />}
      <p className="mb-2 font-display text-sm italic text-primary">{t("essai.surtitre", { cursus: traduireLibelleSerie(session.cursus_display) })}</p>
      <h1 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">{titre}</h1>
      <p className="mt-2 text-muted-foreground">{texte}</p>

      <div className="mt-6 flex items-center gap-5 rounded-2xl border border-border bg-card p-5 shadow-sm">
        <div className="font-display text-5xl font-semibold tabular-nums">
          {score.reussies}
          <span className="text-2xl font-normal text-muted-foreground"> / {score.total}</span>
        </div>
        <p className="text-sm text-muted-foreground">
          {tn("essai.bonnes", score.reussies)}
          {score.repondues < score.total && tn("essai.sur_repondues", score.repondues)}
        </p>
      </div>

      {/* Le gain, avant le reste : l'élève connecté voit ses points défiler à cet endroit, le visiteur n'avait
          qu'un « 3/5 » sec. Ce n'est PAS crédité - la phrase dessous le dit, au lieu de laisser croire le contraire. */}
      <section aria-label={t("essai.points_titre")} className="mt-4 rounded-2xl border border-gold/40 bg-gold/10 p-5">
        <p className="text-sm text-muted-foreground">{t("essai.points_titre")}</p>
        <p className="flex items-center gap-1.5 font-display text-4xl font-semibold tabular-nums text-gold-text">
          <Zap className="size-7" aria-hidden="true" />
          {t("gl.partage_points", { n: pointsAffiches })}
        </p>
        {points === 0 ? (
          <p className="mt-1 text-xs text-muted-foreground">{t("qr.points_bonnes")}</p>
        ) : (
          !isAuthenticated && <p className="mt-1 text-xs text-muted-foreground">{t("essai.points_compte")}</p>
        )}
        {recordBattu && recordAvant && (
          <p className="mt-3 flex items-center gap-2 rounded-xl bg-success/15 px-3 py-2 text-sm font-medium">
            <Trophy className="size-4 shrink-0 text-gold-text" aria-hidden="true" />
            {t("essai.record_battu", { a: recordAvant.reussies, b: recordAvant.total })}
          </p>
        )}
        {!recordBattu && recordAvant && (
          <p className="mt-3 text-sm font-medium">{t("essai.record", { a: recordAvant.reussies, b: recordAvant.total })}</p>
        )}
      </section>

      {score.parTheme.length > 0 && (
        <ul className="mt-4 divide-y divide-border overflow-hidden rounded-2xl border border-border bg-card">
          {score.parTheme.map((t) => {
            const taux = Math.round((100 * t.reussies) / t.total)
            return (
              <li key={t.theme} className="px-4 py-3.5 sm:px-5">
                <div className="flex items-baseline gap-3">
                  <span className="min-w-0 flex-1 truncate font-medium">{capitaliserTheme(t.theme)}</span>
                  <span className="shrink-0 text-sm font-semibold tabular-nums">
                    {t.reussies}
                    <span className="font-normal text-muted-foreground"> / {t.total}</span>
                  </span>
                </div>
                <span className="mt-2 block h-1.5 w-full overflow-hidden rounded-full bg-muted">
                  <span
                    className={cn("block h-full rounded-full", taux >= 70 ? "bg-success" : taux >= 40 ? "bg-gold" : "bg-destructive/70")}
                    style={{ width: `${Math.max(taux, 4)}%` }}
                  />
                </span>
              </li>
            )
          })}
        </ul>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        <Button variant="outline" onClick={refaire} disabled={relance || !subjectId || !themeId} className="rounded-full">
          <RotateCcw />
          {relance ? t("quiz.preparation") : t("essai.refaire")}
        </Button>
        {cheminEssai(session) && (
          <BoutonPartager
            chemin={cheminEssai(session)!} texte={texteDePartageEssai(session)} type="quiz"
            libelle={t("essai.defier")} size="default" className="rounded-full"
          />
        )}
        {themeId && subjectCode && (
          <Button asChild variant="outline" className="rounded-full">
            <Link to={`${themeExercicesPath(country, themeId)}?subject=${subjectCode}&cursus=${session.cursus}`}>
              <FileText />
              {t("essai.exercices_theme")}
            </Link>
          </Button>
        )}
      </div>
      {erreur && (
        <p role="alert" className="mt-3 text-sm text-destructive">
          {erreur}
        </p>
      )}

      {/* L'invitation : ce que le visiteur vient de goûter sur UN thème, ce qu'il y a derrière. */}
      <section className="mt-8 rounded-2xl border border-primary/25 bg-gradient-to-br from-primary/5 via-transparent to-transparent p-5 sm:p-6">
        <p className="flex items-center gap-2 font-display text-lg font-semibold">
          <Sparkles className="size-5 text-gold-text" aria-hidden="true" />
          {t("essai.un_theme")}
        </p>
        <p className="mt-1 text-sm text-muted-foreground">
          {t("essai.un_theme_texte")}
        </p>
        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <Button asChild size="lg" className="w-full sm:w-auto">
            <Link to="/tarifs">
              {t("essai.voir_abonnements")}
              <ArrowRight />
            </Link>
          </Button>
          {!isAuthenticated && (
            <Button asChild size="lg" variant="outline" className="w-full sm:w-auto">
              <Link to="/connexion" state={{ from: "/quiz", intent: t("essai.intent_compte") }}>
                {t("essai.creer_compte")}
              </Link>
            </Button>
          )}
        </div>
        <p className="mt-3 flex items-center gap-1.5 text-xs text-muted-foreground">
          <Lock className="size-3.5" aria-hidden="true" />
          {t("essai.non_enregistre")}
        </p>
      </section>

      <div className="mt-6">
        <Link
          to="/quiz"
          onClick={oublierEssai}
          className="text-sm font-medium text-primary underline-offset-4 hover:underline"
        >
          {t("essai.autre_theme")}
        </Link>
      </div>
    </div>
  )
}
