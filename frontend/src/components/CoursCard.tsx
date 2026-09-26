import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, BookOpenCheck, CheckCircle2, Clock, Eye, ListChecks, Sparkles, Unlock } from "lucide-react"

import type { Cours } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { coursDetailPath, coursReaderPath } from "@/lib/countryPath"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { capitaliserTheme, cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

interface CoursCardProps {
  cours: Cours
  className?: string
  style?: CSSProperties
}

export function CoursCard({ cours, className, style }: CoursCardProps) {
  const SubjectIcon = subjectIcon(cours.subject.code)
  const couleur = couleurMatiere(cours.subject.code)
  const accessible = cours.has_access || cours.est_vitrine

  return (
    <Link
      to={cours.has_access ? coursReaderPath(cours.slug) : coursDetailPath(cours.slug)}
      className={cn("group block h-full rounded-xl focus-visible:outline-none", className)}
      style={style}
    >
      <Card className="relative h-full overflow-hidden transition-all duration-300 group-hover:-translate-y-1 group-hover:border-primary/50 group-hover:shadow-lg group-hover:shadow-primary/[0.07] group-focus-visible:ring-2 group-focus-visible:ring-ring">
        {/* Filet de matière : même repère que sur les cartes d'épreuves, pour reconnaître
            "les maths" d'un coup d'œil dans une grille avant même de lire un titre. */}
        <div aria-hidden className={cn("h-1 w-full", couleur.barre)} />
        <CardContent className="flex h-[calc(100%-0.25rem)] flex-col gap-3 p-4">
          <div className="flex items-start gap-3">
            <span className={cn("flex size-10 shrink-0 items-center justify-center rounded-xl", couleur.puce)}>
              <SubjectIcon className="size-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-medium uppercase tracking-wide text-muted-foreground">
                {cours.subject.label}
                {cours.sous_theme && ` · ${capitaliserTheme(cours.sous_theme)}`}
              </p>
              <h3 className="mt-0.5 line-clamp-2 font-display text-base font-medium leading-snug">{cours.titre}</h3>
            </div>
            {/* L'état "lu" remonte en tête de carte : dans une grille où l'on repasse
                plusieurs fois, c'est le repère qu'on cherche en premier. */}
            {cours.is_read && (
              <span className="flex shrink-0 items-center gap-1 rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
                <CheckCircle2 className="size-3" />
                Lu
              </span>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            {cours.est_vitrine && (
              <Badge variant="success" className="gap-1">
                <Sparkles className="size-3" />
                Gratuit
              </Badge>
            )}
            {cours.cursus.length > 0 ? (
              formatCursusGroups(cours.cursus).map((group) => (
                <Badge key={group.key} variant="secondary">
                  {group.label}
                </Badge>
              ))
            ) : (
              <Badge variant="secondary">Toutes séries</Badge>
            )}
          </div>

          {/* Ce que contient le cours : c'est ce qui fait choisir celui-ci plutôt qu'un
              autre. Détail de contenu, donc en texte sous les badges plutôt qu'en
              pastilles de même poids que la matière. */}
          {(cours.duree_estimee_min || cours.apercu_contenu.has_exemple_resolu || cours.apercu_contenu.exercices_count > 0) && (
            <p className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
              {cours.duree_estimee_min && (
                <span className="inline-flex items-center gap-1">
                  <Clock className="size-3.5" aria-hidden="true" />
                  {cours.duree_estimee_min} min
                </span>
              )}
              {cours.apercu_contenu.has_exemple_resolu && (
                <span className="inline-flex items-center gap-1">
                  <BookOpenCheck className="size-3.5" aria-hidden="true" />
                  Exemple résolu
                </span>
              )}
              {cours.apercu_contenu.exercices_count > 0 && (
                <span className="inline-flex items-center gap-1">
                  <ListChecks className="size-3.5" aria-hidden="true" />
                  {cours.apercu_contenu.exercices_count} exercice{cours.apercu_contenu.exercices_count > 1 ? "s" : ""}
                </span>
              )}
            </p>
          )}

          {/* Le pied dit CE QUE LE CLIC FAIT : "Abonnement" écartait avant d'avoir vu, alors
              qu'un aperçu du cours existe. mt-auto : l'action s'aligne d'une carte à
              l'autre quelle que soit la hauteur du contenu. */}
          <div className="mt-auto flex items-center justify-between gap-2 border-t border-border/70 pt-3 text-sm">
            <span className="flex min-w-0 items-center gap-1.5 font-medium text-foreground">
              {accessible ? (
                <>
                  <Unlock className="size-4 shrink-0 text-success" aria-hidden="true" />
                  <span className="truncate">{cours.est_vitrine && !cours.has_access ? "Lire - accès libre" : "Lire le cours"}</span>
                </>
              ) : (
                <>
                  <Eye className="size-4 shrink-0 text-primary" aria-hidden="true" />
                  <span className="truncate">Voir l'aperçu</span>
                </>
              )}
            </span>
            <ArrowRight
              className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-1"
              aria-hidden="true"
            />
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
