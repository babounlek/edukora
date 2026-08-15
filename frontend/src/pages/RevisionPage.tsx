import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { BookOpenText, CheckCircle2, RotateCcw } from "lucide-react"

import { listRevisionsDues, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { RevisionDue } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { coursDetailPath, coursReaderPath } from "@/lib/countryPath"

/**
 * File "à réviser aujourd'hui" (voir GET /quiz/revisions/, quiz.services.revisions_dues
 * côté backend) : un thème par carte, remonté ici uniquement parce que l'élève l'a déjà
 * raté en Quiz - jamais un simple aiguillon générique. Chaque carte propose de le
 * retravailler tout de suite, en quiz ciblé et/ou via un cours déjà publié sur ce thème.
 */
export function RevisionPage() {
  useSeo({
    title: "À réviser",
    description: "Les notions où tu as le plus échoué récemment, à revoir au bon moment.",
  })

  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()

  const [revisions, setRevisions] = useState<RevisionDue[] | null>(null)
  const [error, setError] = useState("")
  const [startingId, setStartingId] = useState<number | null>(null)

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/revision" } })
      return
    }
    listRevisionsDues()
      .then(setRevisions)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger tes révisions.")
      })
  }, [authLoading, isAuthenticated, navigate])

  async function handleReviser(revision: RevisionDue) {
    if (startingId) return
    setStartingId(revision.id)
    setError("")
    try {
      const session = await startQuizSession({ cursus: revision.cursus, theme: revision.theme_id, n: 10 })
      trackEvent("quiz_started", { cursus_id: revision.cursus, mode: "PRATIQUE", source: "revision" })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible de démarrer ce quiz. Réessaie plus tard.")
      setStartingId(null)
    }
  }

  if (authLoading || (!revisions && !error)) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <Skeleton className="mb-3 h-8 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    )
  }

  if (error && !revisions) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link to="/quiz" className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour au quiz
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl animate-fade-up px-4 py-10">
      <div className="mb-2 flex items-center gap-2">
        <RotateCcw className="size-6 text-primary" />
        <h1 className="font-display text-3xl font-semibold">À réviser</h1>
      </div>
      <p className="mb-8 text-muted-foreground">
        Les notions où tu as le plus échoué en quiz, reproposées au bon moment pour ne pas les oublier.
      </p>

      {revisions && revisions.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-10 text-center text-muted-foreground">
            <CheckCircle2 className="size-8 text-success" />
            <p>Rien à réviser aujourd'hui - reviens après ta prochaine séance de quiz.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="flex flex-col gap-3">
          {revisions?.map((revision) => (
            <Card key={revision.id}>
              <CardContent className="flex flex-col gap-3 pt-6">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="font-display font-medium">{revision.theme}</p>
                    <p className="text-xs text-muted-foreground">
                      {revision.subject_label} · {revision.cursus_display}
                    </p>
                  </div>
                  <Badge variant={revision.jours_retard > 0 ? "outline" : "secondary"} className="shrink-0">
                    {revision.jours_retard > 0 ? `${revision.jours_retard} j de retard` : "Aujourd'hui"}
                  </Badge>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Button size="sm" disabled={startingId !== null} onClick={() => handleReviser(revision)}>
                    {startingId === revision.id ? "Préparation..." : "Réviser en quiz"}
                  </Button>
                  {revision.cours.map((cours) => (
                    <Button key={cours.id} asChild size="sm" variant="outline">
                      <Link to={cours.has_access ? coursReaderPath(cours.slug) : coursDetailPath(cours.slug)}>
                        <BookOpenText />
                        {cours.titre}
                      </Link>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {error && <p className="mt-4 text-sm text-destructive">{error}</p>}
    </div>
  )
}
