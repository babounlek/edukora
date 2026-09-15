import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, ArrowRight, BookOpenText, CheckCircle2, Compass, RotateCcw, Search, Sparkles } from "lucide-react"

import { getParcours, listMySubscriptions, listSubjects, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ParcoursCours, ParcoursModule, ParcoursSavoir, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Etape, Eyebrow, StatChip } from "@/components/Configurateur"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { coursDetailPath, coursListPath } from "@/lib/countryPath"
import { SEUIL_MAITRISE, tauxBarClassName } from "@/lib/maitrise"
import { subjectIcon } from "@/lib/subjectIcon"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

type SavoirEnrichi = ParcoursSavoir & { moduleTitre: string }

/** `savoir.theme_id` (mode Parcours par fréquence) et `savoir.id` (Module→Savoir
 * classique) ne sont jamais le même paramètre côté /quiz/sessions/ (voir
 * StartQuizSessionParams) - centralise la bascule pour ne pas la répéter à chaque
 * appel de lancerQuiz. */
function paramsQuizPourSavoir(savoir: ParcoursSavoir): { savoir?: number; theme?: number } {
  return savoir.theme_id ? { theme: savoir.theme_id } : { savoir: savoir.id }
}

function aplatirSavoirs(modules: ParcoursModule[]): SavoirEnrichi[] {
  return modules.flatMap((module) => module.savoirs.map((savoir) => ({ ...savoir, moduleTitre: module.titre })))
}

// Nombre d'étapes mises en avant en tête de page - au-delà, la file perdrait son
// intérêt (autant reprendre la liste complète en dessous).
const PROCHAINES_ETAPES_MAX = 3

/** Prochaines étapes recommandées, mises en avant en tête de page plutôt que de
 * laisser l'élève chercher lui-même dans la liste. Aucun historique de quiz du tout
 * sur ce cursus : mieux vaut un test de positionnement (couvre tout le programme
 * d'un coup) qu'un plongeon direct dans le premier savoir. Sinon, priorité à ce qui
 * est déjà en échec (voir RevisionSchedule côté backend), puis aux savoirs jamais
 * maîtrisés dans l'ordre du programme - jusqu'à PROCHAINES_ETAPES_MAX, pour que
 * l'élève puisse enchaîner sans revenir chercher la suite dans la liste à chaque
 * fois. Exclut les savoirs sans aucun contenu (ni quiz ni cours) : les recommander
 * n'aiderait personne, il n'y a rien à y faire (voir compterBuckets, même critère
 * pour "sans_contenu"). */
function prochainesEtapes(savoirs: SavoirEnrichi[]): SavoirEnrichi[] | "diagnostic" {
  const aUnHistorique = savoirs.some((s) => s.taux !== null)
  if (!aUnHistorique) return "diagnostic"
  const actionnables = savoirs.filter((s) => s.has_quiz || s.cours.length > 0)
  const enRevision = actionnables.filter((s) => s.en_revision)
  const nonMaitrises = actionnables.filter((s) => !s.en_revision && (s.taux ?? 0) < SEUIL_MAITRISE)
  return [...enRevision, ...nonMaitrises].slice(0, PROCHAINES_ETAPES_MAX)
}

type BucketSavoir = "maitrise" | "en_revision" | "a_decouvrir" | "sans_contenu"

/** Classement d'un savoir en un seul bucket, priorité identique à
 * quiz.services.resume_parcours côté backend - source unique de vérité pour
 * compterBuckets (l'histogramme du bandeau) ET pour le filtre "Masquer maîtrisés/sans
 * contenu" de la liste ci-dessous, pour que les deux racontent toujours la même
 * histoire (un savoir compté "maîtrisé" en haut de page ne doit jamais apparaître
 * "à réviser" dans la liste filtrée, ou inversement). */
function bucketDeSavoir(s: ParcoursSavoir): BucketSavoir {
  if (!s.has_quiz && s.cours.length === 0) return "sans_contenu"
  if (s.taux !== null && s.taux >= SEUIL_MAITRISE) return "maitrise"
  if (s.en_revision) return "en_revision"
  return "a_decouvrir"
}

