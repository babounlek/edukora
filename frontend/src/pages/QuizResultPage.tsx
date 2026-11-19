import { useEffect, useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { ArrowRight, BookOpen, CalendarCheck, CheckCircle2, ChevronDown, FileText, Flame, ListChecks, RotateCcw, Share2, Sprout, Swords, Timer, Trophy, Zap } from "lucide-react"

import { completeQuizSession, listQuizEssais, refaireLesRatees, rejouerQuiz, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { QuizResult, QuizThemeScore, SerieDeJours } from "@/api/types"
import { oublierAccueilEnCache } from "@/lib/accueilCache"
import { ProgressionNiveau } from "@/components/JaugeNiveau"
import { epreuveInediteDetailPath, themeExercicesPath } from "@/lib/countryPath"
import { BoutonPartager } from "@/components/BoutonPartager"
import { Button } from "@/components/ui/button"
import { Confettis } from "@/components/Confettis"
import { Mascotte } from "@/components/Mascotte"
import { NiveauXp } from "@/components/NiveauXp"
import { ObjectifXp } from "@/components/ObjectifXp"
import { RythmeRapide } from "@/components/RythmeRapide"
import { PrioritesExamen } from "@/components/PrioritesExamen"
import { InviteAvis } from "@/components/InviteAvis"
import { InvitePush } from "@/components/ReglagesSeance"
import { QuizFichePdfButtons } from "@/components/QuizFichePdfButtons"
import { SemaineDeSerie } from "@/components/SemaineDeSerie"
import { Skeleton } from "@/components/ui/skeleton"
import { useCountry } from "@/context/CountryContext"
import { useAuth } from "@/context/AuthContext"
import { useCursusAbonne } from "@/lib/abonneActif"
import { formatDureeEcoulee } from "@/lib/duration"
import { partagerScore } from "@/lib/partageScore"
import { jouerRetour } from "@/lib/retours"
import { marquerSeancesJouees } from "@/lib/seancesGratuites"
import { aChangeDeNiveau, nomNiveau } from "@/lib/niveau"
import { comparerDefi, lireDefiMemorise, parametresDefi } from "@/lib/defiEssai"
import { useEssaiSansCompte } from "@/lib/useEssaiSansCompte"
import { libelleRythme } from "@/lib/rythme"
import { SITE_NAME } from "@/lib/site"
import { useCompteur } from "@/lib/useCompteur"
import { useSeo } from "@/lib/seo"
import { capitaliserTheme, cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"
import { lienDeParrainage } from "@/lib/referral"

/**
 * Ce que le quiz a rapporté et où en est la journée : l'XP qui monte, la barre d'objectif, la
 * semaine de série. C'est l'écran qui donne envie de revenir demain, donc il dit les trois
 * choses d'un coup. Le petit jingle de fin part ici, une seule fois, au montage.
 */
function BilanChrono({ result }: { result: QuizResult }) {
  useI18n()
  useEffect(() => {
    jouerRetour(result.nouveau_record ? "objectif" : "fin")
  }, [result.nouveau_record])
  const utilise = result.temps_utilise_secondes
  const alloue = result.duree_limite_secondes
  return (
    <section aria-label={t("chrono.restant")} className="mb-6 rounded-2xl border border-border bg-card p-5 shadow-sm">
      <p className="flex items-center gap-2 font-display text-xl font-semibold tabular-nums">
        <Timer className="size-5 text-primary" aria-hidden="true" />
        {utilise != null && alloue != null
          ? t("chrono.temps_utilise", { utilise: formatDureeEcoulee(utilise), alloue: formatDureeEcoulee(alloue) })
          : t("chrono.pastille")}
      </p>
      {result.nouveau_record ? (
        <p className="animate-quiz-bravo mt-3 flex items-center gap-2 rounded-xl bg-gold/15 px-3 py-2 text-sm font-semibold text-gold-text">
          <Trophy className="size-4 shrink-0" aria-hidden="true" />
          {t("chrono.nouveau_record")}
          {result.record_secondes != null && ` ${formatDureeEcoulee(result.record_secondes)}`}
        </p>
      ) : (
        result.record_secondes != null && (
          <p className="mt-2 text-sm text-muted-foreground">
            {t("chrono.record", { temps: formatDureeEcoulee(result.record_secondes) })}
          </p>
        )
      )}
      {result.questions_repondues === result.total_questions && !result.chrono_ecoule && (
        // Le gain d'un quiz chronométré : tout répondu dans le temps. Un badge, jamais des points (voir quiz.chrono).
        <p className="mt-2 inline-flex items-center gap-2 rounded-full bg-success/15 px-3 py-1 text-sm font-medium">
          <Timer className="size-4 shrink-0 text-success" aria-hidden="true" />
          {t("chrono.tenu")}
        </p>
      )}
      <p className="mt-2 text-sm text-muted-foreground">{t("chrono.neutre")}</p>
    </section>
  )
}

function BilanXp({
  xp, serie, classement, score, total,
}: {
  xp: NonNullable<QuizResult["xp"]>
  serie?: SerieDeJours
  classement?: QuizResult["classement"]
  score: number
  total: number
}) {
  useI18n()
  const gagne = useCompteur(xp.session.total)
  // L'état du jour peut changer ici même (l'élève change de rythme) : une copie locale, repartie de ce que le serveur a dit.
  const [jour, setJour] = useState(xp.jour)
  const { user } = useAuth()
  const [partage, setPartage] = useState(false)
  // Le gain de CE quiz a-t-il fait franchir un palier ? Fêté avant tout le reste de la page.
  const niveauMonte = jour.niveau ? aChangeDeNiveau(jour.niveau, xp.session.total) : false
  useEffect(() => {
    jouerRetour(niveauMonte ? "objectif" : "fin")
    // Visible tout de suite, où que l'élève en soit dans la page : le bandeau du bilan est sous le pli sur téléphone.
    if (niveauMonte && jour.niveau) toast.success(t("niveau.nouveau", { nom: nomNiveau(jour.niveau.rang) }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [niveauMonte])

  async function partager() {
    if (!user || partage) return
    setPartage(true)
    try {
      await partagerScore({
        score, total, xp: xp.session.total, serie: serie?.jours ?? 0, nomSite: SITE_NAME,
        lien: lienDeParrainage(user.referral_code),
      })
    } finally {
      setPartage(false)
    }
  }

  return (
    <section
      aria-label={t("qr.aria_bilan")}
      className="mb-6 grid gap-5 rounded-2xl border border-border bg-card p-5 shadow-sm sm:grid-cols-[auto_1fr_1fr] sm:items-center sm:gap-8"
    >
      <div className="text-center sm:text-left">
        <p className="text-sm text-muted-foreground">{t("qr.gagne")}</p>
        {xp.session.total > 0 ? (
          <p className="flex items-center justify-center gap-1.5 font-display text-4xl font-semibold tabular-nums text-gold-text sm:justify-start">
            <Zap className="size-7" aria-hidden="true" />
            {t("gl.partage_points", { n: gagne })}
          </p>
        ) : (
          // Un rejeu ou un quiz chronométré ne rapporte rien : pas de « +0 points » en gros sous un « Sans faute ! ».
          <p className="font-display text-lg font-semibold">{t("qr.zero_titre")}</p>
        )}
        {xp.session.seance > 0 && (
          <p className="text-xs text-muted-foreground">{t("qr.dont_seance", { n: xp.session.seance })}</p>
        )}
        {/* Zéro point avec des bonnes réponses : rejeu ou quiz chronométré (neutres pour les points). « Les points se gagnent
            sur les bonnes réponses » y sonnait faux. */}
        {xp.session.total === 0 && (
          <p className="text-xs text-muted-foreground">{score > 0 ? t("qr.points_zero_bonnes") : t("qr.points_bonnes")}</p>
        )}
      </div>
      <div>
        <ObjectifXp etat={jour} />
        {/* Le rythme se règle ici, là où l'élève vient de voir ce que son quiz a rapporté. Pas pour un invité : le réglage
            appartient à un compte (le serveur le refuserait). */}
        {user && (
          <RythmeRapide etat={jour} onChange={setJour} className="mt-1.5 text-xs font-medium text-primary underline-offset-2 hover:underline">
            {t("rythme.changer")} · {libelleRythme(jour.objectif)}
          </RythmeRapide>
        )}
      </div>
      {serie && <SemaineDeSerie serie={serie} />}
      {jour.niveau && (
        <div className="sm:col-span-3">
          {/* Fêté quand CE quiz a fait franchir un palier : c'est le moment où un niveau a du sens. */}
          {niveauMonte && (
            <p className="animate-quiz-bravo mb-3 flex items-center gap-2 rounded-xl bg-gold/15 px-3 py-2 text-sm font-semibold text-gold-text">
              <Trophy className="size-4 shrink-0" aria-hidden="true" />
              {t("niveau.nouveau", { nom: nomNiveau(jour.niveau.rang) })}
            </p>
          )}
          <NiveauXp niveau={jour.niveau} />
        </div>
      )}
      {/* Une phrase seulement quand la cohorte est assez grande ET que l'élève est dans la moitié
          haute (voir quiz.classement) : un effort comparé à celui des autres, jamais un niveau, et
          jamais un mot pour qui est en dessous. */}
      {classement?.bande && (
        <p className="flex items-center gap-2 rounded-xl bg-gold/10 px-3 py-2 text-sm font-medium sm:col-span-3">
          <Trophy className="size-4 shrink-0 text-gold-text" aria-hidden="true" />
          {classement.bande === "quart"
            ? t("qr.classement_quart")
            : t("qr.classement_moitie")}
        </p>
      )}
      {/* Le lien de parrainage est celui d'un compte : un invité n'en a pas encore. */}
      {user && (
        <div className="sm:col-span-3">
          <Button variant="outline" size="sm" onClick={partager} disabled={partage} className="rounded-full">
            <Share2 />
            {t("qr.partager")}
          </Button>
        </div>
      )}
    </section>
  )
}

/** Anneau de score : se remplit au montage, la couleur suit le niveau atteint. */
function AnneauScore({ pourcentage, score, total }: { pourcentage: number; score: number; total: number }) {
  const [rempli, setRempli] = useState(false)
  useEffect(() => {
    const minuteur = setTimeout(() => setRempli(true), 100)
    return () => clearTimeout(minuteur)
  }, [])
  const rayon = 52
  const circonference = 2 * Math.PI * rayon
  const couleur = pourcentage >= 70 ? "text-success" : pourcentage >= 40 ? "text-gold-text" : "text-primary"
  return (
    <div className="relative mx-auto size-40">
      <svg viewBox="0 0 120 120" className="size-full -rotate-90">
        <circle cx="60" cy="60" r={rayon} fill="none" strokeWidth="10" className="stroke-secondary" />
        <circle
          cx="60"
          cy="60"
          r={rayon}
          fill="none"
          strokeWidth="10"
          strokeLinecap="round"
          className={"stroke-current transition-all duration-[1400ms] ease-out " + couleur}
          strokeDasharray={circonference}
          strokeDashoffset={rempli ? circonference * (1 - pourcentage / 100) : circonference}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {/* Sous 40 %, le pourcentage en gros enfonce : on met en avant ce qui a été réussi (« 1 / 6 »). */}
        {pourcentage < 40 && total > 0 ? (
          <>
            <span className="font-display text-4xl font-semibold tabular-nums">{score} / {total}</span>
            <span className="text-xs text-muted-foreground">{pourcentage}%</span>
          </>
        ) : (
          <>
            <span className="font-display text-4xl font-semibold tabular-nums">{pourcentage}%</span>
            <span className="text-xs text-muted-foreground">
              {score} / {total}
            </span>
          </>
        )}
      </div>
    </div>
  )
}

/**
 * Un thème du quiz, avec ses suites possibles : exercices corrigés du thème (vrais
 * sujets d'examen), cours à relire s'il y en a un, et un quiz ciblé pour le retravailler
 * tout de suite - le même trio que sur /themes-frequents.
 */
function LigneTheme({
  theme, cursusId, country, onQuiz, lancement, quizCible = true,
}: {
  theme: QuizThemeScore
  cursusId: number
  country: string
  onQuiz: () => void
  lancement: boolean
  /** Faux pour qui n'a pas l'accès : le serveur refuserait un quiz sur ce thème. */
  quizCible?: boolean
}) {
  useI18n()
  const taux = theme.total > 0 ? Math.round((100 * theme.reussies) / theme.total) : 0
  const tonalite = taux >= 70 ? "bg-success" : taux >= 40 ? "bg-gold" : "bg-destructive/70"
  return (
    <li className="flex flex-col gap-3 px-4 py-3.5 sm:flex-row sm:items-center sm:gap-4 sm:px-5">
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-3">
          <span className="min-w-0 flex-1 truncate font-medium">{capitaliserTheme(theme.theme)}</span>
          <span className="shrink-0 text-sm font-semibold tabular-nums">
            {theme.reussies}
            <span className="font-normal text-muted-foreground"> / {theme.total}</span>
          </span>
        </div>
        {theme.niveau_apres && (
          <div className="mt-1">
            <ProgressionNiveau avant={theme.niveau_avant} apres={theme.niveau_apres} />
          </div>
        )}
        <span className="mt-2 block h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <span className={cn("block h-full rounded-full transition-[width] duration-700", tonalite)} style={{ width: `${Math.max(taux, 4)}%` }} />
        </span>
      </div>
      <div className="flex shrink-0 flex-wrap gap-1.5">
        {theme.subject_code && (
          <Button asChild size="sm" variant="outline" className="h-8 px-2.5 text-xs">
            <Link to={`${themeExercicesPath(country, theme.theme_id)}?subject=${theme.subject_code}&cursus=${cursusId}`}>
              <FileText className="size-3.5" />
              {t("qd.exercices")}
            </Link>
          </Button>
        )}
        {theme.cours && (
          <Button asChild size="sm" variant="outline" className="h-8 px-2.5 text-xs">
            <Link to={`/cours/${theme.cours.slug}`}>
              <BookOpen className="size-3.5" />
              {t("nav.cours")}
            </Link>
          </Button>
        )}
        {theme.subject_code && quizCible && (
          <Button size="sm" variant={taux < 70 ? "default" : "outline"} className="h-8 px-2.5 text-xs" onClick={onQuiz} disabled={lancement}>
            <ListChecks className="size-3.5" />
            {lancement ? t("pc.preparation") : t("qr.quiz_cible")}
          </Button>
        )}
      </div>
    </li>
  )
}

function messageDeFin(pourcentage: number, diagnostic: boolean, chrono = false) {
  // Un diagnostic n'est pas une note : un 30 % n'y est pas un échec, c'est un point
  // de départ. Le message ne doit ni féliciter ni consoler.
  if (diagnostic) return { titre: t("qr.diag_titre"), texte: t("qr.diag_texte") }
  if (pourcentage >= 100) return { titre: t("qr.fin100_titre"), texte: t("qr.fin100_texte") }
  if (pourcentage >= 90) return { titre: t("qr.fin90_titre"), texte: t("qr.fin90_texte") }
  if (pourcentage >= 70) return { titre: t("qr.fin70_titre"), texte: t("qr.fin70_texte") }
  // Un quiz chronométré ne rapporte pas de points : ne pas en promettre au prochain essai (test élève 2026-11-02).
  if (pourcentage >= 40) return { titre: t("qr.fin40_titre"), texte: t(chrono ? "qr.fin40_texte_chrono" : "qr.fin40_texte") }
  return { titre: t("qr.fin0_titre"), texte: t("qr.fin0_texte") }
}

/** Un refus d'accès dit ce qui reste ouvert, dans les mots de l'élève ; le texte brut du serveur (« Abonnement requis pour ce cursus. ») ne dit rien. */
function messageErreur(err: unknown, cleDefaut: "qr.err_lancer" | "qr.err_relancer"): string {
  if (err instanceof ApiError && err.status === 403) return t("qr.err_abonnement")
  return err instanceof ApiError ? err.message : t(cleDefaut)
}

export function QuizResultPage() {
  useI18n()
  const queryClient = useQueryClient()
  useSeo({ title: t("qr.seo") })
  // Un visiteur qui a joué avec un compte invité (voir lib/invite) : une vraie séance, mais pas de compte à montrer.
  const invite = useEssaiSansCompte()
  const cursusAbonne = useCursusAbonne()

  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { country } = useCountry()
  const [result, setResult] = useState<QuizResult | null>(null)
  const [error, setError] = useState("")
  const [refaisant, setRefaisant] = useState(false)
  const [erreurRefaire, setErreurRefaire] = useState("")
  const [themeEnLancement, setThemeEnLancement] = useState<number | null>(null)
  const [erreurQuizCible, setErreurQuizCible] = useState("")
  // Le quiz GRATUIT de la même matière : un défi se lance par un lien qui marche sans compte (le quiz de l'élève, lui, est
  // peut-être payant). Les scores se comparent en proportion, donc deux quiz différents restent comparables.
  const { data: essais } = useQuery({ queryKey: ["quiz", "essais"], queryFn: ({ signal }) => listQuizEssais(signal), staleTime: 5 * 60_000 })
  const [encoreEnCours, setEncoreEnCours] = useState<"encore" | "score" | "dur" | "facile" | null>(null)
  const [erreurEncore, setErreurEncore] = useState("")

  // Rebondir tout de suite : « encore 5 questions » sur le thème le plus fragile, ou le même quiz pour battre son score
  // (le rejeu ne rapporte pas de points, voir quiz.historique). Aucune page de choix entre deux : l'envie ne dure pas.
  async function rebondir(mode: "encore" | "score" | "dur" | "facile", themeId?: number) {
    if (!result || encoreEnCours) return
    setEncoreEnCours(mode)
    setErreurEncore("")
    try {
      const session =
        mode === "score"
          ? await rejouerQuiz(Number(id))
          : await startQuizSession({ cursus: result.cursus, theme: themeId, mode: "PRATIQUE", n: 5, plus_dur: mode === "dur", plus_facile: mode === "facile" })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setErreurEncore(messageErreur(err, "qr.err_lancer"))
      setEncoreEnCours(null)
    }
  }

  async function quizCible(themeId: number) {
    if (!result || themeEnLancement !== null) return
    setThemeEnLancement(themeId)
    setErreurQuizCible("")
    try {
      const session = await startQuizSession({ cursus: result.cursus, theme: themeId, mode: "PRATIQUE", n: 10 })
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setErreurQuizCible(messageErreur(err, "qr.err_lancer"))
      setThemeEnLancement(null)
    }
  }

  async function refaireLesRatees_() {
    if (refaisant) return
    setRefaisant(true)
    setErreurRefaire("")
    try {
      const session = await refaireLesRatees(Number(id))
      navigate(`/quiz/session/${session.id}`)
    } catch (err) {
      setErreurRefaire(messageErreur(err, "qr.err_relancer"))
      setRefaisant(false)
    }
  }

  useEffect(() => {
    if (!id) return
    // Endpoint idempotent : si la session est déjà terminée, il se contente de
    // retourner le résultat déjà calculé (voir quiz.views.complete_session).
    completeQuizSession(Number(id))
      .then((resultat) => {
        setResult(resultat)
        // Terminer un quiz change TOUT ce qui se calcule à partir des réponses :
        // le taux de maîtrise d'un thème dans le parcours, l'histogramme par matière,
        // la file de révision espacée, et la séance du jour - que ce quiz vient
        // peut-être de clôturer (voir quiz.views.complete_session).
        //
        // Sans cette invalidation, l'élève revenait sur son parcours et retrouvait
        // ses chiffres d'avant : `staleTime` est à 60 s et `refetchOnWindowFocus` est
        // désactivé (voir main.tsx, choix assumé pour un catalogue qui ne bouge pas),
        // donc rien ne déclenchait de rafraîchissement. Le travail était bien
        // enregistré côté serveur - il ne se voyait simplement pas, ce qui est pire
        // qu'une erreur : l'élève croit que son quiz n'a servi à rien.
        for (const cle of ["accueil", "parcours", "parcours-resume", "maitrise", "revisions-dues", "erreurs", "plan-du-jour", "priorites", "bilan-periode", "quiz-historique", "quiz-en-cours"]) {
          queryClient.invalidateQueries({ queryKey: [cle] })
        }
        // L'accueil garde sa dernière version dans le navigateur pour s'afficher avant la réponse du serveur (voir
        // lib/accueilCache) : juste après un quiz, cette version est fausse (points, séance, « Commencer » au lieu de
        // « Séance faite » : passe Guyguy 2026-11-07, 2 à 3 s d'état périmé). On l'oublie : un squelette d'une
        // seconde vaut mieux que des chiffres d'avant.
        oublierAccueilEnCache()
      })
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : t("qr.err_charger"))
      })
  }, [id, queryClient])

  // Un quiz GRATUIT joué (un seul thème, celui qu'offre cet examen, au moins une réponse) est noté sur l'appareil avec
  // son score : la carte de l'accueil avance à la matière suivante (voir components/PremiereSeance) et le même quiz
  // relancé dira « déjà joué » (voir lib/seancesGratuites). Seulement un quiz gratuit : son thème n'a que quelques
  // questions, le rejouer redonne les mêmes. Un thème d'abonné en compte des dizaines, « déjà joué » y serait faux.
  useEffect(() => {
    if (!result || !essais || result.par_theme.length !== 1 || result.questions_repondues === 0) return
    const theme = result.par_theme[0].theme_id
    if (!essais.some((e) => e.cursus === result.cursus && e.theme === theme)) return
    marquerSeancesJouees(result.cursus, [theme], { reussies: result.score, total: result.total_questions })
  }, [result, essais])

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link to="/quiz" className="mt-3 inline-block text-sm text-primary hover:underline">
          {t("qr.retour_quiz")}
        </Link>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="mx-auto max-w-xl px-4 py-10">
        <Skeleton className="mb-4 h-8 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    )
  }

  const pourcentage = result.questions_repondues > 0 ? Math.round((result.score / result.questions_repondues) * 100) : 0
  const diagnostic = result.mode === "DIAGNOSTIC"
  // Qui n'est pas abonné à cet examen n'a que les quiz gratuits : « encore 5 questions » sur son thème lui rendrait les mêmes
  // questions (ou un refus), et « plus accessible » ou un quiz ciblé seraient refusés.
  const acces = cursusAbonne !== null && cursusAbonne === result.cursus
  // Le thème le plus faible qui a un cours à relire : c'est LE cours à recommander en premier.
  const aRevoir = result.par_theme
    .filter((theme) => theme.cours && 100 * theme.reussies / theme.total < 70)
    .sort((a, b) => a.reussies / a.total - b.reussies / b.total)[0]
  const message = messageDeFin(pourcentage, diagnostic, Boolean(result.chrono_actif))
  // Le score à battre d'un lien de défi, s'il accompagnait CETTE séance (voir lib/defiEssai) : même verdict que celui d'un essai.
  const defi = lireDefiMemorise(Number(id))
  const issueDefi = defi && result.questions_repondues > 0 ? comparerDefi(defi, result.score, result.questions_repondues) : null
  // Par le code de la matière du premier thème : `result.subject` est vide quand le quiz a été lancé par thème (« encore 5 questions »).
  const codeMatiere = result.par_theme[0]?.subject_code
  const essaiDuDefi = codeMatiere ? (essais ?? []).find((e) => e.cursus === result.cursus && e.subject_code === codeMatiere) : undefined
  // Le thème où l'élève a le plus à gagner : c'est sur lui que repart « encore 5 questions ».
  const pireTheme = [...result.par_theme].sort((a, b) => a.reussies / a.total - b.reussies / b.total)[0]
  // « Plus dur » : sur le thème où l'élève a le mieux réussi, celui où il est prêt à monter d'un cran.
  const meilleurTheme = [...result.par_theme].sort((a, b) => b.reussies / b.total - a.reussies / a.total)[0]

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      {/* En-tête : même gabarit que les autres pages - l'anneau de score à gauche, le
          message et les chiffres de la séance à droite. */}
      <div className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        {pourcentage >= 70 && !diagnostic && <Confettis />}
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative flex flex-col items-center gap-6 text-center sm:flex-row sm:gap-10 sm:text-left">
          <div className="shrink-0">
            <AnneauScore pourcentage={pourcentage} score={result.score} total={result.questions_repondues} />
          </div>
          <div className="min-w-0">
            <p className="mb-2 font-display text-sm italic text-primary">
              {diagnostic ? t("qr.diag_fini") : t("qr.quiz_fini")}
            </p>
            <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight sm:text-4xl">{message.titre}</h1>
            <p className="mt-2 max-w-md text-muted-foreground">{message.texte}</p>
            {(result.questions_passees ?? 0) > 0 && (
              <p className="mt-1 max-w-md text-sm text-muted-foreground">{tn("qr.passees", result.questions_passees ?? 0)}</p>
            )}
            {!diagnostic && (result.meilleure_serie > 0 || result.seances_cette_semaine > 0) && (
              <div className="mt-4 flex flex-wrap justify-center gap-2 sm:justify-start">
                {result.meilleure_serie > 0 && <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm shadow-xs">
                  <Flame className="size-4 text-warning" />
                  <span className="font-medium tabular-nums">{result.meilleure_serie}</span>
                  <span className="text-muted-foreground">
                    {tn("qr.serie", result.meilleure_serie)}
                  </span>
                </span>}
                {result.seances_cette_semaine > 0 && <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm shadow-xs">
                  <CalendarCheck className="size-4 text-primary" />
                  <span className="font-medium tabular-nums">{result.seances_cette_semaine}</span>
                  <span className="text-muted-foreground">
                    {tn("qr.seances", result.seances_cette_semaine)}
                  </span>
                </span>}
              </div>
            )}
          </div>
        </div>
      </div>

      {!diagnostic && <Mascotte className="mb-6" contexte={{ pourcentage, serieJours: result.serie?.jours, matiere: result.par_theme[0]?.subject_code ?? result.subject ?? undefined }} />}

      {/* Un quiz chronométré ne rapporte ni points ni maîtrise (voir quiz.chrono) : le bilan dit le temps, pas l'XP. */}
      {result.chrono_actif && <BilanChrono result={result} />}
      {result.xp && !result.chrono_actif && (
        <BilanXp
          xp={result.xp} serie={result.serie} classement={result.classement}
          score={result.score} total={result.questions_repondues}
        />
      )}
      {result.xp && !result.chrono_actif && !invite && <InvitePush className="mb-6" />}

      {/* Un quiz joué sans compte (voir lib/invite) : ses points et sa séance ne sont gardés que sur cet appareil, le temps
          d'un mois. Le compte les reprend, comme la copie d'une épreuve inédite. */}
      {invite && (
        <div className="mb-6 rounded-xl border border-primary/30 bg-primary/5 px-4 py-3.5">
          <p className="text-sm">
            <strong>{t("qr.invite_titre")}</strong> {t("qr.invite_texte")}
          </p>
          <Button asChild className="mt-3 w-full" size="lg">
            <Link to="/connexion" state={{ from: "/quiz", intent: t("qr.invite_intent") }}>
              {t("qr.invite_cta")}
            </Link>
          </Button>
        </div>
      )}

      {defi && issueDefi && (
        <p
          role="status"
          className={cn(
            "mb-6 flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium",
            issueDefi === "gagne" ? "bg-success/15" : "bg-muted/60",
          )}
        >
          <Swords className="size-4 shrink-0 text-gold-text" aria-hidden="true" />
          {t(`defi.${issueDefi}`, { a: result.score, b: result.questions_repondues, c: defi.reussies, d: defi.total })}
        </p>
      )}

      {/* Le geste le plus court pour continuer, avant tout menu : un quiz de plus, ou le même pour faire mieux. */}
      {!diagnostic && result.par_theme.length > 0 && (
        <section aria-label={t("qr.encore_aria")} className="mb-6">
          <div className="flex flex-col gap-2 sm:flex-row">
            {acces ? (
              <Button
                size="lg"
                className="rounded-full"
                disabled={encoreEnCours !== null}
                onClick={() => rebondir("encore", pireTheme?.theme_id)}
              >
                <Zap />
                {encoreEnCours === "encore" ? t("quiz.preparation") : t("qr.encore_cinq")}
              </Button>
            ) : (
              <Button asChild size="lg" className="rounded-full">
                <Link to="/quiz">
                  <Zap />
                  {t("qr.autre_matiere_gratuite")}
                </Link>
              </Button>
            )}
          </div>
          {/* Un seul geste en avant ; les variantes sont repliées (audit du 2026-11-13 : plus de dix boutons de même poids). */}
          <details className="group mt-3 rounded-xl border border-border bg-card">
            <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-2 px-4 text-sm font-medium text-muted-foreground transition-colors hover:text-primary">
              {t("qr.autres_facons")}
              <ChevronDown className="size-4 transition-transform group-open:rotate-180" aria-hidden="true" />
            </summary>
            <div className="flex flex-col gap-2 border-t border-border p-4">
          <Button
            size="lg"
            variant="outline"
            className="rounded-full"
            disabled={encoreEnCours !== null}
            onClick={() => rebondir("score")}
          >
            <RotateCcw />
            {encoreEnCours === "score" ? t("quiz.preparation") : t("qr.bats_score", { score: result.score, total: result.questions_repondues })}
          </Button>
          {acces && meilleurTheme && pourcentage >= 70 && (
            <Button
              size="lg"
              variant="outline"
              className="rounded-full"
              disabled={encoreEnCours !== null}
              onClick={() => rebondir("dur", meilleurTheme.theme_id)}
            >
              <Flame />
              {encoreEnCours === "dur" ? t("quiz.preparation") : t("qr.plus_dur")}
            </Button>
          )}
          {acces && pireTheme && pourcentage < 50 && (
            <Button
              size="lg"
              variant="outline"
              className="rounded-full"
              disabled={encoreEnCours !== null}
              onClick={() => rebondir("facile", pireTheme.theme_id)}
            >
              <Sprout />
              {encoreEnCours === "facile" ? t("quiz.preparation") : t("qr.plus_facile")}
            </Button>
          )}
          {essaiDuDefi && result.questions_repondues >= 3 && (
            <BoutonPartager
              chemin={`/quiz/essai/${essaiDuDefi.cursus}/${essaiDuDefi.subject}/${essaiDuDefi.theme}`}
              texte={t("essai.partage_defi", { a: result.score, b: result.questions_repondues, theme: "", matiere: essaiDuDefi.subject_label, cursus: essaiDuDefi.cursus_display })}
              type="quiz"
              parametres={parametresDefi(result.score, result.questions_repondues)}
              libelle={t("essai.defier")}
              size="lg"
              className="rounded-full"
            />
          )}
          <p className="text-xs text-muted-foreground">{t("qr.bats_score_note")}</p>
            </div>
          </details>
          {erreurEncore && <p role="alert" className="mt-2 text-sm text-destructive">{erreurEncore}</p>}
        </section>
      )}
      {/* Prolongement du quiz vers l'épreuve entière : seulement quand le quiz est réussi (le thème faible a déjà son cours) et
          qu'une inédite existe vraiment pour ce cursus - sinon le bloc n'apparaît pas. */}
      {!diagnostic && !result.chrono_actif && result.inedite_suggeree && pourcentage >= 70 && (
        <div className="mb-6 rounded-xl border border-gold/40 bg-gold/5 px-4 py-3.5" data-testid="quiz-vers-inedite">
          <p className="text-sm">
            <strong>{t("qr.inedite_titre")}</strong> {t("qr.inedite_texte")}
          </p>
          <Button asChild className="mt-3 w-full" size="lg" variant="outline">
            <Link to={epreuveInediteDetailPath(result.inedite_suggeree.country, result.inedite_suggeree.slug || result.inedite_suggeree.id)}>
              <Trophy />
              {t("qr.inedite_cta")}
            </Link>
          </Button>
        </div>
      )}

      {/* Le diagnostic ouvre sur ses priorités : c'est ce que l'élève venait chercher. */}
      {diagnostic && <PrioritesExamen cursusId={result.cursus} className="mb-6" />}

      {/* Le moment qui donne envie de revenir demain : on dit que la séance est faite
          et on ramène à "Aujourd'hui", d'où l'élève pourra en demander une autre. */}
      {result.seance_validee && (
        <div className="mb-6 flex flex-col gap-3 rounded-xl border border-primary/30 bg-primary/5 p-4 sm:flex-row sm:items-center">
          <CheckCircle2 className="size-6 shrink-0 text-primary" />
          <div className="min-w-0 flex-1">
            <p className="font-display font-semibold">{t("qr.seance_validee")}</p>
            <p className="text-sm text-muted-foreground">{t("qr.seance_validee_texte")}</p>
          </div>
          <Button asChild>
            <Link to={`/${country}`}>
              {t("qr.revenir")}
              <ArrowRight />
            </Link>
          </Button>
        </div>
      )}

      {/* « Ça t'a aidé ? » : l'avis de l'élève, à partir de son troisième quiz terminé et une seule fois (le serveur en
          décide, voir InviteAvis). Sous les gestes pour continuer, jamais au-dessus : réviser passe avant. Pas pour un
          invité, qui n'a pas de compte. */}
      {!invite && <InviteAvis role="eleve" className="mb-6" />}

      {/* Par thème, du plus fragile au plus solide : c'est là que se décide la suite. */}
      {result.par_theme.length > 0 && (
        <section aria-labelledby="par-theme-titre" className="mb-6">
          <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
            <h2 id="par-theme-titre" className="font-display text-xl font-semibold">{t("qr.par_theme")}</h2>
            <p className="text-sm text-muted-foreground">{t("qr.fragile_solide")}</p>
          </div>
          <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            {[...result.par_theme]
              .sort((a, b) => a.reussies / a.total - b.reussies / b.total)
              .map((theme) => (
                <LigneTheme
                quizCible={acces}
                  key={theme.theme}
                  theme={theme}
                  cursusId={result.cursus}
                  country={country}
                  onQuiz={() => quizCible(theme.theme_id)}
                  lancement={themeEnLancement === theme.theme_id}
                />
              ))}
          </ul>
          {erreurQuizCible && <p role="alert" className="mt-2 text-sm text-destructive">{erreurQuizCible}</p>}
        </section>
      )}

      <div className="mb-6 hidden sm:block">
        <QuizFichePdfButtons sessionId={Number(id)} cursus={result.cursus} />
      </div>

      {/* La suite, dans l'ordre où elle sert : comprendre ce qui a été raté, PUIS le refaire.
          Quatre boutons de même poids laissaient l'élève choisir seul au moment où il a
          le plus besoin qu'on le guide. Pas pour un diagnostic, dont la suite est la
          première séance (voir PrioritesExamen). */}
      {!diagnostic && (aRevoir || result.nb_ratees > 0) && (
        <section className="mb-6 rounded-2xl border border-primary/25 bg-primary/[0.04] p-4 sm:p-5">
          <h2 className="font-display text-lg font-semibold">{t("qr.progresser")}</h2>
          <ol className="mt-3 flex flex-col gap-2.5">
            {aRevoir?.cours && (
              <li>
                <Link
                  to={`/cours/${aRevoir.cours.slug}`}
                  className="group flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 transition-colors hover:border-primary/50"
                >
                  <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary font-display text-sm font-semibold text-primary-foreground">1</span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-semibold">{t("qr.revoir_cours")}</span>
                    <span className="block truncate text-sm text-muted-foreground">{aRevoir.cours.titre}</span>
                  </span>
                  <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
                </Link>
              </li>
            )}
            {result.nb_ratees > 0 && (
              <li>
                <button
                  type="button"
                  onClick={refaireLesRatees_}
                  disabled={refaisant}
                  className="group flex w-full items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 text-left transition-colors hover:border-primary/50 disabled:opacity-60"
                >
                  <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary font-display text-sm font-semibold text-primary-foreground">
                    {aRevoir?.cours ? 2 : 1}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-semibold">
                      {refaisant ? t("qr.prepare") : tn("qr.refaire", result.nb_ratees)}
                    </span>
                    <span className="block text-sm text-muted-foreground">{t("qr.refaire_texte")}</span>
                  </span>
                  <RotateCcw className="size-4 shrink-0 text-primary" />
                </button>
                {erreurRefaire && <p role="alert" className="mt-2 text-sm text-destructive">{erreurRefaire}</p>}
              </li>
            )}
          </ol>
        </section>
      )}

      <div className="flex flex-col gap-2 sm:flex-row">
        <Button
          onClick={() => navigate("/quiz")}
          className="sm:flex-1"
          size="lg"
          variant={!diagnostic && (aRevoir || result.nb_ratees > 0) ? "outline" : "default"}
        >
          {!diagnostic && (aRevoir || result.nb_ratees > 0) ? t("qr.autre_quiz") : t("qr.refaire_quiz")}
        </Button>
        {/* Parcours et compte n'existent pas pour un invité : ses deux liens menaient à la page de connexion. */}
        {result.subject && !invite && (
          <Button asChild variant="outline" className="sm:flex-1" size="lg">
            <Link to={`/parcours/${result.subject}?cursus=${result.cursus}`}>{t("qr.retour_parcours")}</Link>
          </Button>
        )}
      </div>
      {id && (
        <p className="mt-3 text-center text-sm">
          <Link to={`/historique/quiz/${id}`} className="font-medium text-primary hover:underline">
            {t("hq.voir_reponses")}
          </Link>
        </p>
      )}
    </div>
  )
}
