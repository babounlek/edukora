import { useState, type ReactNode } from "react"
import { Eye, EyeOff } from "lucide-react"

interface SolutionToggleProps {
  children?: ReactNode
}

/**
 * Masque la solution d'un exercice d'auto-évaluation derrière un bouton, pour que
 * l'élève cherche avant de la voir.
 *
 * Pas de `not-prose` sur le conteneur : il désactivait la typographie pour tout le
 * sous-arbre, y compris le `prose` de la solution révélée, qu'un `prose` imbriqué ne
 * réactive jamais (voir l'explication détaillée dans CoursRegleBox) - la solution
 * s'affichait donc sans marges ni puces partout, aussi bien dans les "Exercices
 * d'application" d'un Cours que dans un corrigé d'épreuve. Rien à protéger côté
 * habillage : @tailwindcss/typography ne cible ni les `div`, ni les `button`, ni les
 * `svg` (mesuré), le bouton garde donc son style intact même sous un article `prose`.
 */
export function SolutionToggle({ children }: SolutionToggleProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="my-4">
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
