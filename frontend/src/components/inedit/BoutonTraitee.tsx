import { Check, Circle } from "lucide-react"

import { cn } from "@/lib/utils"

interface BoutonTraiteeProps {
  traitee: boolean
  // Épreuve rendue : on ne peut plus retirer une question traitée, seulement en ajouter
  // une faite sur papier (voir inedit.views.noter_question).
  rendue: boolean
  disabled?: boolean
  onToggle: () => void
}

/** « J'ai traité cette question » - le geste qui remplace la réponse rédigée : l'élève
 * compose sur brouillon ou papier, puis le déclare. Seules les questions traitées sont
 * ensuite à noter ; les autres valent zéro sans rien demander à l'élève. */
export function BoutonTraitee({ traitee, rendue, disabled, onToggle }: BoutonTraiteeProps) {
  if (traitee && rendue) {
    return (
      <span className="inline-flex min-h-9 items-center gap-1.5 text-sm font-medium text-success">
        <Check className="size-4" />
        Traitée
      </span>
    )
  }

  return (
    <button
      type="button"
      role="checkbox"
      aria-checked={traitee}
      disabled={disabled}
      onClick={onToggle}
      className={cn(
        "inline-flex min-h-11 items-center gap-2 rounded-xl border px-3.5 text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none disabled:opacity-60",
        traitee
          ? "border-success bg-success/10 text-foreground"
          : "border-border text-muted-foreground hover:bg-accent/40 hover:text-foreground",
      )}
    >
      {traitee ? <Check className="size-4 text-success" /> : <Circle className="size-4" />}
      {traitee ? "Question traitée" : rendue ? "Je l'avais faite sur papier" : "J'ai traité cette question"}
    </button>
  )
}
