import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
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
import { abonnementsActifsDuProfil, abonnementsDeLExamenPrepare } from "@/lib/changerCursusPrepare"
import { useCountry } from "@/context/CountryContext"
import { StatChip } from "@/components/Configurateur"
import { ErreurChargement } from "@/components/ErreurChargement"
import { QuizCompletVisiteur } from "@/components/QuizCompletVisiteur"
import { EssaisGratuitsQuiz } from "@/components/EssaisGratuitsQuiz"
import { FiltreLigne, PastilleFiltre } from "@/components/FiltresCatalogue"
import { AnneauFrequence } from "@/components/AnneauFrequence"
import { ReprendreQuiz } from "@/components/ReprendreQuiz"
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
import { t, tn, useI18n } from "@/lib/i18n"

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
      setError(err instanceof ApiError ? err.message : t("qd.essai_erreur"))
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
              <span className="tabular-nums">{formatAmount(total)}</span> {tn("qd.sur_programme", total)}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">
              {t("qd.abonne_toi")}
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
                    {tn("quiz.n_questions", subject.nb_questions ?? 0)}
                  </span>
                  {subject.vitrine_theme_id != null && (
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={starting !== null}
                      onClick={() => essayerGratuitement(subject)}
                      className="h-7 rounded-full px-2.5 text-xs"
                    >
                      {starting === subject.id ? t("quiz.preparation") : t("qd.essayer_gratuit")}
                    </Button>
                  )}
                </span>
              </li>
            )
          })}
        </ul>
        {error && <p className="text-sm text-destructive">{error}</p>}
        <Button asChild size="lg" className="w-full sm:w-auto">
          <Link to="/tarifs">
            {t("accueil.voir_prix")}
            <ArrowRight className="size-4" />
          </Link>
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
            {t("qd.sessions_sur", { n: theme.nb_epreuves, total })}
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
          title={theme.quiz_disponible ? undefined : t("qd.pas_de_quiz_theme")}
        >
          <ListChecks className="size-3.5" />
          {lancement ? t("quiz.preparation") : t("qd.quiz_theme")}
        </Button>
        <Button asChild size="sm" variant="outline" className="h-8 px-2.5 text-xs">
          <Link to={lienExercices}>
            <FileText className="size-3.5" />
            {t("qd.exercices")}
          </Link>
        </Button>
      </div>
    </div>
  )
}

