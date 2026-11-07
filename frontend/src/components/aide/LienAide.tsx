import { Link } from "react-router-dom"
import { CircleHelp } from "lucide-react"

import { cn } from "@/lib/utils"

/**
 * Un lien discret vers un article précis du centre d'aide, à poser à côté d'un message d'erreur ou d'une attente
 * (« Je ne reçois pas mon code », « Que faire d'un paiement refusé ? ») : l'élève arrive sur LA réponse, pas sur l'accueil de l'aide.
 */
export function LienAide({ slug, children, className }: { slug: string; children: React.ReactNode; className?: string }) {
  return (
    <Link
      to={`/aide/${slug}`}
      className={cn(
        "inline-flex min-h-8 items-center gap-1.5 text-sm font-medium text-primary underline underline-offset-2 hover:text-primary/80",
        className,
      )}
    >
      <CircleHelp className="size-4 shrink-0" aria-hidden="true" />
      {children}
    </Link>
  )
}
