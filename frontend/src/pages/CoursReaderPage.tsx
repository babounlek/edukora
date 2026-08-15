import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { ArrowLeft } from "lucide-react"

import { getCours, readCours } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cours, CoursContent } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { CoursSection } from "@/components/CoursSection"
import { CoursSommaire } from "@/components/CoursSommaire"
import { CountryBadge } from "@/components/CountryBadge"
import { RelatedCours } from "@/components/RelatedCours"
import { useSeo } from "@/lib/seo"
import { coursListPath, coursReaderPath } from "@/lib/countryPath"

export function CoursReaderPage() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()
  const { country } = useCountry()

  const [content, setContent] = useState<CoursContent | null>(null)
  const [error, setError] = useState<string | null>(null)
  // Requête séparée de readCours (voir EpreuveReaderPage.getEpreuve, même raison) :
  // CoursContent.header ne porte que des libellés d'affichage (matiere, pas
  // subject.code ; pas de cursus.id), insuffisant pour RelatedCours ci-dessous.
  const [cours, setCours] = useState<Cours | null>(null)

  useSeo({ title: content?.title ?? "Cours" })

  useEffect(() => {
    if (!slug) return
    getCours(slug)
      .then(setCours)
      .catch(() => {})
  }, [slug])

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: coursReaderPath(slug ?? "") } })
      return
    }
    if (!slug) return

    readCours(slug)
      .then(setContent)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger ce contenu.")
      })
  }, [slug, isLoading, isAuthenticated, navigate])

  if (isLoading || (!content && !error)) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <Skeleton className="mb-6 h-6 w-40" />
        <Skeleton className="mb-3 h-8 w-2/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="mt-2 h-4 w-full" />
        <Skeleton className="mt-2 h-4 w-3/4" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 text-center sm:px-6">
        <p className="text-destructive">{error}</p>
        <Link to={coursListPath(country)} className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour aux cours
        </Link>
      </div>
    )
  }

  const displayCountry = content?.header.pays.code.toLowerCase() ?? country
  const hasSections = (content?.sections.length ?? 0) > 0
  const hasSommaire = content?.sections.some((section) => section.type !== "accroche") ?? false

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <Link
        to={coursListPath(displayCountry)}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour aux cours
      </Link>

      <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">{content?.title}</h1>
      {content?.header && (
        <div className="mb-6 mt-3 flex flex-wrap gap-1.5">
          <CountryBadge code={content.header.pays.code} label={content.header.pays.label} />
          <Badge variant="secondary">{content.header.matiere}</Badge>
          {content.header.serie && <Badge variant="outline">Série {content.header.serie}</Badge>}
          {content.header.sous_theme && <Badge variant="outline">{content.header.sous_theme}</Badge>}
          {content.header.duree_estimee_min && <Badge variant="outline">{content.header.duree_estimee_min} min</Badge>}
        </div>
      )}

      {hasSections && content ? (
        hasSommaire ? (
          <div className="lg:grid lg:grid-cols-[200px_minmax(0,1fr)] lg:items-start lg:gap-10">
            <CoursSommaire sections={content.sections} />
            <article className="flex min-w-0 flex-col gap-8">
              {content.sections.map((section) => (
                <CoursSection key={section.type} section={section} />
              ))}
            </article>
          </div>
        ) : (
          <article className="mx-auto flex max-w-3xl flex-col gap-8">
            {content.sections.map((section) => (
              <CoursSection key={section.type} section={section} />
            ))}
          </article>
        )
      ) : (
        <div className="mx-auto max-w-3xl">
          <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
            <EpreuveMarkdown markdown={content?.content_markdown ?? ""} directCoursLinks />
          </article>
        </div>
      )}

      {cours && (
        <RelatedCours
          subjectCode={cours.subject.code}
          subjectLabel={cours.subject.label}
          countryCode={cours.subject.country.code.toLowerCase()}
          cursusId={cours.cursus[0]?.id}
          excludeId={cours.id}
        />
      )}
    </div>
  )
}
