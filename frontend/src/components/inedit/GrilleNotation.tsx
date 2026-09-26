import { Minus, Plus } from "lucide-react"

import type { TentativeInediteQuestion } from "@/api/types"
import { arrondiQuart, formatPoints, libellePoints, pointsDuNiveau } from "@/lib/notation"
import { cn } from "@/lib/utils"

interface GrilleNotationProps {
  question: TentativeInediteQuestion
  onCriteres: (indices: number[]) => void
  onPoints: (points: number) => void
}

const NIVEAUX = [
  { cle: "echec", label: "Échec" },
  { cle: "partiel", label: "Partiel" },
  { cle: "reussi", label: "Réussi" },
] as const

/**
 * Auto-notation d'une question ouverte, affichée sous le corrigé une fois la question
 * traitée. Deux formes :
 * - avec une grille (QuestionInedite.criteres_notation) : l'élève coche ce qu'il a obtenu,
 *   comme un correcteur - plus objectif que trois boutons, et il apprend à quoi sont
 *   attribués les points ;
 * - sans grille (le cas de tout le corpus actuel) : trois niveaux rapides, plus un réglage
 *   fin par quarts de point.
 * Composant contrôlé : l'état vit dans la question (mise à jour optimiste par la page).
 */
export function GrilleNotation({ question, onCriteres, onPoints }: GrilleNotationProps) {
  const criteres = question.criteres_notation ?? []
  const notee = question.reponse?.notee === true
  const obtenus = question.reponse?.points_obtenus ?? 0
  const legende = (
    <legend className="px-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
      Note ta réponse
    </legend>
  )

  if (criteres.length > 0) {
    const coches = question.reponse?.criteres_valides ?? []
    const basculer = (indice: number) =>
      onCriteres(coches.includes(indice) ? coches.filter((i) => i !== indice) : [...coches, indice])

    return (
      <fieldset className="rounded-xl border border-border bg-card px-3 py-2.5 sm:px-4">
        {legende}
        <ul className="flex flex-col">
          {criteres.map((critere, indice) => (
            <li key={indice}>
              <label className="flex min-h-11 cursor-pointer items-start gap-3 rounded-lg px-2 py-2.5 transition-colors hover:bg-accent/40 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-ring/50">
                <input
                  type="checkbox"
                  className="mt-0.5 size-5 shrink-0 accent-primary"
                  checked={coches.includes(indice)}
                  onChange={() => basculer(indice)}
                />
                <span className="flex-1 text-sm">{critere.libelle}</span>
                <span className="shrink-0 text-sm tabular-nums text-muted-foreground">
                  +{formatPoints(critere.points)}
                </span>
              </label>
            </li>
          ))}
        </ul>
        <div className="mt-1 flex items-center justify-between gap-3 border-t border-border px-2 pt-2.5">
          {notee ? (
            <span className="text-sm font-semibold">Total</span>
          ) : (
            <button
              type="button"
              onClick={() => onCriteres([])}
              className="min-h-9 rounded-md text-sm text-primary underline-offset-2 hover:underline focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none"
            >
              Je n'ai validé aucun critère
            </button>
          )}
          <span aria-live="polite" className="text-sm font-semibold tabular-nums">
            {notee ? `${formatPoints(obtenus)} / ${formatPoints(question.points)} pts` : `? / ${formatPoints(question.points)} pts`}
          </span>
        </div>
      </fieldset>
    )
  }

  const pas = 0.25
  const regler = (valeur: number) => onPoints(Math.min(question.points, Math.max(0, arrondiQuart(valeur))))

  return (
    <fieldset className="rounded-xl border border-border bg-card px-3 py-3 sm:px-4">
      {legende}
      <div className="grid grid-cols-3 gap-2">
        {NIVEAUX.map(({ cle, label }) => {
          const points = pointsDuNiveau(cle, question.points)
          const actif = notee && Math.abs(obtenus - points) < 0.001
          return (
            <button
              key={cle}
              type="button"
              aria-pressed={actif}
              onClick={() => onPoints(points)}
              className={cn(
                "flex min-h-14 flex-col items-center justify-center rounded-xl border px-2 py-2 text-sm transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
                actif
                  ? cle === "reussi"
                    ? "border-success bg-success/10 text-foreground"
                    : cle === "echec"
                      ? "border-destructive bg-destructive/10 text-foreground"
                      : "border-warning bg-warning/10 text-foreground"
                  : "border-border hover:bg-accent/40",
              )}
            >
              <span className="font-medium">{label}</span>
              <span className="text-xs tabular-nums text-muted-foreground">
                {cle === "echec" ? "0 pt" : libellePoints(points)}
              </span>
            </button>
          )
        })}
      </div>
      <div className="mt-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between sm:gap-3">
        <span className="text-xs text-muted-foreground">
          {notee ? "Ajuster au quart de point" : "Choisis un niveau, puis ajuste si besoin"}
        </span>
        <div className="flex items-center gap-1" role="group" aria-label="Points obtenus">
          <button
            type="button"
            aria-label="Retirer un quart de point"
            disabled={!notee || obtenus <= 0}
            onClick={() => regler(obtenus - pas)}
            className="grid size-11 place-items-center rounded-lg border border-border transition-colors hover:bg-accent/40 focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none disabled:opacity-40"
          >
            <Minus className="size-4" />
          </button>
          <span aria-live="polite" className="min-w-24 text-center text-sm font-semibold tabular-nums">
            {notee ? `${formatPoints(obtenus)} / ${formatPoints(question.points)} pts` : `— / ${formatPoints(question.points)} pts`}
          </span>
          <button
            type="button"
            aria-label="Ajouter un quart de point"
            disabled={!notee || obtenus >= question.points}
            onClick={() => regler(obtenus + pas)}
            className="grid size-11 place-items-center rounded-lg border border-border transition-colors hover:bg-accent/40 focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none disabled:opacity-40"
          >
            <Plus className="size-4" />
          </button>
        </div>
      </div>
    </fieldset>
  )
}
