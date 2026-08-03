import { Link } from "react-router-dom"
import { ArrowUp } from "lucide-react"

interface BackToTopBarProps {
  links: { to: string; label: string }[]
}

/**
 * Barre de navigation de fin de page (sujet/corrigé) : après avoir défilé une épreuve
 * à plusieurs exercices, remonter en haut ou revenir au catalogue ne doit pas obliger
 * à tout redéfiler - on répète ici, en pied de page, les liens déjà présents en tête.
 */
export function BackToTopBar({ links }: BackToTopBarProps) {
  return (
    <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-5 text-sm text-muted-foreground">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        {links.map((link, index) => (
          <span key={link.to} className="flex items-center gap-3">
            {index > 0 && <span aria-hidden="true">·</span>}
            <Link to={link.to} className="transition-colors hover:text-primary">
              {link.label}
            </Link>
          </span>
        ))}
      </div>
      <button
        type="button"
        onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        className="inline-flex items-center gap-1.5 transition-colors hover:text-primary"
      >
        <ArrowUp className="size-4" />
        Retour en haut
      </button>
    </div>
  )
}
