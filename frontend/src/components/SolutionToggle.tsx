import { useState, type ReactNode } from "react"
import { Eye, EyeOff } from "lucide-react"

interface SolutionToggleProps {
  children?: ReactNode
}

/** Masque la solution d'un exercice d'auto-évaluation derrière un bouton, pour que l'élève cherche avant de la voir. */
export function SolutionToggle({ children }: SolutionToggleProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="not-prose my-4">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm font-medium text-primary transition-colors hover:bg-accent"
      >
        {open ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
        {open ? "Masquer la solution" : "Voir la solution"}
      </button>
      {open && (
        <div className="prose prose-neutral mt-3 max-w-none text-justify border-l-2 border-border pl-4 dark:prose-invert">
          {children}
        </div>
      )}
    </div>
  )
}
