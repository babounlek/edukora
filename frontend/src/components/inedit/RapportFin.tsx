import type { ComparaisonCandidats, PertesParCause, TempsExercice } from "@/api/types"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { formatPoints } from "@/lib/notation"
import { cn } from "@/lib/utils"

/** « 42 min », « 1 h 05 » - un temps de travail, jamais des secondes brutes. */
function formatMinutes(secondes: number): string {
  const minutes = Math.round(secondes / 60)
  if (minutes < 60) return `${minutes} min`
  return `${Math.floor(minutes / 60)} h ${String(minutes % 60).padStart(2, "0")}`
}

/**
 * « Où sont passés tes points » : ce que la note seule ne dit pas. Les points perdus par
 * manque de temps, par erreur de calcul ou par ignorance ne se rattrapent pas de la même
 * façon - c'est cette répartition, plus que le total, qui dit quoi travailler.
 */
export function CartePertes({ pertes }: { pertes: PertesParCause }) {
  if (pertes.causes.length === 0) {
    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="font-display text-lg">Où sont passés tes points</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Tu n'as perdu aucun point sur cette épreuve. Bravo.</p>
        </CardContent>
      </Card>
    )
  }
  const nonPrecisees = pertes.causes.find((c) => c.cause === "NON_PRECISEE")
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="font-display text-lg">Où sont passés tes points</CardTitle>
        <p className="text-xs text-muted-foreground">Tu as perdu {formatPoints(pertes.total_perdu)} points, répartis ainsi.</p>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-4">
          {pertes.causes.map((cause) => (
            <li key={cause.cause}>
              <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                <span>{cause.libelle}</span>
                <span className="shrink-0 tabular-nums text-muted-foreground">
                  {formatPoints(cause.points)} pts · {cause.part} %
                </span>
              </div>
              <div
                role="progressbar"
                aria-label={cause.libelle}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={cause.part}
                className="h-2 overflow-hidden rounded-full bg-secondary"
              >
                <div className="h-full rounded-full bg-primary" style={{ width: `${cause.part}%` }} />
              </div>
            </li>
          ))}
        </ul>
        {nonPrecisees && nonPrecisees.part >= 30 && (
          <p className="mt-4 text-xs text-muted-foreground">
            Une bonne part de tes points perdus n'a pas de cause. En revoyant ta copie corrigée, précise pourquoi sous
            chaque question : ce rapport devient alors beaucoup plus utile.
          </p>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * « Ton temps » : le temps passé sur chaque exercice face aux points qu'il rapportait. Une
 * estimation (elle vient des moments où les questions ont été cochées), présentée comme telle.
 */
export function CarteTemps({ temps, chronophage }: { temps: TempsExercice[]; chronophage: string | null }) {
  const pire = chronophage ? temps.find((t) => t.numero_exercice === chronophage) : null
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="font-display text-lg">Ton temps</CardTitle>
        <p className="text-xs text-muted-foreground">Estimé d'après les moments où tu as coché tes questions.</p>
      </CardHeader>
      <CardContent>
        <ul className="flex flex-col gap-4">
          {temps.map((ligne) => (
            <li key={ligne.numero_exercice}>
              <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                <span className={cn(ligne.numero_exercice === chronophage && "font-semibold")}>
                  Exercice {ligne.numero_exercice}
                </span>
                <span className="shrink-0 tabular-nums text-muted-foreground">
                  {formatMinutes(ligne.secondes)} · {ligne.part_du_temps} % du temps
                </span>
              </div>
              {/* Deux barres superposées : le temps consommé, et - en repère - la part des points. */}
              <div className="relative h-2 overflow-hidden rounded-full bg-secondary" aria-hidden="true">
                <div className="h-full rounded-full bg-primary/80" style={{ width: `${ligne.part_du_temps}%` }} />
                <div
                  className="absolute inset-y-0 w-0.5 bg-foreground/70"
                  style={{ left: `${Math.min(ligne.part_des_points, 99)}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-muted-foreground">Vaut {ligne.part_des_points} % des points</p>
            </li>
          ))}
        </ul>
        {pire && (
          <p className="mt-4 rounded-lg bg-warning/10 px-3 py-2 text-sm">
            L'exercice {pire.numero_exercice} a pris {pire.part_du_temps} % de ton temps pour {pire.part_des_points} % des
            points. La prochaine fois, fixe-toi une limite de temps par exercice et passe au suivant.
          </p>
        )}
      </CardContent>
    </Card>
  )
}

/** « Ta position » : parmi les autres candidats de la même épreuve en conditions réelles. */
export function CartePosition({ comparaison }: { comparaison: ComparaisonCandidats }) {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="font-display text-lg">Ta position</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm">
          Tu fais mieux que <strong className="tabular-nums">{comparaison.percentile} %</strong> des candidats qui ont
          passé cette épreuve en conditions réelles.
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          {comparaison.effectif} candidats · note moyenne {formatPoints(comparaison.moyenne)}. Comparaison anonyme, sur la
          meilleure note de chacun.
        </p>
      </CardContent>
    </Card>
  )
}
