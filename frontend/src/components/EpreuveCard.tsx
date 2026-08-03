import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Lock, Unlock } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

interface EpreuveCardProps {
  epreuve: Epreuve
  className?: string
  style?: CSSProperties
}

export function EpreuveCard({ epreuve, className, style }: EpreuveCardProps) {
  return (
    <Link
      to={epreuve.has_access ? `/epreuves/${epreuve.slug}/lire` : `/epreuves/${epreuve.slug}`}
      className={className}
      style={style}
    >
      <Card className="group h-full overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
        <CardContent className="flex flex-col gap-2 p-4">
          <div className="flex items-start justify-between gap-2">
            <h2 className="line-clamp-2 font-display font-medium leading-snug">
              {epreuve.title}
            </h2>
            <Badge variant={epreuve.lesson_type === "SUJET" ? "gold" : "outline"} className="shrink-0">
              {epreuve.lesson_type_display}
            </Badge>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            <Badge variant="secondary">{epreuve.subject.label}</Badge>
            {formatCursusGroups(epreuve.cursus).map((group) => (
              <Badge key={group.key} variant="outline">{group.label}</Badge>
            ))}
            {epreuve.year && <Badge variant="outline">{epreuve.year}</Badge>}
            {epreuve.origine !== "OFFICIEL" && (
              <Badge variant="outline">
                {epreuve.origine_display}
                {epreuve.etablissement ? ` - ${epreuve.etablissement}` : ""}
              </Badge>
            )}
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
            {epreuve.has_access ? (
              <>
                <Unlock className="size-3.5 text-success" />
                Accès inclus dans ton abonnement
              </>
            ) : (
              <>
                <Lock className="size-3.5" />
                Abonnement requis
              </>
            )}
            {epreuve.is_read && (
              <>
                <span aria-hidden="true">·</span>
                <CheckCircle2 className="size-3.5 text-success" />
                Lu
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
