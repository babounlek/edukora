import { useEffect, useRef } from "react"
import { Link } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, BookOpen, Check, Lock, PenLine, Sparkles, Target } from "lucide-react"

import { continuerSeanceDuJour, getPlanDuJour, terminerSeanceDuJour } from "@/api/endpoints"
import type { EtapeSeance, PlanDuJour, Seance } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { coursReaderPath, epreuveReaderPath, themesFrequentsPath } from "@/lib/countryPath"
import { trackEvent } from "@/lib/analytics"
import { formatCompteARebours } from "@/components/CompteAReboursBadge"

/**
 * "Aujourd'hui : Limites de fonctions - 25 min" : une seule chose à faire, et un seul
 * bouton pour la commencer.
 *
 * C'est le cœur du passage de bibliothèque à coach. Tout le reste de l'accueil (hero,
 * rails, catalogue) continue d'exister DESSOUS, inchangé - ce bloc s'ajoute en tête,
 * il ne remplace rien : `/cm` reste la page la plus indexée du site et doit rester
 * riche pour un visiteur anonyme comme pour un robot.
 *
 * Silencieusement absent pour qui n'a pas déclaré de cursus, dont l'examen est passé,
 * ou dont le cursus n'a rien d'exploitable : un bloc vide serait pire que pas de bloc.
 */
export function SeanceDuJour({ country }: { country: string }) {
  const { isAuthenticated } = useAuth()
  const queryClient = useQueryClient()

  const { data } = useQuery({
    queryKey: ["plan-du-jour"],
    queryFn: ({ signal }) => getPlanDuJour(signal),
    enabled: isAuthenticated,
  })

  const terminer = useMutation({
    mutationFn: terminerSeanceDuJour,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] }),
  })

  // La réponse de "continuer" a exactement la forme du plan (voir
  // quiz.views._charge_utile_plan) : on l'écrit directement dans le cache plutôt que
  // de réinvalider, pour que la séance suivante s'affiche sans un aller-retour de plus.
  const continuer = useMutation({
    mutationFn: continuerSeanceDuJour,
    onSuccess: (plan) => queryClient.setQueryData(["plan-du-jour"], plan),
  })

  // "Séance affichée" une seule fois par séance, jamais à chaque rendu : le
  // dénominateur du seul chiffre qui compte (combien reviennent faire une séance) ne
  // vaut rien s'il enfle à chaque re-rendu de React.
  const seanceTracee = useRef<number | null>(null)
  const seanceId = data?.seance?.id ?? null
  const verrouillee = data?.seance?.verrouillee
  useEffect(() => {
    if (seanceId === null || seanceTracee.current === seanceId) return
    seanceTracee.current = seanceId
    trackEvent("plan_affiche", { verrouillee: Boolean(verrouillee) })
  }, [seanceId, verrouillee])

  if (!isAuthenticated || !data || !data.seance) return null
  if (data.etat !== "plan_pret" && data.etat !== "deja_fait_aujourdhui") return null

  return (
    <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
      <div className="animate-fade-up rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-5 sm:p-6">
        <EnTete plan={data} />
        {data.etat === "deja_fait_aujourdhui" ? (
          <SeanceFaite
            plan={data}
            country={country}
            onContinuer={() => continuer.mutate()}
            continuationEnCours={continuer.isPending}
            // Le serveur a répondu "rien à proposer" : la demande a abouti, il n'y
            // avait simplement plus rien (voir seance_supplementaire).
            plusRienAProposer={continuer.isSuccess && continuer.data?.etat === "rien_a_proposer"}
          />
        ) : (
          <SeanceAFaire
            plan={data}
            country={country}
            onTerminer={() => terminer.mutate()}
            terminaisonEnCours={terminer.isPending}
          />
        )}
      </div>
    </section>
  )
}

function EnTete({ plan }: { plan: PlanDuJour }) {
  const compte = plan.compte_a_rebours ? formatCompteARebours(plan.compte_a_rebours) : ""
  return (
    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
      {plan.cursus?.examen_display}
      {plan.cursus?.series ? ` ${plan.cursus.series.code}` : ""}
      {/* Le compte à rebours vit ici aussi, pas seulement dans l'en-tête : c'est ce
          qui transforme "réviser les limites" en "réviser les limites parce qu'il
          reste 244 jours". Toujours en gris, jamais en rouge. */}
      {compte && <span className="normal-case"> · {compte}</span>}
    </p>
  )
}