function compterBuckets(savoirs: SavoirEnrichi[]) {
  const buckets = { maitrises: 0, en_revision: 0, a_decouvrir: 0, sans_contenu: 0 }
  for (const s of savoirs) {
    const bucket = bucketDeSavoir(s)
    if (bucket === "maitrise") buckets.maitrises++
    else if (bucket === "sans_contenu") buckets.sans_contenu++
    else if (bucket === "en_revision") buckets.en_revision++
    else buckets.a_decouvrir++
  }
  return buckets
}

function BadgeSavoir({ savoir }: { savoir: ParcoursSavoir }) {
  if (savoir.en_revision) return <Badge variant="outline">À réviser</Badge>
  if (savoir.taux !== null && savoir.taux >= SEUIL_MAITRISE) return <Badge variant="success">Maîtrisé</Badge>
  if (savoir.taux !== null) return <Badge variant="outline">{savoir.taux}% de réussite</Badge>
  // Cours lu mais jamais encore quizzé - distinct de "à découvrir" (jamais ouvert du
  // tout), sinon ces deux situations rendent le même badge alors que l'élève sait déjà
  // laquelle des deux le concerne (voir ParcoursSavoir.a_lu_le_cours, calculé côté
  // backend mais jusqu'ici jamais affiché).
  if (savoir.a_lu_le_cours) return <Badge variant="outline">Cours lu</Badge>
  if (savoir.has_quiz || savoir.cours.length > 0) return <Badge variant="outline">À découvrir</Badge>
  return <Badge variant="outline">Contenu à venir</Badge>
}

/** Fréquence d'examen d'un thème (mode Parcours par fréquence uniquement - voir
 * quiz.services.construire_parcours_par_frequence, `nb_epreuves`/`frequence_pct`
 * absents en Module→Savoir classique). Rend explicite ce que le numéro d'ordre
 * seul ne dit pas : sans lui, "3. Dérivation" ne renseigne pas sur l'écart avec le
 * thème suivant. */
function OccurrenceBadge({ savoir }: { savoir: ParcoursSavoir }) {
  if (savoir.nb_epreuves == null) return null
  return (
    <Badge variant="outline" className="text-muted-foreground">
      Vu dans {savoir.nb_epreuves} épreuve{savoir.nb_epreuves > 1 ? "s" : ""} ({savoir.frequence_pct}%)
    </Badge>
  )
}

/** Un savoir peut avoir un quiz sans qu'aucun Cours ne le couvre encore (courant sur
 * les cursus les moins servis en contenu, ex. Terminale A) - sans ce rappel, la ligne
 * ne montre alors qu'un bouton de quiz seul, ce qui se lit comme un oubli plutôt que
 * comme une absence de contenu assumée. */
function SansCoursIndice({ savoir }: { savoir: ParcoursSavoir }) {
  if (savoir.cours.length > 0 || !savoir.has_quiz) return null
  return (
    <p className="mt-1.5 text-xs text-muted-foreground">
      Pas encore de cours sur ce point - tu peux tester tes connaissances directement.
    </p>
  )
}

/** URL du catalogue de cours filtré sur ce savoir précis (voir le nouveau paramètre
 * `savoir` de CoursListView, même relation Cours.tags -> Tag.savoir_officiel que
 * construire_parcours) - permet de dépasser le plafond d'affichage de 3 cours par
 * savoir ici (voir PARCOURS_COURS_PAR_SAVOIR_MAX côté backend), jamais exposé au
 * frontend puisque cette page n'a pas besoin de savoir si elle a été plafonnée. Le
 * matière/cursus restent aussi en filtre pour ne jamais mélanger avec une autre série.
 * `savoir_label` est un paramètre d'affichage pur (jamais lu par l'API), voir
 * CoursListPage. */
function lienCoursDuSavoir(country: string, subjectCode: string, cursusId: string, savoir: ParcoursSavoir): string {
  const params = new URLSearchParams({
    subject: subjectCode,
    cursus: cursusId,
    // theme_id (mode Parcours par fréquence) et id-en-tant-que-Savoir (Module→Savoir
    // classique) ne sont pas le même paramètre côté API (voir catalog.views.
    // CoursListView) - même bascule que lancerQuiz ci-dessous.
    ...(savoir.theme_id ? { theme: String(savoir.theme_id) } : { savoir: String(savoir.id) }),
    savoir_label: savoir.intitule,
  })
  return `${coursListPath(country)}?${params.toString()}`
}

