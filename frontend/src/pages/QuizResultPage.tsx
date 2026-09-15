import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { Trophy } from "lucide-react"

import { completeQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizResult } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { QuizFichePdfButtons } from "@/components/QuizFichePdfButtons"
import { Skeleton } from "@/components/ui/skeleton"
import { useSeo } from "@/lib/seo"

export function QuizResultPage() {
  useSeo({ title: "Résultat du quiz" })

  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [result, setResult] = useState<QuizResult | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!id) return
    // Endpoint idempotent : si la session est déjà terminée, il se contente de
    // retourner le résultat déjà calculé (voir quiz.views.complete_session).
    completeQuizSession(Number(id))
      .then(setResult)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger ce résultat.")
      })
  }, [id])

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link to="/quiz" className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour au quiz
        </Link>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="mx-auto max-w-xl px-4 py-10">
        <Skeleton className="mb-4 h-8 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    )
  }

  const pourcentage = result.questions_repondues > 0 ? Math.round((result.score / result.questions_repondues) * 100) : 0

  return (
    <div className="mx-auto max-w-xl animate-fade-up px-4 py-10">
      <div className="mb-8 text-center">
        <Trophy className="mx-auto mb-3 size-8 text-gold" />
        <h1 className="font-display text-3xl font-semibold">Quiz terminé !</h1>
        <p className="mt-2 text-muted-foreground">
          {result.score} / {result.questions_repondues} bonnes réponses ({pourcentage}%)
        </p>
      </div>

      {result.par_theme.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">Résultat par thème</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-3">
              {result.par_theme.map((theme) => (
                <li key={theme.theme} className="flex items-center justify-between text-sm">
                  <span>{theme.theme}</span>
                  <span className="text-muted-foreground">
                    {theme.reussies} / {theme.total}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <div className="mb-6">
        <QuizFichePdfButtons sessionId={Number(id)} />
      </div>

      <div className="flex flex-col gap-2 sm:flex-row">
        <Button onClick={() => navigate("/quiz")} className="flex-1" size="lg">
          Refaire un quiz
        </Button>
        {result.subject && (
          <Button asChild variant="outline" className="flex-1" size="lg">
            <Link to={`/parcours/${result.subject}?cursus=${result.cursus}`}>Retour au parcours</Link>
          </Button>
        )}
        <Button asChild variant="outline" className="flex-1" size="lg">
          <Link to="/compte">Mon compte</Link>
        </Button>
      </div>
    </div>
  )
}
