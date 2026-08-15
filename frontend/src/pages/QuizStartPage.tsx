import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, CheckCircle2, ListChecks, Lock, RotateCcw, Sparkles, Target, Trophy } from "lucide-react"

import { getMaitrise, listMySubscriptions, listQuizSubjects, listRevisionsDues, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { MaitriseTheme, ModeQuiz, RevisionDue, Subject, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

const TOUTES_MATIERES = "toutes"

export function QuizStartPage() {
  useSeo({
    title: "Quiz",
    description: "Entraîne-toi ou évalue ton niveau avec des questions tirées des corrigés de ton cursus.",
  })

  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()

  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [selectedCursus, setSelectedCursus] = useState("")
  const [selectedSubject, setSelectedSubject] = useState(TOUTES_MATIERES)
  const [mode, setMode] = useState<ModeQuiz>("PRATIQUE")
  const [subscriptionsLoaded, setSubscriptionsLoaded] = useState(false)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState("")
  const [revisions, setRevisions] = useState<RevisionDue[]>([])
  const [maitrise, setMaitrise] = useState<MaitriseTheme[]>([])

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/quiz" } })
      return
    }
    listMySubscriptions().then((subs) => {
      const active = subs.filter((sub) => sub.is_active)
      setSubscriptions(active)
      setSubscriptionsLoaded(true)
      if (active.length > 0) setSelectedCursus(String(active[0].cursus.id))
    })
    // Best-effort, jamais bloquant pour l'écran de démarrage : un échec ici ne doit
    // pas empêcher de configurer/lancer un quiz normalement.
    listRevisionsDues().then(setRevisions).catch(() => {})
  }, [authLoading, isAuthenticated, navigate])

  // Uniquement les matières ayant déjà une banque de quiz pour CE cursus (voir
  // quiz.views.list_quiz_subjects) - lister toutes les matières du pays (comme sur
  // /fiches) laisserait choisir une matière sans aucune question, avec l'échec de
  // démarrage seulement une fois le quiz lancé.
  useEffect(() => {
    const sub = subscriptions.find((s) => String(s.cursus.id) === selectedCursus)
    if (!sub) {
      setSubjects([])
      return
    }
    setSelectedSubject(TOUTES_MATIERES)
    listQuizSubjects(sub.cursus.id).then(setSubjects)
  }, [selectedCursus, subscriptions])

  // Teaser de progression dans le hero, jamais bloquant pour la config du quiz : un
  // échec ou une absence d'historique ne doit rien changer à l'écran de démarrage.
  useEffect(() => {
    if (!selectedCursus) {
      setMaitrise([])
      return
    }
    getMaitrise(Number(selectedCursus)).then(setMaitrise).catch(() => {})
  }, [selectedCursus])

  const maitriseStats = useMemo(() => {
    if (maitrise.length === 0) return null
    const moyenne = Math.round(maitrise.reduce((sum, t) => sum + t.taux, 0) / maitrise.length)
    const maitrises = maitrise.filter((t) => t.taux >= 70).length
    return { moyenne, maitrises, total: maitrise.length }
  }, [maitrise])

  async function handleStart() {
    if (!selectedCursus) return
    setStarting(true)
    setError("")
    try {
      const session = await startQuizSession({
        cursus: Number(selectedCursus),
        mode,
        subject: selectedSubject === TOUTES_MATIERES ? undefined : Number(selectedSubject),
      })
      trackEvent("quiz_started", { cursus_id: Number(selectedCursus), mode })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Impossible de démarrer le quiz pour le moment. Réessaie plus tard.",
      )
      setStarting(false)
    }
  }

  if (authLoading || !subscriptionsLoaded) {
    return (
      <div className="mx-auto max-w-xl px-4 py-10">
        <Skeleton className="mb-3 h-8 w-32" />
        <Skeleton className="mb-8 h-4 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-xl animate-fade-up px-4 py-10">
      <div className="relative mb-6 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative">
          <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Target className="size-5" />
          </div>
          <p className="mb-1 font-display text-sm italic text-primary">Entraînement personnalisé</p>
          <h1 className="font-display text-3xl font-semibold">Quiz</h1>
          <p className="mt-2 text-muted-foreground">
            Entraîne-toi librement ou fais un test de niveau à partir des corrigés de ton cursus - le quiz repère ce
            que tu dois retravailler et te le repropose au bon moment.
          </p>

          {maitriseStats && (
            <div className="mt-5 flex flex-wrap gap-2">
              <div className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
                <Target className="size-3.5 text-primary" />
                <span className="font-medium">{maitriseStats.moyenne}%</span>
                <span className="text-muted-foreground">de maîtrise moyenne</span>
              </div>
              <div className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
                <Trophy className="size-3.5 text-gold" />
                <span className="font-medium">
                  {maitriseStats.maitrises}/{maitriseStats.total}
                </span>
                <span className="text-muted-foreground">thèmes maîtrisés</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {revisions.length > 0 && (
        <Card className="mb-5 overflow-hidden border-warning/30 bg-gradient-to-br from-warning/10 via-transparent to-transparent">
          <CardContent className="flex flex-col gap-3 pt-6">
            <div className="flex items-center gap-2.5">
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-warning/15 text-warning">
                <RotateCcw className="size-4" />
              </span>
              <p className="text-sm font-medium">
                {revisions.length} notion{revisions.length > 1 ? "s" : ""} à réviser
              </p>
            </div>
            <ul className="flex flex-col gap-1 pl-10 text-sm text-muted-foreground">
              {revisions.slice(0, 3).map((revision) => (
                <li key={revision.id}>{revision.theme}</li>
              ))}
              {revisions.length > 3 && <li>+ {revisions.length - 3} autre{revisions.length - 3 > 1 ? "s" : ""}</li>}
            </ul>
            <Button asChild size="sm" variant="outline" className="ml-10 w-fit">
              <Link to="/revision">
                Réviser maintenant
                <ArrowRight className="size-3.5" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {subscriptions.length === 0 ? (
        <Card className="overflow-hidden border-primary/25 bg-gradient-to-br from-primary/5 via-transparent to-transparent">
          <CardContent className="flex flex-col items-start gap-4 pt-6">
            <span className="flex size-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Lock className="size-5" />
            </span>
            <div>
              <p className="font-display text-base font-semibold">Débloque le Quiz</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Réservé aux cursus avec un abonnement actif - repère tes lacunes et révise exactement ce qu'il faut,
                au bon moment.
              </p>
            </div>
            <ul className="flex flex-col gap-1.5 text-sm">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="size-4 shrink-0 text-success" />
                Questions ciblées sur ton cursus
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="size-4 shrink-0 text-success" />
                Détection automatique de tes lacunes
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="size-4 shrink-0 text-success" />
                Suivi de ta progression, thème par thème
              </li>
            </ul>
            <Button asChild size="lg" className="w-full sm:w-auto">
              <a href="/tarifs">
                Voir les tarifs
                <ArrowRight className="size-4" />
              </a>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="font-display text-lg">Configure ton quiz</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-5">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Cursus</label>
              <Select value={selectedCursus} onValueChange={setSelectedCursus}>
                <SelectTrigger>
                  <SelectValue placeholder="Choisis ton cursus" />
                </SelectTrigger>
                <SelectContent>
                  {subscriptions.map((sub) => (
                    <SelectItem key={sub.cursus.id} value={String(sub.cursus.id)}>
                      {sub.cursus.examen_display}
                      {sub.cursus.series ? ` - Série ${sub.cursus.series.code}` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Matière</label>
              <Select value={selectedSubject} onValueChange={setSelectedSubject}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={TOUTES_MATIERES}>Toutes les matières</SelectItem>
                  {subjects.map((subject) => (
                    <SelectItem key={subject.id} value={String(subject.id)}>
                      {subject.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Mode</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setMode("PRATIQUE")}
                  className={cn(
                    "group relative flex flex-col items-start gap-2 rounded-xl border px-3.5 py-3 text-left transition-all",
                    mode === "PRATIQUE"
                      ? "border-primary bg-primary/5 shadow-sm"
                      : "border-border hover:border-primary/40 hover:bg-accent/40",
                  )}
                >
                  {mode === "PRATIQUE" && (
                    <CheckCircle2 className="absolute right-2.5 top-2.5 size-4 text-primary" />
                  )}
                  <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Sparkles className="size-3.5" />
                  </span>
                  <span className="text-sm font-medium">Pratique libre</span>
                  <span className="text-xs text-muted-foreground">
                    Cible davantage les thèmes où tu échoues, au fil de tes sessions.
                  </span>
                </button>
                <button
                  type="button"
                  onClick={() => setMode("DIAGNOSTIC")}
                  className={cn(
                    "group relative flex flex-col items-start gap-2 rounded-xl border px-3.5 py-3 text-left transition-all",
                    mode === "DIAGNOSTIC"
                      ? "border-primary bg-primary/5 shadow-sm"
                      : "border-border hover:border-primary/40 hover:bg-accent/40",
                  )}
                >
                  {mode === "DIAGNOSTIC" && (
                    <CheckCircle2 className="absolute right-2.5 top-2.5 size-4 text-primary" />
                  )}
                  <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <ListChecks className="size-3.5" />
                  </span>
                  <span className="text-sm font-medium">Test de niveau</span>
                  <span className="text-xs text-muted-foreground">Difficultés variées, pour situer ton niveau.</span>
                </button>
              </div>
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}

            <Button onClick={handleStart} disabled={!selectedCursus || starting} size="lg" className="w-full gap-2">
              {starting ? (
                "Préparation..."
              ) : (
                <>
                  Lancer mon quiz
                  <ArrowRight className="size-4" />
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