function SeanceAFaire({
  plan, country, onTerminer, terminaisonEnCours,
}: {
  plan: PlanDuJour
  country: string
  onTerminer: () => void
  terminaisonEnCours: boolean
}) {
  const seance = plan.seance as Seance
  const premiere = seance.etapes[0]

  return (
    <>
      <h2 className="mt-1 font-display text-2xl font-semibold">
        Aujourd'hui : {titreDeLaSeance(seance)}
      </h2>
      <p className="mt-1 text-sm text-muted-foreground">
        {seance.subject ? `${seance.subject.label} · ` : ""}
        {seance.duree_estimee_min} min
        {seance.nb_etapes > 1 ? ` · ${seance.nb_etapes} étapes` : ""}
      </p>

      <Frequence seance={seance} />

      {seance.verrouillee ? (
        <Verrou />
      ) : (
        <>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            {premiere && (
              <Button asChild size="lg">
                <Link
                  to={lienEtape(premiere, country, plan)}
                  onClick={() => trackEvent("plan_seance_demarree", { origine: seance.origine })}
                >
                  Commencer
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
            )}
            {/* Marquer la séance faite reste une action de l'élève : on ne sait pas
                détecter qu'il a vraiment lu et compris, et un "terminé" décidé à sa
                place fausserait le seul chiffre qui dira si ce plan marche. */}
            <Button variant="ghost" size="sm" onClick={onTerminer} disabled={terminaisonEnCours}>
              <Check className="size-4" />
              J'ai fini
            </Button>
          </div>
          <ol className="mt-4 flex flex-col gap-1.5">
            {seance.etapes.map((etape, index) => (
              <li key={index}>
                <Link
                  to={lienEtape(etape, country, plan)}
                  className="group flex items-center gap-2.5 rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-accent/50"
                >
                  <IconeEtape type={etape.type} />
                  <span className="min-w-0 flex-1 truncate">{etape.libelle}</span>
                  <span className="shrink-0 text-xs text-muted-foreground">{etape.duree_min} min</span>
                </Link>
              </li>
            ))}
          </ol>
        </>
      )}

      {/* Sortie de secours, volontairement discrète : un plan qu'on ne peut pas
          contourner est vécu comme une contrainte, mais le remonter au même niveau
          que "Commencer" rendrait à l'élève la charge de choisir - exactement ce
          dont ce bloc le décharge. */}
      <p className="mt-4 text-xs text-muted-foreground">
        Ce n'est pas ce que tu veux réviser ?{" "}
        <Link
          to={themesFrequentsPath(country)}
          onClick={() => trackEvent("plan_theme_ignore", { origine: seance.origine })}
          className="underline underline-offset-4 hover:text-primary"
        >
          Choisir un autre thème
        </Link>
      </p>
    </>
  )
}

