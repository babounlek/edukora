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
 *
 * Pas de `not-prose` sur le conteneur : il désactivait la typographie pour tout le
 * sous-arbre, y compris le `prose` de l'énoncé déplié, qu'un `prose` imbriqué ne
 * réactive jamais (voir l'explication détaillée dans CoursRegleBox). Rien à protéger
 * côté habillage : @tailwindcss/typography ne cible ni les `div`, ni les `button`, ni
 * les `svg` (mesuré), le bouton garde son style intact sous l'article `prose` du
 * lecteur d'épreuve.
 */
export function EnonceToggle({ children }: EnonceToggleProps) {
  const [open, setOpen] = useState(false)

  return (
    <div className="my-4 rounded-lg border border-border">
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
