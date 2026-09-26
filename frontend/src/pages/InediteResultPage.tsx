import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ClipboardCheck, Info, Trophy } from "lucide-react"

import { completeTentative } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { TentativeInediteResult } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDuration } from "@/lib/duration"
import { formatPoints } from "@/lib/notation"
import { useSeo } from "@/lib/seo"
import { epreuvesListPath } from "@/lib/countryPath"
import { capitaliserTheme, cn } from "@/lib/utils"

/** Barre « points obtenus / points possibles » : la couleur suit le taux, pas le libellé -
 * un thème à 30 % doit se voir sans qu'on lise les chiffres. */
function BarrePoints({ obtenus, possibles, label }: { obtenus: number; possibles: number; label: string }) {
  const taux = possibles > 0 ? obtenus / possibles : 0
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={possibles}
      aria-valuenow={obtenus}
      className="h-2 overflow-hidden rounded-full bg-secondary"
    >
      <div
        className={cn("h-full rounded-full transition-all", taux >= 0.7 ? "bg-success" : taux >= 0.5 ? "bg-primary" : "bg-warning")}
        style={{ width: `${Math.round(taux * 100)}%` }}
      />
    </div>
  )
}

/** « aujourd'hui », « demain », « dans 3 jours » - jamais une date brute. */
function echeanceRelative(iso: string): string {
  const [annee, mois, jour] = iso.split("-").map(Number)
  const debutAujourdhui = new Date()
  debutAujourdhui.setHours(0, 0, 0, 0)
  const jours = Math.round((new Date(annee, mois - 1, jour).getTime() - debutAujourdhui.getTime()) / 86_400_000)
  if (jours <= 0) return "aujourd'hui"
  if (jours === 1) return "demain"
  return `dans ${jours} jours`
}

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

  const surVingt = result.bareme === 20
  // Du plus fragile au plus solide : c'est ce qu'on veut retravailler qui doit sauter aux yeux.
  const themes = [...result.par_theme].sort((a, b) => {
    const tauxA = a.points_possibles ? (a.points_obtenus ?? 0) / a.points_possibles : 1
    const tauxB = b.points_possibles ? (b.points_obtenus ?? 0) / b.points_possibles : 1
    return tauxA - tauxB
  })

  return (
    <div className="mx-auto max-w-xl animate-fade-up px-4 py-10">
      <div className="mb-8 text-center">
        <Trophy className="mx-auto mb-3 size-8 text-gold-text" />
        <h1 className="font-display text-3xl font-semibold">Épreuve terminée !</h1>

        {result.note !== null && result.bareme !== null && (
          <>
            <p className="mt-5 font-display text-6xl font-semibold tabular-nums" aria-label={`Note : ${formatPoints(result.note)} sur ${formatPoints(result.bareme)}`}>
              {formatPoints(result.note)}
              <span className="text-2xl font-normal text-muted-foreground"> / {formatPoints(result.bareme)}</span>
            </p>
            {!surVingt && result.note_sur_20 !== null && (
              <p className="mt-1 text-sm text-muted-foreground">
                soit <strong className="tabular-nums">{formatPoints(result.note_sur_20)} / 20</strong>
              </p>
            )}
            <p className="mt-2 text-sm font-medium">
              {result.definitive ? "Note définitive" : "Note provisoire"}
              {result.score !== null && <span className="font-normal text-muted-foreground"> · {result.score} % du barème</span>}
            </p>
          </>
        )}

        <p className="mt-3 text-sm text-muted-foreground">
          {result.questions_repondues} question{result.questions_repondues > 1 ? "s" : ""} traitée{result.questions_repondues > 1 ? "s" : ""} sur{" "}
          {result.total_questions}
          {result.temps_total_secondes !== null && <> · Temps utilisé : {formatDuration(result.temps_total_secondes)}</>}
        </p>
      </div>

      {result.questions_a_noter > 0 && (
        <div role="status" className="mb-6 rounded-xl border border-primary/30 bg-primary/5 px-4 py-3.5">
          <p className="flex items-start gap-2 text-sm">
            <ClipboardCheck className="mt-0.5 size-5 shrink-0 text-primary" />
            <span>
              <strong>Ta note est provisoire.</strong> Il te reste {result.questions_a_noter} question
              {result.questions_a_noter > 1 ? "s" : ""} traitée{result.questions_a_noter > 1 ? "s" : ""} à noter avec le corrigé.
            </span>
          </p>
          <Button asChild className="mt-3 w-full" size="lg">
            <Link to={`/inedit/tentative/${result.id}?noter=1`}>Terminer ma notation</Link>
          </Button>
        </div>
      )}

      {result.questions_non_traitees > 0 && (
        <p className="mb-6 flex items-start gap-2 text-sm text-muted-foreground">
          <Info className="mt-0.5 size-4 shrink-0" />
          <span>
            {result.questions_non_traitees} question{result.questions_non_traitees > 1 ? "s" : ""} non traitée
            {result.questions_non_traitees > 1 ? "s ont" : " a"} compté 0 point : la note porte sur l'ensemble du barème,
            comme à l'examen.
          </span>
        </p>
      )}

      {result.par_exercice.length > 1 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">Résultat par exercice</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-4">
              {result.par_exercice.map((exercice) => (
                <li key={exercice.numero_exercice}>
                  <div className="mb-1.5 flex items-center justify-between text-sm">
                    <span>Exercice {exercice.numero_exercice}</span>
                    <span className="tabular-nums text-muted-foreground">
                      {formatPoints(exercice.points_obtenus)} / {formatPoints(exercice.points_possibles)}
                    </span>
                  </div>
                  <BarrePoints
                    obtenus={exercice.points_obtenus ?? 0}
                    possibles={exercice.points_possibles ?? 0}
                    label={`Exercice ${exercice.numero_exercice}`}
                  />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {themes.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">Résultat par compétence</CardTitle>
            <p className="text-xs text-muted-foreground">De la plus fragile à la plus solide.</p>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-4">
              {themes.map((theme) => (
                <li key={theme.theme}>
                  <div className="mb-1.5 flex items-start justify-between gap-3 text-sm">
                    <span>{capitaliserTheme(theme.theme)}</span>
                    <span className="shrink-0 tabular-nums text-muted-foreground">
                      {formatPoints(theme.points_obtenus)} / {formatPoints(theme.points_possibles)} pts
                    </span>
                  </div>
                  <BarrePoints
                    obtenus={theme.points_obtenus ?? 0}
                    possibles={theme.points_possibles ?? 0}
                    label={capitaliserTheme(theme.theme)}
                  />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {result.themes_a_reviser.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="font-display text-lg">Ce que tu reverras</CardTitle>
            <p className="text-xs text-muted-foreground">
              Ces thèmes reviennent dans ta séance du jour, pour qu'ils tiennent jusqu'à l'examen.
            </p>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-2">
              {result.themes_a_reviser.map((theme) => (
                <li key={theme.theme} className="flex items-center justify-between gap-3 text-sm">
                  <span>{capitaliserTheme(theme.theme)}</span>
                  <span className="shrink-0 text-muted-foreground">{echeanceRelative(theme.echeance)}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {result.bareme_estime && (
        <p className="mb-6 flex items-start gap-2 text-xs text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" />
          Barème estimé : les points de chaque exercice sont répartis à parts égales entre ses questions.
        </p>
      )}

      <div className="flex flex-col gap-2">
        <Button asChild size="lg">
          <Link to={`/inedit/tentative/${result.id}`}>Revoir ma copie corrigée</Link>
        </Button>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button asChild variant="outline" className="flex-1" size="lg">
            <Link to={`${epreuvesListPath(result.country.toLowerCase())}?origine=INEDITE`}>Voir les épreuves inédites</Link>
          </Button>
          <Button asChild variant="outline" className="flex-1" size="lg">
            <Link to="/parcours">Voir mon parcours</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