export function QuizStartPage() {
  useI18n()
  useSeo({
    title: t("qd.onglet_quiz"),
    description: t("qd.seo_description"),
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

  // Tous les abonnements actifs du profil ; `subscriptions` (plus bas) n'en garde que ceux
  // que le quiz propose, voir abonnementsDeLExamenPrepare.
  const [abonnementsProfil, setAbonnementsProfil] = useState<Subscription[]>([])
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
  // Échecs de chargement : sans eux, un .then sans .catch laissait le squelette (ou la liste de
  // matières) à l'écran pour toujours. Les compteurs d'essai relancent les effets via « Réessayer ».
  const [erreurAbonnements, setErreurAbonnements] = useState(false)
  const [essaiAbonnements, setEssaiAbonnements] = useState(0)
  const [erreurMatieres, setErreurMatieres] = useState(false)
  const [essaiMatieres, setEssaiMatieres] = useState(0)
  const [starting, setStarting] = useState(false)
  const [startingThemeId, setStartingThemeId] = useState<number | null>(null)
  const [error, setError] = useState("")

  // Examen préparé du compte (sélecteur du bandeau) : le quiz s'y limite, un profil qui a
  // payé BEPC et BAC C ne retrouve pas l'autre examen en pastille. Suit le sélecteur : si
  // l'élève change d'examen depuis le bandeau, la liste et la sélection suivent.
  const cursusPrepareId = user?.cursus_prepare?.id ?? null
  const subscriptions = useMemo(
    () => abonnementsDeLExamenPrepare(abonnementsProfil, cursusPrepareId, cursusParam),
    [abonnementsProfil, cursusPrepareId, cursusParam],
  )

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
    setErreurAbonnements(false)
    listMySubscriptions()
      .then((subs) => {
        // L'enfant connecté seulement : pas les cursus de la fratrie.
        const active = abonnementsActifsDuProfil(subs, user?.profil_actif?.id)
        setAbonnementsProfil(active)
        setSubscriptionsLoaded(true)
        // Sans lien direct, la sélection par défaut vient de l'effet de synchronisation ci-dessous
        // (l'examen préparé), pas du premier abonnement de la liste.
        const viaParam = cursusParam && active.some((sub) => String(sub.cursus.id) === cursusParam)
        if (viaParam) setSelectedCursus(cursusParam)
      })
      .catch(() => setErreurAbonnements(true))
    // cursusParam volontairement absent des deps : un changement d'URL après coup ne
    // doit pas redéclencher un nouvel appel listMySubscriptions(), seule la valeur au
    // moment où l'authentification se résout compte (ou un clic sur « Réessayer »).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, isAuthenticated, essaiAbonnements])

  // La sélection reste toujours dans la liste proposée : à l'arrivée elle prend l'examen
  // préparé, et elle y revient si l'élève en change depuis le bandeau pendant que la page est ouverte.
  useEffect(() => {
    if (!subscriptionsLoaded || subscriptions.length === 0) return
    setSelectedCursus((courant) =>
      subscriptions.some((sub) => String(sub.cursus.id) === courant) ? courant : String(subscriptions[0].cursus.id),
    )
  }, [subscriptionsLoaded, subscriptions])

  // Sans abonnement actif mais un cursus déclaré (gratuit) : list_quiz_subjects
  // n'exige pas d'abonnement (voir sa docstring côté backend) - on peut donc montrer la
  // vraie structure de la banque avant le mur payant plutôt qu'une question de démo.
  useEffect(() => {
    if (!subscriptionsLoaded || subscriptions.length > 0 || cursusPrepareId === null) {
      setPreviewSubjects(null)
      return
    }
    let annule = false
    listQuizSubjects(cursusPrepareId)
      .then((data) => {
        if (!annule) setPreviewSubjects(data)
      })
      // L'aperçu est un confort : en cas d'échec, la carte générique "Débloque le Quiz" reprend la place.
      .catch(() => {
        if (!annule) setPreviewSubjects([])
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
    setErreurMatieres(false)
    // Drapeau d'annulation : un changement d'examen rapide ne doit pas laisser la réponse la plus
    // lente écraser les matières de l'examen courant.
    let annule = false
    listQuizSubjects(sub.cursus.id)
      .then((data) => {
        if (annule) return
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
      .catch(() => {
        if (annule) return
        setSubjects([])
        setErreurMatieres(true)
        setSubjectsLoaded(true)
      })
    return () => {
      annule = true
    }
  }, [selectedCursus, subscriptions, essaiMatieres])

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
          : t("qd.demarrage_erreur"),
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

  if (!authLoading && isAuthenticated && erreurAbonnements && !subscriptionsLoaded) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-6 sm:px-6 sm:py-10">
        <ErreurChargement objet={t("qd.objet_quiz")} onRetry={() => setEssaiAbonnements((n) => n + 1)} />
      </div>
    )
  }

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
          <p className="mb-2 font-display text-sm italic text-primary">{t("qd.surtitre")}</p>
          <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight text-balance sm:text-4xl">
            {t("qd.titre_debut")} <span className="text-primary">{t("qd.titre_accent")}</span>{t("qd.titre_fin")}
          </h1>
          <p className="mt-2 max-w-xl text-muted-foreground">
            {t("qd.hero_texte")}
          </p>
          {nbQuestionsBanque > 0 && (
            <div className="mt-4 flex flex-wrap gap-2 sm:mt-5">
              <StatChip icon={<ListChecks className="size-3.5 text-primary" />}>
                <span className="font-medium tabular-nums">{formatAmount(nbQuestionsBanque)}</span>
                <span className="text-muted-foreground">{t("qd.stat_questions")}</span>
              </StatChip>
              <StatChip icon={<Layers className="size-3.5 text-primary" />}>
                <span className="font-medium tabular-nums">{nbMatieres}</span>
                <span className="text-muted-foreground">{tn("qd.stat_matieres", nbMatieres)}</span>
              </StatChip>
            </div>
          )}
        </div>
      </div>

      <ReprendreQuiz className="mb-6" />

      {/* Les quiz gratuits, sans compte : seulement quand aucun aperçu de cursus déclaré n'offre déjà
          son propre essai (ApercuMatieresQuiz). */}
      {!abonne && !(previewSubjects && previewSubjects.length > 0) && (
        <EssaisGratuitsQuiz cursusInitial={cursusParam ? Number(cursusParam) : cursusPrepareId} />
      )}

      {!abonne ? (
        previewSubjects && previewSubjects.length > 0 && cursusPrepareId != null ? (
          <ApercuMatieresQuiz cursusId={cursusPrepareId} subjects={previewSubjects} />
        ) : (
          // Après les essais gratuits : le produit complet, un seul bloc et un seul appel principal
          // (voir QuizCompletVisiteur). Au visiteur déconnecté, aucun cadenas : le bloc dit ce qu'est le Quiz.
          <QuizCompletVisiteur connecte={isAuthenticated} />
        )
      ) : (
        <>
          {/* Configuration : la même carte surélevée et les mêmes pastilles que
              /epreuves et /themes-frequents, lancement au pied de la carte. */}
          <div className="mb-8 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:p-6">
            <p className="font-display text-lg font-semibold">{t("qd.ta_seance")}</p>
            <p className="text-sm text-muted-foreground">{t("qd.tout_pret")}</p>

            <FiltreLigne titre={t("quiz.examen")}>
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

            <FiltreLigne titre={t("quiz.matiere")}>
              {!subjectsLoaded ? (
                [0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-9 w-24 shrink-0 rounded-full" />)
              ) : erreurMatieres ? (
                <p role="alert" className="flex flex-wrap items-center gap-x-2 py-1.5 text-sm text-muted-foreground">
                  {t("qd.matieres_erreur")}
                  <button
                    type="button"
                    onClick={() => setEssaiMatieres((n) => n + 1)}
                    className="font-medium text-primary underline-offset-4 hover:underline"
                  >
                    {t("erreur.reessayer")}
                  </button>
                </p>
              ) : subjects.length === 0 ? (
                <p className="py-1.5 text-sm text-muted-foreground">{t("qd.aucune_matiere")}</p>
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
              <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{t("qd.mode")}</p>
              <div className="grid gap-2 sm:grid-cols-2">
                <CarteMode
                  actif={mode === "PRATIQUE"}
                  onClick={() => setMode("PRATIQUE")}
                  icon={<Sparkles className="size-4" />}
                  titre={t("qd.mode_pratique")}
                  texte={t("qd.mode_pratique_texte")}
                />
                <CarteMode
                  actif={mode === "DIAGNOSTIC"}
                  onClick={() => setMode("DIAGNOSTIC")}
                  icon={<ListChecks className="size-4" />}
                  titre={t("quiz_en_cours.test_niveau")}
                  texte={t("qd.mode_diagnostic_texte")}
                />
              </div>
            </div>

            {!(Number.isInteger(nParam) && nParam > 0) && (
              <FiltreLigne titre={t("qd.nombre_questions")}>
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
                    {subjectChoisi ? subjectChoisi.label : t("qd.choisis_matiere")}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {t("qd.recap", {
                      n: nEffectif,
                      mode: mode === "PRATIQUE" ? t("qd.mode_pratique") : t("quiz_en_cours.test_niveau"),
                      m: Math.max(1, Math.round(nEffectif * 0.75)),
                    })}
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
                  t("quiz.preparation")
                ) : (
                  <>
                    {t("qd.lancer")}
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
                    {t("qd.vise_titre")}
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    {t("qd.vise_texte", { matiere: subjectChoisi.label, n: classement.nb_sessions_disponibles })}
                  </p>
                </div>
                <Link
                  to={`${themesFrequentsPath(country)}?subject=${subjectChoisi.code}&cursus=${selectedCursus}`}
                  className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
                >
                  {t("qd.tout_classement")}
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
                      {t("qd.themes_classes", { n: classement.nb_themes_verrouilles })}
                    </p>
                    <p className="text-xs text-muted-foreground">{t("qd.avec_abonnement")}</p>
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-gold-text group-hover:underline">
                      {t("qd.debloquer")}
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
