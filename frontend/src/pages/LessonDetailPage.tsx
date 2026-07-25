import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ArrowLeft, BookOpenText, FileDown, GraduationCap, Lock, Unlock } from "lucide-react"

import { getLesson, previewLesson } from "@/api/endpoints"
import type { Lesson, LessonPreview } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { LessonMarkdown } from "@/components/LessonMarkdown"
import { formatCursusGroups } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath } from "@/lib/countryPath"

export function LessonDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { country } = useCountry()

  const [lesson, setLesson] = useState<Lesson | null>(null)
  const [preview, setPreview] = useState<LessonPreview | null>(null)

  useSeo({
    title: lesson?.title ?? "Corrigé",
    description: lesson
      ? `${lesson.lesson_type_display} de ${lesson.subject.label}${lesson.year ? ` (${lesson.year})` : ""} - sujet en accès libre, corrigé détaillé par abonnement.`
      : undefined,
  })

  useEffect(() => {
    if (!id) return
    getLesson(Number(id)).then(setLesson)
  }, [id])

  useEffect(() => {
    if (!lesson || lesson.has_access) return
    previewLesson(lesson.id).then(setPreview).catch(() => {})
  }, [lesson])

  if (!lesson) {
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
        to={catalogueHomePath(country)}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour au catalogue
      </Link>

      <div className="flex animate-fade-up flex-col gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">{lesson.title}</h1>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <Badge variant="secondary">{lesson.subject.label}</Badge>
            {formatCursusGroups(lesson.cursus).map((group) => (
              <Badge key={group.key} variant="outline">{group.label}</Badge>
            ))}
            <Badge variant="outline">{lesson.lesson_type_display}</Badge>
            {lesson.year && <Badge variant="outline">Session {lesson.year}</Badge>}
            {lesson.origine !== "OFFICIEL" && (
              <Badge variant="outline">
                {lesson.origine_display}
                {lesson.etablissement ? ` - ${lesson.etablissement}` : ""}
              </Badge>
            )}
            {lesson.exercises_count > 0 && (
              <Badge variant="outline">
                {lesson.exercises_count} exercice{lesson.exercises_count > 1 ? "s" : ""}
              </Badge>
            )}
          </div>
        </div>

        {lesson.themes.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {lesson.themes.map((theme) => (
              <span key={theme.id} className="text-xs text-muted-foreground">
                #{theme.name}
              </span>
            ))}
          </div>
        )}

        <div className="mt-2 border-t border-border pt-5">
          {lesson.has_access ? (
            <div className="flex flex-wrap gap-2">
              <Button asChild size="lg">
                <Link to={`/lecons/${lesson.id}/lire`}>
                  <BookOpenText />
                  Lire le corrigé
                </Link>
              </Button>
              {lesson.sujet_pdf_url && (
                <Button asChild variant="outline" size="lg">
                  <a href={lesson.sujet_pdf_url} target="_blank" rel="noopener noreferrer">
                    <FileDown />
                    Télécharger le sujet en PDF
                  </a>
                </Button>
              )}
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {preview && (
                <>
                  <div className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-dashed border-border bg-muted/40 px-3 py-2 text-xs font-medium text-muted-foreground">
                    <span className="flex items-center gap-1.5">
                      <Unlock className="size-3.5 shrink-0" />
                      Sujet en accès libre
                      {lesson.exercises_count > 0
                        ? ` - ${lesson.exercises_count} exercice${lesson.exercises_count > 1 ? "s" : ""}`
                        : ""}
                    </span>
                    {lesson.sujet_pdf_url && (
                      <a
                        href={lesson.sujet_pdf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 font-medium text-primary hover:underline"
                      >
                        <FileDown className="size-3.5" />
                        PDF
                      </a>
                    )}
                  </div>
                  <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display">
                    <LessonMarkdown markdown={preview.preview_markdown} />
                  </article>
                </>
              )}

              <div className="flex flex-col gap-3 rounded-lg border border-dashed border-border bg-muted/40 p-4">
                <p className="flex items-center gap-1.5 text-sm font-medium">
                  <Lock className="size-4 shrink-0" />
                  Le sujet est en libre accès. Abonne-toi pour lire la correction complète
                  {lesson.cursus.length > 1 ? " (l'un des cursus suivants suffit)" : ""}.
                </p>
                <div className="flex flex-wrap gap-2">
                  {lesson.cursus.map((c) => (
                    <Button key={c.id} asChild size="lg">
                      <Link to={`/abonnement?cursus=${c.id}`}>
                        S'abonner{lesson.cursus.length > 1 ? ` (${c.series ? c.series.code : c.examen_display})` : ""}
                      </Link>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {lesson.related_cours.length > 0 && (
          <div className="mt-2 border-t border-border pt-5">
            <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">Cours associés</h2>
            <div className="flex flex-col gap-2">
              {lesson.related_cours.map((cours) => (
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
      </div>
    </div>
  )
}
