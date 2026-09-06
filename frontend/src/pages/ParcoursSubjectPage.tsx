import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, ArrowRight, BookOpenText, Compass, Sparkles } from "lucide-react"

import { getParcours, listMySubscriptions, listSubjects, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ParcoursModule, ParcoursSavoir, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Etape } from "@/components/Configurateur"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { coursDetailPath } from "@/lib/countryPath"
import { SEUIL_MAITRISE } from "@/lib/maitrise"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"

type SavoirEnrichi = ParcoursSavoir & { moduleTitre: string }

function aplatirSavoirs(modules: ParcoursModule[]): SavoirEnrichi[] {
  return modules.flatMap((module) => module.savoirs.map((savoir) => ({ ...savoir, moduleTitre: module.titre })))
}

/** Étape suivante recommandée, mise en avant en tête de page plutôt que de laisser
 * l'élève chercher lui-même dans la liste. Aucun historique de quiz du tout sur ce
 * cursus : mieux vaut un test de positionnement (couvre tout le programme d'un coup)
 * qu'un plongeon direct dans le premier savoir. Sinon, priorité à ce qui est déjà en
 * échec (voir RevisionSchedule côté backend), puis au premier savoir jamais maîtrisé
 * dans l'ordre du programme. */
function prochaineEtape(savoirs: SavoirEnrichi[]): SavoirEnrichi | "diagnostic" | null {
  const aUnHistorique = savoirs.some((s) => s.taux !== null)
  if (!aUnHistorique) return "diagnostic"
  return savoirs.find((s) => s.en_revision) ?? savoirs.find((s) => (s.taux ?? 0) < SEUIL_MAITRISE) ?? null
}

function BadgeSavoir({ savoir }: { savoir: ParcoursSavoir }) {
  if (savoir.en_revision) return <Badge variant="outline">À réviser</Badge>
  if (savoir.taux !== null && savoir.taux >= SEUIL_MAITRISE) return <Badge variant="success">Maîtrisé</Badge>
  if (savoir.taux !== null) return <Badge variant="outline">{savoir.taux}% de réussite</Badge>
  if (savoir.has_quiz || savoir.cours) return <Badge variant="outline">À découvrir</Badge>
  return <Badge variant="outline">Contenu à venir</Badge>
}