function SeanceFaite({
  plan, country, onContinuer, continuationEnCours, plusRienAProposer,
}: {
  plan: PlanDuJour
  country: string
  onContinuer: () => void
  continuationEnCours: boolean
  plusRienAProposer: boolean
}) {
  const seance = plan.seance as Seance
  return (
    <>
      <h2 className="mt-1 flex items-center gap-2 font-display text-2xl font-semibold">
        <Check className="size-6 shrink-0 text-primary" />
        Séance faite
      </h2>
      <p className="mt-1 text-sm text-muted-foreground">
        {titreDeLaSeance(seance)}
        {/* Le score du quiz quand il y en avait un - jamais un "0/0", qui se lirait
            comme un échec là où il n'y avait simplement rien à noter. */}
        {seance.score && <> · {seance.score.reussies}/{seance.score.total}</>}
        {/* Un compte sur 7 jours glissants, jamais une série de jours consécutifs :
            une journée manquée ne remet rien à zéro (voir
            seances_terminees_cette_semaine). */}
        {typeof plan.seances_cette_semaine === "number" && (
          <> · {plan.seances_cette_semaine} séance{plan.seances_cette_semaine > 1 ? "s" : ""} cette semaine</>
        )}
      </p>
      {/* "Continuer" enchaîne sur une VRAIE séance suivante, jamais sur la liste des
          thèmes : renvoyer au catalogue quelqu'un qui vient de faire ce qu'on lui a
          demandé, c'est lui rendre la charge de choisir au moment précis où il
          méritait qu'on continue à le guider. */}
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <span className="text-sm text-muted-foreground">Prochaine séance demain.</span>
        <Button variant="outline" size="sm" onClick={onContinuer} disabled={continuationEnCours}>
          {continuationEnCours ? "Je cherche…" : "Continuer maintenant"}
          <ArrowRight className="size-4" />
        </Button>
      </div>
      {/* Il n'y avait plus rien à proposer - dit franchement plutôt que par un bouton
          qui ne fait rien. */}
      {plusRienAProposer && (
        <p className="mt-2 text-xs text-muted-foreground">
          Tu as fait le tour de ce qu'on peut te proposer aujourd'hui.{" "}
          <Link to={themesFrequentsPath(country)} className="underline underline-offset-4 hover:text-primary">
            Choisir un thème toi-même
          </Link>
        </p>
      )}
    </>
  )
}

function Frequence({ seance }: { seance: Seance }) {
  if (!seance.frequence) return null
  const { occurrences, epreuves_total } = seance.frequence
  return (
    <p className="mt-3 inline-flex items-center gap-2 rounded-full border border-gold/40 bg-gold/10 px-3 py-1 text-xs font-medium">
      <Target className="size-3.5 shrink-0" />
      Tombé dans {occurrences} des {epreuves_total} dernières épreuves
    </p>
  )
}

function Verrou() {
  return (
    <div className="mt-4 flex flex-wrap items-center gap-3">
      <Button asChild size="lg">
        <Link to="/tarifs" onClick={() => trackEvent("plan_verrouille_clic")}>
          <Lock className="size-4" />
          Débloquer ma séance
        </Link>
      </Button>
      <span className="text-xs text-muted-foreground">Abonnement requis pour ouvrir le contenu.</span>
    </div>
  )
}

function IconeEtape({ type }: { type: EtapeSeance["type"] }) {
  const commun = "size-4 shrink-0 text-primary"
  if (type === "cours") return <BookOpen className={commun} />
  if (type === "exercice") return <PenLine className={commun} />
  return <Sparkles className={commun} />
}

/** Le thème travaillé, ou à défaut ce que la séance propose de faire. */
function titreDeLaSeance(seance: Seance): string {
  if (seance.theme) return seance.theme.name
  if (seance.savoir) return seance.savoir.intitule
  if (seance.origine === "DIAGNOSTIC") return "on situe ton niveau"
  return seance.origine_display
}

/**
 * Où mène une étape. Le quiz part vers QuizStartPage avec son thème prérempli
 * (paramètres déjà supportés, voir QuizStartPage) plutôt que de créer la session ici :
 * une session créée par un clic qui n'aboutit pas laisserait une session vide en base.
 */
function lienEtape(etape: EtapeSeance, country: string, plan: PlanDuJour): string {
  if (etape.type === "cours") return coursReaderPath(etape.slug)
  if (etape.type === "exercice") return epreuveReaderPath(country, etape.lesson_slug)
  const params = new URLSearchParams()
  if (plan.cursus) params.set("cursus", String(plan.cursus.id))
  if (plan.seance?.theme) params.set("theme", String(plan.seance.theme.id))
  // Fait remonter au serveur que ce quiz est l'étape finale de la séance : c'est lui
  // qui la clôt et en garde le score, l'élève n'a plus à déclarer ce qu'il vient de
  // faire sous les yeux de l'application.
  if (plan.seance) params.set("seance", String(plan.seance.id))
  // Le nombre de questions annoncé par l'étape, sinon la séance promet "5 questions"
  // et en sert 10 (le défaut de QuizStartPage) : un budget de 25 minutes qui déborde
  // dès la première séance, c'est la promesse du plan qui tombe.
  params.set("n", String(etape.n))
  const query = params.toString()
  return query ? `/quiz?${query}` : "/quiz"
}
