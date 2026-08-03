import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Lock, Unlock } from "lucide-react"

import type { Cours } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface CoursListRowProps {
  cours: Cours
  className?: string
  style?: CSSProperties
}

/** Variante compacte de CoursCard - une ligne par cours, pour scanner plus de
 * résultats à l'écran sans dérouler autant que la grille de cartes. */
export function CoursListRow({ cours, className, style }: CoursListRowProps) {
  return (
    <Link
      to={cours.has_access ? `/cours/${cours.id}/lire` : `/cours/${cours.id}`}
      className={cn(
        "flex items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:border-primary/50 hover:bg-accent",
        className,
      )}
      style={style}
    >
      <div className="flex min-w-0 flex-1 items-baseline gap-2">
        <h2 className="truncate font-display text-sm font-medium">{cours.titre}</h2>
        {cours.duree_estimee_min && (
          <span className="shrink-0 text-xs text-muted-foreground">{cours.duree_estimee_min} min</span>
        )}
      </div>
      <div className="flex shrink-0 items-center gap-1.5">
        <Badge variant="secondary" className="hidden sm:inline-flex">{cours.subject.label}</Badge>
        {cours.has_access ? (
          <Unlock className="size-3.5 shrink-0 text-success" />
        ) : (
          <Lock className="size-3.5 shrink-0 text-muted-foreground" />
        )}
        {cours.is_read && <CheckCircle2 className="size-3.5 shrink-0 text-success" />}
      </div>
    </Link>
  )
}
