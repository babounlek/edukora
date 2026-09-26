import { useEffect, useRef, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { ArrowLeft, Check, NotebookPen, Unlock } from "lucide-react"

import { getCours, readCours } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cours, CoursContent, CoursSectionData } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { BarreLecture } from "@/components/BarreLecture"
import { CoursSection } from "@/components/CoursSection"
import { MarquesSection } from "@/components/MarquesSection"
import { CoursSommaire } from "@/components/CoursSommaire"
import { CountryBadge } from "@/components/CountryBadge"
import { EtapeSuivante } from "@/components/BarreSeance"
import { RelatedCours } from "@/components/RelatedCours"
import { useEtude } from "@/lib/useEtude"
import { useSeo } from "@/lib/seo"
import { coursListPath, coursReaderPath } from "@/lib/countryPath"
import { capitaliserTheme } from "@/lib/utils"

export function CoursReaderPage() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()
  const { country } = useCountry()

  const [content, setContent] = useState<CoursContent | null>(null)
  const [error, setError] = useState<string | null>(null)
  // Requête séparée de readCours (voir EpreuveReaderPage.getEpreuve, même raison) :
  // CoursContent.header ne porte que des libellés d'affichage (matiere, pas
  // subject.code ; pas de cursus.id), insuffisant pour RelatedCours ci-dessous. Sert
  // aussi, pour un visiteur non connecté, à savoir si ce cours est "vitrine" (voir
  // l'effet ci-dessous) avant de décider de rediriger ou non vers la connexion.
  const [cours, setCours] = useState<Cours | null>(null)
  const [coursFailed, setCoursFailed] = useState(false)

  useSeo({ title: content?.title ?? "Cours" })

  const articleRef = useRef<HTMLElement>(null)
  // Outils d'étude : réservés à un élève connecté (un visiteur sur un cours vitrine n'a nulle
  // part où ranger une note). Voir MarquesSection.
  const etude = useEtude(slug ? { type: "cours", slug } : null, isAuthenticated && Boolean(content))

  useEffect(() => {
    if (!slug) return
    getCours(slug)
      .then(setCours)
      .catch(() => setCoursFailed(true))
  }, [slug])

  useEffect(() => {
    if (isLoading) return
    if (!slug) return

    if (!isAuthenticated) {
      // Un visiteur anonyme peut lire un cours vitrine sans connexion (voir
      // catalog.Cours.est_vitrine, dérivé de sa/ses épreuve(s) source(s)) - il faut
      // d'abord savoir si c'en est un (voir l'effet ci-dessus) avant de trancher ; en
      // cas d'échec de cette requête, on retombe sur le comportement d'origine
      // (connexion requise) plutôt que de rester bloqué indéfiniment. Même patron
      // que EpreuveReaderPage.
      if (!cours && !coursFailed) return
      if (!cours?.has_access) {
        navigate("/connexion", { state: { from: coursReaderPath(slug) } })
        return
      }
    }

    readCours(slug)
      .then(setContent)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger ce contenu.")
      })
  }, [slug, isLoading, isAuthenticated, navigate, cours, coursFailed])

  useEffect(() => {
    // Même raison que dans EpreuveReaderPage : le contenu arrive en asynchrone, le #hash
    // (posé par le carnet) doit être rejoué une fois les sections rendues.
    if (!content) return
    const id = window.location.hash.slice(1)
    if (id) document.getElementById(id)?.scrollIntoView()
  }, [content])

  useEffect(() => {
    // Même raison que dans EpreuveReaderPage : le contenu arrive en asynchrone, le #hash
    // (posé par le carnet) doit être rejoué une fois les sections rendues.
    if (!content) return
    const id = window.location.hash.slice(1)
    if (id) document.getElementById(id)?.scrollIntoView()
  }, [content])

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
  // Les sections dont on peut déclarer la compréhension : ni l'accroche (un texte d'ouverture)
  // ni les prérequis (une liste de renvois).
  const sectionsAComprendre = (content?.sections ?? []).filter(
    (section) => section.type !== "accroche" && section.type !== "prerequis",
  )
  const toutComprisCours =
    sectionsAComprendre.length > 0 && sectionsAComprendre.every((section) => etude.marques[section.type]?.compris)
  const pied = (section: CoursSectionData) =>
    section.type === "accroche" ? undefined : (
      <MarquesSection etude={etude} cle={section.type} avecCompris={section.type !== "prerequis"} />
    )
  const hasSommaire = content?.sections.some((section) => section.type !== "accroche") ?? false

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <BarreLecture cibleRef={articleRef} contenuKey={content?.id} />
      <div className="mb-6 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
        <Link
          to={coursListPath(displayCountry)}
          className="inline-flex items-center gap-1.5 text-muted-foreground transition-colors hover:text-primary"
        >
          <ArrowLeft className="size-4" />
          Retour aux cours
        </Link>
        {etude.disponible && (
          <Link
            to="/carnet"
            className="inline-flex items-center gap-1.5 text-muted-foreground transition-colors hover:text-primary"
          >
            <NotebookPen className="size-4" />
            Mon carnet
          </Link>
        )}
      </div>

      <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">{content?.title}</h1>
      {content?.header && (
        <div className="mb-6 mt-3 flex flex-wrap gap-1.5">
          <CountryBadge code={content.header.pays.code} label={content.header.pays.label} />
          {cours?.est_vitrine && (
            <Badge variant="success">
              <Unlock className="mr-1 size-3" />
              Cours en accès libre
            </Badge>
          )}
          <Badge variant="secondary">{content.header.matiere}</Badge>
          {content.header.serie && <Badge variant="outline">Série {content.header.serie}</Badge>}
          {content.header.sous_theme && <Badge variant="outline">{capitaliserTheme(content.header.sous_theme)}</Badge>}
          {content.header.duree_estimee_min && <Badge variant="outline">{content.header.duree_estimee_min} min</Badge>}
        </div>
      )}

      {etude.disponible && sectionsAComprendre.length > 0 && (
        <div className="mb-6 flex flex-col gap-1.5" aria-live="polite">
          <div className="flex items-center justify-between gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5">
              {toutComprisCours && <Check className="size-3.5 text-success" />}
              {toutComprisCours
                ? "Tu as tout compris de ce cours - vérifie-le avec un quiz."
                : `${etude.nbComprises} section${etude.nbComprises > 1 ? "s" : ""} comprise${etude.nbComprises > 1 ? "s" : ""} sur ${sectionsAComprendre.length}`}
            </span>
          </div>
          <div className="flex h-1.5 gap-1">
            {sectionsAComprendre.map((section) => (
              <span
                key={section.type}
                className={"h-full flex-1 rounded-full transition-colors duration-500 " + (etude.marques[section.type]?.compris ? "bg-primary" : "bg-muted")}
              />
            ))}
          </div>
        </div>
      )}

      {hasSections && content ? (
        hasSommaire ? (
          <div className="lg:grid lg:grid-cols-[200px_minmax(0,1fr)] lg:items-start lg:gap-10">
            <CoursSommaire sections={content.sections} />
            <article ref={articleRef} className="flex min-w-0 flex-col gap-8">
              {content.sections.map((section) => (
                <CoursSection key={section.type} section={section} pied={pied(section)} />
              ))}
            </article>
          </div>
        ) : (
          <article ref={articleRef} className="mx-auto flex max-w-3xl flex-col gap-8">
            {content.sections.map((section) => (
              <CoursSection key={section.type} section={section} pied={pied(section)} />
            ))}
          </article>
        )
      ) : (
        <div className="mx-auto max-w-3xl">
          <article ref={articleRef} className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
            <EpreuveMarkdown markdown={content?.content_markdown ?? ""} directCoursLinks />
          </article>
        </div>
      )}

      <EtapeSuivante />

      {cours && (
        <RelatedCours
          subjectCode={cours.subject.code}
          subjectLabel={cours.subject.label}
          countryCode={cours.subject.country.code.toLowerCase()}
          cursusId={cours.cursus[0]?.id}
          excludeId={cours.id}
          sousTheme={cours.sous_theme || undefined}
        />
      )}
    </div>
  )
}
