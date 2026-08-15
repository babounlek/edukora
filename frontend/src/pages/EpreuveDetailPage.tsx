import { useEffect, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, ArrowRight, BookOpenText, Crown, FileDown, GraduationCap, Lock, Sparkles, Unlock, Zap } from "lucide-react"

import { getEpreuve, previewEpreuve } from "@/api/endpoints"
import type { Epreuve, EpreuvePreview } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { EpreuveSommaire, exerciceAnchorId } from "@/components/EpreuveSommaire"
import { ParrainageHint } from "@/components/ParrainageHint"
import { RelatedEpreuves } from "@/components/RelatedEpreuves"
import { BackToTopBar } from "@/components/BackToTopBar"
import { CountryBadge } from "@/components/CountryBadge"
import { formatCursusGroups } from "@/lib/cursus"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { catalogueHomePath, coursDetailPath, coursReaderPath, epreuveDetailPath, epreuveReaderPath } from "@/lib/countryPath"

export function EpreuveDetailPage() {
  const { country, slug } = useParams<{ country?: string; slug: string }>()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

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
    // ?ref=pdf_sujet : posé par le PDF du sujet généré (voir backend
    // catalog.sujet_pdf._lesson_deep_link) sur son propre CTA - seule façon de
    // mesurer combien de visites viennent réellement d'un PDF partagé hors
    // plateforme, plutôt que de le supposer sans donnée.
    if (!epreuve) return
    if (searchParams.get("ref") !== "pdf_sujet") return
    trackEvent("pdf_sujet_landing", { subject_code: epreuve.subject.code })
  }, [epreuve, searchParams])

  useEffect(() => {
    // Le sujet (preview_markdown) est public - voir access.views.preview_lesson
    // côté backend - donc récupéré pour tout le monde, abonné ou non : un abonné
    // doit pouvoir consulter l'épreuve sans passer par la lecture du corrigé.
    if (!epreuve) return
    // getEpreuve(slug) (effet ci-dessus) ne renvoie jamais qu'une Lesson classique -
    // cette page n'est jamais atteinte pour une inédite (voir EpreuveInediteDetailPage).
    previewEpreuve(epreuve.slug as string).then(setPreview).catch(() => {})
  }, [epreuve])

  useEffect(() => {
    // Recanonicalise vers /{pays}/epreuves/{slug} dès que le pays réel de l'épreuve
    // est connu - couvre à la fois les anciens liens sans préfixe pays (voir
    // App.tsx) et un préfixe pays incorrect dans l'URL visitée (jamais deux URLs
    // différentes indexables pour le même contenu).
    if (!epreuve) return
    const canonicalCountry = epreuve.subject.country.code.toLowerCase()
    if (country !== canonicalCountry) {
      navigate(epreuveDetailPath(canonicalCountry, epreuve.slug as string), { replace: true })
    }
  }, [epreuve, country, navigate])

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

  // Décidé sur exercises_count (déjà là avec l'épreuve) et non sur preview.exercises,
  // qui arrive une requête plus tard : sinon la page se réagence sous les yeux du
  // visiteur une fois le sujet chargé. Même seuil et même grille que le lecteur
  // (EpreuveReaderPage) - un sommaire d'une seule entrée ne ferait que rétrécir la
  // colonne de lecture.
  const hasSommaire = epreuve.exercises_count > 1

  return (
    <div className={`mx-auto px-4 py-8 sm:px-6 ${hasSommaire ? "max-w-5xl" : "max-w-3xl"}`}>
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
            {epreuve.est_vitrine && (
              <Badge variant="success">
                <Sparkles className="mr-1 size-3" />
                Corrigé en accès libre
              </Badge>
            )}
            <Badge variant="secondary">{epreuve.subject.label}</Badge>
            {epreuve.nature_epreuve_display && (
              <Badge variant="outline">{epreuve.nature_epreuve_display}</Badge>
            )}
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
              <Link to={epreuveReaderPath(epreuve.subject.country.code.toLowerCase(), epreuve.slug as string)}>
                {epreuve.lesson_type === "FICHE" ? (
                  <>
                    <Zap />
                    Réviser cette fiche
                  </>
                ) : (
                  <>
                    <BookOpenText />
                    Lire le corrigé
                  </>
                )}
              </Link>
            </Button>
          )}
        </div>

        {/* Consulter l'épreuve : le sujet (énoncés seuls) est public, voir
            access.views.preview_lesson côté backend - toujours affiché ici, abonné ou non. */}
        {preview && (
          <div className="mt-2 border-t border-border pt-5">
            <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">Sujet</h2>
            {preview.exercises.length > 0 ? (
              <div
                className={
                  hasSommaire
                    ? "lg:grid lg:grid-cols-[220px_minmax(0,1fr)] lg:items-start lg:gap-10"
                    : undefined
                }
              >
                {hasSommaire && <EpreuveSommaire exercises={preview.exercises} />}
                <div className="flex min-w-0 flex-col gap-8">
                  {preview.exercises.map((exercise) => (
                    <div
                      key={exercise.numero_exercice}
                      id={exerciceAnchorId(exercise.numero_exercice)}
                      className="scroll-mt-24"
                    >
                      <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
                        <EpreuveMarkdown markdown={exercise.enonce_markdown} />
                      </article>
                      {/* Bloqué sur cet exercice précisément : on renvoie vers SON corrigé,
                          pas vers le haut d'un corrigé qu'il faudrait re-défiler. Réservé aux
                          abonnés - sinon c'est le bloc "S'abonner" ci-dessous qui prend le relais. */}
                      {epreuve.has_access && (
                        <Link
                          to={`${epreuveReaderPath(epreuve.subject.country.code.toLowerCase(), epreuve.slug as string)}#${exerciceAnchorId(exercise.numero_exercice)}`}
                          className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
                        >
                          <BookOpenText className="size-4" />
                          Lire le corrigé de cet exercice
                          <ArrowRight className="size-3.5" />
                        </Link>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
                <EpreuveMarkdown markdown={preview.preview_markdown} />
              </article>
            )}
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
              <ParrainageHint />
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
                  to={cours.has_access ? coursReaderPath(cours.slug) : coursDetailPath(cours.slug)}
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

        <div className="mt-2 border-t border-border pt-5">
          <Link
            to={`${catalogueHomePath(epreuve.subject.country.code.toLowerCase())}?origine=INEDITE#catalogue`}
            className="group flex items-center justify-between gap-3 rounded-lg border border-dashed border-gold/40 bg-gold/5 px-4 py-3 text-sm transition-colors hover:border-gold/60 hover:bg-gold/10"
          >
            <span className="flex items-center gap-2">
              <Crown className="size-4 shrink-0 text-gold" />
              <span>
                <span className="font-medium">Envie d'aller plus loin ?</span>{" "}
                <span className="text-muted-foreground">Teste-toi sur une épreuve jamais vue, en conditions réelles.</span>
              </span>
            </span>
            <ArrowRight className="size-3.5 shrink-0 text-primary opacity-0 transition-opacity group-hover:opacity-100" />
          </Link>
        </div>

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
