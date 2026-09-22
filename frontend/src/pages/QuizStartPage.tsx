import { useEffect, useRef, useState } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import {
  ArrowRight,
  CheckCircle2,
  ListChecks,
  Lock,
  Minus,
  Plus,
  Sparkles,
  Target,
} from "lucide-react"

import { listMySubscriptions, listQuizSubjects, startQuizSession } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ModeQuiz, Subject, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Etape, EtapesPresentation, Eyebrow, LigneRecap, RecapVide } from "@/components/Configurateur"
import { DemoQuizQuestion } from "@/components/DemoQuizQuestion"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { trackEvent } from "@/lib/analytics"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

// Bornes du nombre de questions. Le maximum n'est pas connu du client (contrairement à
// /fiches, aucun endpoint d'éligibilité ici) : le backend sert simplement moins de
// questions si la banque est plus courte (voir quiz.services.generer_session, qui
// tronque au lieu d'échouer). 30 reste un plafond raisonnable pour une seule séance.
const N_MIN = 1
const N_MAX = 30
const N_PRESETS = [5, 10, 15, 20]

export function QuizStartPage() {
  useSeo({
    title: "Quiz",
    description: "Entraîne-toi ou évalue ton niveau avec des questions tirées des corrigés de ton cursus.",
  })

  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()

  // Lancement direct depuis un bouton "Quiz" externe (voir ThemesFrequents.tsx) -
  // `cursus` prime sur le premier abonnement actif tant qu'il en fait partie, `theme`
  // déclenche lancer() dès que ce cursus est effectivement sélectionné (voir l'effet
  // plus bas). Sans abonnement actif sur ce cursus précis, ces paramètres restent
  // simplement sans effet - la page retombe sur son comportement normal.
  const [searchParams] = useSearchParams()
  const cursusParam = searchParams.get("cursus")
  const themeParam = searchParams.get("theme")
  const themeAutoLanceRef = useRef(false)

  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
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
      const active = subs.filter((sub) => sub.is_active)
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
    setSelectedSubject("")
    // Une seule matière servie sur ce cursus : la présélectionner supprime un choix qui
    // n'en est pas un, maintenant que "Toutes les matières" ne fournit plus de valeur
    // par défaut au sélecteur.
    listQuizSubjects(sub.cursus.id).then((data) => {
      setSubjects(data)
      if (data.length === 1) setSelectedSubject(String(data[0].id))
    })
  }, [selectedCursus, subscriptions])

  /**
   * Démarre une séance. Sans `theme` : la configuration du formulaire. Avec `theme` :
   * un entraînement ciblé lancé depuis un lien externe (voir l'auto-lancement plus
   * bas) - toujours en pratique libre (un test de niveau sur un thème unique n'a pas
   * de sens) et sans filtre matière, déjà impliqué par le thème lui-même.
   */
  async function lancer(theme?: number) {
    // Un thème ciblé porte déjà sa matière ; sans lui, le formulaire exige désormais
    // un choix explicite (plus d'option "Toutes les matières").
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
        n,
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
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <Skeleton className="mb-6 h-40 w-full rounded-2xl" />
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)]">
          <Skeleton className="h-96 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  const cursusChoisi = subscriptions.find((s) => String(s.cursus.id) === selectedCursus)?.cursus
  const subjectChoisi = subjects.find((s) => String(s.id) === selectedSubject)
  const enCours = starting || startingThemeId !== null

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
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
            <Target className="size-5" />
          </div>
          <Eyebrow>Entraînement personnalisé</Eyebrow>
          <h1 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">Quiz</h1>
          <p className="mt-3 max-w-md text-lg font-medium leading-snug text-foreground/90">
            Entraîne-toi librement, ou fais le point avec un test de niveau.
          </p>
          <p className="mt-2 max-w-md text-muted-foreground">
            Chaque réponse est rattachée à un thème précis de ton programme - le quiz repère ce que tu dois
            retravailler et te le repropose au bon moment.
          </p>
        </div>
      </div>

      {/* Même structure que /fiches : configurateur à gauche, récapitulatif collant et
          panneau personnel à droite - les deux outils de la plateforme doivent se
          prendre en main de la même façon. */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)]">
        <div className="flex min-w-0 flex-col gap-6">
          {subscriptions.length === 0 ? (
            <Card className="overflow-hidden border-primary/25 bg-gradient-to-br from-primary/5 via-transparent to-transparent">
              <CardContent className="flex flex-col items-start gap-4 pt-6">
                {/* Le cadenas ne s'affiche que s'il dit vrai : à un abonné sans cursus
                    actif, il nomme un accès à débloquer. Au visiteur déconnecté, il
                    annonçait une interdiction avant même d'avoir dit ce qu'est le Quiz -
                    mauvaise première impression pour la seule page qui doit l'expliquer. */}
                <span className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
                  {isAuthenticated ? <Lock className="size-5" /> : <Target className="size-5" />}
                </span>
                <div>
                  <p className="font-display text-base font-semibold">
                    {isAuthenticated ? "Débloque le Quiz" : "Comment marche le Quiz"}
                  </p>
                  {/* Rien de plus quand la page est publique : le hero au-dessus porte déjà
                      la promesse, la répéter ici la faisait lire deux fois en quinze
                      centimètres. Les étapes ci-dessous disent le "comment", pas le "quoi". */}
                  {isAuthenticated && (
                    <p className="mt-1 text-sm text-muted-foreground">
                      Réservé aux cursus avec un abonnement actif - repère tes lacunes et révise exactement ce qu'il
                      faut, au bon moment.
                    </p>
                  )}
                </div>
                <EtapesPresentation
                  etapes={[
                    "Tu choisis ta matière, ton mode et le nombre de questions.",
                    "Tu réponds ; chaque réponse est rattachée à un thème précis de ton programme.",
                    "Les thèmes fragiles reviennent d'eux-mêmes les jours suivants, jusqu'à être acquis.",
                  ]}
                />
                {/* Déconnecté, la connexion passe devant les tarifs : un abonnement déjà
                    actif sur un autre appareil est le cas le plus fréquent ici, et payer
                    une deuxième fois faute de s'être connecté serait le pire aboutissement
                    possible de cette page. Le w-full va sur le conteneur des deux liens,
                    pas seulement sur le bouton : sous un parent items-start il se
                    rétracterait à la largeur de son contenu, et le w-full du bouton
                    n'aurait plus que ça à remplir (269px au lieu de la pleine largeur,
                    constaté à 375px). */}
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
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="font-display text-lg">Configurer ma séance</CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="flex flex-col">
                  <Etape numero={1} titre="Cursus et matière" fait={Boolean(selectedCursus && selectedSubject)}>
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="flex flex-col gap-1.5">
                        <label
                          htmlFor="quiz-cursus"
                          className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                        >
                          Cursus
                        </label>
                        <Select value={selectedCursus} onValueChange={setSelectedCursus}>
                          <SelectTrigger id="quiz-cursus">
                            <SelectValue placeholder="Choisis ton cursus" />
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

                      <div className="flex flex-col gap-1.5">
                        <label
                          htmlFor="quiz-matiere"
                          className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                        >
                          Matière
                        </label>
                        <Select
                          value={selectedSubject}
                          onValueChange={setSelectedSubject}
                          disabled={!selectedCursus || subjects.length === 0}
                        >
                          <SelectTrigger id="quiz-matiere">
                            <SelectValue placeholder="Choisis la matière" />
                          </SelectTrigger>
                          <SelectContent>
                            {subjects.map((subject) => (
                              <SelectItem key={subject.id} value={String(subject.id)}>
                                {subject.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {/* La liste ne contient que les matières déjà servies : quand
                            elle est vide, le sélecteur désactivé ne dit pas pourquoi. */}
                        {selectedCursus && subjects.length === 0 && (
                          <p className="text-xs text-muted-foreground">
                            Aucune matière n'a encore de questions sur ce cursus.
                          </p>
                        )}
                      </div>
                    </div>
                  </Etape>

                  <Etape
                    numero={2}
                    titre="Mode"
                    aide="Deux façons de travailler : creuser tes lacunes, ou faire le point."
                    fait
                    inactif={!selectedCursus}
                  >
                    <div className="grid gap-2 sm:grid-cols-2">
                      <button
                        type="button"
                        onClick={() => setMode("PRATIQUE")}
                        aria-pressed={mode === "PRATIQUE"}
                        className={cn(
                          "relative flex flex-col items-start gap-2 rounded-xl border px-3.5 py-3 text-left transition-all",
                          mode === "PRATIQUE"
                            ? "border-primary bg-primary/5 shadow-sm"
                            : "border-border hover:border-primary/40 hover:bg-accent/40",
                        )}
                      >
                        {mode === "PRATIQUE" && (
                          <CheckCircle2 className="absolute right-2.5 top-2.5 size-4 text-primary" />
                        )}
                        <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                          <Sparkles className="size-3.5" />
                        </span>
                        <span className="text-sm font-medium">Pratique libre</span>
                        <span className="text-xs text-muted-foreground">
                          Cible davantage les thèmes où tu échoues, au fil de tes sessions.
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setMode("DIAGNOSTIC")}
                        aria-pressed={mode === "DIAGNOSTIC"}
                        className={cn(
                          "relative flex flex-col items-start gap-2 rounded-xl border px-3.5 py-3 text-left transition-all",
                          mode === "DIAGNOSTIC"
                            ? "border-primary bg-primary/5 shadow-sm"
                            : "border-border hover:border-primary/40 hover:bg-accent/40",
                        )}
                      >
                        {mode === "DIAGNOSTIC" && (
                          <CheckCircle2 className="absolute right-2.5 top-2.5 size-4 text-primary" />
                        )}
                        <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                          <ListChecks className="size-3.5" />
                        </span>
                        <span className="text-sm font-medium">Test de niveau</span>
                        <span className="text-xs text-muted-foreground">
                          Difficultés variées, pour situer ton niveau.
                        </span>
                      </button>
                    </div>
                  </Etape>

                  <Etape numero={3} titre="Longueur" fait inactif={!selectedCursus} dernier>
                    <div className="flex flex-col gap-1.5">
                      <label
                        htmlFor="quiz-n"
                        className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                      >
                        Nombre de questions
                      </label>
                      <div className="flex flex-wrap items-center gap-2">
                        <div className="flex items-center gap-1">
                          <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            className="size-10 shrink-0"
                            onClick={() => setN((v) => Math.max(N_MIN, v - 1))}
                            disabled={n <= N_MIN}
                            aria-label="Une question de moins"
                          >
                            <Minus className="size-4" />
                          </Button>
                          <Input
                            id="quiz-n"
                            type="number"
                            min={N_MIN}
                            max={N_MAX}
                            value={n}
                            onChange={(e) =>
                              setN(Math.max(N_MIN, Math.min(N_MAX, Number(e.target.value) || N_MIN)))
                            }
                            className="w-16 text-center tabular-nums"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            className="size-10 shrink-0"
                            onClick={() => setN((v) => Math.min(N_MAX, v + 1))}
                            disabled={n >= N_MAX}
                            aria-label="Une question de plus"
                          >
                            <Plus className="size-4" />
                          </Button>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {N_PRESETS.map((valeur) => (
                            <button
                              key={valeur}
                              type="button"
                              onClick={() => setN(valeur)}
                              className={cn(
                                "rounded-full border px-3 py-1.5 text-xs font-medium tabular-nums transition-colors",
                                n === valeur
                                  ? "border-primary bg-primary/10 text-primary"
                                  : "border-border text-muted-foreground hover:border-primary/40 hover:bg-accent/40",
                              )}
                            >
                              {valeur}
                            </button>
                          ))}
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Tu peux quitter une séance en cours de route : tes réponses déjà validées sont conservées.
                      </p>
                    </div>
                  </Etape>
                </ol>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Récapitulatif ET points faibles collent ensemble, dans un même conteneur :
            rendre la seule carte du haut collante la ferait glisser par-dessus la
            suivante au défilement (un élément collant reste dans le flux, ses frères
            ne se décalent pas). Même correctif que sur /fiches. */}
        <aside className="min-w-0">
          <div className="flex flex-col gap-6 lg:sticky lg:top-20">
            {/* Sans abonnement, cette colonne ne rendait rien : la présentation occupait
                60 % de la largeur et les 40 % restants étaient blancs, ce qui se lisait
                comme une page inachevée plutôt que comme une page de présentation. */}
            {subscriptions.length === 0 && (
              <DemoQuizQuestion
                lienConnexion={
                  !isAuthenticated ? (
                    <Link
                      to="/connexion"
                      state={{ from: "/quiz", intent: "Connecte-toi pour lancer ton quiz." }}
                      className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                    >
                      Lancer une vraie séance
                    </Link>
                  ) : (
                    <Link
                      to="/tarifs"
                      className="text-sm font-medium text-primary underline-offset-4 hover:underline"
                    >
                      Lancer une vraie séance
                    </Link>
                  )
                }
              />
            )}

            {subscriptions.length > 0 && (
              <Card>
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 font-display text-base">
                    <Sparkles className="size-4 text-primary" />
                    Récapitulatif
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  <div className="flex flex-col gap-2.5">
                    <LigneRecap label="Cursus">
                      {cursusChoisi ? (
                        <>
                          {cursusChoisi.examen_display}
                          {cursusChoisi.series ? ` - ${cursusChoisi.series.code}` : ""}
                        </>
                      ) : (
                        <RecapVide />
                      )}
                    </LigneRecap>
                    <LigneRecap label="Matière">
                      {subjectChoisi?.label ?? <RecapVide />}
                    </LigneRecap>
                    <LigneRecap label="Mode">
                      {mode === "PRATIQUE" ? "Pratique libre" : "Test de niveau"}
                    </LigneRecap>
                    <LigneRecap label="Questions">
                      <span className="tabular-nums">{n}</span>
                    </LigneRecap>
                  </div>

                  {error && <p className="text-sm text-destructive">{error}</p>}

                  <div className="h-px bg-gradient-to-r from-gold/0 via-gold/60 to-gold/0" />

                  <Button
                    onClick={() => lancer()}
                    disabled={!selectedCursus || !selectedSubject || enCours}
                    size="lg"
                    className="w-full"
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
                  {(!selectedCursus || !selectedSubject) && (
                    <p className="text-center text-xs text-muted-foreground">
                      {!selectedCursus ? "Choisis un cursus pour commencer." : "Choisis une matière."}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
