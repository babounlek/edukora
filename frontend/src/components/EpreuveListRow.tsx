import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Lock, Unlock } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface EpreuveListRowProps {
  epreuve: Epreuve
  className?: string
  style?: CSSProperties
}

/** Variante compacte d'EpreuveCard - une ligne par épreuve, pour scanner plus de
 * résultats à l'écran sans dérouler autant que la grille de cartes. */
export function EpreuveListRow({ epreuve, className, style }: EpreuveListRowProps) {
  return (
    <Link
      to={epreuve.has_access ? `/epreuves/${epreuve.slug}/lire` : `/epreuves/${epreuve.slug}`}
      className={cn(
        "flex items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:border-primary/50 hover:bg-accent",
        className,
      )}
      style={style}
    >
      <div className="flex min-w-0 flex-1 items-baseline gap-2">
        <h2 className="truncate font-display text-sm font-medium">{epreuve.title}</h2>
        {epreuve.year && <span className="shrink-0 text-xs text-muted-foreground">{epreuve.year}</span>}
      </div>
      <div className="flex shrink-0 items-center gap-1.5">
        <Badge variant="secondary" className="hidden sm:inline-flex">{epreuve.subject.label}</Badge>
        <Badge variant={epreuve.lesson_type === "SUJET" ? "gold" : "outline"} className="hidden sm:inline-flex">
          {epreuve.lesson_type_display}
        </Badge>
        {epreuve.has_access ? (
          <Unlock className="size-3.5 shrink-0 text-success" />
        ) : (
          <Lock className="size-3.5 shrink-0 text-muted-foreground" />
        )}
        {epreuve.is_read && <CheckCircle2 className="size-3.5 shrink-0 text-success" />}
      </div>
    </Link>
  )
}
