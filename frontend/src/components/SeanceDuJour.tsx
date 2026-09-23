import { useEffect, useRef } from "react"
import { Link } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, BookOpen, Check, Lock, PenLine, RotateCcw, Sparkles, Target } from "lucide-react"

import {
  continuerSeanceDuJour, getPlanDuJour, listCursus, proposerAutreChose, terminerSeanceDuJour, updateMe,
} from "@/api/endpoints"
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

  // Même principe : la réponse EST le plan, on l'écrit dans le cache. Un
  // "rien_a_proposer" ne doit surtout pas l'écraser - la séance refusée reste à
  // l'écran, et c'est seulement là qu'on rend la main sur le catalogue.
  const autreChose = useMutation({
    mutationFn: proposerAutreChose,
    onSuccess: (plan) => {
      if (plan.seance) queryClient.setQueryData(["plan-du-jour"], plan)
    },
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

  if (!isAuthenticated || !data) return null

  // Connecté mais sans examen déclaré : on ne peut rien proposer, mais se taire
  // laissait l'élève sans aucun chemin - l'écran d'onboarding ne revenait pas et la
  // page Compte ne propose pas ce réglage. Un coach qui ne sait pas ce qu'on prépare
  // doit le demander, pas disparaître.
  if (data.etat === "cursus_inconnu") return <DeclarerSonExamen country={country} />

  if (!data.seance) return null
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
            onAutreChose={() => {
              // L'évènement part du refus lui-même, jamais du succès du remplacement :
              // c'est le refus qui est le contre-indicateur à surveiller (au-delà
              // d'environ 30 % des séances, la sélection n'est pas crédible).
              trackEvent("plan_theme_ignore", { origine: data.seance?.origine })
              autreChose.mutate()
            }}
            remplacementEnCours={autreChose.isPending}
            plusRienAProposer={autreChose.isSuccess && autreChose.data?.etat === "rien_a_proposer"}
          />
        )}
      </div>
    </section>
  )
}

/**
 * "BAC C · J-243" au-dessus de la séance - mais UNIQUEMENT là où la barre du haut ne
 * l'affiche pas déjà.
 *
 * Le badge du Header est en `hidden sm:inline` : visible à partir de 640 px, et
 * relégué dans le menu hamburger en dessous. Sans ce `sm:hidden` complémentaire, la
 * même ligne apparaissait donc deux fois sur desktop, à quelques dizaines de pixels
 * d'écart ; en la retirant purement et simplement, on l'aurait perdue sur téléphone,
 * où elle est justement le plus utile. Résultat : affichée exactement une fois, à
 * toutes les largeurs.
 */
function EnTete({ plan }: { plan: PlanDuJour }) {
  const compte = plan.compte_a_rebours ? formatCompteARebours(plan.compte_a_rebours) : ""
  return (
    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground sm:hidden">
      {plan.cursus?.examen_display}
      {plan.cursus?.series ? ` ${plan.cursus.series.code}` : ""}
      {/* Ce qui transforme "réviser les limites" en "réviser les limites parce qu'il
          reste 243 jours". Toujours en gris, jamais en rouge. */}
      {compte && <span className="normal-case"> · {compte}</span>}
    </p>
  )
}

