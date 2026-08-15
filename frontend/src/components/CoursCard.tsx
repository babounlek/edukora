import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, ListChecks, Lock, Sparkles, Unlock } from "lucide-react"

import type { Cours } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { coursDetailPath, coursReaderPath } from "@/lib/countryPath"
import { subjectIcon } from "@/lib/subjectIcon"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

interface CoursCardProps {
  cours: Cours
  className?: string
  style?: CSSProperties
}

export function CoursCard({ cours, className, style }: CoursCardProps) {
  const SubjectIcon = subjectIcon(cours.subject.code)

  return (
    <Link
      to={cours.has_access ? coursReaderPath(cours.slug) : coursDetailPath(cours.slug)}
      className={className}
      style={style}
    >
      <Card className="group h-full overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5">
        <CardContent className="flex flex-col gap-2 p-4">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <SubjectIcon className="size-4.5" aria-hidden="true" />
          </div>
          <h2 className="line-clamp-2 font-display font-medium leading-snug">
            {cours.titre}
          </h2>
          {cours.sous_theme && (
            <p className="line-clamp-1 text-xs text-muted-foreground">{cours.sous_theme}</p>
          )}
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
            {cours.apercu_contenu.has_exemple_resolu && (
              <Badge variant="outline" className="gap-1">
                <Sparkles className="size-3" />
                Exemple résolu
              </Badge>
            )}
            {cours.apercu_contenu.exercices_count > 0 && (
              <Badge variant="outline" className="gap-1">
                <ListChecks className="size-3" />
                {cours.apercu_contenu.exercices_count} exercice{cours.apercu_contenu.exercices_count > 1 ? "s" : ""}
              </Badge>
            )}
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
