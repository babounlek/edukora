import { cn } from "@/lib/utils"

export type CauseCode = "TEMPS" | "CONNAISSANCE" | "METHODE" | "CALCUL" | "INATTENTION"

const CAUSES: { code: CauseCode; label: string }[] = [
  { code: "CONNAISSANCE", label: "Notion à revoir" },
  { code: "METHODE", label: "Erreur de méthode" },
  { code: "CALCUL", label: "Erreur de calcul" },
  { code: "INATTENTION", label: "Inattention à l'énoncé" },
  { code: "TEMPS", label: "Manque de temps" },
]

// Une question laissée de côté ne relève que de deux causes : le temps, ou la notion.
const CAUSES_NON_TRAITEE = CAUSES.filter((c) => c.code === "TEMPS" || c.code === "CONNAISSANCE")

interface CausePerteProps {
  valeur: string
  // Question non traitée : moins de choix, une autre formulation.
  nonTraitee?: boolean
  onChoisir: (cause: CauseCode | "") => void
}

/**
 * « Pourquoi as-tu perdu des points ici ? » - facultatif, deux clics au plus. Chaque réponse
 * nourrit le rapport de fin d'épreuve (voir InediteResultPage) : savoir qu'on perd ses points
 * par erreurs de calcul plutôt que par ignorance change ce qu'on révise. Cliquer sur la cause
 * déjà choisie l'efface : on ne reste jamais coincé sur un clic malheureux.
 */
export function CausePerte({ valeur, nonTraitee, onChoisir }: CausePerteProps) {
  const choix = nonTraitee ? CAUSES_NON_TRAITEE : CAUSES
  return (
    <fieldset className="rounded-xl border border-dashed border-border px-3 py-2.5">
      <legend className="px-1 text-xs font-medium text-muted-foreground">
        {nonTraitee ? "Pourquoi ne l'as-tu pas traitée ? (facultatif)" : "Pourquoi as-tu perdu des points ? (facultatif)"}
      </legend>
      <div className="flex flex-wrap gap-1.5">
        {choix.map(({ code, label }) => (
          <button
            key={code}
            type="button"
            aria-pressed={valeur === code}
            onClick={() => onChoisir(valeur === code ? "" : code)}
            className={cn(
              "min-h-9 rounded-full border px-3 text-sm transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
              valeur === code ? "border-primary bg-primary/10 font-medium" : "border-border hover:bg-accent/40",
            )}
          >
            {label}
          </button>
        ))}
      </div>
    </fieldset>
  )
}
