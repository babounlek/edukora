import { useEffect, useRef, useState, type ReactNode } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import {
  ArrowRight,
  CheckCircle2,
  Crown,
  FileText,
  Layers,
  ListChecks,
  Lock,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react"

import { getThemesFrequents, listMySubscriptions, listQuizSubjects, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ModeQuiz, Subject, Subscription, ThemeFrequent } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { abonnementsActifsDuProfil } from "@/lib/changerCursusPrepare"
import { useCountry } from "@/context/CountryContext"
import { EtapesPresentation, StatChip } from "@/components/Configurateur"
import { DemoQuizQuestion } from "@/components/DemoQuizQuestion"
import { FiltreLigne, PastilleFiltre } from "@/components/FiltresCatalogue"
import { AnneauFrequence } from "@/components/AnneauFrequence"
import { ReviserTabs } from "@/components/ReviserTabs"
import { lienExercicesTheme } from "@/components/ThemesFrequents"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { themesFrequentsPath } from "@/lib/countryPath"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { subjectShortLabel } from "@/lib/subjectLabel"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn, formatAmount } from "@/lib/utils"

// Nombres de questions proposés. Le maximum n'est pas connu du client (contrairement à
// /fiches, aucun endpoint d'éligibilité ici) : le backend sert simplement moins de
// questions si la banque est plus courte (voir quiz.services.generer_session, qui
// tronque au lieu d'échouer). 30 reste un plafond raisonnable pour une seule séance.
const N_MAX = 30
const N_PRESETS = [5, 10, 15, 20, 30]
// Thèmes fréquents proposés en lancement direct - le classement complet reste sur
// /themes-frequents.
const NB_THEMES_CIBLES = 6

/** Aperçu des matières/questions d'un cursus DÉCLARÉ (gratuit) mais pas encore abonné -
 * remplace la question de démo générique par la vraie structure de la banque de quiz,
 * verrou sur le lancement d'une séance, SAUF sur le thème vitrine d'une matière s'il y
 * en a un (voir CompetenceItem.est_vitrine, project_gating_non_abonne_quiz_parcours) :
 * ce thème-là se lance en entier, sans abonnement - un vrai essai plutôt qu'une démo. */
function ApercuMatieresQuiz({ cursusId, subjects }: { cursusId: number; subjects: Subject[] }) {
  const navigate = useNavigate()
  const [starting, setStarting] = useState<number | null>(null)
  const [error, setError] = useState("")
  const total = subjects.reduce((somme, s) => somme + (s.nb_questions ?? 0), 0)

  async function essayerGratuitement(subject: Subject) {
    if (subject.vitrine_theme_id == null || starting !== null) return
    setStarting(subject.id)
    setError("")
    try {
      const session = await startQuizSession({
        cursus: cursusId, subject: subject.id, theme: subject.vitrine_theme_id, mode: "PRATIQUE", n: N_MAX,
      })
      trackEvent("quiz_started", { cursus_id: cursusId, mode: "PRATIQUE", source: "vitrine" })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible de démarrer cet essai. Réessaie plus tard.")
      setStarting(null)
    }
  }

  return (
    <Card className="overflow-hidden rounded-2xl border-primary/25 bg-gradient-to-br from-primary/5 via-transparent to-transparent shadow-lg shadow-primary/5">
      <CardContent className="flex flex-col gap-4 pt-6">
        <div className="flex items-start gap-3">
          <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
            <Lock className="size-5" />
          </span>
          <div>
            <p className="font-display text-lg font-semibold">
              <span className="tabular-nums">{formatAmount(total)}</span> question{total > 1 ? "s" : ""} sur ton programme
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              Abonne-toi pour lancer une séance - voici déjà tout ce qu'il y a à réviser.
            </p>
          </div>
        </div>
        <ul className="flex flex-col divide-y divide-border/60 overflow-hidden rounded-xl border border-border/70">
          {subjects.map((subject) => {
            const SubjectIcon = subjectIcon(subject.code)
            return (
              <li key={subject.id} className="flex items-center justify-between gap-3 bg-card px-3.5 py-2.5">
                <span className="flex min-w-0 items-center gap-2.5">
                  <span className={cn("flex size-7 shrink-0 items-center justify-center rounded-full", couleurMatiere(subject.code).puce)}>
                    <SubjectIcon className="size-3.5" aria-hidden="true" />
                  </span>
                  <span className="truncate text-sm font-medium">{subject.label}</span>
                </span>
                <span className="flex shrink-0 items-center gap-2">
                  <span className="text-xs tabular-nums text-muted-foreground">
                    {subject.nb_questions ?? 0} question{(subject.nb_questions ?? 0) > 1 ? "s" : ""}
                  </span>
                  {subject.vitrine_theme_id != null && (
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={starting !== null}
                      onClick={() => essayerGratuitement(subject)}
                      className="h-7 rounded-full px-2.5 text-xs"
                    >
                      {starting === subject.id ? "Préparation..." : "Essayer gratuitement"}
                    </Button>
                  )}
                </span>
              </li>
            )
          })}
        </ul>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <Button asChild size="lg" className="w-full sm:w-auto">
          <a href="/tarifs">
            Voir les tarifs
            <ArrowRight className="size-4" />
          </a>
        </Button>
      </CardContent>
    </Card>
  )
}

