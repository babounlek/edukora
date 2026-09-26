import { useEffect, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, ArrowRight, BookOpenText, Check, Crown, FileDown, Lock, Sparkles, Unlock, Zap } from "lucide-react"

import { getEpreuve, previewEpreuve } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Epreuve, EpreuvePreview } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { exerciceAnchorId, libelleLong } from "@/components/EpreuveSommaire"
import { ParrainageHint } from "@/components/ParrainageHint"
import { RelatedEpreuves } from "@/components/RelatedEpreuves"
import { BackToTopBar } from "@/components/BackToTopBar"
import { CountryBadge } from "@/components/CountryBadge"
import { EnTeteEpreuve, faitsEpreuve } from "@/components/EnTeteEpreuve"
import { formatCursusGroups } from "@/lib/cursus"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { cn } from "@/lib/utils"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { coursDetailPath, coursReaderPath, epreuveDetailPath, epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"

export function EpreuveDetailPage() {
  const { country, slug } = useParams<{ country?: string; slug: string }>()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isAuthenticated, isLoading: authLoading } = useAuth()

  const [epreuve, setEpreuve] = useState<Epreuve | null>(null)
  const [preview, setPreview] = useState<EpreuvePreview | null>(null)
  const [error, setError] = useState("")

  useSeo({
    title: epreuve?.title ?? "Corrigé",
    description: epreuve
      ? `${epreuve.lesson_type_display} de ${epreuve.subject.label}${epreuve.year ? ` (${epreuve.year})` : ""} - sujet en accès libre, corrigé détaillé par abonnement.`
      : undefined,
  })

  useEffect(() => {
    if (!slug) return
    getEpreuve(slug)
      .then(setEpreuve)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          setError("Cette épreuve n'existe pas ou n'est plus disponible.")
        } else {
          setError(err instanceof ApiError ? err.message : "Impossible de charger cette épreuve.")
        }
      })
  }, [slug])

  // Le premier appel ci-dessus part avant que la session ne soit reconfirmée (voir
  // AuthContext - l'access token ne survit jamais à un rechargement de page) : un
  // abonné qui arrive ici juste après un F5 peut recevoir un has_access calculé en
  // anonyme. On recharge une fois la session confirmée pour corriger un has_access
  // qui aurait été sous-évalué - jamais déclenché pour un visiteur réellement
  // anonyme (isAuthenticated resterait false), donc sans coût pour l'aperçu public.
  useEffect(() => {
    if (authLoading || !isAuthenticated || !slug) return
    getEpreuve(slug).then(setEpreuve)
  }, [authLoading, isAuthenticated, slug])

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
    // Le sujet arrive en asynchrone (effet ci-dessus) : au moment où le navigateur
    // traite le #hash d'une URL partagée (ex. .../exercices d'un thème, posé par
    // ThemeExercicesPage), la cible n'existe pas encore dans le DOM et le saut n'a pas
    // lieu. On le rejoue une fois les exercices rendus - même correctif que
    // EpreuveReaderPage, jamais au montage.
    if (!preview) return
    const id = window.location.hash.slice(1)
    if (!id) return
    document.getElementById(id)?.scrollIntoView()
  }, [preview])

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

  if (error && !epreuve) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link to="/" className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour au catalogue
        </Link>
      </div>
    )
  }

  if (!epreuve) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-3">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-5 w-1/2" />
          <Skeleton className="h-10 w-40" />
        </div>
      </div>
    )
  }

  const countryCode = epreuve.subject.country.code.toLowerCase()
  const cursusGroupes = formatCursusGroups(epreuve.cursus).map((g) => g.label).join(" · ")
  const lecteur = epreuveReaderPath(countryCode, epreuve.slug as string)
  const exercices = preview?.exercises ?? []

  return (
    <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-8">
      <Link
        to={epreuvesListPath(countryCode)}
        className="mb-5 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour au catalogue
      </Link>

      <div className="flex animate-fade-up flex-col gap-6">
        <EnTeteEpreuve
          titre={epreuve.title}
          matiereCode={epreuve.subject.code}
          matiere={epreuve.subject.label}
          cursus={cursusGroupes}
          session={epreuve.year}
          faits={faitsEpreuve({
            exercices: epreuve.exercises_count,
            duree: epreuve.duree_epreuve,
            coefficient: epreuve.coefficient,
          })}
          badges={
            <>
              <CountryBadge code={epreuve.subject.country.code} label={epreuve.subject.country.label} />
              {epreuve.est_vitrine && (
                <Badge variant="success" className="gap-1">
                  <Sparkles className="size-3" />
                  Corrigé en accès libre
                </Badge>
              )}
              <Badge variant="outline">{epreuve.lesson_type_display}</Badge>
              {epreuve.nature_epreuve_display && <Badge variant="outline">{epreuve.nature_epreuve_display}</Badge>}
              {epreuve.origine !== "OFFICIEL" && (
                <Badge variant="outline">
                  {epreuve.origine_display}
                  {epreuve.etablissement ? ` - ${epreuve.etablissement}` : ""}
                </Badge>
              )}
              {/* Jamais en doublon de l'établissement, déjà affiché juste avant quand c'est lui
                  l'organisateur (épreuve d'établissement). */}
              {epreuve.institution && epreuve.institution !== epreuve.etablissement && (
                <Badge variant="outline">{epreuve.institution}</Badge>
              )}
            </>
          }
        >
          {epreuve.has_access && (
            <Button asChild size="lg" className="group h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5">
              <Link to={lecteur}>
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
                <ArrowRight className="transition-transform group-hover:translate-x-1" />
              </Link>
            </Button>
          )}
          {epreuve.sujet_pdf_url && (
            <Button asChild variant="outline" size="lg" className="h-12 rounded-full">
              <a href={epreuve.sujet_pdf_url} target="_blank" rel="noopener noreferrer">
                <FileDown />
                Télécharger l'épreuve
              </a>
            </Button>
          )}
        </EnTeteEpreuve>

        {/* Pas d'accès : la proposition vient tout de suite après l'en-tête, avec ce qu'elle
            débloque - et non en bas de page, après un sujet entier, quand l'envie est retombée. Le
            sujet reste en libre accès, dit franchement. */}
        {!epreuve.has_access && (
          <section className="relative overflow-hidden rounded-3xl border border-primary/25 bg-gradient-to-br from-primary/[0.08] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-7">
            <div className="flex items-start gap-4">
              <span className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <Lock className="size-6" aria-hidden="true" />
              </span>
              <div className="min-w-0">
                <h2 className="font-display text-xl font-semibold sm:text-2xl">Débloque le corrigé complet</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Le sujet ci-dessous est en libre accès. La correction détaillée est réservée aux abonnés
                  {epreuve.cursus.length > 1 ? " (l'un des cursus suivants suffit)" : ""}.
                </p>
              </div>
            </div>
            <ul className="mt-5 grid gap-2 sm:grid-cols-3">
              {[
                "Correction pas à pas, exercice par exercice",
                "Cours et rappels de méthode liés",
                "Quiz et suivi de ta progression",
              ].map((avantage) => (
                <li key={avantage} className="flex items-start gap-2 rounded-xl bg-background/70 px-3 py-2.5 text-sm">
                  <Check className="mt-0.5 size-4 shrink-0 text-primary" strokeWidth={3} aria-hidden="true" />
                  {avantage}
                </li>
              ))}
            </ul>
            <div className="mt-5 flex flex-wrap gap-2">
              {epreuve.cursus.map((c) => (
                <Button key={c.id} asChild size="lg" className="h-12 rounded-full px-6 shadow-lg shadow-primary/25">
                  <Link to={`/abonnement?cursus=${c.id}`}>
                    S'abonner{epreuve.cursus.length > 1 ? ` (${c.series ? c.series.code : c.examen_display})` : ""}
                    <ArrowRight />
                  </Link>
                </Button>
              ))}
            </div>
            <div className="mt-4">
              <ParrainageHint />
            </div>
          </section>
        )}

        {/* Au programme : les exercices d'un coup d'œil, chacun un lien vers son énoncé (et vers son
            corrigé pour un abonné). C'est ce qui donne envie d'ouvrir : on voit ce qu'on va travailler. */}
        {exercices.length > 1 && (
          <section aria-labelledby="au-programme">
            <h2 id="au-programme" className="mb-3 font-display text-xl font-semibold">
              Au programme
            </h2>
            <ol className="grid gap-2.5 sm:grid-cols-2">
              {exercices.map((exercise, index) => (
                <li key={exercise.numero_exercice}>
                  <a
                    href={`#${exerciceAnchorId(exercise.numero_exercice)}`}
                    className="group flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3 transition-colors hover:border-primary/40"
                  >
                    <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 font-display text-sm font-semibold text-primary">
                      {index + 1}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium" title={exercise.titre || undefined}>
                        {libelleLong(exercise)}
                      </span>
                    </span>
                    {exercise.points && (
                      <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs font-medium tabular-nums text-muted-foreground">
                        {exercise.points} pts
                      </span>
                    )}
                  </a>
                </li>
              ))}
            </ol>
          </section>
        )}

        {/* Consulter l'épreuve : le sujet (énoncés seuls) est public, voir
            access.views.preview_lesson côté backend - toujours affiché ici, abonné ou non. */}
        {preview && (
          <section aria-labelledby="le-sujet">
            <h2 id="le-sujet" className="mb-3 font-display text-xl font-semibold">
              Le sujet
            </h2>
            {preview.introduction_markdown && (
              // Consigne d'épreuve entière - voir EpreuveReaderPage, même contenu que côté lecture
              // abonnée, ici avant même le premier exercice.
              <div className="prose prose-neutral mb-5 max-w-none rounded-2xl border border-border bg-muted/40 p-4 text-justify dark:prose-invert">
                <EpreuveMarkdown markdown={preview.introduction_markdown} />
              </div>
            )}
            {exercices.length > 0 ? (
              <div className="flex min-w-0 flex-col gap-5">
                {exercices.map((exercise, index) => (
                  <div
                    key={exercise.numero_exercice}
                    id={exerciceAnchorId(exercise.numero_exercice)}
                    className="scroll-mt-24 rounded-3xl border border-border bg-card p-4 shadow-sm sm:p-6"
                  >
                    <div className="mb-3 flex items-center gap-3">
                      <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary font-display text-sm font-semibold text-primary-foreground shadow-sm shadow-primary/30">
                        {index + 1}
                      </span>
                      <p className="min-w-0 flex-1 truncate font-display text-base font-semibold" title={exercise.titre || undefined}>
                        {libelleLong(exercise)}
                      </p>
                      {exercise.points && (
                        <span className="shrink-0 rounded-full bg-muted px-2.5 py-0.5 text-xs font-medium tabular-nums text-muted-foreground">
                          {exercise.points} pts
                        </span>
                      )}
                    </div>
                    <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
                      <EpreuveMarkdown markdown={exercise.enonce_markdown} />
                    </article>
                    {/* Bloqué sur cet exercice précisément : on renvoie vers SON corrigé, pas vers le
                        haut d'un corrigé qu'il faudrait re-défiler. Réservé aux abonnés - sinon c'est le
                        bloc "Débloque le corrigé" plus haut qui prend le relais. */}
                    {epreuve.has_access && (
                      <Link
                        to={`${lecteur}#${exerciceAnchorId(exercise.numero_exercice)}`}
                        className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3.5 py-1.5 text-sm font-medium text-primary transition-colors hover:bg-primary/15"
                      >
                        <BookOpenText className="size-4" />
                        Lire le corrigé de cet exercice
                        <ArrowRight className="size-3.5" />
                      </Link>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display prose-hr:my-8">
                <EpreuveMarkdown markdown={preview.preview_markdown} />
              </article>
            )}
          </section>
        )}

        {epreuve.related_cours.length > 0 && (
          <section aria-labelledby="cours-associes">
            <h2 id="cours-associes" className="mb-3 font-display text-xl font-semibold">
              Cours associés
            </h2>
            <div className="grid gap-2.5 sm:grid-cols-2">
              {epreuve.related_cours.map((cours) => {
                const CoursIcone = subjectIcon(epreuve.subject.code)
                return (
                  <Link
                    key={cours.id}
                    to={cours.has_access ? coursReaderPath(cours.slug) : coursDetailPath(cours.slug)}
                    className="group flex items-center gap-3 rounded-2xl border border-border bg-card px-4 py-3 text-sm transition-colors hover:border-primary/40"
                  >
                    <span className={cn("flex size-9 shrink-0 items-center justify-center rounded-xl", couleurMatiere(epreuve.subject.code).puce)}>
                      <CoursIcone className="size-4" aria-hidden="true" />
                    </span>
                    <span className="min-w-0 flex-1 font-medium leading-snug">{cours.titre}</span>
                    {cours.has_access ? (
                      <Unlock className="size-4 shrink-0 text-success" aria-label="Inclus" />
                    ) : (
                      <Lock className="size-4 shrink-0 text-muted-foreground" aria-label="Abonnement requis" />
                    )}
                  </Link>
                )
              })}
            </div>
          </section>
        )}

        <Link
          to={`${epreuvesListPath(countryCode)}?origine=INEDITE`}
          className="group flex items-center justify-between gap-3 rounded-2xl border border-dashed border-gold/40 bg-gold/5 px-5 py-4 text-sm transition-colors hover:border-gold/60 hover:bg-gold/10"
        >
          <span className="flex items-center gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold">
              <Crown className="size-5" />
            </span>
            <span>
              <span className="block font-medium">Envie d'aller plus loin ?</span>
              <span className="text-muted-foreground">Teste-toi sur une épreuve jamais vue, en conditions réelles.</span>
            </span>
          </span>
          <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-1" />
        </Link>

        <RelatedEpreuves
          subjectCode={epreuve.subject.code}
          subjectLabel={epreuve.subject.label}
          countryCode={countryCode}
          cursusId={epreuve.cursus[0]?.id}
          excludeId={epreuve.id}
        />

        <BackToTopBar links={[{ to: epreuvesListPath(countryCode), label: "Retour au catalogue" }]} />
      </div>
    </div>
  )
}