function LienCoursDuSavoir({ href, savoir, size }: { href: string; savoir: ParcoursSavoir; size?: "sm" }) {
  if (savoir.cours.length === 0) return null
  return (
    <Button asChild size={size} variant="ghost">
      <Link to={href}>
        <Search />
        Voir tous les cours
      </Link>
    </Button>
  )
}

/** Un bouton par cours candidat (voir ParcoursSavoir.cours, plusieurs leçons peuvent
 * couvrir un même savoir) plutôt qu'un unique "Lire le cours" générique : le
 * sous-thème (court, curaté - voir catalog.Cours.sous_theme) distingue les cours
 * entre eux, ce que le libellé générique ne permettait pas. Fallback sur le
 * générique pour les rares cours sans sous_theme renseigné. */
function BoutonsCours({ cours, size }: { cours: ParcoursCours[]; size?: "sm" }) {
  return (
    <>
      {cours.map((c) => (
        <Button key={c.slug} asChild size={size} variant="outline">
          <Link to={coursDetailPath(c.slug)}>
            <BookOpenText />
            {c.sous_theme || "Lire le cours"}
          </Link>
        </Button>
      ))}
    </>
  )
}

export function ParcoursSubjectPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const cursusFromUrl = searchParams.get("cursus") ?? ""

  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [selectedCursus, setSelectedCursus] = useState("")
  const [subjectLabel, setSubjectLabel] = useState("")
  const [subjectCode, setSubjectCode] = useState("")
  const [modules, setModules] = useState<ParcoursModule[] | null>(null)
  const [subscriptionsLoaded, setSubscriptionsLoaded] = useState(false)
  const [error, setError] = useState("")
  const [starting, setStarting] = useState(false)
  // Replié par défaut : la promesse de la page est "ce qu'il te reste à travailler",
  // pas un inventaire complet - masquer maîtrisés/sans contenu recentre la liste sans
  // les faire disparaître pour de bon (voir bucketDeSavoir, le bouton juste en dessous).
  const [afficherTout, setAfficherTout] = useState(false)

  useSeo({
    title: subjectLabel ? `Parcours ${subjectLabel}` : "Ton parcours",
    description: "Ce qu'il te reste à travailler pour ta matière, dans l'ordre le plus utile pour progresser.",
  })

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: `/parcours/${subjectId}` } })
      return
    }
    listMySubscriptions()
      .then((subs) => {
        const active = subs.filter((sub) => sub.is_active)
        setSubscriptions(active)
        const depuisUrl = active.find((sub) => String(sub.cursus.id) === cursusFromUrl)
        if (depuisUrl) setSelectedCursus(cursusFromUrl)
        else if (active.length > 0) setSelectedCursus(String(active[0].cursus.id))
      })
      .catch(() => setError("Impossible de charger tes abonnements."))
      .finally(() => setSubscriptionsLoaded(true))
    // cursusFromUrl volontairement omis : ne sert qu'à l'initialisation, pas de
    // resynchronisation si l'utilisateur change ensuite le select ci-dessous.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, isAuthenticated, navigate, subjectId])

  // Résolu depuis le référentiel complet des matières (pas listQuizSubjects, qui
  // n'expose que celles ayant déjà une banque de quiz - une matière encore sans
  // aucun contenu doit quand même pouvoir afficher son libellé ici, on y arrive
  // justement depuis une carte du tableau de bord qui l'affiche grisée).
  useEffect(() => {
    const sub = subscriptions.find((s) => String(s.cursus.id) === selectedCursus)
    if (!sub) return
    listSubjects(sub.cursus.country.code.toLowerCase()).then((data) => {
      const subject = data.find((s) => String(s.id) === subjectId)
      if (subject) {
        setSubjectLabel(subject.label)
        setSubjectCode(subject.code)
      }
    })
  }, [selectedCursus, subscriptions, subjectId])

  useEffect(() => {
    if (!selectedCursus || !subjectId) return
    setModules(null)
    getParcours(Number(selectedCursus), Number(subjectId))
      .then(setModules)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Impossible de charger ton parcours."))
  }, [selectedCursus, subjectId])

  // Pays du cursus sélectionné - nécessaire pour construire un lien vers le
  // catalogue de cours (/:country/cours), qui est préfixé par pays.
  const countryCode = subscriptions
    .find((s) => String(s.cursus.id) === selectedCursus)
    ?.cursus.country.code.toLowerCase()

  // numero vide = pseudo-module du mode Parcours par fréquence (voir
  // construire_parcours_par_frequence côté backend) - un seul module, sans numérotation.
  const isModeFrequence = modules?.length === 1 && modules[0].numero === ""
  const savoirs = useMemo(() => (modules ? aplatirSavoirs(modules) : []), [modules])
  const etapes = useMemo(() => prochainesEtapes(savoirs), [savoirs])
  const buckets = useMemo(() => compterBuckets(savoirs), [savoirs])
  const totalAvecContenu = savoirs.length - buckets.sans_contenu
  const pourcentageMaitrise = totalAvecContenu > 0 ? Math.round((100 * buckets.maitrises) / totalAvecContenu) : 0

  async function lancerQuiz(params: { savoir?: number; theme?: number; mode?: "DIAGNOSTIC" }) {
    if (starting || !subjectId) return
    setStarting(true)
    setError("")
    try {
      const session = await startQuizSession({
        cursus: Number(selectedCursus),
        subject: Number(subjectId),
        n: params.mode === "DIAGNOSTIC" ? 20 : 10,
        ...params,
      })
      trackEvent("quiz_started", { cursus_id: Number(selectedCursus), mode: params.mode ?? "PRATIQUE", source: "parcours" })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible de démarrer ce quiz. Réessaie plus tard.")
      setStarting(false)
    }
  }

  if (authLoading || !subscriptionsLoaded) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <Skeleton className="mb-8 h-56 w-full rounded-2xl" />
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)]">
          <Skeleton className="h-96 w-full rounded-2xl" />
          <Skeleton className="h-64 w-full rounded-2xl" />
        </div>
      </div>
    )
  }

  if (subscriptions.length === 0) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col items-center px-4 py-20 text-center">
        <span className="mb-4 flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
          <Compass className="size-5" />
        </span>
        <p className="font-display text-lg font-semibold">Aucun abonnement actif</p>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          Le parcours te montre exactement ce qu'il te reste à travailler pour cette matière - il te faut un
          abonnement actif pour y accéder.
        </p>
        <Button asChild className="mt-5">
          <Link to="/tarifs">Voir les tarifs</Link>
        </Button>
      </div>
    )
  }

  const SubjectIcon = subjectIcon(subjectCode)

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      <Link
        to="/parcours"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour à tes matières
      </Link>

      <div className="relative mb-8 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6 sm:p-8 lg:p-12">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative max-w-2xl">
          <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <SubjectIcon className="size-5" />
          </div>
          <Eyebrow>Ton parcours</Eyebrow>
          <h1 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">
            {subjectLabel || "Chargement..."}
          </h1>
          <p className="mt-3 max-w-md text-lg font-medium leading-snug text-foreground/90">
            {isModeFrequence
              ? "Les thèmes qui reviennent le plus à l'examen, du plus fréquent au moins fréquent."
              : "Le programme officiel, dans l'ordre - avec ce qu'il te reste à découvrir, réviser ou maîtriser."}
          </p>

          {totalAvecContenu > 0 && (
            <div className="mt-5 flex flex-wrap gap-2">
              <StatChip icon={<CheckCircle2 className="size-3.5 text-success" />}>
                <span className="font-medium">
                  {buckets.maitrises}/{totalAvecContenu}
                </span>
                <span className="text-muted-foreground">savoirs maîtrisés</span>
              </StatChip>
              {buckets.en_revision > 0 && (
                <StatChip icon={<RotateCcw className="size-3.5 text-gold" />}>
                  <span className="font-medium">{buckets.en_revision}</span>
                  <span className="text-muted-foreground">à réviser</span>
                </StatChip>
              )}
            </div>
          )}

          {subscriptions.length > 1 && (
            <div className="mt-5">
              <Select
                value={selectedCursus}
                onValueChange={(value) => {
                  setSelectedCursus(value)
                  setSearchParams({ cursus: value })
                }}
              >
                <SelectTrigger className="w-full sm:w-72">
                  <SelectValue placeholder="Choisir un cursus" />
                </SelectTrigger>
                <SelectContent>
                  {subscriptions.map((sub) => (
                    <SelectItem key={sub.cursus.id} value={String(sub.cursus.id)}>
                      {sub.cursus.examen_display}
                      {sub.cursus.series ? ` - Série ${sub.cursus.series.code}` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
      </div>

      {!modules ? (
        <div className="flex flex-col gap-6">
          <Skeleton className="h-20 w-full rounded-2xl" />
          <Skeleton className="h-96 w-full rounded-2xl" />
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          {/* Récapitulatif en bandeau horizontal plutôt qu'en colonne latérale : sur
              cette page, la liste des modules est le contenu principal et mérite toute
              la largeur - un résumé de progression se lit d'un coup d'œil, il n'a pas
              besoin d'une colonne dédiée qui rétrécit le reste. */}
          <Card>
            <CardContent className="flex flex-col gap-4 pt-6 sm:flex-row sm:items-center sm:gap-6">
              <div className="flex min-w-0 flex-1 items-center gap-3">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Compass className="size-4" />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="font-display text-sm font-semibold">Ta progression</p>
                  {totalAvecContenu > 0 && (
                    <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className={cn("h-full rounded-full transition-all", tauxBarClassName(pourcentageMaitrise))}
                        style={{ width: `${pourcentageMaitrise}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                <StatChip icon={<CheckCircle2 className="size-3.5 text-success" />}>
                  <span className="font-medium">{buckets.maitrises}</span>
                  <span className="text-muted-foreground">maîtrisés</span>
                </StatChip>
                {buckets.en_revision > 0 && (
                  <StatChip icon={<RotateCcw className="size-3.5 text-gold" />}>
                    <span className="font-medium">{buckets.en_revision}</span>
                    <span className="text-muted-foreground">à réviser</span>
                  </StatChip>
                )}
                {buckets.a_decouvrir > 0 && (
                  <StatChip icon={<Compass className="size-3.5 text-muted-foreground" />}>
                    <span className="font-medium">{buckets.a_decouvrir}</span>
                    <span className="text-muted-foreground">à découvrir</span>
                  </StatChip>
                )}
                {buckets.sans_contenu > 0 && (
                  <StatChip icon={<BookOpenText className="size-3.5 text-muted-foreground" />}>
                    <span className="font-medium">{buckets.sans_contenu}</span>
                    <span className="text-muted-foreground">à venir</span>
                  </StatChip>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="flex min-w-0 flex-col gap-6">
            {(etapes === "diagnostic" || etapes.length > 0) && (
              <Card className="overflow-hidden border-primary/20 bg-gradient-to-br from-primary/[0.06] via-transparent to-transparent">
                <CardContent className="pt-6">
                  <p className="flex items-center gap-2 font-display text-sm font-semibold text-primary">
                    <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10">
                      <Sparkles className="size-3.5" />
                    </span>
                    {etapes === "diagnostic" || etapes.length === 1
                      ? "Prochaine étape recommandée"
                      : "Prochaines étapes recommandées"}
                  </p>
                  {etapes === "diagnostic" ? (
                    <>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Tu n'as encore rien tenté sur ce cursus - commence par un test de positionnement pour savoir
                        d'où partir.
                      </p>
                      <Button className="mt-3" disabled={starting} onClick={() => lancerQuiz({ mode: "DIAGNOSTIC" })}>
                        {starting ? "Préparation..." : "Faire le test de positionnement"}
                      </Button>
                    </>
                  ) : (
                    <div className="mt-3 flex flex-col divide-y divide-border/60">
                      {etapes.map((etape, index) => (
                        <div key={etape.id} className={cn("flex flex-col gap-2", index > 0 && "pt-4")}>
                          <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                            <span className="text-xs text-muted-foreground">{etape.moduleTitre}</span>
                            {isModeFrequence && <OccurrenceBadge savoir={etape} />}
                          </div>
                          <p className="font-display font-medium">
                            {etapes.length > 1 && <span className="text-muted-foreground">{index + 1}. </span>}
                            {etape.intitule}
                          </p>
                          <div className="flex flex-wrap gap-2">
                            <BoutonsCours cours={etape.cours} size={etapes.length > 1 ? "sm" : undefined} />
                            {etape.has_quiz && (
                              <Button
                                size={etapes.length > 1 ? "sm" : undefined}
                                disabled={starting}
                                onClick={() => lancerQuiz(paramsQuizPourSavoir(etape))}
                              >
                                {starting ? "Préparation..." : "Tester mes connaissances"}
                                <ArrowRight />
                              </Button>
                            )}
                            {countryCode && (
                              <LienCoursDuSavoir
                                href={lienCoursDuSavoir(countryCode, subjectCode, selectedCursus, etape)}
                                savoir={etape}
                                size={etapes.length > 1 ? "sm" : undefined}
                              />
                            )}
                          </div>
                          <SansCoursIndice savoir={etape} />
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {buckets.maitrises + buckets.sans_contenu > 0 && (
              <button
                type="button"
                onClick={() => setAfficherTout((v) => !v)}
                className="self-start text-sm font-medium text-primary hover:underline"
              >
                {afficherTout
                  ? "Masquer les savoirs maîtrisés et sans contenu"
                  : `Afficher aussi les savoirs maîtrisés et sans contenu (${buckets.maitrises + buckets.sans_contenu})`}
              </button>
            )}

            {!afficherTout && buckets.en_revision + buckets.a_decouvrir === 0 && savoirs.length > 0 && (
              <Card>
                <CardContent className="flex flex-col items-center gap-1 py-10 text-center">
                  <CheckCircle2 className="size-6 text-success" />
                  <p className="font-display font-medium">Tout est maîtrisé ou sans contenu pour l'instant</p>
                  <p className="text-sm text-muted-foreground">
                    Reviens plus tard, ou affiche le détail avec le bouton ci-dessus.
                  </p>
                </CardContent>
              </Card>
            )}

            {modules.map((module) => {
              // Masqués par défaut, jamais retirés pour de bon (voir bucketDeSavoir et
              // le bouton juste au-dessus) : la promesse de la page est "ce qu'il te
              // reste à travailler", pas un inventaire complet du programme.
              const savoirsAffiches = afficherTout
                ? module.savoirs
                : module.savoirs.filter((s) => {
                    const bucket = bucketDeSavoir(s)
                    return bucket === "en_revision" || bucket === "a_decouvrir"
                  })
              if (savoirsAffiches.length === 0) return null

              return (
              <Card key={module.numero} className="overflow-hidden">
                <CardContent className="pt-6">
                  <p className="mb-5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    {/* numero vide = pseudo-module du mode Parcours par fréquence (voir
                        quiz.services.construire_parcours_par_frequence) - un seul thème
                        de "module" pour toute la matière, "Module ·" n'aurait aucun sens. */}
                    {module.numero ? `Module ${module.numero} · ${module.titre}` : module.titre}
                  </p>
                  <div>
                    {savoirsAffiches.map((savoir, index) => (
                      <Etape
                        key={savoir.id}
                        numero={index + 1}
                        titre={savoir.intitule}
                        fait={savoir.taux !== null && savoir.taux >= SEUIL_MAITRISE}
                        inactif={!savoir.has_quiz && savoir.cours.length === 0}
                        dernier={index === savoirsAffiches.length - 1}
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <BadgeSavoir savoir={savoir} />
                          {isModeFrequence && <OccurrenceBadge savoir={savoir} />}
                          <BoutonsCours cours={savoir.cours} size="sm" />
                          {savoir.has_quiz && (
                            <Button size="sm" disabled={starting} onClick={() => lancerQuiz(paramsQuizPourSavoir(savoir))}>
                              Tester mes connaissances
                            </Button>
                          )}
                          {countryCode && (
                            <LienCoursDuSavoir
                              href={lienCoursDuSavoir(countryCode, subjectCode, selectedCursus, savoir)}
                              savoir={savoir}
                              size="sm"
                            />
                          )}
                        </div>
                        <SansCoursIndice savoir={savoir} />
                      </Etape>
                    ))}
                  </div>
                </CardContent>
              </Card>
              )
            })}
          </div>
        </div>
      )}

      {error && <p className="mt-4 text-sm text-destructive">{error}</p>}
    </div>
  )
}
