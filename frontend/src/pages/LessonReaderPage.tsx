import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { ArrowLeft, FileDown } from "lucide-react"

import { readLesson } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { LessonContent } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { LessonMarkdown } from "@/components/LessonMarkdown"
import { useSeo } from "@/lib/seo"
import { catalogueHomePath } from "@/lib/countryPath"

export function LessonReaderPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()
  const { country } = useCountry()

  const [content, setContent] = useState<LessonContent | null>(null)
  const [error, setError] = useState<string | null>(null)

  useSeo({ title: content?.title ?? "Corrigé" })

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: `/lecons/${id}/lire` } })
      return
    }
    if (!id) return

    readLesson(Number(id))
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
        <Link to={catalogueHomePath(country)} className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour au catalogue
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        to={`/lecons/${id}`}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour à la fiche de la leçon
      </Link>

      <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display">
        <h1 className="font-display">{content?.title}</h1>
        {content?.header && (
          <div className="not-prose mb-6 flex flex-wrap gap-1.5">
            <Badge variant="secondary">{content.header.matiere}</Badge>
            {content.header.serie && <Badge variant="outline">Série {content.header.serie}</Badge>}
            {content.header.examen && <Badge variant="outline">{content.header.examen}</Badge>}
            {content.header.annee && <Badge variant="outline">Session {content.header.annee}</Badge>}
            {content.header.duree && <Badge variant="outline">Durée : {content.header.duree}</Badge>}
            {content.header.coefficient && <Badge variant="outline">Coefficient : {content.header.coefficient}</Badge>}
          </div>
        )}
        {content?.sujet_pdf_url && (
          <div className="not-prose mb-6">
            <Button asChild variant="outline" size="sm">
              <a href={content.sujet_pdf_url} target="_blank" rel="noopener noreferrer">
                <FileDown />
                Télécharger le sujet en PDF
              </a>
            </Button>
          </div>
        )}
        <LessonMarkdown markdown={content?.content_markdown ?? ""} directCoursLinks />
      </article>
    </div>
  )
}
