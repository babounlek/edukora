import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Clock, ListChecks, Lock, Sparkles, Unlock } from "lucide-react"

import type { Cours } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { coursDetailPath, coursReaderPath } from "@/lib/countryPath"
import { subjectIcon } from "@/lib/subjectIcon"
import { capitaliserTheme } from "@/lib/utils"
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
        <CardContent className="flex h-full flex-col gap-2.5 p-4">
          <div className="flex items-start justify-between gap-2">
            <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <SubjectIcon className="size-4.5" aria-hidden="true" />
            </div>
            {/* L'état "lu" remonte en tête de carte : dans une grille où l'on repasse
                plusieurs fois, c'est le repère qu'on cherche en premier - il se
                perdait en bas au milieu de la mention d'accès. */}
            {cours.is_read && (
              <span className="flex items-center gap-1 rounded-full bg-success/10 px-2 py-0.5 text-[11px] font-medium text-success">
                <CheckCircle2 className="size-3" />
                Lu
              </span>
            )}
          </div>

          <div>
            <h3 className="line-clamp-2 font-display font-medium leading-snug">{cours.titre}</h3>
            {cours.sous_theme && (
              <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">{capitaliserTheme(cours.sous_theme)}</p>
            )}
          </div>

          {/* Deux badges au maximum - la matière et le public visé. Durée, exemple
              résolu et exercices descendent en pied de carte : ce sont des détails de
              contenu, les mettre au même poids visuel que la matière donnait six
              pastilles identiques par carte et plus aucune hiérarchie de lecture. */}
          <div className="flex flex-wrap items-center gap-1.5">
            <Badge variant="secondary">{cours.subject.label}</Badge>
            {cours.cursus.length > 0 ? (
              formatCursusGroups(cours.cursus).map((group) => (
                <Badge key={group.key} variant="outline">
                  {group.label}
                </Badge>
              ))
            ) : (
              <Badge variant="outline">Toutes séries</Badge>
            )}
          </div>

          {/* mt-auto : cale ce pied en bas quelle que soit la longueur du titre, pour
              que les mentions d'accès s'alignent d'une carte à l'autre sur une ligne
              de la grille. */}
          <div className="mt-auto flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-border/70 pt-2.5 text-xs text-muted-foreground">
            {cours.duree_estimee_min && (
              <span className="flex items-center gap-1">
                <Clock className="size-3.5" />
                {cours.duree_estimee_min} min
              </span>
            )}
            {cours.apercu_contenu.has_exemple_resolu && (
              <span className="flex items-center gap-1">
                <Sparkles className="size-3.5" />
                Exemple résolu
              </span>
            )}
            {cours.apercu_contenu.exercices_count > 0 && (
              <span className="flex items-center gap-1">
                <ListChecks className="size-3.5" />
                {cours.apercu_contenu.exercices_count} exercice
                {cours.apercu_contenu.exercices_count > 1 ? "s" : ""}
              </span>
            )}
            {/* Libellé court plutôt que la phrase entière : répétée à l'identique sur
                les trois mille cartes du catalogue, "Accès inclus dans ton abonnement"
                ne se lisait plus. Le titre complet reste au survol et pour les
                lecteurs d'écran. */}
            {cours.has_access ? (
              <span
                className="ml-auto flex items-center gap-1 text-success"
                title="Accès inclus dans ton abonnement"
              >
                <Unlock className="size-3.5" />
                Inclus
              </span>
            ) : (
              <span className="ml-auto flex items-center gap-1" title="Abonnement requis pour lire ce cours">
                <Lock className="size-3.5" />
                Abonnement
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