function SeanceAFaire({
  plan, country, onTerminer, terminaisonEnCours, onAutreChose, remplacementEnCours, plusRienAProposer,
}: {
  plan: PlanDuJour
  country: string
  onTerminer: () => void
  terminaisonEnCours: boolean
  onAutreChose: () => void
  remplacementEnCours: boolean
  plusRienAProposer: boolean
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
          contourner est vécu comme une contrainte, mais la remonter au même niveau
          que "Commencer" rendrait à l'élève la charge de choisir - exactement ce
          dont ce bloc le décharge.

          Elle propose une AUTRE séance, jamais le catalogue : quand l'élève dit "pas
          ça", un coach propose autre chose, il ne tend pas le sommaire. Le catalogue
          ne réapparaît que lorsqu'on a réellement épuisé ce qu'on sait proposer. */}
      <p className="mt-4 text-xs text-muted-foreground">
        Ce n'est pas ce que tu veux réviser ?{" "}
        <button
          type="button"
          onClick={onAutreChose}
          disabled={remplacementEnCours}
          className="underline underline-offset-4 hover:text-primary disabled:opacity-60"
        >
          {remplacementEnCours ? "Je cherche…" : "Propose-moi autre chose"}
        </button>
      </p>
      {plusRienAProposer && (
        <p className="mt-1 text-xs text-muted-foreground">
          On ne trouve pas mieux pour aujourd'hui.{" "}
          <Link to={themesFrequentsPath(country)} className="underline underline-offset-4 hover:text-primary">
            Choisir un thème toi-même
          </Link>
        </p>
      )}
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
      {/* Ce qui ferme la boucle : l'élève sait que ce qu'il vient de rater lui
          reviendra, et n'a donc rien à noter de son côté. Le chiffre existait déjà
          (paliers de révision espacée) et n'était simplement jamais montré. Absent
          quand le thème n'est pas dans la file - annoncer une révision qui n'aura pas
          lieu serait pire que se taire. */}
      {seance.prochaine_revision && (
        <p className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
          <RotateCcw className="size-3.5 shrink-0 text-primary" />
          On te le repropose {formatEcheance(seance.prochaine_revision)}.
        </p>
      )}

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

/**
 * "Pourquoi cette séance ?" - la fréquence à l'examen en tête, puis les autres
 * raisons.
 *
 * Tout le produit repose sur la crédibilité de sa recommandation : un élève qui ne
 * comprend pas pourquoi on lui propose ce thème n'a aucune raison de nous croire
 * plutôt que de retourner choisir lui-même. Ces lignes sont donc affichées, pas
 * repliées derrière un "voir pourquoi" - cacher l'argument, c'est le perdre.
 */
function Frequence({ seance }: { seance: Seance }) {
  if (!seance.frequence && seance.raisons.length === 0) return null
  const titre = (
    <p className="mt-4 text-xs font-medium uppercase tracking-wide text-muted-foreground">
      Pourquoi cette séance ?
    </p>
  )
  if (!seance.frequence) {
    return (
      <>
        {titre}
        <AutresRaisons seance={seance} />
      </>
    )
  }
  const { occurrences, epreuves_total, annees } = seance.frequence
  return (
    <>
      {titre}
      <div className="mt-2">
      <p className="inline-flex items-center gap-2 rounded-full border border-gold/40 bg-gold/10 px-3 py-1 text-xs font-medium">
        <Target className="size-3.5 shrink-0" />
        Tombé dans {occurrences} des {epreuves_total} dernières épreuves
      </p>
      {/* Les années concernées : sans elles, le chiffre est à croire sur parole. Le
          "…" dit qu'il y en a d'autres plutôt que de laisser croire à une liste
          complète (voir ANNEES_FREQUENCE_MAX côté serveur). */}
      {annees.length > 0 && (
        <p className="mt-1.5 text-xs text-muted-foreground">
          {annees.join(", ")}
          {occurrences > annees.length ? "…" : ""}
        </p>
      )}
      </div>
      <AutresRaisons seance={seance} />
    </>
  )
}

/** Les raisons autres que la fréquence - coefficient, ratage précédent, thème jamais
 * travaillé. Chacune est un fait déjà en base (voir raisons_de_la_seance). */
function AutresRaisons({ seance }: { seance: Seance }) {
  if (seance.raisons.length === 0) return null
  return (
    <ul className="mt-2 flex flex-col gap-1">
      {seance.raisons.map((raison) => (
        <li key={raison.code} className="flex items-start gap-1.5 text-xs text-muted-foreground">
          <Check className="mt-0.5 size-3 shrink-0 text-primary" />
          {raison.texte}
        </li>
      ))}
    </ul>
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


/**
 * "Dis-moi ce que tu prépares" : le seul écran possible tant qu'on ne sait pas quel
 * examen l'élève passe.
 *
 * Il existe parce que le silence était pire : un élève connecté sans `cursus_prepare`
 * ne voyait plus rien du coach, et n'avait aucun moyen de le réparer - l'onboarding ne
 * revenait pas (drapeau de navigateur posé une fois pour toutes) et la page Compte
 * n'offre pas ce réglage. Choisir ici écrit la déclaration sur le compte, donc elle
 * suit l'élève d'un appareil à l'autre.
 */
function DeclarerSonExamen({ country }: { country: string }) {
  const { updateUser } = useAuth()
  const queryClient = useQueryClient()

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
    enabled: Boolean(country),
  })

  const declarer = useMutation({
    mutationFn: (cursusId: number) => updateMe({ cursus_prepare: cursusId }),
    onSuccess: (utilisateur) => {
      updateUser(utilisateur)
      // La séance ne peut pas se construire tant que le cursus n'est pas connu :
      // c'est ce rechargement qui la fait apparaître dans la foulée.
      queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] })
    },
  })

  if (cursusList.length === 0) return null

  return (
    <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
      <div className="animate-fade-up rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-5 sm:p-6">
        <h2 className="font-display text-xl font-semibold">Qu'est-ce que tu prépares ?</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Dis-le une fois et tu auras chaque jour une séance faite pour ton examen, avec le compte à rebours.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {cursusList.map((cursus) => (
            <Button
              key={cursus.id}
              variant="outline"
              size="sm"
              disabled={declarer.isPending}
              onClick={() => declarer.mutate(cursus.id)}
            >
              {cursus.examen_display}
              {cursus.series ? ` ${cursus.series.code}` : ""}
            </Button>
          ))}
        </div>
      </div>
    </section>
  )
}

/**
 * "demain", "dans 3 jours" - en jours et jamais en date brute : l'échéance ne vaut
 * que par la distance qui la sépare d'aujourd'hui, et "le 26/09" oblige l'élève à
 * faire le calcul lui-même.
 *
 * Comparaison en dates locales (l'échéance est une date sans heure, voir
 * RevisionSchedule.due_at) : passer par des horodatages ferait basculer le résultat
 * d'un jour selon l'heure à laquelle l'élève ouvre la page.
 */
function formatEcheance(dueAt: string): string {
  const [annee, mois, jour] = dueAt.split("-").map(Number)
  const echeance = new Date(annee, mois - 1, jour)
  const maintenant = new Date()
  const aujourdhui = new Date(maintenant.getFullYear(), maintenant.getMonth(), maintenant.getDate())
  const jours = Math.round((echeance.getTime() - aujourdhui.getTime()) / 86400000)
  if (jours <= 0) return "dès aujourd'hui"
  if (jours === 1) return "demain"
  return `dans ${jours} jours`
}
