import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { ArrowRight } from "lucide-react"

type CalloutVariant = "piege" | "conseil" | "rappel"

interface CalloutProps {
  variant: CalloutVariant
  children?: ReactNode
  coursHrefs?: string[]
}

const STYLES: Record<CalloutVariant, { icon: string; title: string; className: string }> = {
  piege: { icon: "⚠️", title: "Piège à éviter", className: "border-warning bg-warning/10" },
  conseil: { icon: "💡", title: "Conseil", className: "border-primary bg-accent" },
  rappel: { icon: "📖", title: "Rappel de méthode", className: "border-info bg-info/10" },
}

/** Encadré distinct pour les blocs "Piège à éviter" / "Conseil" / "Rappel de méthode" produits par correction-experte. */
export function Callout({ variant, children, coursHrefs }: CalloutProps) {
  const { icon, title, className } = STYLES[variant]

  return (
    <div className={`not-prose my-4 rounded-lg border-l-4 px-4 py-3 text-sm leading-relaxed text-foreground ${className}`}>
      <p className="mb-1 flex items-center gap-1.5 font-semibold">
        <span aria-hidden="true">{icon}</span>
        {title}
      </p>
      <div>{children}</div>
      {coursHrefs && coursHrefs.length > 0 && (
        <div className="mt-2 flex flex-col items-start gap-1">
          {coursHrefs.map((href) => (
            <Link key={href} to={href} className="flex items-center gap-1 font-medium text-primary hover:underline">
              Voir le cours complet
              <ArrowRight className="size-3.5" />
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
