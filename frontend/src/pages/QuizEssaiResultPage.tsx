import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, FileText, Lock, RotateCcw, Sparkles } from "lucide-react"

import { startQuizEssai } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { themeExercicesPath } from "@/lib/countryPath"
import { lireEssai, memoriserEssai, oublierEssai, scoreEssai } from "@/lib/quizEssai"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn } from "@/lib/utils"

function message(pourcentage: number) {
  if (pourcentage >= 90) return { titre: "Sans faute, ou presque !", texte: "Tu maîtrises ce thème." }
  if (pourcentage >= 70) return { titre: "Très beau score !", texte: "Encore un petit effort sur les points ratés." }
  if (pourcentage >= 40) return { titre: "Bon début !", texte: "Relis les corrections des questions ratées : c'est là que tu progresses." }
  return { titre: "Chaque quiz te rapproche de l'examen", texte: "Relis les corrections puis refais l'essai : tu verras la différence." }
}

/**
 * Fin de l'essai gratuit d'un visiteur sans compte (voir lib/quizEssai.ts) : le score vient des
 * réponses gardées dans le navigateur, rien n'a été enregistré côté serveur. L'écran dit ce que
 * le visiteur a fait et ce que l'abonnement ajoute - sans rien promettre que le site ne garde
 * (pas de « ton score est sauvegardé » : il ne l'est pas).
 */
export function QuizEssaiResultPage() {
  useSeo({ title: "Résultat de l'essai gratuit" })
  const navigate = useNavigate()
  const { country } = useCountry()
  const { isAuthenticated } = useAuth()
  const [session] = useState(() => lireEssai())
  const [relance, setRelance] = useState(false)
  const [erreur, setErreur] = useState("")

  const score = useMemo(() => (session ? scoreEssai(session) : null), [session])
  const aRepondu = Boolean(score && score.repondues > 0)

  useEffect(() => {
    if (!aRepondu) navigate("/quiz", { replace: true })
  }, [aRepondu, navigate])

  if (!session || !score || !aRepondu) return null

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
      setErreur(err instanceof ApiError ? err.message : "Impossible de relancer l'essai.")
      setRelance(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 pb-12 pt-6 sm:px-6 sm:pt-10">
      <p className="mb-2 font-display text-sm italic text-primary">Essai gratuit · {session.cursus_display}</p>
      <h1 className="font-display text-3xl font-semibold tracking-tight text-balance sm:text-4xl">{titre}</h1>
      <p className="mt-2 text-muted-foreground">{texte}</p>

      <div className="mt-6 flex items-center gap-5 rounded-2xl border border-border bg-card p-5 shadow-sm">
        <div className="font-display text-5xl font-semibold tabular-nums">
          {score.reussies}
          <span className="text-2xl font-normal text-muted-foreground"> / {score.total}</span>
        </div>
        <p className="text-sm text-muted-foreground">
          bonne{score.reussies > 1 ? "s" : ""} réponse{score.reussies > 1 ? "s" : ""}
          {score.repondues < score.total && ` sur ${score.repondues} question${score.repondues > 1 ? "s" : ""} répondue${score.repondues > 1 ? "s" : ""}`}
        </p>
      </div>

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
          {relance ? "Préparation..." : "Refaire cet essai"}
        </Button>
        {themeId && subjectCode && (
          <Button asChild variant="outline" className="rounded-full">
            <Link to={`${themeExercicesPath(country, themeId)}?subject=${subjectCode}&cursus=${session.cursus}`}>
              <FileText />
              Exercices corrigés sur ce thème
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
          Ce n'était qu'un thème
        </p>
        <p className="mt-1 text-sm text-muted-foreground">
          Avec un abonnement, le quiz couvre tout ton programme : les thèmes que tu rates reviennent d'eux-mêmes
          les jours suivants, jusqu'à être acquis.
        </p>
        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <Button asChild size="lg" className="w-full sm:w-auto">
            <Link to="/tarifs">
              Voir les abonnements
              <ArrowRight />
            </Link>
          </Button>
          {!isAuthenticated && (
            <Button asChild size="lg" variant="outline" className="w-full sm:w-auto">
              <Link to="/connexion" state={{ from: "/quiz", intent: "Crée ton compte pour continuer à t'entraîner." }}>
                Créer mon compte
              </Link>
            </Button>
          )}
        </div>
        <p className="mt-3 flex items-center gap-1.5 text-xs text-muted-foreground">
          <Lock className="size-3.5" aria-hidden="true" />
          Ton score de cet essai n'est pas enregistré : il disparaît quand tu fermes l'onglet.
        </p>
      </section>

      <div className="mt-6">
        <Link
          to="/quiz"
          onClick={oublierEssai}
          className="text-sm font-medium text-primary underline-offset-4 hover:underline"
        >
          Essayer un autre thème gratuit
        </Link>
      </div>
    </div>
  )
}
