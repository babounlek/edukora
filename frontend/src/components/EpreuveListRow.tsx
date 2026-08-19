import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Crown, Lock, Unlock } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { epreuveDetailPath, epreuveInediteDetailPath, epreuveReaderPath } from "@/lib/countryPath"

interface EpreuveListRowProps {
  epreuve: Epreuve
  className?: string
  style?: CSSProperties
}

/** Variante compacte d'EpreuveCard - une ligne par épreuve, pour scanner plus de
 * résultats à l'écran sans dérouler autant que la grille de cartes. */
export function EpreuveListRow({ epreuve, className, style }: EpreuveListRowProps) {
  const country = epreuve.subject.country.code.toLowerCase()
  const to =
    epreuve.kind === "inedite"
      ? epreuveInediteDetailPath(country, epreuve.slug ?? epreuve.id)
      : epreuve.has_access
        ? epreuveReaderPath(country, epreuve.slug as string)
        : epreuveDetailPath(country, epreuve.slug as string)
  return (
    <Link
      to={to}
      className={cn(
        "flex items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:border-primary/50 hover:bg-accent",
        // Même signal "premium" que sur EpreuveCard (voir son commentaire) - cette
        // variante liste ne doit pas perdre la distinction en passant en vue compacte.
        epreuve.kind === "inedite" && "border-gold/40 hover:border-gold/70",
        className,
      )}
      style={style}
    >
      <div className="flex min-w-0 flex-1 items-baseline gap-2">
        <h3 className="truncate font-display text-sm font-medium">{epreuve.title}</h3>
        {epreuve.year && <span className="shrink-0 text-xs text-muted-foreground">{epreuve.year}</span>}
      </div>
      <div className="flex shrink-0 items-center gap-1.5">
        {epreuve.est_vitrine && <Badge variant="success">Gratuit</Badge>}
        <Badge variant="secondary" className="hidden sm:inline-flex">{epreuve.subject.label}</Badge>
        {epreuve.nature_epreuve_display && (
          <Badge variant="outline" className="hidden sm:inline-flex">{epreuve.nature_epreuve_display}</Badge>
        )}
        {epreuve.kind === "inedite" ? (
          <Badge variant="gold" className="hidden items-center gap-1 sm:inline-flex">
            <Crown className="size-3" />
            Épreuve inédite
          </Badge>
        ) : (
          <Badge variant={epreuve.lesson_type === "SUJET" ? "gold" : "outline"} className="hidden sm:inline-flex">
            {epreuve.lesson_type_display}
          </Badge>
        )}
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
