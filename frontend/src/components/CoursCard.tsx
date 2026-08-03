import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Lock, Unlock } from "lucide-react"

import type { Cours } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

interface CoursCardProps {
  cours: Cours
  className?: string
  style?: CSSProperties
}

export function CoursCard({ cours, className, style }: CoursCardProps) {
  return (
    <Link
      to={cours.has_access ? `/cours/${cours.id}/lire` : `/cours/${cours.id}`}
      className={className}
      style={style}
    >
      <Card className="group h-full overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
        <CardContent className="flex flex-col gap-2 p-4">
          <h2 className="line-clamp-2 font-display font-medium leading-snug">
            {cours.titre}
          </h2>
          <div className="flex flex-wrap items-center gap-1.5">
            <Badge variant="secondary">{cours.subject.label}</Badge>
            {cours.cursus.length > 0 ? (
              formatCursusGroups(cours.cursus).map((group) => (
                <Badge key={group.key} variant="outline">{group.label}</Badge>
              ))
            ) : (
              <Badge variant="outline">Toutes séries</Badge>
            )}
            {cours.duree_estimee_min && <Badge variant="outline">{cours.duree_estimee_min} min</Badge>}
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
            {cours.has_access ? (
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
            {cours.is_read && (
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
