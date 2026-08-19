import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { ArrowLeft, FileDown, Unlock } from "lucide-react"

import { getEpreuve, readEpreuve } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Epreuve, EpreuveContent } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { EnonceToggle } from "@/components/EnonceToggle"
import { EpreuveSommaire, exerciceAnchorId } from "@/components/EpreuveSommaire"
import { ExerciceNav } from "@/components/ExerciceNav"
import { FicheReader } from "@/components/FicheReader"
import { RelatedEpreuves } from "@/components/RelatedEpreuves"
import { BackToTopBar } from "@/components/BackToTopBar"
import { CountryBadge } from "@/components/CountryBadge"
import { useSeo } from "@/lib/seo"
import { epreuveDetailPath, epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"

export function EpreuveReaderPage() {
  const { country: countryParam, slug } = useParams<{ country?: string; slug: string }>()
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()
  const { country: fallbackCountry } = useCountry()

  const [content, setContent] = useState<EpreuveContent | null>(null)
  const [epreuve, setEpreuve] = useState<Epreuve | null>(null)
  const [epreuveFailed, setEpreuveFailed] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useSeo({ title: content?.title ?? "Corrigé" })

  useEffect(() => {
    // Requête publique séparée de readEpreuve (réservée aux abonnés) : sert à
    // alimenter "Autres épreuves" (subject.code/cursus, absents de
    // EpreuveContent.header qui ne porte que des libellés d'affichage) - voir
    // RelatedEpreuves - et, pour un visiteur non connecté, à savoir si cette épreuve
    // est une "vitrine" (has_access déjà vrai côté API même sans compte) avant de
    // décider de rediriger ou non vers la connexion ci-dessous.
    if (!slug) return
    getEpreuve(slug)
      .then(setEpreuve)
      .catch(() => setEpreuveFailed(true))
  }, [slug])

  useEffect(() => {
    // Même principe que EpreuveDetailPage : recanonicalise vers /{pays}/epreuves/...
    // dès que le pays réel de l'épreuve est connu (ancien lien sans préfixe, ou
    // préfixe incorrect dans l'URL visitée).
    if (!epreuve || !slug) return
    const canonicalCountry = epreuve.subject.country.code.toLowerCase()
    if (countryParam !== canonicalCountry) {
      navigate(epreuveReaderPath(canonicalCountry, slug), { replace: true })
    }
  }, [epreuve, slug, countryParam, navigate])

  useEffect(() => {
    if (isLoading) return
    if (!slug) return

    if (!isAuthenticated) {
      // Un visiteur anonyme peut lire une épreuve vitrine sans connexion - il faut
      // d'abord savoir si c'en est une (voir l'effet ci-dessus) avant de trancher ;
      // en cas d'échec de cette requête publique, on retombe sur le comportement
      // d'origine (connexion requise) plutôt que de rester bloqué indéfiniment.
      if (!epreuve && !epreuveFailed) return
      if (!epreuve?.has_access) {
        navigate("/connexion", { state: { from: epreuveReaderPath(countryParam ?? fallbackCountry, slug) } })
        return
      }
    }

    readEpreuve(slug)
      .then(setContent)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Impossible de charger ce contenu.")
      })
  }, [slug, isLoading, isAuthenticated, navigate, epreuve, epreuveFailed, countryParam, fallbackCountry])

  useEffect(() => {
    // Le contenu arrive en asynchrone : au moment où le navigateur traite le #hash
    // d'une URL partagée (ex. /lire#exercice-3, posé par le sommaire), la cible
    // n'existe pas encore dans le DOM et le saut n'a pas lieu. On le rejoue une fois
    // les exercices rendus - jamais au montage.
    if (!content) return
    const id = window.location.hash.slice(1)
    if (!id) return
    document.getElementById(id)?.scrollIntoView()
  }, [content])

  // Le pays réel de l'épreuve dès qu'il est connu, sinon le pays de l'URL visitée,
  // sinon le pays courant du visiteur - toujours une valeur utilisable pour les liens
  // "retour" pendant que epreuve charge encore.
  const displayCountry = epreuve?.subject.country.code.toLowerCase() ?? countryParam ?? fallbackCountry

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
        <Link to={epreuvesListPath(displayCountry)} className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour au catalogue
        </Link>
      </div>
    )
  }

  // Un sommaire n'a de sens qu'à partir de deux exercices - en dessous, il ne ferait
  // qu'ajouter une barre sticky et rétrécir la colonne de lecture pour une seule entrée.
  const exercises = content?.exercises ?? []
  const hasSommaire = content?.lesson_type !== "FICHE" && exercises.length > 1

  const article = (
    <article className="prose prose-neutral min-w-0 max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
      {exercises.length > 0 ? (
        exercises.map((exercise, index) => (
          <div key={exercise.numero_exercice} id={exerciceAnchorId(exercise.numero_exercice)} className="scroll-mt-24">
            {index > 0 && <hr />}
            {exercise.enonce_intro_markdown && <EpreuveMarkdown markdown={exercise.enonce_intro_markdown} />}
            <EnonceToggle>
              <EpreuveMarkdown markdown={exercise.enonce_markdown} />
            </EnonceToggle>
            <EpreuveMarkdown markdown={exercise.corrige_markdown} directCoursLinks />
            {exercises.length > 1 && <ExerciceNav exercises={exercises} index={index} />}
          </div>
        ))
      ) : (
        <EpreuveMarkdown markdown={content?.content_markdown ?? ""} directCoursLinks />
      )}
    </article>
  )

  return (
    <div className={`mx-auto px-4 py-8 sm:px-6 ${hasSommaire ? "max-w-5xl" : "max-w-3xl"}`}>
      <div className="mb-6 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
        <Link
          to={epreuvesListPath(displayCountry)}
          className="inline-flex items-center gap-1.5 transition-colors hover:text-primary"
        >
          <ArrowLeft className="size-4" />
          Retour au catalogue
        </Link>
        <span aria-hidden="true">·</span>
        <Link to={epreuveDetailPath(displayCountry, slug ?? "")} className="transition-colors hover:text-primary">
          Retour à la fiche de l'épreuve
        </Link>
      </div>

      {content?.lesson_type === "FICHE" ? (
        <FicheReader title={content.title} header={content.header} markdown={content.content_markdown} />
      ) : (
        <>
          {/* Titre, badges et PDF restent pleine largeur, au-dessus de la grille : la
              sidebar du sommaire ne doit commencer qu'au niveau du premier exercice. */}
          <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">{content?.title}</h1>
          {content?.header && (
            <div className="mb-6 mt-3 flex flex-wrap gap-1.5">
              <CountryBadge code={content.header.pays.code} label={content.header.pays.label} />
              {epreuve?.est_vitrine && (
                <Badge variant="success">
                  <Unlock className="mr-1 size-3" />
                  Corrigé en accès libre
                </Badge>
              )}
              <Badge variant="secondary">{content.header.matiere}</Badge>
              {content.header.nature && <Badge variant="outline">{content.header.nature}</Badge>}
              {content.header.serie && <Badge variant="outline">Série {content.header.serie}</Badge>}
              {content.header.examen && <Badge variant="outline">{content.header.examen}</Badge>}
              {content.header.annee && <Badge variant="outline">Session {content.header.annee}</Badge>}
              {content.header.duree && <Badge variant="outline">Durée : {content.header.duree}</Badge>}
              {content.header.coefficient && <Badge variant="outline">Coefficient : {content.header.coefficient}</Badge>}
              {content.header.institution && content.header.institution !== content.header.etablissement && (
                <Badge variant="outline">{content.header.institution}</Badge>
              )}
            </div>
          )}
          {content?.sujet_pdf_url && (
            <div className="mb-6">
              <Button asChild variant="outline" size="sm">
                <a href={content.sujet_pdf_url} target="_blank" rel="noopener noreferrer">
                  <FileDown />
                  Télécharger l'épreuve
                </a>
              </Button>
            </div>
          )}
          {content?.introduction_markdown && (
            // Consigne d'épreuve entière (ex. "le candidat traitera un seul sujet au
            // choix") - avant le sommaire/premier exercice, jamais répétée par exercice
            // (contrairement à exercise.enonce_intro_markdown, propre à CHAQUE exercice).
            <div className="prose prose-neutral mb-6 max-w-none text-justify dark:prose-invert">
              <EpreuveMarkdown markdown={content.introduction_markdown} />
            </div>
          )}
          {hasSommaire ? (
            <div className="lg:grid lg:grid-cols-[220px_minmax(0,1fr)] lg:items-start lg:gap-10">
              <EpreuveSommaire exercises={exercises} />
              {article}
            </div>
          ) : (
            article
          )}
        </>
      )}

      {epreuve && (
        <RelatedEpreuves
          subjectCode={epreuve.subject.code}
          subjectLabel={epreuve.subject.label}
          countryCode={epreuve.subject.country.code.toLowerCase()}
          cursusId={epreuve.cursus[0]?.id}
          excludeId={epreuve.id}
        />
      )}

      <BackToTopBar
        links={[
          { to: epreuvesListPath(displayCountry), label: "Retour au catalogue" },
          { to: epreuveDetailPath(displayCountry, slug ?? ""), label: "Retour à la fiche de l'épreuve" },
        ]}
      />
    </div>
  )
}
