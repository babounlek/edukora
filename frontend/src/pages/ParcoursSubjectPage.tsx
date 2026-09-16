import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, ArrowRight, BookOpenText, CheckCircle2, Compass, RotateCcw, Search, Sparkles } from "lucide-react"

import { getParcours, listMySubscriptions, listSubjects, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ParcoursModule, ParcoursSavoir, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Etape, Eyebrow, StatChip } from "@/components/Configurateur"
import { SommaireNav, type SommaireEntry } from "@/components/SommaireNav"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { coursDetailPath } from "@/lib/countryPath"
import { SEUIL_MAITRISE, tauxBarClassName } from "@/lib/maitrise"
import { subjectIcon } from "@/lib/subjectIcon"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn } from "@/lib/utils"

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

// Au-delà de ce nombre de savoirs affichés dans un même module, la carte passe en
// pagination "Afficher plus" - sans ça, le mode Parcours par fréquence (un seul
// pseudo-module qui peut dépasser 200 thèmes, voir isModeFrequence) rendait une page
// d'un seul tenant, bien plus longue que n'importe quel module du programme classique.
// Même palier que FICHES_RECENTES_VISIBLES dans FichesPage.tsx (même principe de
// divulgation progressive), sans lien de valeur entre les deux.
const SAVOIRS_PAGE_SIZE = 25

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

/** Savoirs d'un module à afficher compte tenu du filtre "Afficher tout" - même
 * critère que le bouton de bascule sous la carte "prochaines étapes", factorisé ici
 * pour servir à la fois au rendu de chaque Card module et au sommaire de navigation
 * (un module sans savoir affiché ne doit pas non plus apparaître dans le sommaire). */
function savoirsVisibles(module: ParcoursModule, afficherTout: boolean): ParcoursSavoir[] {
  if (afficherTout) return module.savoirs
  return module.savoirs.filter((s) => {
    const bucket = bucketDeSavoir(s)
    return bucket === "en_revision" || bucket === "a_decouvrir"
  })
}