function CompteurPastille({ actif, children }: { actif: boolean; children: ReactNode }) {
  return (
    <span
      className={cn(
        "rounded-full px-1.5 text-[0.7rem] font-semibold tabular-nums",
        actif ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground",
      )}
    >
      {children}
    </span>
  )
}

/** Une carte de mode : deux façons de travailler, décrites plutôt que nommées seules. */
function CarteMode({
  actif, onClick, icon, titre, texte,
}: { actif: boolean; onClick: () => void; icon: ReactNode; titre: string; texte: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={actif}
      className={cn(
        "relative flex items-start gap-3 rounded-xl border px-4 py-3 text-left transition-all",
        actif ? "border-primary bg-primary/5 shadow-sm" : "border-border hover:border-primary/40 hover:bg-accent/40",
      )}
    >
      {actif && <CheckCircle2 className="absolute right-3 top-3 size-4 text-primary" />}
      <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">{icon}</span>
      <span className="pr-5">
        <span className="block text-sm font-semibold">{titre}</span>
        <span className="block text-xs text-muted-foreground">{texte}</span>
      </span>
    </button>
  )
}

/** Un thème fréquent en lancement direct : la fréquence dit pourquoi, le bouton lance. */
function CarteThemeCible({
  rang, theme, total, lienExercices, onLancer, lancement, desactive,
}: {
  rang: number
  theme: ThemeFrequent
  total: number
  lienExercices: string
  onLancer: () => void
  lancement: boolean
  desactive: boolean
}) {
  const premier = rang === 1
  return (
    <div
      className={cn(
        "flex flex-col gap-3 rounded-2xl border p-4 transition-shadow hover:shadow-md",
        premier ? "border-gold/50 bg-gradient-to-br from-gold/[0.12] via-card to-card" : "border-border bg-card",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <span
            className={cn(
              "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[0.7rem] font-bold uppercase tracking-wider",
              premier ? "bg-gold text-gold-foreground" : "bg-primary/10 text-primary",
            )}
          >
            {premier && <Crown className="size-3" />}
            N°{rang}
          </span>
          <p className="mt-2 font-display text-base font-semibold leading-snug">{capitaliserTheme(theme.tag)}</p>
          <p className="mt-0.5 text-xs text-muted-foreground">
            {theme.nb_epreuves} sessions sur {total}
          </p>
        </div>
        <AnneauFrequence pct={theme.frequence_pct} dore={premier} />
      </div>
      <div className="mt-auto flex gap-1.5">
        <Button
          size="sm"
          className="h-8 flex-1 text-xs"
          onClick={onLancer}
          disabled={!theme.quiz_disponible || desactive}
          title={theme.quiz_disponible ? undefined : "Pas encore de question de quiz sur ce thème précis"}
        >
          <ListChecks className="size-3.5" />
          {lancement ? "Préparation..." : "Quiz sur ce thème"}
        </Button>
        <Button asChild size="sm" variant="outline" className="h-8 px-2.5 text-xs">
          <Link to={lienExercices}>
            <FileText className="size-3.5" />
            Exercices
          </Link>
        </Button>
      </div>
    </div>
  )
}

export function QuizStartPage() {
  useSeo({
    title: "Quiz",
    description: "Entraîne-toi ou évalue ton niveau avec des questions tirées des corrigés de ton cursus.",
  })

  const { isAuthenticated, isLoading: authLoading, user } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()

  // Lancement direct depuis un bouton "Quiz" externe (voir ThemesFrequents.tsx) -
  // `cursus` prime sur le premier abonnement actif tant qu'il en fait partie, `theme`
  // déclenche lancer() dès que ce cursus est effectivement sélectionné (voir l'effet
  // plus bas). Sans abonnement actif sur ce cursus précis, ces paramètres restent
  // simplement sans effet - la page retombe sur son comportement normal.
  const [searchParams] = useSearchParams()
  const cursusParam = searchParams.get("cursus")
  const themeParam = searchParams.get("theme")
  // Posé par l'étape quiz de la séance du jour (voir SeanceDuJour) : transmis tel quel
  // au serveur, qui s'en sert seulement comme drapeau "ce quiz vient du plan".
  const seanceParam = searchParams.get("seance")
  // Nombre de questions imposé par l'appelant (l'étape quiz d'une séance annonce sa
  // taille et son budget temps) - sinon le formulaire garde son propre défaut.
  const nParam = Number(searchParams.get("n"))
  const themeAutoLanceRef = useRef(false)

  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [subjectsLoaded, setSubjectsLoaded] = useState(false)
  // Structure réelle du cursus déclaré (gratuit, voir user.cursus_prepare) quand
  // l'utilisateur n'a aucun abonnement actif - remplace la question de démo générique
  // (voir project_gating_non_abonne_quiz_parcours). null tant que non chargé/non
  // pertinent, [] si le cursus déclaré n'a encore aucune banque de quiz.
  const [previewSubjects, setPreviewSubjects] = useState<Subject[] | null>(null)
  const [selectedCursus, setSelectedCursus] = useState("")
  const [selectedSubject, setSelectedSubject] = useState("")
  const [mode, setMode] = useState<ModeQuiz>("PRATIQUE")
  const [n, setN] = useState(10)
  const [subscriptionsLoaded, setSubscriptionsLoaded] = useState(false)
  const [starting, setStarting] = useState(false)
  const [startingThemeId, setStartingThemeId] = useState<number | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      // Aperçu public plutôt que redirection vers /connexion : "Quiz" est un onglet du
      // header, y répondre par un formulaire OTP réclamait un numéro de téléphone avant
      // d'avoir dit à quoi sert la page. Le hero et la carte de présentation plus bas
      // restent visibles, seules les données personnelles ne sont pas chargées.
      setSubscriptionsLoaded(true)
      return
    }
    listMySubscriptions().then((subs) => {
      // L'enfant connecté seulement : pas les cursus de la fratrie.
      const active = abonnementsActifsDuProfil(subs, user?.profil_actif?.id)
      setSubscriptions(active)
      setSubscriptionsLoaded(true)
      const viaParam = cursusParam && active.some((sub) => String(sub.cursus.id) === cursusParam)
      if (viaParam) setSelectedCursus(cursusParam)
      else if (active.length > 0) setSelectedCursus(String(active[0].cursus.id))
    })
    // cursusParam volontairement absent des deps : un changement d'URL après coup ne
    // doit pas redéclencher un nouvel appel listMySubscriptions(), seule la valeur au
    // moment où l'authentification se résout compte.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, isAuthenticated])

  // Sans abonnement actif mais un cursus déclaré (gratuit) : list_quiz_subjects
  // n'exige pas d'abonnement (voir sa docstring côté backend) - on peut donc montrer la
  // vraie structure de la banque avant le mur payant plutôt qu'une question de démo.
  const cursusPrepareId = user?.cursus_prepare?.id ?? null
  useEffect(() => {
    if (!subscriptionsLoaded || subscriptions.length > 0 || cursusPrepareId === null) {
      setPreviewSubjects(null)
      return
    }
    let annule = false
    listQuizSubjects(cursusPrepareId).then((data) => {
      if (!annule) setPreviewSubjects(data)
    })
    return () => {
      annule = true
    }
  }, [subscriptionsLoaded, subscriptions.length, cursusPrepareId])

  // Uniquement les matières ayant déjà une banque de quiz pour CE cursus (voir
  // quiz.views.list_quiz_subjects) - lister toutes les matières du pays (comme sur
  // /fiches) laisserait choisir une matière sans aucune question, avec l'échec de
  // démarrage seulement une fois le quiz lancé.
  useEffect(() => {
    const sub = subscriptions.find((s) => String(s.cursus.id) === selectedCursus)
    if (!sub) {
      setSubjects([])
      return
    }
    setSubjectsLoaded(false)
    listQuizSubjects(sub.cursus.id).then((data) => {
      setSubjects(data)
      setSubjectsLoaded(true)
      // La matière en cours est gardée d'un examen à l'autre quand elle y existe ; sinon
      // la plus fournie est présélectionnée - comme sur /themes-frequents, on arrive sur
      // une séance prête à lancer, jamais sur un formulaire à compléter.
      setSelectedSubject((courante) => {
        const precedente = data.find((s) => String(s.id) === courante)
        if (precedente) return courante
        const plusFournie = [...data].sort((a, b) => (b.nb_questions ?? 0) - (a.nb_questions ?? 0))[0]
        return plusFournie ? String(plusFournie.id) : ""
      })
    })
  }, [selectedCursus, subscriptions])

  const subjectChoisi = subjects.find((s) => String(s.id) === selectedSubject)

  // Thèmes les plus fréquents de la matière choisie, à lancer en un clic - le quiz et le
  // classement des thèmes parlent enfin la même langue. Même clé de cache que
  // /themes-frequents.
  const { data: classement } = useQuery({
    queryKey: ["themes-frequents", Number(selectedCursus), subjectChoisi?.code ?? ""],
    queryFn: ({ signal }) => getThemesFrequents(Number(selectedCursus), subjectChoisi!.code, signal),
    enabled: Boolean(selectedCursus && subjectChoisi),
  })
  const themesCibles = classement?.disponible ? classement.themes.slice(0, NB_THEMES_CIBLES) : []

  /**
   * Démarre une séance. Sans `theme` : la configuration du formulaire. Avec `theme` :
   * un entraînement ciblé lancé depuis un lien externe (voir l'auto-lancement plus
   * bas) ou depuis un thème fréquent - toujours en pratique libre (un test de niveau
   * sur un thème unique n'a pas de sens) et sans filtre matière, déjà impliqué par le
   * thème lui-même.
   */
  async function lancer(theme?: number) {
    if (!selectedCursus || (!theme && !selectedSubject)) return
    if (theme) setStartingThemeId(theme)
    else setStarting(true)
    setError("")
    const modeEffectif: ModeQuiz = theme ? "PRATIQUE" : mode
    try {
      const session = await startQuizSession({
        cursus: Number(selectedCursus),
        mode: modeEffectif,
        subject: theme ? undefined : Number(selectedSubject),
        theme,
        n: Number.isInteger(nParam) && nParam > 0 ? nParam : n,
        seance: seanceParam ? Number(seanceParam) : undefined,
      })
      trackEvent("quiz_started", { cursus_id: Number(selectedCursus), mode: modeEffectif })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Impossible de démarrer le quiz pour le moment. Réessaie plus tard.",
      )
      setStarting(false)
      setStartingThemeId(null)
    }
  }

  // Lancement automatique depuis ThemesFrequents.tsx (bouton "Quiz") - n'attend que
  // selectedCursus rejoigne effectivement cursusParam (donc que l'abonnement
  // correspondant ait été trouvé ci-dessus), jamais un simple montage : sinon l'appel
  // partirait avant que la sélection ne soit prête. Une seule tentative (themeAutoLanceRef)
  // même si lancer() échoue - pas de boucle de relance sur une session qui ne peut pas
  // s'ouvrir (ex. thème sans aucune question, déjà géré par le bouton désactivé côté
  // ThemesFrequents mais un lien direct pourrait contourner ce garde-fou).
  useEffect(() => {
    if (themeAutoLanceRef.current) return
    if (!themeParam || !cursusParam || selectedCursus !== cursusParam) return
    themeAutoLanceRef.current = true
    lancer(Number(themeParam))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCursus, cursusParam, themeParam])

  if (authLoading || !subscriptionsLoaded) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-10">
        <Skeleton className="mb-6 h-44 w-full rounded-3xl" />
        <Skeleton className="h-80 w-full rounded-2xl" />
      </div>
    )
  }

  const enCours = starting || startingThemeId !== null
  const abonne = subscriptions.length > 0
  const nbQuestionsBanque = abonne
    ? subjects.reduce((somme, s) => somme + (s.nb_questions ?? 0), 0)
    : (previewSubjects ?? []).reduce((somme, s) => somme + (s.nb_questions ?? 0), 0)
  const nbMatieres = abonne ? subjects.length : (previewSubjects ?? []).length
  const nEffectif = Number.isInteger(nParam) && nParam > 0 ? nParam : n
  const SubjectIcon = subjectIcon(subjectChoisi?.code ?? "")

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <ReviserTabs />
      {/* Hero : même gabarit que /epreuves et /themes-frequents. */}
      <div className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <Target aria-hidden className="pointer-events-none absolute -bottom-6 -right-4 hidden size-44 rotate-[-12deg] text-primary/[0.07] sm:block" />
        <div className="relative max-w-2xl">
          <p className="mb-2 font-display text-sm italic text-primary">Entraînement personnalisé</p>
          <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight text-balance sm:text-4xl">
            Un quiz qui <span className="text-primary">cible tes lacunes</span>, thème par thème.
          </h1>
          <p className="mt-2 max-w-xl text-muted-foreground">
            Entraîne-toi librement, vise un thème qui tombe souvent, ou fais le point avec un test de niveau. Les
            thèmes fragiles reviennent d'eux-mêmes, jusqu'à être acquis.
          </p>
          {nbQuestionsBanque > 0 && (
            <div className="mt-4 flex flex-wrap gap-2 sm:mt-5">
              <StatChip icon={<ListChecks className="size-3.5 text-primary" />}>
                <span className="font-medium tabular-nums">{formatAmount(nbQuestionsBanque)}</span>
                <span className="text-muted-foreground">questions corrigées</span>
              </StatChip>
              <StatChip icon={<Layers className="size-3.5 text-primary" />}>
                <span className="font-medium tabular-nums">{nbMatieres}</span>
                <span className="text-muted-foreground">matière{nbMatieres > 1 ? "s" : ""}</span>
              </StatChip>
            </div>
          )}
        </div>
      </div>

      {!abonne ? (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)]">
          {previewSubjects && previewSubjects.length > 0 && cursusPrepareId != null ? (
            <ApercuMatieresQuiz cursusId={cursusPrepareId} subjects={previewSubjects} />
          ) : (
            <Card className="overflow-hidden rounded-2xl border-primary/25 bg-gradient-to-br from-primary/5 via-transparent to-transparent shadow-lg shadow-primary/5">
              <CardContent className="flex flex-col items-start gap-4 pt-6">
                {/* Le cadenas ne s'affiche que s'il dit vrai : à un abonné sans cursus
                    actif, il nomme un accès à débloquer. Au visiteur déconnecté, il
                    annonçait une interdiction avant même d'avoir dit ce qu'est le Quiz. */}
                <span className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
                  {isAuthenticated ? <Lock className="size-5" /> : <Target className="size-5" />}
                </span>
                <div>
                  <p className="font-display text-lg font-semibold">
                    {isAuthenticated ? "Débloque le Quiz" : "Comment marche le Quiz"}
                  </p>
                  {isAuthenticated && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      Réservé aux cursus avec un abonnement actif - repère tes lacunes et révise exactement ce qu'il
                      faut, au bon moment.
                    </p>
                  )}
                </div>
                <EtapesPresentation
                  etapes={[
                    "Tu choisis ta matière, ou un thème qui tombe souvent.",
                    "Tu réponds ; chaque réponse est rattachée à un thème précis de ton programme.",
                    "Les thèmes fragiles reviennent d'eux-mêmes les jours suivants, jusqu'à être acquis.",
                  ]}
                />
                {/* Déconnecté, la connexion passe devant les tarifs : un abonnement déjà
                    actif sur un autre appareil est le cas le plus fréquent ici. Le w-full
                    va sur le conteneur des deux liens (voir l'historique : sous un parent
                    items-start, le bouton se rétractait à 269px à 375px de large). */}
                {isAuthenticated ? (
                  <Button asChild size="lg" className="w-full sm:w-auto">
                    <a href="/tarifs">
                      Voir les tarifs
                      <ArrowRight className="size-4" />
                    </a>
                  </Button>
                ) : (
                  <div className="flex w-full flex-col items-start gap-2">
                    <Button asChild size="lg" className="w-full sm:w-auto">
                      <Link to="/connexion" state={{ from: "/quiz", intent: "Connecte-toi pour lancer ton quiz." }}>
                        Se connecter pour commencer
                        <ArrowRight className="size-4" />
                      </Link>
                    </Button>
                    <Link to="/tarifs" className="text-sm text-muted-foreground underline-offset-4 hover:underline">
                      Pas encore d'abonnement ? Voir les tarifs
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
          {/* Une question de démo factice n'a plus de sens une fois la vraie liste
              affichée (voir ApercuMatieresQuiz) - seul le cas "aucun cursus connu" la garde. */}
          {!(previewSubjects && previewSubjects.length > 0) && (
            <aside className="min-w-0">
              <DemoQuizQuestion
                lienConnexion={
                  <Link
                    to={isAuthenticated ? "/tarifs" : "/connexion"}
                    state={isAuthenticated ? undefined : { from: "/quiz", intent: "Connecte-toi pour lancer ton quiz." }}
                    className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                  >
                    Lancer une vraie séance
                  </Link>
                }
              />
            </aside>
          )}
        </div>
      ) : (
        <>
          {/* Configuration : la même carte surélevée et les mêmes pastilles que
              /epreuves et /themes-frequents, lancement au pied de la carte. */}
          <div className="mb-8 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:p-6">
            <p className="font-display text-lg font-semibold">Ta séance</p>
            <p className="text-sm text-muted-foreground">Tout est prêt : ajuste si tu veux, puis lance.</p>

            <FiltreLigne titre="Examen">
              {subscriptions.map((sub) => (
                <PastilleFiltre
                  key={sub.id}
                  actif={selectedCursus === String(sub.cursus.id)}
                  onClick={() => setSelectedCursus(String(sub.cursus.id))}
                >
                  {sub.cursus.examen_display}
                  {sub.cursus.series ? ` ${sub.cursus.series.code}` : ""}
                </PastilleFiltre>
              ))}
            </FiltreLigne>

            <FiltreLigne titre="Matière">
              {!subjectsLoaded ? (
                [0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-9 w-24 shrink-0 rounded-full" />)
              ) : subjects.length === 0 ? (
                <p className="py-1.5 text-sm text-muted-foreground">Aucune matière n'a encore de questions sur ce cursus.</p>
              ) : (
                subjects.map((subject) => {
                  const Icon = subjectIcon(subject.code)
                  const actif = selectedSubject === String(subject.id)
                  return (
                    <PastilleFiltre key={subject.id} actif={actif} onClick={() => setSelectedSubject(String(subject.id))}>
                      <span className={cn("flex size-5 items-center justify-center rounded-full", couleurMatiere(subject.code).puce)}>
                        <Icon className="size-3" aria-hidden="true" />
                      </span>
                      {subjectShortLabel(subject.code, subject.label)}
                      <CompteurPastille actif={actif}>{subject.nb_questions ?? 0}</CompteurPastille>
                    </PastilleFiltre>
                  )
                })
              )}
            </FiltreLigne>

            <div className="mt-4">
              <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Mode</p>
              <div className="grid gap-2 sm:grid-cols-2">
                <CarteMode
                  actif={mode === "PRATIQUE"}
                  onClick={() => setMode("PRATIQUE")}
                  icon={<Sparkles className="size-4" />}
                  titre="Pratique libre"
                  texte="Cible davantage les thèmes où tu échoues, au fil de tes séances."
                />
                <CarteMode
                  actif={mode === "DIAGNOSTIC"}
                  onClick={() => setMode("DIAGNOSTIC")}
                  icon={<ListChecks className="size-4" />}
                  titre="Test de niveau"
                  texte="Difficultés variées, pour situer ton niveau."
                />
              </div>
            </div>

            {!(Number.isInteger(nParam) && nParam > 0) && (
              <FiltreLigne titre="Nombre de questions">
                {N_PRESETS.map((valeur) => (
                  <PastilleFiltre key={valeur} actif={n === valeur} onClick={() => setN(valeur)}>
                    <span className="tabular-nums">{valeur}</span>
                  </PastilleFiltre>
                ))}
              </FiltreLigne>
            )}

            {/* Pied de carte : le récapitulatif en une ligne, et l'unique action. */}
            <div className="mt-6 flex flex-col gap-3 border-t border-border pt-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex min-w-0 items-center gap-3">
                <span className={cn("flex size-10 shrink-0 items-center justify-center rounded-xl", couleurMatiere(subjectChoisi?.code).puce)}>
                  <SubjectIcon className="size-5" aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="truncate font-medium">
                    {subjectChoisi ? subjectChoisi.label : "Choisis une matière"}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    <span className="tabular-nums">{nEffectif}</span> questions ·{" "}
                    {mode === "PRATIQUE" ? "Pratique libre" : "Test de niveau"} · environ{" "}
                    <span className="tabular-nums">{Math.max(1, Math.round(nEffectif * 0.75))}</span> min
                  </p>
                </div>
              </div>
              <Button
                onClick={() => lancer()}
                disabled={!selectedCursus || !selectedSubject || enCours}
                size="lg"
                className="shrink-0"
              >
                {starting ? (
                  "Préparation..."
                ) : (
                  <>
                    Lancer mon quiz
                    <ArrowRight className="size-4" />
                  </>
                )}
              </Button>
            </div>
            {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
          </div>

          {/* Le pont avec /themes-frequents : viser directement ce qui tombe le plus. */}
          {themesCibles.length > 0 && subjectChoisi && classement && (
            <section aria-labelledby="themes-cibles-titre">
              <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                <div>
                  <h2 id="themes-cibles-titre" className="flex items-center gap-2 font-display text-xl font-semibold">
                    <TrendingUp className="size-5 text-primary" />
                    Vise ce qui tombe le plus
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    Les thèmes les plus fréquents en {subjectChoisi.label}, sur{" "}
                    <span className="tabular-nums">{classement.nb_sessions_disponibles}</span> sessions officielles.
                  </p>
                </div>
                <Link
                  to={`${themesFrequentsPath(country)}?subject=${subjectChoisi.code}&cursus=${selectedCursus}`}
                  className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
                >
                  Tout le classement
                  <ArrowRight className="size-3.5" />
                </Link>
              </div>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {themesCibles.map((theme, index) => (
                  <CarteThemeCible
                    key={theme.id}
                    rang={index + 1}
                    theme={theme}
                    total={classement.nb_sessions_disponibles}
                    lienExercices={lienExercicesTheme(
                      country, theme, subjectChoisi.code, Number(selectedCursus), classement.nb_sessions_disponibles,
                    )}
                    onLancer={() => lancer(theme.id)}
                    lancement={startingThemeId === theme.id}
                    desactive={enCours}
                  />
                ))}
                {/* Classement tronqué (abonnement sans Jusqu'à l'Examen) : la suite se voit,
                    verrouillée, comme sur /themes-frequents. */}
                {!classement.has_access && classement.nb_themes_verrouilles > 0 && (
                  <Link
                    to={`/abonnement?cursus=${selectedCursus}`}
                    className="group flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-gold/50 bg-gold/[0.04] p-4 text-center transition-colors hover:bg-gold/[0.08]"
                  >
                    <span className="flex size-10 items-center justify-center rounded-full bg-gold/15 text-gold-text">
                      <Lock className="size-4" />
                    </span>
                    <p className="font-display text-base font-semibold">
                      +{classement.nb_themes_verrouilles} thèmes classés
                    </p>
                    <p className="text-xs text-muted-foreground">Avec l'abonnement Jusqu'à l'Examen</p>
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-gold-text group-hover:underline">
                      Débloquer
                      <ArrowRight className="size-3.5" />
                    </span>
                  </Link>
                )}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}
