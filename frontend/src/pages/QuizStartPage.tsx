import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { ListChecks, Sparkles } from "lucide-react"

import { listMySubscriptions, listSubjects, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ModeQuiz, Subject, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
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
  }, [authLoading, isAuthenticated, navigate])

  useEffect(() => {
    const sub = subscriptions.find((s) => String(s.cursus.id) === selectedCursus)
    if (!sub) {
      setSubjects([])
      return
    }
    setSelectedSubject(TOUTES_MATIERES)
    listSubjects(sub.cursus.country.code).then(setSubjects)
  }, [selectedCursus, subscriptions])

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

  if (authLoading || !subscriptionsLoaded) return null

  return (
    <div className="mx-auto max-w-xl animate-fade-up px-4 py-10">
      <h1 className="mb-1 font-display text-3xl font-semibold">Quiz</h1>
      <p className="mb-8 text-muted-foreground">
        Entraîne-toi librement ou fais un test de niveau à partir des corrigés de ton cursus.
      </p>

      {subscriptions.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-start gap-3 pt-6">
            <p className="text-sm text-muted-foreground">
              Le quiz est réservé aux cursus pour lesquels tu as un abonnement actif.
            </p>
            <Button asChild size="sm">
              <a href="/tarifs">Voir les tarifs</a>
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
                    "flex flex-col items-start gap-1 rounded-md border px-3 py-2.5 text-left transition-colors",
                    mode === "PRATIQUE" ? "border-primary bg-primary/5" : "border-border hover:bg-accent/40",
                  )}
                >
                  <span className="flex items-center gap-1.5 text-sm font-medium">
                    <Sparkles className="size-3.5 text-primary" />
                    Pratique libre
                  </span>
                  <span className="text-xs text-muted-foreground">Questions au hasard, pour t'entraîner.</span>
                </button>
                <button
                  type="button"
                  onClick={() => setMode("DIAGNOSTIC")}
                  className={cn(
                    "flex flex-col items-start gap-1 rounded-md border px-3 py-2.5 text-left transition-colors",
                    mode === "DIAGNOSTIC" ? "border-primary bg-primary/5" : "border-border hover:bg-accent/40",
                  )}
                >
                  <span className="flex items-center gap-1.5 text-sm font-medium">
                    <ListChecks className="size-3.5 text-primary" />
                    Test de niveau
                  </span>
                  <span className="text-xs text-muted-foreground">Difficultés variées, pour situer ton niveau.</span>
                </button>
              </div>
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}

            <Button onClick={handleStart} disabled={!selectedCursus || starting} size="lg">
              {starting ? "Préparation..." : "Commencer"}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
