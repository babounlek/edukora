import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ArrowLeft, BookOpenText, FileDown, GraduationCap, Lock, Unlock } from "lucide-react"

import { getEpreuve, previewEpreuve } from "@/api/endpoints"
import type { Epreuve, EpreuvePreview } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { RelatedEpreuves } from "@/components/RelatedEpreuves"
import { BackToTopBar } from "@/components/BackToTopBar"
import { CountryBadge } from "@/components/CountryBadge"
import { formatCursusGroups } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { catalogueHomePath } from "@/lib/countryPath"

export function EpreuveDetailPage() {
  const { slug } = useParams<{ slug: string }>()

  const [epreuve, setEpreuve] = useState<Epreuve | null>(null)
  const [preview, setPreview] = useState<EpreuvePreview | null>(null)

  useSeo({
    title: epreuve?.title ?? "Corrigé",
    description: epreuve
      ? `${epreuve.lesson_type_display} de ${epreuve.subject.label}${epreuve.year ? ` (${epreuve.year})` : ""} - sujet en accès libre, corrigé détaillé par abonnement.`
      : undefined,
  })

  useEffect(() => {
    if (!slug) return
    getEpreuve(slug).then(setEpreuve)
  }, [slug])

  useEffect(() => {
    // Le sujet (preview_markdown) est public - voir access.views.preview_lesson
    // côté backend - donc récupéré pour tout le monde, abonné ou non : un abonné
    // doit pouvoir consulter l'épreuve sans passer par la lecture du corrigé.
    if (!epreuve) return
    previewEpreuve(epreuve.slug).then(setPreview).catch(() => {})
  }, [epreuve])

  if (!epreuve) {
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
        to={catalogueHomePath(epreuve.subject.country.code.toLowerCase())}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour au catalogue
      </Link>

      <div className="flex animate-fade-up flex-col gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">{epreuve.title}</h1>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <CountryBadge code={epreuve.subject.country.code} label={epreuve.subject.country.label} />
            <Badge variant="secondary">{epreuve.subject.label}</Badge>
            {formatCursusGroups(epreuve.cursus).map((group) => (
              <Badge key={group.key} variant="outline">{group.label}</Badge>
            ))}
            <Badge variant="outline">{epreuve.lesson_type_display}</Badge>
            {epreuve.year && <Badge variant="outline">Session {epreuve.year}</Badge>}
            {epreuve.origine !== "OFFICIEL" && (
              <Badge variant="outline">
                {epreuve.origine_display}
                {epreuve.etablissement ? ` - ${epreuve.etablissement}` : ""}
              </Badge>
            )}
            {epreuve.exercises_count > 0 && (
              <Badge variant="outline">
                {epreuve.exercises_count} exercice{epreuve.exercises_count > 1 ? "s" : ""}
              </Badge>
            )}
          </div>
        </div>

        <div className="mt-2 flex flex-wrap gap-2 border-t border-border pt-5">
          {epreuve.sujet_pdf_url && (
            <Button asChild variant="outline" size="lg">
              <a href={epreuve.sujet_pdf_url} target="_blank" rel="noopener noreferrer">
                <FileDown />
                Télécharger l'épreuve
              </a>
            </Button>
          )}
          {epreuve.has_access && (
            <Button asChild size="lg">
              <Link to={`/epreuves/${epreuve.slug}/lire`}>
                <BookOpenText />
                Lire le corrigé
              </Link>
            </Button>
          )}
        </div>

        {/* Consulter l'épreuve : le sujet (énoncés seuls) est public, voir
            access.views.preview_lesson côté backend - toujours affiché ici, abonné ou non. */}
        {preview && (
          <div className="mt-2 border-t border-border pt-5">
            <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">Sujet</h2>
            <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
              <EpreuveMarkdown markdown={preview.preview_markdown} />
            </article>
          </div>
        )}

        {!epreuve.has_access && (
          <div className="mt-2 border-t border-border pt-5">
            <div className="flex flex-col gap-3 rounded-lg border border-dashed border-border bg-muted/40 p-4">
              <p className="flex items-center gap-1.5 text-sm font-medium">
                <Lock className="size-4 shrink-0" />
                Le sujet est en libre accès. Abonne-toi pour lire la correction complète
                {epreuve.cursus.length > 1 ? " (l'un des cursus suivants suffit)" : ""}.
              </p>
              <div className="flex flex-wrap gap-2">
                {epreuve.cursus.map((c) => (
                  <Button key={c.id} asChild size="lg">
                    <Link to={`/abonnement?cursus=${c.id}`}>
                      S'abonner{epreuve.cursus.length > 1 ? ` (${c.series ? c.series.code : c.examen_display})` : ""}
                    </Link>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}

        {epreuve.related_cours.length > 0 && (
          <div className="mt-2 border-t border-border pt-5">
            <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">Cours associés</h2>
            <div className="flex flex-col gap-2">
              {epreuve.related_cours.map((cours) => (
                <Link
                  key={cours.id}
                  to={cours.has_access ? `/cours/${cours.id}/lire` : `/cours/${cours.id}`}
                  className="flex items-center justify-between gap-2 rounded-lg border border-border px-3.5 py-2.5 text-sm transition-colors hover:border-primary/50 hover:bg-accent"
                >
                  <span className="flex items-center gap-2">
                    <GraduationCap className="size-4 text-primary" />
                    {cours.titre}
                  </span>
                  {cours.has_access ? (
                    <Unlock className="size-3.5 shrink-0 text-success" />
                  ) : (
                    <Lock className="size-3.5 shrink-0 text-muted-foreground" />
                  )}
                </Link>
              ))}
            </div>
          </div>
        )}

        <RelatedEpreuves
          subjectCode={epreuve.subject.code}
          subjectLabel={epreuve.subject.label}
          countryCode={epreuve.subject.country.code.toLowerCase()}
          cursusId={epreuve.cursus[0]?.id}
          excludeId={epreuve.id}
        />

        <BackToTopBar links={[{ to: catalogueHomePath(epreuve.subject.country.code.toLowerCase()), label: "Retour au catalogue" }]} />
      </div>
    </div>
  )
}
