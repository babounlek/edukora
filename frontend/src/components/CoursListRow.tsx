import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Clock, ListChecks, Lock, Unlock } from "lucide-react"

import type { Cours } from "@/api/types"
import { Badge } from "@/components/ui/badge"
import { capitaliserTheme, cn } from "@/lib/utils"
import { coursDetailPath, coursReaderPath } from "@/lib/countryPath"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"

interface CoursListRowProps {
  cours: Cours
  className?: string
  style?: CSSProperties
}

/** Variante compacte de CoursCard - une ligne par cours, pour scanner plus de
 * résultats à l'écran sans dérouler autant que la grille de cartes. */
export function CoursListRow({ cours, className, style }: CoursListRowProps) {
  const SubjectIcon = subjectIcon(cours.subject.code)

  return (
    <Link
      to={cours.has_access ? coursReaderPath(cours.slug) : coursDetailPath(cours.slug)}
      className={cn(
        "flex items-center justify-between gap-3 rounded-lg border border-border bg-card px-4 py-3 transition-colors hover:border-primary/50 hover:bg-accent",
        className,
      )}
      style={style}
    >
      <div className="flex min-w-0 flex-1 items-center gap-3">
        <div className={cn("flex size-9 shrink-0 items-center justify-center rounded-lg", couleurMatiere(cours.subject.code).puce)}>
          <SubjectIcon className="size-4" aria-hidden="true" />
        </div>
        {/* Le chapitre (sous_theme) passe sur une seconde ligne plutôt que d'être
            omis : deux cours d'une même matière portent souvent des titres proches,
            c'est lui qui les distingue au survol de la liste. */}
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-display text-sm font-medium">{cours.titre}</h3>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            {cours.sous_theme && <span className="truncate">{capitaliserTheme(cours.sous_theme)}</span>}
            {cours.duree_estimee_min && (
              <span className="flex shrink-0 items-center gap-0.5">
                <Clock className="size-3" />
                {cours.duree_estimee_min} min
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-1.5">
        {cours.is_read && (
          <span className="hidden items-center gap-1 rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-success sm:inline-flex">
            <CheckCircle2 className="size-3" />
            Lu
          </span>
        )}
        <Badge variant="secondary" className="hidden sm:inline-flex">
          {cours.subject.label}
        </Badge>
        {cours.apercu_contenu.exercices_count > 0 && (
          <span className="hidden items-center gap-0.5 text-xs text-muted-foreground sm:inline-flex">
            <ListChecks className="size-3" />
            {cours.apercu_contenu.exercices_count}
          </span>
        )}
        {cours.has_access ? (
          <Unlock className="size-3.5 shrink-0 text-success" aria-label="Accès inclus dans ton abonnement" />
        ) : (
          <Lock className="size-3.5 shrink-0 text-muted-foreground" aria-label="Abonnement requis" />
        )}
        {/* Repli mobile du badge "Lu" masqué ci-dessus : la coche seule tient dans la
            largeur d'un téléphone, le badge texte non. */}
        {cours.is_read && <CheckCircle2 className="size-3.5 shrink-0 text-success sm:hidden" aria-label="Déjà lu" />}
      </div>
    </Link>
  )
}
