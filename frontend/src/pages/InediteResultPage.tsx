import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { Trophy } from "lucide-react"

import { completeTentative } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { TentativeInediteResult } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDuration } from "@/lib/duration"
import { useSeo } from "@/lib/seo"
import { epreuvesListPath } from "@/lib/countryPath"
import { capitaliserTheme } from "@/lib/utils"

export function InediteResultPage() {
  useSeo({ title: "Résultat de l'épreuve inédite" })

  const { id } = useParams<{ id: string }>()
  const [result, setResult] = useState<TentativeInediteResult | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!id) return
    // Endpoint idempotent : si la tentative est déjà soumise, il se contente de
    // retourner le résultat déjà calculé (voir inedit.views.complete_tentative).
    completeTentative(Number(id))
      .then(setResult)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger ce résultat.")
      })
  }, [id])

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link
          to={result ? `${epreuvesListPath(result.country.toLowerCase())}?origine=INEDITE` : "/"}
          className="mt-3 inline-block text-sm text-primary hover:underline"
        >
          Retour au catalogue
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

  return (
    <div className="mx-auto max-w-xl animate-fade-up px-4 py-10">
      <div className="mb-8 text-center">
        <Trophy className="mx-auto mb-3 size-8 text-gold" />
        <h1 className="font-display text-3xl font-semibold">Épreuve terminée !</h1>
        <p className="mt-2 text-muted-foreground">
          {result.score !== null
            ? `${result.score}% de bonnes réponses (${result.questions_repondues} / ${result.total_questions} questions répondues)`
            : `${result.questions_repondues} / ${result.total_questions} questions répondues`}
        </p>
        {result.temps_total_secondes !== null && (
          <p className="mt-1 text-sm text-muted-foreground">
            Temps utilisé : {formatDuration(result.temps_total_secondes)}
          </p>
        )}
      </div>

      {result.par_theme.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">Résultat par compétence</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-3">
              {result.par_theme.map((theme) => (
                <li key={theme.theme} className="flex items-center justify-between text-sm">
                  <span>{capitaliserTheme(theme.theme)}</span>
                  <span className="text-muted-foreground">
                    {theme.reussies} / {theme.total}
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <div className="flex flex-col gap-2 sm:flex-row">
        <Button asChild className="flex-1" size="lg">
          <Link to={`${epreuvesListPath(result.country.toLowerCase())}?origine=INEDITE`}>
            Voir les épreuves inédites
          </Link>
        </Button>
        <Button asChild variant="outline" className="flex-1" size="lg">
          <Link to="/parcours">Voir mon parcours</Link>
        </Button>
      </div>
    </div>
  )
}
