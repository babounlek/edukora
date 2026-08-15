import { useEffect, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, Clock, Crown, FileDown, GraduationCap, Lock, Sparkles, Unlock } from "lucide-react"

import { downloadSujetPdf, getEpreuveInedite, listPlans, startTentativeInedite } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Epreuve } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { ParrainageHint } from "@/components/ParrainageHint"
import { BackToTopBar } from "@/components/BackToTopBar"
import { CountryBadge } from "@/components/CountryBadge"
import { formatCursusGroups } from "@/lib/cursus"
import { trackEvent } from "@/lib/analytics"
import { formatAmount } from "@/lib/utils"
import { useSeo } from "@/lib/seo"
import { catalogueHomePath, coursDetailPath, coursReaderPath, epreuveInediteDetailPath } from "@/lib/countryPath"

/** Fiche détail d'une épreuve inédite - miroir simplifié d'EpreuveDetailPage.tsx : pas
 * de sujet complet en aperçu public (contrairement à previewEpreuve côté classique,
 * tout le contenu reste gated) - seul apercu_enonce_markdown (une unique question)
 * est public, voir sa section plus bas. "Commencer" crée une tentative (POST) plutôt
 * que de mener directement à un lecteur. */
export function EpreuveInediteDetailPage() {
  const { country: countryParam, id } = useParams<{ country?: string; id: string }>()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [epreuve, setEpreuve] = useState<Epreuve | null>(null)
  const [error, setError] = useState("")
  const [starting, setStarting] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [minPrice, setMinPrice] = useState<number | null>(null)

  useSeo({
    title: epreuve?.title ?? "Épreuve inédite",
    description: epreuve
      ? `${epreuve.subject.label} - épreuve inédite jamais vue, jamais publiée ailleurs.`
      : undefined,
  })

  useEffect(() => {
    if (!id) return
    getEpreuveInedite(id)
      .then(setEpreuve)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Impossible de charger cette épreuve."))
  }, [id])

  useEffect(() => {
    // ?ref=pdf_sujet_inedit : posé par le PDF du sujet (voir backend
    // inedit.sujet_pdf._epreuve_deep_link) - même mécanique que EpreuveDetailPage.tsx,
    // mais ce lecteur est déjà abonné (ce PDF est privé, voir la note de partage
    // affichée dessus) : on mesure ici un retour vers l'appli depuis un sujet
    // imprimé, pas une acquisition.
    if (!epreuve) return
    if (searchParams.get("ref") !== "pdf_sujet_inedit") return
    trackEvent("pdf_sujet_inedit_landing", { subject_code: epreuve.subject.code })
  }, [epreuve, searchParams])

  useEffect(() => {
    // Recanonicalise vers /{pays}/epreuves-inedites/{slug} dès que l'épreuve réelle
    // est connue - même principe que EpreuveDetailPage.tsx (préfixe pays), étendu au
    // slug lui-même : un ancien lien par id (voir EpreuveInedite.slug, résolu en
    // lecture côté backend pour compat) ne doit jamais rester l'URL affichée/indexée
    // une fois le slug connu - jamais deux URLs différentes pour le même contenu.
    if (!epreuve || !epreuve.slug) return
    const canonicalCountry = epreuve.subject.country.code.toLowerCase()
    if (countryParam !== canonicalCountry || id !== epreuve.slug) {
      navigate(epreuveInediteDetailPath(canonicalCountry, epreuve.slug), { replace: true })
    }
  }, [epreuve, countryParam, id, navigate])

  useEffect(() => {
    // Prix d'appel affiché sur le mur payant (voir plus bas) - inutile si l'élève a
    // déjà accès. Formule la moins chère qui débloque réellement l'add-on (inclut_inedit),
    // jamais le prix d'Essentiel/Performance qui ne débloqueraient pas cette épreuve.
    if (!epreuve || epreuve.has_access) return
    const cursusId = epreuve.cursus[0]?.id
    if (!cursusId) return
    listPlans(cursusId).then((plans) => {
      const eligibles = plans.filter((p) => p.inclut_inedit)
      if (eligibles.length === 0) return
      setMinPrice(Math.min(...eligibles.map((p) => p.price)))
    })
  }, [epreuve])

  async function handleStart() {
    if (!epreuve || starting) return
    setStarting(true)
    setError("")
    try {
      const tentative = await startTentativeInedite(epreuve.id)
      navigate(`/inedit/tentative/${tentative.id}`)
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Impossible de démarrer cette épreuve pour le moment. Réessaie plus tard.",
      )
      setStarting(false)
    }
  }

  async function handleDownloadPdf() {
    if (!epreuve || downloading) return
    setDownloading(true)
    setError("")
    try {
      await downloadSujetPdf(epreuve.id)
    } catch {
      setError("Impossible d'ouvrir l'épreuve pour le moment. Réessaie plus tard.")
    } finally {
      setDownloading(false)
    }
  }

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
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-3">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-5 w-1/2" />
          <Skeleton className="h-10 w-40" />
        </div>
      </div>
    )
  }

  const country = epreuve.subject.country.code.toLowerCase()

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
          <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">{epreuve.title}</h1>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <CountryBadge code={epreuve.subject.country.code} label={epreuve.subject.country.label} />
            <Badge variant="gold" className="gap-1">
              <Crown className="size-3" />
              Épreuve inédite
            </Badge>
            <Badge variant="secondary">{epreuve.subject.label}</Badge>
            {formatCursusGroups(epreuve.cursus).map((group) => (
              <Badge key={group.key} variant="outline">{group.label}</Badge>
            ))}
            {epreuve.duree_minutes && (
              <Badge variant="outline">
                <Clock className="mr-1 size-3" />
                Durée indicative : {epreuve.duree_minutes} min
              </Badge>
            )}
            {epreuve.exercises_count > 0 && (
              <Badge variant="outline">
                {epreuve.exercises_count} exercice{epreuve.exercises_count > 1 ? "s" : ""}
              </Badge>
            )}
          </div>
        </div>

        <p className="text-sm text-muted-foreground">
          Une épreuve d'examen jamais vue, jamais publiée ailleurs - même niveau, même structure, même barème que
          l'examen réel. Le seul moyen de te tester en conditions réelles sans déjà connaître les réponses.
        </p>

        {/* Aperçu public minimal : une seule question, jamais le sujet entier (voir
            catalog.inedit_bridge._apercu_enonce_markdown côté backend) - donner le
            niveau sans dévoiler l'épreuve ni compromettre les conditions d'examen. */}
        {epreuve.apercu_enonce_markdown && (
          <div className="border-t border-border pt-5">
            <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">Aperçu</h2>
            <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display">
              <EpreuveMarkdown markdown={epreuve.apercu_enonce_markdown} />
            </article>
            <p className="mt-3 text-xs text-muted-foreground">
              Le reste de l'épreuve reste inédit jusqu'à ce que tu la commences.
            </p>
          </div>
        )}

        <div className="mt-2 flex flex-wrap gap-2 border-t border-border pt-5">
          {/* Contrairement à "Cours associés" plus bas, le PDF du sujet n'est PAS un teaser :
              il ne doit apparaître que pour un abonné Max de ce cursus (has_access), sous
              peine de proposer un bouton qui échoue systématiquement en 403 côté serveur
              (voir inedit.views.download_sujet_pdf, gated par has_access_inedite). */}
          {epreuve.sujet_pdf_disponible && epreuve.has_access && (
            <Button size="lg" variant="outline" onClick={handleDownloadPdf} disabled={downloading}>
              <FileDown />
              {downloading ? "Ouverture..." : "Ouvrir l'épreuve en PDF"}
            </Button>
          )}
          {epreuve.has_access ? (
            <Button size="lg" onClick={handleStart} disabled={starting}>
              <Sparkles />
              {starting ? "Préparation..." : "Commencer cette épreuve"}
            </Button>
          ) : (
            <div className="flex w-full flex-col gap-3 rounded-lg border border-dashed border-border bg-muted/40 p-4">
              <p className="flex items-center gap-1.5 text-sm font-medium">
                <Lock className="size-4 shrink-0" />
                Réservée aux abonnés de la formule Max sur ce cursus.
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <Button asChild size="lg" className="w-fit">
                  {/* require=inedit : SubscribePage ne propose alors que les formules qui
                      débloquent réellement l'add-on Épreuves Inédites (voir sa docstring) -
                      sans ça, rien n'empêchait de repartir avec Essentiel/Performance. */}
                  <Link to={`/abonnement?cursus=${epreuve.cursus[0]?.id}&require=inedit`}>Débloquer avec Max</Link>
                </Button>
                {minPrice !== null && (
                  <span className="text-sm text-muted-foreground">à partir de {formatAmount(minPrice)} FCFA par an</span>
                )}
              </div>
              <ParrainageHint />
            </div>
          )}
        </div>

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

        {error && <p className="text-sm text-destructive">{error}</p>}

        <BackToTopBar links={[{ to: catalogueHomePath(country), label: "Retour au catalogue" }]} />
      </div>
    </div>
  )
}
