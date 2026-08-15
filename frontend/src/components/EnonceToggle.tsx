import { useState, type ReactNode } from "react"
import { ChevronDown, ChevronRight } from "lucide-react"

interface EnonceToggleProps {
  children?: ReactNode
}

/**
 * Replie l'énoncé d'un exercice dans le corrigé lu en ligne - fermé par défaut :
 * l'élève arrive directement sur la correction (ce qu'il est venu lire), l'énoncé
 * reste à un clic pour qui veut se remettre le problème en tête sans changer de page
 * (voir l'audit UX, reco sur la répétition énoncé/corrigé).
 */
export function EnonceToggle({ children }: EnonceToggleProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="not-prose my-4 rounded-lg border border-border">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center gap-1.5 px-3.5 py-2.5 text-left text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
      >
        {open ? <ChevronDown className="size-3.5 shrink-0" /> : <ChevronRight className="size-3.5 shrink-0" />}
        {open ? "Masquer l'énoncé" : "Voir l'énoncé"}
      </button>
      {open && (
        <div className="prose prose-neutral max-w-none border-t border-border px-3.5 py-3 text-justify dark:prose-invert">
          {children}
        </div>
      )}
    </div>
  )
}