function BadgeSavoir({ savoir }: { savoir: ParcoursSavoir }) {
  // "gold" reprend la même convention que tauxBarClassName/RotateCcw ailleurs sur la
  // page (or = zone "à réviser") - un simple "outline" rendait ce statut aussi discret
  // que "Contenu à venir", alors que c'est le plus urgent à repérer en balayant la liste.
  if (savoir.en_revision) return <Badge variant="gold">À réviser</Badge>
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

/** Actions d'une étape (liste par module ET "prochaines étapes") : un seul CTA
 * principal - le quiz s'il existe, sinon le premier cours candidat - plutôt qu'un
 * bouton par cours candidat empilé à côté du quiz : la ligne indiquait jusqu'ici
 * jusqu'à 4-5 boutons d'un coup, sans dire lequel faire en premier. Pas de "Voir tous
 * les cours" ici (retiré le 2026-09-16, le lien vers le catalogue filtré ne menait
 * nulle part d'utilisable) - le premier cours candidat reste la seule porte d'entrée
 * vers les cours de ce savoir. `arrow` accentue le CTA quiz dans la carte "prochaines
 * étapes" (mise en avant), pas dans la liste. */
function ActionsSavoir({
  savoir, starting, onQuiz, size, arrow,
}: {
  savoir: ParcoursSavoir
  starting: boolean
  onQuiz: () => void
  size?: "sm"
  arrow?: boolean
}) {
  const premierCours = savoir.cours[0]
  return (
    <div className="flex flex-wrap items-center gap-2">
      {savoir.has_quiz && (
        // Toujours ouvert dans un nouvel onglet : ce Parcours reste affiché pendant
        // le quiz plutôt que de disparaître derrière une navigation en place.
        <Button size={size} disabled={starting} onClick={() => onQuiz()}>
          {starting ? "Préparation..." : "Tester mes connaissances"}
          {arrow && <ArrowRight />}
        </Button>
      )}
      {premierCours && (
        <Button asChild size={size} variant={savoir.has_quiz ? "outline" : "default"}>
          <Link to={coursDetailPath(premierCours.slug)}>
            <BookOpenText />
            {premierCours.sous_theme ? capitaliserTheme(premierCours.sous_theme) : "Lire le cours"}
          </Link>
        </Button>
      )}
    </div>
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
  // Nombre de savoirs révélés par module ("module-<numero>", voir sommaireEntries) -
  // absent de la map = encore au premier palier (SAVOIRS_PAGE_SIZE). Un compteur par
  // module plutôt qu'un simple booléen "déplié" : chaque clic sur "Afficher plus"
  // ajoute un palier de plus au lieu de tout révéler d'un coup (moins de contenu qui
  // apparaît en une fois). Réinitialisé au changement de cursus/matière (effet
  // ci-dessous) : sans ça un module resterait déplié pour un programme sans rapport.
  const [visibleParModule, setVisibleParModule] = useState<Record<string, number>>({})
  // Filtre texte sur l'intitulé des savoirs (voir son seuil d'affichage,
  // totalSavoirsAffiches ci-dessous) - contourne la pagination : un thème cherché doit
  // apparaître tout de suite, pas après plusieurs "Afficher plus".
  const [recherche, setRecherche] = useState("")

  useEffect(() => {
    setVisibleParModule({})
    setRecherche("")
  }, [selectedCursus, subjectId])

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

  // numero vide = pseudo-module du mode Parcours par fréquence (voir
  // construire_parcours_par_frequence côté backend) - un seul module, sans numérotation.
  const isModeFrequence = modules?.length === 1 && modules[0].numero === ""
  const savoirs = useMemo(() => (modules ? aplatirSavoirs(modules) : []), [modules])
  const etapes = useMemo(() => prochainesEtapes(savoirs), [savoirs])
  const buckets = useMemo(() => compterBuckets(savoirs), [savoirs])
  const totalAvecContenu = savoirs.length - buckets.sans_contenu
  const pourcentageMaitrise = totalAvecContenu > 0 ? Math.round((100 * buckets.maitrises) / totalAvecContenu) : 0

  // Sommaire de navigation entre modules - seulement utile à partir de 2 modules
  // effectivement affichés (voir SommaireNav, qui se masque déjà si `entries` est
  // vide) ; le mode Parcours par fréquence n'a qu'un seul pseudo-module donc ne
  // l'affiche jamais. `long` reste court ("Module N") pour la sidebar desktop, le
  // titre complet du module n'apparaissant qu'en infobulle et dans la Card elle-même.
  const sommaireEntries: SommaireEntry[] = useMemo(() => {
    if (!modules || modules.length < 2) return []
    const rechercheNormalisee = recherche.trim().toLowerCase()
    return modules
      .filter((m) => {
        const visibles = savoirsVisibles(m, afficherTout)
        if (!rechercheNormalisee) return visibles.length > 0
        return visibles.some((s) => s.intitule.toLowerCase().includes(rechercheNormalisee))
      })
      .map((m) => ({
        id: `module-${m.numero || "unique"}`,
        short: m.numero ? `M${m.numero}` : m.titre,
        long: m.numero ? `Module ${m.numero}` : m.titre,
        title: m.titre,
      }))
  }, [modules, afficherTout, recherche])

  // Décide si le champ de recherche mérite sa place - inutile sur un petit programme
  // que l'œil parcourt déjà d'un coup (voir SAVOIRS_PAGE_SIZE, même palier que la
  // pagination : au-delà, balayer visuellement devient plus lent que taper un mot).
  const totalSavoirsAffiches = useMemo(
    () => (modules ? modules.reduce((sum, m) => sum + savoirsVisibles(m, afficherTout).length, 0) : 0),
    [modules, afficherTout],
  )

  async function lancerQuiz(
    params: { savoir?: number; theme?: number; mode?: "DIAGNOSTIC" },
    openInNewTab = false,
  ) {
    if (starting || !subjectId) return
    setStarting(true)
    setError("")
    // Ouvert tout de suite, de façon synchrone dans le gestionnaire de clic - après un
    // await, la plupart des navigateurs ne rattachent plus un window.open() au geste
    // utilisateur et le bloquent comme un pop-up. On ouvre donc un onglet vide dès
    // maintenant, qu'on redirige une fois la session créée (pas de noopener : on doit
    // garder la référence pour le rediriger, la destination reste notre propre site).
    const nouvelOnglet = openInNewTab ? window.open("", "_blank") : null
    try {
      const session = await startQuizSession({
        cursus: Number(selectedCursus),
        subject: Number(subjectId),
        n: params.mode === "DIAGNOSTIC" ? 20 : 10,
        ...params,
      })
      trackEvent("quiz_started", { cursus_id: Number(selectedCursus), mode: params.mode ?? "PRATIQUE", source: "parcours" })
      const url = `/quiz/session/${session.id}`
      if (openInNewTab) {
        // Reste sur cette page plutôt que de naviguer : contrairement au cas normal,
        // rien n'unmonte ce composant, donc `starting` doit redescendre à false pour
        // que le bouton reste utilisable dans cet onglet. Repli sur l'onglet courant
        // si l'onglet vide n'a pas pu s'ouvrir (bloqueur de pop-up malgré tout).
        if (nouvelOnglet) nouvelOnglet.location.href = url
        else navigate(url)
        setStarting(false)
      } else {
        navigate(url)
      }
    } catch (err) {
      nouvelOnglet?.close()
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

          {/* Barre + puces de progression - seul endroit de la page qui les affiche
              désormais (voir l'ancienne Card "Ta progression" juste en dessous du hero,
              supprimée : elle répétait presque les mêmes chiffres immédiatement après). */}
          {totalAvecContenu > 0 && (
            <div className="mt-5 max-w-md">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium text-foreground/90">Ta progression</span>
                <span className="font-display font-semibold text-primary">{pourcentageMaitrise}%</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className={cn("h-full rounded-full transition-all", tauxBarClassName(pourcentageMaitrise))}
                  style={{ width: `${pourcentageMaitrise}%` }}
                />
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <StatChip icon={<CheckCircle2 className="size-3.5 text-success" />}>
                  <span className="font-medium">
                    {buckets.maitrises}/{totalAvecContenu}
                  </span>
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
                            <BadgeSavoir savoir={etape} />
                            {isModeFrequence && <OccurrenceBadge savoir={etape} />}
                          </div>
                          <p className="font-display font-medium">
                            {etapes.length > 1 && <span className="text-muted-foreground">{index + 1}. </span>}
                            {capitaliserTheme(etape.intitule)}
                          </p>
                          <ActionsSavoir
                            savoir={etape}
                            starting={starting}
                            onQuiz={() => lancerQuiz(paramsQuizPourSavoir(etape), true)}
                            size={etapes.length > 1 ? "sm" : undefined}
                            arrow
                          />
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

            {totalSavoirsAffiches > SAVOIRS_PAGE_SIZE && (
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={recherche}
                  onChange={(e) => setRecherche(e.target.value)}
                  placeholder="Filtrer les thèmes..."
                  className="pl-9"
                  aria-label="Filtrer les thèmes"
                />
              </div>
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

            {(() => {
              const rechercheNormalisee = recherche.trim().toLowerCase()

              // Masqués par défaut, jamais retirés pour de bon (voir bucketDeSavoir et
              // le bouton juste au-dessus) : la promesse de la page est "ce qu'il te
              // reste à travailler", pas un inventaire complet du programme.
              const cartes = modules.map((module) => {
                const savoirsAffiches = savoirsVisibles(module, afficherTout)
                // Rang conservé depuis la liste complète du module (pas l'index dans les
                // résultats de recherche) : un thème trouvé en 3ᵉ position de la
                // recherche garde le numéro qui reflète sa vraie place dans l'ordre de
                // fréquence, pas son rang parmi les seuls résultats.
                const indexes = savoirsAffiches.map((savoir, i) => ({ savoir, rang: i + 1 }))
                const resultats = rechercheNormalisee
                  ? indexes.filter(({ savoir }) => savoir.intitule.toLowerCase().includes(rechercheNormalisee))
                  : indexes
                if (resultats.length === 0) return null

                const moduleKey = module.numero || "unique"
                const visibleCount = visibleParModule[moduleKey] ?? SAVOIRS_PAGE_SIZE
                // Pagination désactivée pendant une recherche : un thème trouvé doit
                // apparaître tout de suite, jamais caché derrière un "Afficher plus".
                const resultatsMontres = rechercheNormalisee ? resultats : resultats.slice(0, visibleCount)
                const resteAAfficher = rechercheNormalisee ? 0 : resultats.length - resultatsMontres.length

                return (
                  <Card key={module.numero} id={`module-${moduleKey}`} className="scroll-mt-24 overflow-hidden">
                    <CardContent className="pt-6">
                      <p className="mb-5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                        {/* numero vide = pseudo-module du mode Parcours par fréquence (voir
                            quiz.services.construire_parcours_par_frequence) - un seul thème
                            de "module" pour toute la matière, "Module ·" n'aurait aucun sens. */}
                        {module.numero ? `Module ${module.numero} · ${module.titre}` : module.titre}
                      </p>
                      <div>
                        {resultatsMontres.map(({ savoir, rang }, index) => (
                          <Etape
                            key={savoir.id}
                            numero={rang}
                            titre={capitaliserTheme(savoir.intitule)}
                            fait={savoir.taux !== null && savoir.taux >= SEUIL_MAITRISE}
                            inactif={!savoir.has_quiz && savoir.cours.length === 0}
                            // Repère or sur les étapes déjà en révision - distinct du bleu
                            // neutre des autres, pour repérer l'urgent d'un simple balayage
                            // de la liste (voir Etape.accent et BadgeSavoir, même code couleur).
                            accent={savoir.en_revision ? "gold" : undefined}
                            dernier={resteAAfficher === 0 && index === resultatsMontres.length - 1}
                          >
                            <div className="flex flex-wrap items-center gap-2">
                              <BadgeSavoir savoir={savoir} />
                              {isModeFrequence && <OccurrenceBadge savoir={savoir} />}
                            </div>
                            <div className="mt-2">
                              <ActionsSavoir
                                savoir={savoir}
                                starting={starting}
                                onQuiz={() => lancerQuiz(paramsQuizPourSavoir(savoir), true)}
                                size="sm"
                              />
                            </div>
                            <SansCoursIndice savoir={savoir} />
                          </Etape>
                        ))}
                      </div>
                      {resteAAfficher > 0 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="mt-4 w-full"
                          onClick={() =>
                            setVisibleParModule((prev) => ({
                              ...prev,
                              [moduleKey]: visibleCount + SAVOIRS_PAGE_SIZE,
                            }))
                          }
                        >
                          Afficher plus
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                )
              })

              if (rechercheNormalisee && cartes.every((carte) => carte === null)) {
                return (
                  <Card>
                    <CardContent className="flex flex-col items-center gap-1 py-10 text-center">
                      <Search className="size-6 text-muted-foreground" />
                      <p className="font-display font-medium">Aucun thème ne correspond à « {recherche.trim()} »</p>
                      <p className="text-sm text-muted-foreground">Essaie un autre mot, ou efface la recherche.</p>
                    </CardContent>
                  </Card>
                )
              }

              // À partir de 2 modules affichés, un sommaire cliquable donne un repère
              // spatial sur un programme long (voir sommaireEntries) - en dessous, la
              // colonne latérale ne ferait que gaspiller de la place pour rien à sauter.
              if (sommaireEntries.length > 1) {
                return (
                  <div className="lg:grid lg:grid-cols-[200px_minmax(0,1fr)] lg:items-start lg:gap-10">
                    <SommaireNav entries={sommaireEntries} ariaLabel="Sommaire des modules" />
                    <div className="flex min-w-0 flex-col gap-6">{cartes}</div>
                  </div>
                )
              }
              return cartes
            })()}
        </div>
      )}

      {error && <p className="mt-4 text-sm text-destructive">{error}</p>}
    </div>
  )
}