export function ParcoursSubjectPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const cursusFromUrl = searchParams.get("cursus") ?? ""

  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [selectedCursus, setSelectedCursus] = useState("")
  const [subjectLabel, setSubjectLabel] = useState("")
  const [modules, setModules] = useState<ParcoursModule[] | null>(null)
  const [subscriptionsLoaded, setSubscriptionsLoaded] = useState(false)
  const [error, setError] = useState("")
  const [starting, setStarting] = useState(false)

  useSeo({
    title: subjectLabel ? `Parcours ${subjectLabel}` : "Ton parcours",
    description: "Le programme officiel de ta matière, dans l'ordre, avec ce qu'il te reste à travailler.",
  })

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: `/parcours/${subjectId}` } })
      return
    }
    listMySubscriptions()
      .then((subs) => {
        const active = subs.filter((sub) => sub.is_active)
        setSubscriptions(active)
        const depuisUrl = active.find((sub) => String(sub.cursus.id) === cursusFromUrl)
        if (depuisUrl) setSelectedCursus(cursusFromUrl)
        else if (active.length > 0) setSelectedCursus(String(active[0].cursus.id))
      })
      .catch(() => setError("Impossible de charger tes abonnements."))
      .finally(() => setSubscriptionsLoaded(true))
    // cursusFromUrl volontairement omis : ne sert qu'à l'initialisation, pas de
    // resynchronisation si l'utilisateur change ensuite le select ci-dessous.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, isAuthenticated, navigate, subjectId])

  // Résolu depuis le référentiel complet des matières (pas listQuizSubjects, qui
  // n'expose que celles ayant déjà une banque de quiz - une matière encore sans
  // aucun contenu doit quand même pouvoir afficher son libellé ici, on y arrive
  // justement depuis une carte du tableau de bord qui l'affiche grisée).
  useEffect(() => {
    const sub = subscriptions.find((s) => String(s.cursus.id) === selectedCursus)
    if (!sub) return
    listSubjects(sub.cursus.country.code.toLowerCase()).then((data) => {
      const subject = data.find((s) => String(s.id) === subjectId)
      if (subject) setSubjectLabel(subject.label)
    })
  }, [selectedCursus, subscriptions, subjectId])

  useEffect(() => {
    if (!selectedCursus || !subjectId) return
    setModules(null)
    getParcours(Number(selectedCursus), Number(subjectId))
      .then(setModules)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Impossible de charger ton parcours."))
  }, [selectedCursus, subjectId])

  const savoirs = useMemo(() => (modules ? aplatirSavoirs(modules) : []), [modules])
  const etape = useMemo(() => prochaineEtape(savoirs), [savoirs])

  async function lancerQuiz(params: { savoir?: number; mode?: "DIAGNOSTIC" }) {
    if (starting || !subjectId) return
    setStarting(true)
    setError("")
    try {
      const session = await startQuizSession({
        cursus: Number(selectedCursus),
        subject: Number(subjectId),
        n: params.mode === "DIAGNOSTIC" ? 20 : 10,
        ...params,
      })
      trackEvent("quiz_started", { cursus_id: Number(selectedCursus), mode: params.mode ?? "PRATIQUE", source: "parcours" })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible de démarrer ce quiz. Réessaie plus tard.")
      setStarting(false)
    }
  }

  if (authLoading || !subscriptionsLoaded) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-10">
        <Skeleton className="mb-3 h-8 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    )
  }

  if (subscriptions.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <Compass className="mx-auto mb-3 size-8 text-muted-foreground" />
        <p className="font-display text-lg font-medium">Aucun abonnement actif</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Le parcours suit le programme officiel de ton cursus - il te faut un abonnement actif pour en avoir un.
        </p>
        <Button asChild className="mt-4">
          <Link to="/tarifs">Voir les tarifs</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-10">
      <Link
        to="/parcours"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour à tes matières
      </Link>
      <div className="mb-2 flex items-center gap-2">
        <Compass className="size-6 text-primary" />
        <h1 className="font-display text-3xl font-semibold">{subjectLabel || "Ton parcours"}</h1>
      </div>
      <p className="mb-6 text-muted-foreground">
        Le programme officiel, dans l'ordre - avec ce qu'il te reste à découvrir, réviser ou maîtriser.
      </p>

      {subscriptions.length > 1 && (
        <select
          value={selectedCursus}
          onChange={(e) => {
            setSelectedCursus(e.target.value)
            setSearchParams({ cursus: e.target.value })
          }}
          className="mb-6 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
        >
          {subscriptions.map((sub) => (
            <option key={sub.cursus.id} value={sub.cursus.id}>
              {sub.cursus.examen_display}
              {sub.cursus.series ? ` - Série ${sub.cursus.series.code}` : ""}
            </option>
          ))}
        </select>
      )}

      {!modules ? (
        <div className="flex flex-col gap-3">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
      ) : (
        <>
          {etape && (
            <div className="mb-8 rounded-xl border border-primary/20 bg-primary/[0.03] p-5">
              <p className="flex items-center gap-1.5 font-display text-sm font-semibold text-primary">
                <Sparkles className="size-4" />
                Prochaine étape recommandée
              </p>
              {etape === "diagnostic" ? (
                <>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Tu n'as encore rien tenté sur ce cursus - commence par un test de positionnement pour savoir
                    d'où partir.
                  </p>
                  <Button className="mt-3" disabled={starting} onClick={() => lancerQuiz({ mode: "DIAGNOSTIC" })}>
                    {starting ? "Préparation..." : "Faire le test de positionnement"}
                  </Button>
                </>
              ) : (
                <>
                  <p className="mt-1 text-sm text-muted-foreground">{etape.moduleTitre}</p>
                  <p className="font-display font-medium">{etape.intitule}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {etape.cours && (
                      <Button asChild variant="outline">
                        <Link to={coursDetailPath(etape.cours.slug)}>
                          <BookOpenText />
                          Lire le cours
                        </Link>
                      </Button>
                    )}
                    {etape.has_quiz && (
                      <Button disabled={starting} onClick={() => lancerQuiz({ savoir: etape.id })}>
                        {starting ? "Préparation..." : "Tester mes connaissances"}
                        <ArrowRight />
                      </Button>
                    )}
                  </div>
                </>
              )}
            </div>
          )}

          <div className="flex flex-col gap-8">
            {modules.map((module) => (
              <div key={module.numero}>
                <p className="mb-4 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Module {module.numero} · {module.titre}
                </p>
                <div>
                  {module.savoirs.map((savoir, index) => (
                    <Etape
                      key={savoir.id}
                      numero={index + 1}
                      titre={savoir.intitule}
                      fait={savoir.taux !== null && savoir.taux >= SEUIL_MAITRISE}
                      inactif={!savoir.has_quiz && !savoir.cours}
                      dernier={index === module.savoirs.length - 1}
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <BadgeSavoir savoir={savoir} />
                        {savoir.cours && (
                          <Button asChild size="sm" variant="outline">
                            <Link to={coursDetailPath(savoir.cours.slug)}>
                              <BookOpenText />
                              {savoir.cours.titre}
                            </Link>
                          </Button>
                        )}
                        {savoir.has_quiz && (
                          <Button size="sm" disabled={starting} onClick={() => lancerQuiz({ savoir: savoir.id })}>
                            Tester mes connaissances
                          </Button>
                        )}
                      </div>
                    </Etape>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {error && <p className="mt-4 text-sm text-destructive">{error}</p>}
    </div>
  )
}
