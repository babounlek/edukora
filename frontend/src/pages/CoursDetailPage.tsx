import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ArrowLeft, BookOpenText, Lock } from "lucide-react"

import { getCours, previewCours } from "@/api/endpoints"
import type { Cours, CoursPreview } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { CountryBadge } from "@/components/CountryBadge"
import { coursListPath } from "@/lib/countryPath"

export function CoursDetailPage() {
  const { id } = useParams<{ id: string }>()

  const [cours, setCours] = useState<Cours | null>(null)
  const [preview, setPreview] = useState<CoursPreview | null>(null)

  useSeo({
    title: cours?.titre ?? "Cours",
    description: cours
      ? `Cours de ${cours.subject.label}${cours.sous_theme ? ` - ${cours.sous_theme}` : ""} : méthode, exemple résolu, erreurs classiques et exercices d'appropriation.`
      : undefined,
  })

  useEffect(() => {
    if (!id) return
    getCours(Number(id)).then(setCours)
  }, [id])

  useEffect(() => {
    if (!cours || cours.has_access) return
    previewCours(cours.id).then(setPreview).catch(() => {})
  }, [cours])

  if (!cours) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-3">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-5 w-1/2" />
          <Skeleton className="h-10 w-40" />
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        to={coursListPath(cours.subject.country.code.toLowerCase())}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour aux cours
      </Link>

      <div className="flex animate-fade-up flex-col gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">{cours.titre}</h1>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <CountryBadge code={cours.subject.country.code} label={cours.subject.country.label} />
            <Badge variant="secondary">{cours.subject.label}</Badge>
            {cours.cursus.length > 0 ? (
              formatCursusGroups(cours.cursus).map((group) => (
                <Badge key={group.key} variant="outline">{group.label}</Badge>
              ))
            ) : (
              <Badge variant="outline">Toutes séries</Badge>
            )}
            {cours.sous_theme && <Badge variant="outline">{cours.sous_theme}</Badge>}
            {cours.duree_estimee_min && <Badge variant="outline">{cours.duree_estimee_min} min</Badge>}
          </div>
        </div>

        {cours.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {cours.tags.map((tag) => (
              <span key={tag.id} className="text-xs text-muted-foreground">
                #{tag.name}
              </span>
            ))}
          </div>
        )}

        <div className="mt-2 border-t border-border pt-5">
          {cours.has_access ? (
            <Button asChild size="lg">
              <Link to={`/cours/${cours.id}/lire`}>
                <BookOpenText />
                Lire le cours
              </Link>
            </Button>
          ) : (
            <div className="flex flex-col gap-4">
              {preview && (
                <>
                  <div className="flex items-center gap-1.5 rounded-md border border-dashed border-border bg-muted/40 px-3 py-2 text-xs font-medium text-muted-foreground">
                    <Lock className="size-3.5 shrink-0" />
                    Aperçu - la méthode seulement
                  </div>
                  <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
                    <EpreuveMarkdown markdown={preview.preview_markdown} />
                  </article>
                </>
              )}

              <div className="flex flex-col gap-3 rounded-lg border border-dashed border-border bg-muted/40 p-4">
                <p className="flex items-center gap-1.5 text-sm font-medium">
                  <Lock className="size-4 shrink-0" />
                  Abonne-toi pour accéder à l'exemple résolu, aux erreurs classiques et aux exercices d'application.
                </p>
                <div className="flex flex-wrap gap-2">
                  {cours.cursus.length > 0 ? (
                    cours.cursus.map((c) => (
                      <Button key={c.id} asChild size="lg">
                        <Link to={`/abonnement?cursus=${c.id}`}>
                          S'abonner{cours.cursus.length > 1 ? ` (${c.series ? c.series.code : c.examen_display})` : ""}
                        </Link>
                      </Button>
                    ))
                  ) : (
                    <Button asChild size="lg">
                      <Link to="/abonnement">S'abonner</Link>
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
