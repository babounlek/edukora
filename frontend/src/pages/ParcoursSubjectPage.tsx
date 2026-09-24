import { useEffect, useMemo, useState } from "react"
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ArrowLeft, ArrowRight, BookOpenText, Check, CheckCircle2, Compass, Eye, EyeOff, GraduationCap, RotateCcw, Search,
  Sparkles, Target,
} from "lucide-react"

import { getParcours, listMySubscriptions, listSubjects, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ParcoursModule, ParcoursSavoir, ResumeMatiere, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { AnneauProgression, BarreSegmentee, Ecrin, LegendeProgression } from "@/components/Progression"
import { SommaireNav, type SommaireEntry } from "@/components/SommaireNav"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { coursDetailPath } from "@/lib/countryPath"
import { SEUIL_MAITRISE } from "@/lib/maitrise"
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

type BucketSavoir = "maitrise" | "en_revision" | "en_cours" | "a_decouvrir" | "sans_contenu"

/** Classement d'un savoir en un seul bucket, priorité identique à
 * quiz.services.resume_parcours côté backend - source unique de vérité pour
 * compterBuckets (l'histogramme du bandeau) ET pour le filtre "Masquer maîtrisés/sans
 * contenu" de la liste ci-dessous, pour que les deux racontent toujours la même
 * histoire (un savoir compté "maîtrisé" en haut de page ne doit jamais apparaître
 * "à réviser" dans la liste filtrée, ou inversement).
 *
 * "en_cours" (taux connu, pas encore maîtrisé, pas dans la file de révision) est
 * distinct de "a_decouvrir" (jamais pratiqué) - un savoir peut GRADUER hors de la
 * file de révision (Leitner, 3 réussites consécutives) tout en gardant une moyenne
 * historique sous SEUIL_MAITRISE, puisque le taux ne s'efface jamais. Sans cette
 * distinction, ce travail redevenait invisible dans l'agrégat dès qu'il quittait la
 * file de révision. */
function bucketDeSavoir(s: ParcoursSavoir): BucketSavoir {
  if (!s.has_quiz && s.cours.length === 0) return "sans_contenu"
  if (s.taux !== null && s.taux >= SEUIL_MAITRISE) return "maitrise"
  if (s.en_revision) return "en_revision"
  if (s.taux !== null) return "en_cours"
  return "a_decouvrir"
}

function compterBuckets(savoirs: SavoirEnrichi[]) {
  const buckets = { maitrises: 0, en_revision: 0, en_cours: 0, a_decouvrir: 0, sans_contenu: 0 }
  for (const s of savoirs) {
    const bucket = bucketDeSavoir(s)
    if (bucket === "maitrise") buckets.maitrises++
    else if (bucket === "sans_contenu") buckets.sans_contenu++
    else if (bucket === "en_revision") buckets.en_revision++
    else if (bucket === "en_cours") buckets.en_cours++
    else buckets.a_decouvrir++
  }
  return buckets
}

/** Savoirs d'un module à afficher compte tenu du filtre "Afficher tout" - même
 * critère que le bouton de bascule sous la carte "prochaines étapes", factorisé ici
 * pour servir à la fois au rendu de chaque carte module et au sommaire de navigation
 * (un module sans savoir affiché ne doit pas non plus apparaître dans le sommaire). */
function savoirsVisibles(module: ParcoursModule, afficherTout: boolean): ParcoursSavoir[] {
  if (afficherTout) return module.savoirs
  return module.savoirs.filter((s) => {
    const bucket = bucketDeSavoir(s)
    return bucket === "en_revision" || bucket === "en_cours" || bucket === "a_decouvrir"
  })
}

function libelleCursus(sub: Subscription): string {
  return `${sub.cursus.examen_display}${sub.cursus.series ? ` ${sub.cursus.series.code}` : ""}`
}

/** Pastille de statut d'un savoir. Or = "à réviser", la même convention que les
 * barres et les compteurs du haut : c'est le statut le plus urgent à repérer en
 * balayant la liste, il ne doit jamais être aussi discret que "Contenu à venir". */
function BadgeSavoir({ savoir }: { savoir: ParcoursSavoir }) {
  const base = "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium"
  if (savoir.en_revision) {
    return (
      <span className={cn(base, "bg-gold/15 text-gold-foreground dark:text-gold")}>
        <RotateCcw className="size-3" />À réviser
      </span>
    )
  }
  if (savoir.taux !== null && savoir.taux >= SEUIL_MAITRISE) {
    return (
      <span className={cn(base, "bg-primary/10 text-primary")}>
        <Check className="size-3" strokeWidth={3} />Maîtrisé
      </span>
    )
  }
  const neutre = cn(base, "border border-border/80 text-muted-foreground")
  if (savoir.taux !== null) return <span className={neutre}>{savoir.taux}% de réussite</span>
  // Cours lu mais jamais encore quizzé - distinct de "à découvrir" (jamais ouvert du
  // tout), sinon ces deux situations rendent le même badge alors que l'élève sait déjà
  // laquelle des deux le concerne (voir ParcoursSavoir.a_lu_le_cours).
  if (savoir.a_lu_le_cours) return <span className={neutre}>Cours lu</span>
  if (savoir.has_quiz || savoir.cours.length > 0) return <span className={neutre}>À découvrir</span>
  return <span className={cn(neutre, "border-dashed")}>Contenu à venir</span>
}

/** Fréquence d'examen d'un thème (mode Parcours par fréquence uniquement - voir
 * quiz.services.construire_parcours_par_frequence, `nb_epreuves`/`frequence_pct`
 * absents en Module→Savoir classique). Rend explicite ce que le numéro d'ordre
 * seul ne dit pas : sans lui, "3. Dérivation" ne renseigne pas sur l'écart avec le
 * thème suivant. Une mini-jauge en plus du chiffre : l'écart entre deux thèmes se
 * voit alors d'un simple balayage de la liste. */
function Frequence({ savoir }: { savoir: ParcoursSavoir }) {
  if (savoir.nb_epreuves == null) return null
  return (
    <span className="inline-flex items-center gap-2 text-[11px] text-muted-foreground">
      <span className="h-1 w-12 overflow-hidden rounded-full bg-gold/15" aria-hidden>
        <span className="block h-full rounded-full bg-gold" style={{ width: `${Math.min(100, savoir.frequence_pct ?? 0)}%` }} />
      </span>
      Vu dans {savoir.nb_epreuves} épreuve{savoir.nb_epreuves > 1 ? "s" : ""} ({savoir.frequence_pct}%)
    </span>
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
  savoir, starting, onQuiz, size, arrow, className,
}: {
  savoir: ParcoursSavoir
  starting: boolean
  onQuiz: () => void
  size?: "sm"
  arrow?: boolean
  className?: string
}) {
  const premierCours = savoir.cours[0]
  return (
    <div className={cn("flex flex-wrap items-center gap-2", className)}>
      {savoir.has_quiz && (
        // Toujours ouvert dans un nouvel onglet : ce Parcours reste affiché pendant
        // le quiz plutôt que de disparaître derrière une navigation en place.
        <Button
          size={size}
          disabled={starting}
          onClick={() => onQuiz()}
          className={cn("group rounded-full", arrow && "shadow-md shadow-primary/20")}
        >
          {starting ? "Préparation..." : "Tester mes connaissances"}
          {arrow && <ArrowRight className="transition-transform group-hover:translate-x-0.5" />}
        </Button>
      )}
      {premierCours && (
        <Button asChild size={size} variant={savoir.has_quiz ? "outline" : "default"} className="max-w-full rounded-full">
          <Link to={coursDetailPath(premierCours.slug)}>
            <BookOpenText />
            <span className="truncate">
              {premierCours.sous_theme ? capitaliserTheme(premierCours.sous_theme) : "Lire le cours"}
            </span>
          </Link>
        </Button>
      )}
    </div>
  )
}

/**
 * Un savoir de la liste : un jalon sur un fil vertical. Le jalon dit l'état d'un
 * coup d'œil (coche verte = maîtrisé, or = à réviser, gris = sans contenu), la ligne
 * garde le rang dans l'ordre du programme ou de la fréquence.
 */
function LigneSavoir({
  savoir, rang, dernier, isModeFrequence, starting, onQuiz,
}: {
  savoir: ParcoursSavoir
  rang: number
  dernier: boolean
  isModeFrequence: boolean
  starting: boolean
  onQuiz: () => void
}) {
  const bucket = bucketDeSavoir(savoir)
  const inactif = bucket === "sans_contenu"
  return (
    <div className="relative flex gap-4 pb-2">
      {!dernier && (
        <span
          aria-hidden
          className={cn("absolute bottom-0 left-[17px] top-10 w-px", bucket === "maitrise" ? "bg-primary/40" : "bg-border")}
        />
      )}
      <span
        className={cn(
          "relative mt-3 flex size-9 shrink-0 items-center justify-center rounded-full font-display text-sm font-semibold tabular-nums",
          bucket === "maitrise" && "bg-primary text-primary-foreground shadow-sm shadow-primary/30 ring-4 ring-primary/10",
          bucket === "en_revision" && "bg-gold/20 text-gold-foreground ring-4 ring-gold/10 dark:text-gold",
          bucket === "en_cours" && "bg-info/15 text-info ring-4 ring-info/10",
          bucket === "a_decouvrir" && "bg-primary/10 text-primary",
          inactif && "bg-muted text-muted-foreground",
        )}
      >
        {bucket === "maitrise" ? <Check className="size-4" strokeWidth={3} /> : rang}
      </span>
      <div
        className={cn(
          "min-w-0 flex-1 rounded-2xl px-3 py-3 transition-colors sm:px-4",
          inactif ? "opacity-60" : "hover:bg-primary/[0.035]",
        )}
      >
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <p className="font-display text-base font-semibold leading-snug">{capitaliserTheme(savoir.intitule)}</p>
            <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1.5">
              <BadgeSavoir savoir={savoir} />
              {isModeFrequence && <Frequence savoir={savoir} />}
            </div>
            <SansCoursIndice savoir={savoir} />
          </div>
          {!inactif && (
            <div className="shrink-0 sm:max-w-[55%]">
              <ActionsSavoir savoir={savoir} starting={starting} onQuiz={onQuiz} size="sm" className="sm:justify-end" />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function Compteur({ valeur, libelle, pastille }: { valeur: number; libelle: string; pastille: string }) {
  return (
    <div className="rounded-2xl border border-border/70 bg-background/70 px-3 py-3 backdrop-blur-sm sm:px-4">
      <p className="flex items-center gap-1.5 whitespace-nowrap text-[11px] text-muted-foreground sm:text-xs">
        <span className={cn("inline-block size-2 shrink-0 rounded-full", pastille)} />
        {libelle}
      </p>
      <p className="mt-1 font-display text-2xl font-semibold tabular-nums sm:text-3xl">{valeur}</p>
    </div>
  )
}

function Squelette() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <Skeleton className="mb-6 h-6 w-40 rounded-full" />
      <Skeleton className="mb-8 h-80 w-full rounded-3xl" />
      <Skeleton className="mb-6 h-48 w-full rounded-3xl" />
      <Skeleton className="h-96 w-full rounded-3xl" />
    </div>
  )
}

export function ParcoursSubjectPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const cursusFromUrl = searchParams.get("cursus") ?? ""

  const [cursusChoisi, setCursusChoisi] = useState("")
  const [error, setError] = useState("")
  const [starting, setStarting] = useState(false)
  // Replié par défaut : la promesse de la page est "ce qu'il te reste à travailler",
  // pas un inventaire complet - masquer maîtrisés/sans contenu recentre la liste sans
  // les faire disparaître pour de bon (voir bucketDeSavoir, le bouton de bascule).
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
    if (!authLoading && !isAuthenticated) navigate("/connexion", { state: { from: `/parcours/${subjectId}` } })
  }, [authLoading, isAuthenticated, navigate, subjectId])

  const { data: subscriptions, isError: erreurAbonnements } = useQuery({
    queryKey: ["mes-abonnements"],
    queryFn: listMySubscriptions,
    enabled: isAuthenticated,
  })
  const actifs = useMemo(() => subscriptions?.filter((sub) => sub.is_active) ?? [], [subscriptions])

  // Le cursus de l'URL est pris au mot tant que la liste des abonnements n'est pas
  // arrivée : le parcours part ainsi en même temps qu'elle au lieu d'attendre derrière
  // (la page enchaînait session → abonnements → matières → parcours, quatre allers-
  // retours en file). Une fois la liste là, un cursus de l'URL sans abonnement actif
  // retombe sur le premier abonnement, comme avant.
  const parDefaut = subscriptions
    ? (actifs.find((sub) => String(sub.cursus.id) === cursusFromUrl) ?? actifs[0])?.cursus.id.toString() ?? ""
    : cursusFromUrl
  const selectedCursus = cursusChoisi || parDefaut

  useEffect(() => {
    setVisibleParModule({})
    setRecherche("")
  }, [selectedCursus, subjectId])

  const { data: modules, error: erreurParcours } = useQuery({
    queryKey: ["parcours", selectedCursus, subjectId],
    queryFn: () => getParcours(Number(selectedCursus), Number(subjectId)),
    enabled: isAuthenticated && Boolean(selectedCursus) && Boolean(subjectId),
  })

  // Le nom de la matière : déjà en cache quand on arrive depuis Ma progression (le
  // résumé le porte), sinon depuis le référentiel complet des matières - pas
  // listQuizSubjects, qui n'expose que celles ayant déjà une banque de quiz (une
  // matière encore sans contenu doit quand même afficher son libellé ici).
  const depuisResume = queryClient
    .getQueryData<ResumeMatiere[]>(["parcours-resume", Number(selectedCursus)])
    ?.find((m) => String(m.subject_id) === subjectId)
  const pays = actifs.find((s) => String(s.cursus.id) === selectedCursus)?.cursus.country.code.toLowerCase() ?? ""
  const { data: matieresDuPays } = useQuery({
    queryKey: ["subjects", pays],
    queryFn: ({ signal }) => listSubjects(pays, signal),
    enabled: Boolean(pays) && !depuisResume,
  })
  const depuisReferentiel = matieresDuPays?.find((s) => String(s.id) === subjectId)
  const subjectLabel = depuisResume?.subject_label ?? depuisReferentiel?.label ?? ""
  const subjectCode = depuisResume?.subject_code ?? depuisReferentiel?.code ?? ""

  useSeo({
    title: subjectLabel ? `Parcours ${subjectLabel}` : "Ton parcours",
    description: "Ce qu'il te reste à travailler pour ta matière, dans l'ordre le plus utile pour progresser.",
  })

  // numero vide = pseudo-module du mode Parcours par fréquence (voir
  // construire_parcours_par_frequence côté backend) - un seul module, sans numérotation.
  const isModeFrequence = modules?.length === 1 && modules[0].numero === ""
  const savoirs = useMemo(() => (modules ? aplatirSavoirs(modules) : []), [modules])
  const etapes = useMemo(() => prochainesEtapes(savoirs), [savoirs])
  const buckets = useMemo(() => compterBuckets(savoirs), [savoirs])
  const totalAvecContenu = savoirs.length - buckets.sans_contenu

  // Sommaire de navigation entre modules - seulement utile à partir de 2 modules
  // effectivement affichés (voir SommaireNav, qui se masque déjà si `entries` est
  // vide) ; le mode Parcours par fréquence n'a qu'un seul pseudo-module donc ne
  // l'affiche jamais. `long` reste court ("Module N") pour la sidebar desktop, le
  // titre complet du module n'apparaissant qu'en infobulle et dans la carte elle-même.
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

  if (erreurAbonnements) {
    return <p className="mx-auto max-w-5xl px-4 py-10 text-sm text-destructive sm:px-6">Impossible de charger tes abonnements.</p>
  }
  // La page s'affiche dès que le parcours est là, même si la liste des abonnements
  // n'est pas encore arrivée (voir parDefaut).
  if (authLoading || (!subscriptions && !modules)) return <Squelette />

  if (subscriptions && actifs.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <Ecrin className="text-center">
          <span className="mx-auto mb-4 flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
            <Compass className="size-5" />
          </span>
          <p className="font-display text-xl font-semibold">Aucun abonnement actif</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
            Le parcours te montre exactement ce qu'il te reste à travailler pour cette matière - il te faut un
            abonnement actif pour y accéder.
          </p>
          <Button asChild className="mt-5 rounded-full px-6">
            <Link to="/tarifs">Voir les tarifs</Link>
          </Button>
        </Ecrin>
      </div>
    )
  }

  const SubjectIcon = subjectIcon(subjectCode)
  const abonnementAffiche = actifs.find((sub) => String(sub.cursus.id) === selectedCursus)
  const erreurChargement = error || (erreurParcours
    ? erreurParcours instanceof ApiError ? erreurParcours.message : "Impossible de charger ton parcours."
    : "")

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <Link
        to="/parcours"
        className="group mb-5 inline-flex items-center gap-1.5 rounded-full border border-border/80 bg-card px-3 py-1 text-sm text-muted-foreground transition-colors hover:border-primary/30 hover:text-primary"
      >
        <ArrowLeft className="size-4 transition-transform group-hover:-translate-x-0.5" />
        Toutes mes matières
      </Link>

      <Ecrin>
        <div className="flex items-start justify-between gap-6">
          <div className="min-w-0">
            <div className="flex items-center gap-3">
              <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-md shadow-primary/25">
                <SubjectIcon className="size-5" />
              </span>
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Ton parcours</p>
            </div>
            <h1 className="mt-4 font-display text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl">
              {subjectLabel || <span className="inline-block h-11 w-64 max-w-full animate-pulse rounded-xl bg-muted align-middle" />}
            </h1>
            <p className="mt-3 max-w-lg text-base leading-snug text-muted-foreground sm:text-lg">
              {isModeFrequence
                ? "Les thèmes qui reviennent le plus à l'examen, du plus fréquent au moins fréquent."
                : "Le programme officiel, dans l'ordre - avec ce qu'il te reste à découvrir, réviser ou maîtriser."}
            </p>
          </div>
          {totalAvecContenu > 0 && (
            <AnneauProgression
              part={buckets.maitrises / totalAvecContenu}
              className="hidden sm:block sm:size-32 [&>span]:text-3xl"
            />
          )}
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-2">
          {/* Plusieurs abonnements : un sélecteur segmenté, les autres choix restent
              visibles ; un seul : le cursus en pastille, pour savoir de quel
              programme on parle. */}
          {actifs.length > 1 ? (
            <div role="group" aria-label="Cursus" className="inline-flex flex-wrap rounded-full border border-border/80 bg-muted/60 p-1">
              {actifs.map((sub) => (
                <button
                  key={sub.cursus.id}
                  type="button"
                  aria-pressed={String(sub.cursus.id) === selectedCursus}
                  onClick={() => {
                    setCursusChoisi(String(sub.cursus.id))
                    setSearchParams({ cursus: String(sub.cursus.id) })
                  }}
                  className={cn(
                    "rounded-full px-3.5 py-1 text-xs font-medium transition-all",
                    String(sub.cursus.id) === selectedCursus
                      ? "bg-background text-primary shadow-sm ring-1 ring-primary/25"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  {libelleCursus(sub)}
                </button>
              ))}
            </div>
          ) : (
            abonnementAffiche && (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-border/80 bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground">
                <GraduationCap className="size-3.5 text-primary" />
                {libelleCursus(abonnementAffiche)}
              </span>
            )
          )}
          {isModeFrequence && (
            <span className="inline-flex items-center gap-1.5 rounded-full border border-gold/40 bg-gold/10 px-3 py-1 text-xs font-medium">
              <Target className="size-3.5" />
              Classé par fréquence à l'examen
            </span>
          )}
        </div>

        {/* Seul endroit de la page qui affiche ces chiffres - une ancienne carte "Ta
            progression" juste en dessous les répétait presque à l'identique. */}
        {totalAvecContenu > 0 && (
          <>
            <div className="mt-6 flex items-center gap-4 sm:hidden">
              <AnneauProgression part={buckets.maitrises / totalAvecContenu} />
              <p className="text-sm text-muted-foreground">
                <span className="font-semibold tabular-nums text-foreground">{buckets.maitrises}</span> sur{" "}
                <span className="tabular-nums">{totalAvecContenu}</span> maîtrisé{buckets.maitrises > 1 ? "s" : ""}
              </p>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-3">
              <Compteur valeur={buckets.maitrises} libelle="Maîtrisés" pastille="bg-primary" />
              <Compteur valeur={buckets.en_revision} libelle="À réviser" pastille="bg-gold" />
              <Compteur valeur={buckets.en_cours} libelle="En cours" pastille="bg-info" />
              <Compteur valeur={buckets.a_decouvrir} libelle="À découvrir" pastille="bg-muted ring-1 ring-border" />
            </div>
            <BarreSegmentee
              className="mt-4 h-2.5"
              maitrises={buckets.maitrises}
              enRevision={buckets.en_revision}
              enCours={buckets.en_cours}
              exploitables={totalAvecContenu}
            />
            {buckets.sans_contenu > 0 && (
              <p className="mt-2 text-xs text-muted-foreground">
                + {buckets.sans_contenu} savoir{buckets.sans_contenu > 1 ? "s" : ""} dont le contenu arrive bientôt.
              </p>
            )}
          </>
        )}
      </Ecrin>

      {!modules ? (
        erreurParcours ? null : (
          <div className="mt-8 flex flex-col gap-6">
            <Skeleton className="h-48 w-full rounded-3xl" />
            <Skeleton className="h-96 w-full rounded-3xl" />
          </div>
        )
      ) : (
        <div className="mt-8 flex min-w-0 flex-col gap-6">
          {(etapes === "diagnostic" || etapes.length > 0) && (
            <section className="animate-fade-up rounded-3xl border border-primary/20 bg-gradient-to-br from-primary/[0.07] via-card to-card p-5 sm:p-7">
              <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                <Sparkles className="size-3.5" />
                {etapes === "diagnostic" || etapes.length === 1 ? "Prochaine étape recommandée" : "À faire maintenant"}
              </p>
              {etapes === "diagnostic" ? (
                <div className="mt-3 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="max-w-lg">
                    <p className="font-display text-2xl font-semibold tracking-tight">Commence par te situer</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Tu n'as encore rien tenté sur ce cursus - un test de positionnement de 20 questions dit d'où
                      partir, sur tout le programme d'un coup.
                    </p>
                  </div>
                  <Button
                    size="lg"
                    className="group h-12 shrink-0 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5"
                    disabled={starting}
                    onClick={() => lancerQuiz({ mode: "DIAGNOSTIC" })}
                  >
                    <Target className="size-4" />
                    {starting ? "Préparation..." : "Faire le test de positionnement"}
                  </Button>
                </div>
              ) : (
                <div className={cn("mt-4 grid gap-3", etapes.length > 1 && "md:grid-cols-2", etapes.length > 2 && "lg:grid-cols-3")}>
                  {etapes.map((etape, index) => (
                    <div
                      key={etape.id}
                      className="flex flex-col rounded-2xl border border-border/70 bg-card/90 p-4 shadow-sm backdrop-blur-sm"
                    >
                      <div className="flex items-center justify-between gap-2">
                        {etapes.length > 1 && (
                          <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                            {index + 1}
                          </span>
                        )}
                        <BadgeSavoir savoir={etape} />
                      </div>
                      <p className="mt-3 font-display text-lg font-semibold leading-snug">
                        {capitaliserTheme(etape.intitule)}
                      </p>
                      {!isModeFrequence && (
                        <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">{etape.moduleTitre}</p>
                      )}
                      {isModeFrequence && <div className="mt-1.5"><Frequence savoir={etape} /></div>}
                      <SansCoursIndice savoir={etape} />
                      <div className="mt-auto pt-4">
                        <ActionsSavoir
                          savoir={etape}
                          starting={starting}
                          onQuiz={() => lancerQuiz(paramsQuizPourSavoir(etape), true)}
                          size="sm"
                          arrow
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}

          {/* Barre d'outils de la liste : bascule "tout afficher", légende et, sur un
              programme long, la recherche - regroupées sur une ligne plutôt qu'empilées. */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
              <h2 className="font-display text-2xl font-semibold tracking-tight">
                {isModeFrequence ? "Tous les thèmes" : "Le programme"}
              </h2>
              {buckets.maitrises + buckets.sans_contenu > 0 && (
                <button
                  type="button"
                  onClick={() => setAfficherTout((v) => !v)}
                  aria-pressed={afficherTout}
                  className="inline-flex items-center gap-1.5 rounded-full border border-border/80 bg-card px-3 py-1 text-xs font-medium text-muted-foreground transition-colors hover:border-primary/30 hover:text-primary"
                >
                  {afficherTout ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                  {afficherTout
                    ? "Masquer maîtrisés et sans contenu"
                    : `Afficher aussi maîtrisés et sans contenu (${buckets.maitrises + buckets.sans_contenu})`}
                </button>
              )}
            </div>
            {totalSavoirsAffiches > SAVOIRS_PAGE_SIZE && (
              <div className="relative sm:w-64">
                <Search className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={recherche}
                  onChange={(e) => setRecherche(e.target.value)}
                  placeholder="Filtrer les thèmes..."
                  className="rounded-full pl-10"
                  aria-label="Filtrer les thèmes"
                />
              </div>
            )}
          </div>

          {!afficherTout && buckets.en_revision + buckets.en_cours + buckets.a_decouvrir === 0 && savoirs.length > 0 && (
            <Ecrin variante="sobre" className="text-center">
              <span className="mx-auto flex size-12 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/25 ring-4 ring-primary/10">
                <CheckCircle2 className="size-6" />
              </span>
              <p className="mt-3 font-display text-lg font-semibold">Tout est maîtrisé ou sans contenu pour l'instant</p>
              <p className="text-sm text-muted-foreground">Reviens plus tard, ou affiche le détail avec le bouton ci-dessus.</p>
            </Ecrin>
          )}

          {(() => {
            const rechercheNormalisee = recherche.trim().toLowerCase()

            // Masqués par défaut, jamais retirés pour de bon (voir bucketDeSavoir et
            // la bascule juste au-dessus) : la promesse de la page est "ce qu'il te
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
              // Avancement du module sur TOUS ses savoirs avec contenu, pas seulement
              // ceux affichés : masquer les maîtrisés ne doit pas faire chuter la barre.
              const avecContenu = module.savoirs.filter((s) => bucketDeSavoir(s) !== "sans_contenu")
              const maitrisesModule = avecContenu.filter((s) => bucketDeSavoir(s) === "maitrise").length
              const revisionModule = avecContenu.filter((s) => bucketDeSavoir(s) === "en_revision").length
              const enCoursModule = avecContenu.filter((s) => bucketDeSavoir(s) === "en_cours").length

              return (
                <section
                  key={module.numero}
                  id={`module-${moduleKey}`}
                  className="scroll-mt-24 overflow-hidden rounded-3xl border border-border/70 bg-card shadow-sm"
                >
                  <header className="flex flex-col gap-3 border-b border-border/60 bg-gradient-to-r from-primary/[0.05] to-transparent px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
                    <div className="flex min-w-0 items-center gap-3">
                      {/* numero vide = pseudo-module du mode Parcours par fréquence (voir
                          quiz.services.construire_parcours_par_frequence) - un seul
                          "module" pour toute la matière, "Module ·" n'aurait aucun sens. */}
                      {module.numero && (
                        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 font-display text-base font-semibold text-primary">
                          {module.numero}
                        </span>
                      )}
                      <div className="min-w-0">
                        {module.numero && (
                          <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                            Module {module.numero}
                          </p>
                        )}
                        <p className="font-display text-lg font-semibold leading-snug">{module.titre}</p>
                      </div>
                    </div>
                    {avecContenu.length > 0 && (
                      <div className="flex shrink-0 items-center gap-3 sm:w-48">
                        <BarreSegmentee
                          className="flex-1"
                          maitrises={maitrisesModule}
                          enRevision={revisionModule}
                          enCours={enCoursModule}
                          exploitables={avecContenu.length}
                        />
                        <span className="text-xs tabular-nums text-muted-foreground">
                          {maitrisesModule}/{avecContenu.length}
                        </span>
                      </div>
                    )}
                  </header>
                  <div className="px-3 py-4 sm:px-5">
                    {resultatsMontres.map(({ savoir, rang }, index) => (
                      <LigneSavoir
                        key={savoir.id}
                        savoir={savoir}
                        rang={rang}
                        dernier={resteAAfficher === 0 && index === resultatsMontres.length - 1}
                        isModeFrequence={isModeFrequence}
                        starting={starting}
                        onQuiz={() => lancerQuiz(paramsQuizPourSavoir(savoir), true)}
                      />
                    ))}
                    {resteAAfficher > 0 && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="mt-3 w-full rounded-full"
                        onClick={() =>
                          setVisibleParModule((prev) => ({
                            ...prev,
                            [moduleKey]: visibleCount + SAVOIRS_PAGE_SIZE,
                          }))
                        }
                      >
                        Afficher plus ({resteAAfficher} restant{resteAAfficher > 1 ? "s" : ""})
                      </Button>
                    )}
                  </div>
                </section>
              )
            })

            if (rechercheNormalisee && cartes.every((carte) => carte === null)) {
              return (
                <Ecrin variante="sobre" className="text-center">
                  <Search className="mx-auto size-6 text-muted-foreground" />
                  <p className="mt-2 font-display text-lg font-semibold">Aucun thème ne correspond à « {recherche.trim()} »</p>
                  <p className="text-sm text-muted-foreground">Essaie un autre mot, ou efface la recherche.</p>
                </Ecrin>
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

          <LegendeProgression />
        </div>
      )}

      {erreurChargement && <p className="mt-4 text-sm text-destructive">{erreurChargement}</p>}
    </div>
  )
}
