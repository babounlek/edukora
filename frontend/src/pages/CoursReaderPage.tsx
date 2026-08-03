import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { ArrowLeft } from "lucide-react"

import { readCours } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { CoursContent } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { CountryBadge } from "@/components/CountryBadge"
import { useSeo } from "@/lib/seo"
import { coursListPath } from "@/lib/countryPath"

export function CoursReaderPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()
  const { country } = useCountry()

  const [content, setContent] = useState<CoursContent | null>(null)
  const [error, setError] = useState<string | null>(null)

  useSeo({ title: content?.title ?? "Cours" })

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: `/cours/${id}/lire` } })
      return
    }
    if (!id) return

    readCours(Number(id))
      .then(setContent)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger ce contenu.")
      })
  }, [id, isLoading, isAuthenticated, navigate])

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

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        to={coursListPath(content?.header.pays.code.toLowerCase() ?? country)}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour aux cours
      </Link>

      <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
        <h1 className="font-display">{content?.title}</h1>
        {content?.header && (
          <div className="not-prose mb-6 flex flex-wrap gap-1.5">
            <CountryBadge code={content.header.pays.code} label={content.header.pays.label} />
            <Badge variant="secondary">{content.header.matiere}</Badge>
            {content.header.serie && <Badge variant="outline">Série {content.header.serie}</Badge>}
            {content.header.sous_theme && <Badge variant="outline">{content.header.sous_theme}</Badge>}
            {content.header.duree_estimee_min && <Badge variant="outline">{content.header.duree_estimee_min} min</Badge>}
          </div>
        )}
        <EpreuveMarkdown markdown={content?.content_markdown ?? ""} directCoursLinks />
      </article>
    </div>
  )
}
