import { useEffect, useRef, useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ArrowRight, BookOpen, Check, ChevronDown, ChevronRight, Clock, ListChecks, Lock, PenLine, RotateCcw,
  Shuffle, Sparkles, Target, type LucideIcon,
} from "lucide-react"

import {
  ajusterDureeSeance, continuerSeanceDuJour, definirObjectifMatiere, getPlanDuJour,
  proposerAutreChose, retirerObjectifMatiere, terminerSeanceDuJour,
} from "@/api/endpoints"
import type { EtapeSeance, PlanDuJour, Seance } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { themeExercicesPath, themesFrequentsPath } from "@/lib/countryPath"
import { lienEtape, ouvrirEtapeDeSeance } from "@/lib/seance"
import { trackEvent } from "@/lib/analytics"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { useMediaQuery } from "@/lib/useMediaQuery"
import { cn } from "@/lib/utils"
import { Ecrin } from "@/components/Progression"

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

  // Recomposition de la séance pour le temps disponible - le thème ne change pas,
  // seule sa mise en œuvre se resserre ou s'étire (voir ajuster_duree_seance).
  const duree = useMutation({
    mutationFn: ajusterDureeSeance,
    onSuccess: (plan) => queryClient.setQueryData(["plan-du-jour"], plan),
  })

  // Choisir (ou lâcher) une matière pour la semaine : la réponse est le plan recalculé.
  const objectif = useMutation({
    mutationFn: (subject: number | null) =>
      subject === null ? retirerObjectifMatiere() : definirObjectifMatiere(subject),
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

  if (!isAuthenticated || !data) return null

  // Connecté mais sans examen déclaré : rien à proposer ici. C'est le bandeau global
  // (BandeauCursus) qui le demande, sur toutes les pages - pas une invite de plus ici.
  if (data.etat === "cursus_inconnu") return null

  if (!data.seance) return null
  if (data.etat !== "plan_pret" && data.etat !== "deja_fait_aujourdhui") return null

  return (
    <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
      <Ecrin>
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
            onOuvrirEtape={(etape) => ouvrirEtapeDeSeance(queryClient, etape)}
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
            onChoisirDuree={(minutes) => duree.mutate(minutes)}
            ajustementEnCours={duree.isPending}
          />
        )}
        <ObjectifMatiereControle
          plan={data}
          enCours={objectif.isPending}
          onChoisir={(subject) => {
            trackEvent("objectif_matiere", { action: subject === null ? "retire" : "definit" })
            objectif.mutate(subject)
          }}
        />
      </Ecrin>
    </section>
  )
}

function SeanceAFaire({
  plan, country, onOuvrirEtape, onTerminer, terminaisonEnCours, onAutreChose, remplacementEnCours, plusRienAProposer,
  onChoisirDuree, ajustementEnCours,
}: {
  plan: PlanDuJour
  country: string
  onOuvrirEtape: (etape: EtapeSeance) => void
  onTerminer: () => void
  terminaisonEnCours: boolean
  onAutreChose: () => void
  remplacementEnCours: boolean
  plusRienAProposer: boolean
  onChoisirDuree: (minutes: number) => void
  ajustementEnCours: boolean
}) {
  const seance = plan.seance as Seance
  // "Reprendre" plutôt que "Commencer" dès qu'une étape a été ouverte, et on repart de
  // la première qui ne l'est pas - à défaut, de la dernière (le quiz, qui valide).
  const dejaCommencee = seance.etapes.some((e) => e.ouverte)
  const prochaine = seance.etapes.find((e) => !e.ouverte) ?? seance.etapes[seance.etapes.length - 1]
  const avecParcours = !seance.verrouillee && seance.etapes.length > 0
  const avecQuiz = seance.etapes.some((e) => e.type === "quiz")

  return (
    <div className={cn("grid gap-x-10 gap-y-6", avecParcours && "lg:grid-cols-[minmax(0,1fr)_minmax(0,24rem)] lg:grid-rows-[auto_1fr]")}>
      <div className="min-w-0">
        {/* "Aujourd'hui" en surtitre et le thème en grand : le thème est ce que l'élève
            doit retenir d'un coup d'œil, le jour n'est que le cadre. Un seul <h2> pour
            que les lecteurs d'écran lisent toujours "Aujourd'hui, concentration
            molaire" d'une traite. */}
        <h2 className="font-display">
          <span className="flex items-center gap-2 font-sans text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <Sparkles className="size-3.5" />
            Aujourd'hui
          </span>
          <span className="mt-2 block text-3xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-4xl">
            {majuscule(titreDeLaSeance(seance))}
          </span>
        </h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {seance.subject && <PastilleMatiere code={seance.subject.code} label={seance.subject.label} />}
          <Pastille icone={Clock}>{seance.duree_estimee_min} min</Pastille>
          {seance.nb_etapes > 1 && <Pastille icone={ListChecks}>{seance.nb_etapes} étapes</Pastille>}
        </div>

        <Frequence seance={seance} />

        {!seance.verrouillee && (
          <ChoixDuree seance={seance} onChoisir={onChoisirDuree} enCours={ajustementEnCours} />
        )}

        {seance.verrouillee ? (
          <Verrou />
        ) : (
          <div className="mt-6 flex flex-wrap items-center gap-3">
            {prochaine && (
              <Button
                asChild
                size="lg"
                className="group h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/30"
              >
                <Link
                  to={lienEtape(prochaine, country, plan)}
                  onClick={() => {
                    // Le démarrage ne se compte qu'une fois : reprendre n'est pas démarrer.
                    if (!dejaCommencee) trackEvent("plan_seance_demarree", { origine: seance.origine })
                    onOuvrirEtape(prochaine)
                  }}
                >
                  {dejaCommencee ? "Reprendre la séance" : "Commencer la séance"}
                  <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
            )}
            {/* Marquer la séance faite reste une action de l'élève : on ne sait pas
                détecter qu'il a vraiment lu et compris, et un "terminé" décidé à sa
                place fausserait le seul chiffre qui dira si ce plan marche. */}
            <Button
              variant="ghost"
              size="sm"
              className="rounded-full text-muted-foreground"
              onClick={onTerminer}
              disabled={terminaisonEnCours}
            >
              <Check className="size-4" />
              J'ai fini
            </Button>
            {/* Ce qui valide la séance, dit une fois près de l'action : sans ça, un
                élève qui lit le cours se croit quitte et la séance reste "à faire". */}
            {avecQuiz && (
              <p className="basis-full text-xs text-muted-foreground">
                La séance est validée quand tu termines le quiz.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Sur desktop, le parcours occupe toute la hauteur de la colonne de droite ; sur
          téléphone il vient juste sous "Commencer", avant la sortie de secours - qui
          sinon s'intercalait entre le bouton et ce qu'il lance. */}
      {avecParcours && (
        <div className="lg:col-start-2 lg:row-span-2 lg:row-start-1">
          <EtapesParPhase seance={seance} country={country} plan={plan} onOuvrirEtape={onOuvrirEtape} />
        </div>
      )}

      <div className="min-w-0 lg:col-start-1">
        {/* Sortie de secours, volontairement discrète : un plan qu'on ne peut pas
          contourner est vécu comme une contrainte, mais la remonter au même niveau
          que "Commencer" rendrait à l'élève la charge de choisir - exactement ce
          dont ce bloc le décharge.

          Elle propose une AUTRE séance, jamais le catalogue : quand l'élève dit "pas
          ça", un coach propose autre chose, il ne tend pas le sommaire. Le catalogue
          ne réapparaît que lorsqu'on a réellement épuisé ce qu'on sait proposer. */}
        <p className="flex flex-wrap items-center gap-x-1.5 text-xs text-muted-foreground">
          <Shuffle className="size-3 shrink-0" />
          Ce n'est pas ce que tu veux réviser ?
          <button
            type="button"
            onClick={onAutreChose}
            disabled={remplacementEnCours}
            className="underline underline-offset-4 transition-colors hover:text-primary disabled:opacity-60"
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
      </div>
    </div>
  )
}

/**
 * "Un devoir bientôt ? Me concentrer sur une matière" - le choix de l'élève, qui prime
 * sur la sélection automatique pendant une semaine (voir quiz.models.ObjectifMatiere).
 *
 * Volontairement une ligne discrète et non un sélecteur permanent : le plan reste "une
 * seule chose à faire", et cette ligne n'est qu'un réglage pour qui sait déjà ce qu'il
 * veut. Le choix expire de lui-même - le libellé le dit, pour qu'il ne soit jamais
 * perçu comme un enfermement.
 */
function ObjectifMatiereControle({
  plan, enCours, onChoisir,
}: {
  plan: PlanDuJour
  enCours: boolean
  onChoisir: (subject: number | null) => void
}) {
  const [ouvert, setOuvert] = useState(false)
  const matieres = plan.matieres_objectif ?? []
  const choisi = plan.objectif_matiere ?? null
  if (matieres.length < 2 && !choisi) return null

  if (choisi && !ouvert) {
    return (
      <p className="mt-4 flex flex-wrap items-center gap-x-1.5 border-t border-border/60 pt-3 text-xs text-muted-foreground">
        <Target className="size-3 shrink-0 text-primary" />
        <span>
          Tu te concentres sur <strong className="font-semibold text-foreground">{choisi.label}</strong> jusqu'au{" "}
          {formaterJourMois(choisi.jusqu_au)}.
        </span>
        <button
          type="button"
          onClick={() => onChoisir(null)}
          disabled={enCours}
          className="underline underline-offset-4 transition-colors hover:text-primary disabled:opacity-60"
        >
          Revenir au choix automatique
        </button>
        <button
          type="button"
          onClick={() => setOuvert(true)}
          className="underline underline-offset-4 transition-colors hover:text-primary"
        >
          Changer
        </button>
      </p>
    )
  }

  if (!ouvert) {
    return (
      <p className="mt-4 flex flex-wrap items-center gap-x-1.5 border-t border-border/60 pt-3 text-xs text-muted-foreground">
        <Target className="size-3 shrink-0" />
        Un devoir bientôt ?
        <button
          type="button"
          onClick={() => setOuvert(true)}
          className="underline underline-offset-4 transition-colors hover:text-primary"
        >
          Me concentrer sur une matière cette semaine
        </button>
      </p>
    )
  }

  return (
    <div className="mt-4 border-t border-border/60 pt-3">
      <p className="text-xs text-muted-foreground">Je me concentre sur… (pendant 7 jours, puis on reprend le choix automatique)</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {matieres.map((matiere) => (
          <button
            key={matiere.id}
            type="button"
            disabled={enCours}
            onClick={() => {
              onChoisir(matiere.id)
              setOuvert(false)
            }}
            className={cn(
              "rounded-full border px-3 py-1 text-xs font-medium transition-colors disabled:opacity-60",
              choisi?.subject === matiere.id
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:border-primary hover:text-foreground",
            )}
          >
            {matiere.label}
          </button>
        ))}
        <button
          type="button"
          onClick={() => setOuvert(false)}
          className="px-2 py-1 text-xs text-muted-foreground underline underline-offset-4 hover:text-primary"
        >
          Annuler
        </button>
      </div>
    </div>
  )
}

/** "02/10" à partir de la date AAAA-MM-JJ de l'API, sans passer par un fuseau. */
function formaterJourMois(dateIso: string): string {
  const [, mois, jour] = dateIso.split("-")
  return `${jour}/${mois}`
}

/** La matière, à sa couleur et son icône : la même identité que sur la progression. */
function PastilleMatiere({ code, label }: { code: string; label: string }) {
  const Icone = subjectIcon(code)
  const couleur = couleurMatiere(code)
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold", couleur.puce)}>
      <Icone className="size-3.5 shrink-0" />
      {label}
    </span>
  )
}

function Pastille({ icone: Icone, children }: { icone: LucideIcon; children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border/80 bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground backdrop-blur-sm">
      <Icone className="size-3.5 shrink-0 text-primary" />
      {children}
    </span>
  )
}

/** "concentration molaire" → "Concentration molaire" : les thèmes sont stockés en
 * minuscules, ce qui passait inaperçu après "Aujourd'hui :" mais pas en titre seul. */
function majuscule(texte: string): string {
  return texte.charAt(0).toLocaleUpperCase("fr") + texte.slice(1)
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
      <h2 className="flex items-center gap-3 font-display text-2xl font-semibold sm:text-3xl">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/25 ring-4 ring-primary/10">
          <Check className="size-5" strokeWidth={3} />
        </span>
        Séance faite
      </h2>
      <p className="mt-3 text-sm text-muted-foreground">
        {majuscule(titreDeLaSeance(seance))}
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
      <div className="mt-5 flex flex-wrap items-center gap-3">
        <span className="text-sm text-muted-foreground">Prochaine séance demain.</span>
        <Button variant="outline" size="sm" className="rounded-full" onClick={onContinuer} disabled={continuationEnCours}>
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
  // Sur téléphone, la carte "Pourquoi cette séance ?" pesait presque un écran avant même
  // le bouton "Commencer". On garde l'ARGUMENT (le chiffre de fréquence, ce qui fait
  // croire la recommandation) et on replie le détail - jauge, années, autres raisons - à
  // un toucher. Ailleurs, tout reste déplié : cacher l'argument, c'est le perdre.
  const large = useMediaQuery("(min-width: 640px)")
  const [ouvertMobile, setOuvertMobile] = useState(false)
  const ouvert = large || ouvertMobile
  if (!seance.frequence && seance.raisons.length === 0) return null
  const aDuDetail = seance.raisons.length > 0 || (seance.frequence?.annees.length ?? 0) > 0
  return (
    <div className="mt-6 max-w-2xl rounded-2xl border border-gold/30 bg-gold/[0.06] p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Pourquoi cette séance ?</p>
      {seance.frequence && <StatFrequence frequence={seance.frequence} detail={ouvert} />}
      {ouvert && <AutresRaisons seance={seance} />}
      {!large && aDuDetail && (
        <button
          type="button"
          onClick={() => setOuvertMobile((v) => !v)}
          aria-expanded={ouvertMobile}
          className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-primary"
        >
          {ouvertMobile ? "Masquer le détail" : "Voir le détail"}
          <ChevronDown className={cn("size-4 transition-transform", ouvertMobile && "rotate-180")} />
        </button>
      )}
    </div>
  )
}

/** Le chiffre en grand, et une jauge qui le rend lisible sans lire : "8 sur 10" se
 * voit avant de se comprendre. */
function StatFrequence({
  frequence, detail = true,
}: { frequence: NonNullable<Seance["frequence"]>; detail?: boolean }) {
  const { occurrences, epreuves_total, annees } = frequence
  const part = epreuves_total > 0 ? Math.min(100, Math.round((occurrences / epreuves_total) * 100)) : 0
  return (
    <div className="mt-3">
      <div className="flex items-center gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gold/20 text-gold-foreground dark:text-gold">
          <Target className="size-5" />
        </span>
        <p className="text-sm leading-snug">
          Tombé dans{" "}
          <span className="font-display text-2xl font-semibold tabular-nums">{occurrences}</span>
          <span className="text-muted-foreground"> des {epreuves_total} dernières épreuves</span>
        </p>
      </div>
      {detail && (
      <div
        className="mt-3 h-1.5 overflow-hidden rounded-full bg-gold/15"
        role="img"
        aria-label={`${occurrences} épreuves sur ${epreuves_total}`}
      >
        <div className="h-full rounded-full bg-gradient-to-r from-gold/70 to-gold" style={{ width: `${part}%` }} />
      </div>
      )}
      {/* Les années concernées : sans elles, le chiffre est à croire sur parole. Le
          "…" dit qu'il y en a d'autres plutôt que de laisser croire à une liste
          complète (voir ANNEES_FREQUENCE_MAX côté serveur). */}
      {detail && annees.length > 0 && (
        <p className="mt-2 text-xs tabular-nums text-muted-foreground">
          {annees.join(" · ")}
          {occurrences > annees.length ? " …" : ""}
        </p>
      )}
    </div>
  )
}

/** Les raisons autres que la fréquence - coefficient, ratage précédent, thème jamais
 * travaillé. Chacune est un fait déjà en base (voir raisons_de_la_seance). */
function AutresRaisons({ seance }: { seance: Seance }) {
  if (seance.raisons.length === 0) return null
  return (
    <ul className="mt-3 flex flex-col gap-1.5">
      {seance.raisons.map((raison) => (
        <li key={raison.code} className="flex items-start gap-2 text-xs text-muted-foreground">
          <span className="mt-px flex size-4 shrink-0 items-center justify-center rounded-full bg-primary/15">
            <Check className="size-2.5 text-primary" strokeWidth={3} />
          </span>
          {raison.texte}
        </li>
      ))}
    </ul>
  )
}

function Verrou() {
  return (
    <div className="mt-6 flex flex-wrap items-center gap-3">
      <Button
        asChild
        size="lg"
        className="h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/30"
      >
        <Link to="/tarifs" onClick={() => trackEvent("plan_verrouille_clic")}>
          <Lock className="size-4" />
          Débloquer ma séance
        </Link>
      </Button>
      <span className="text-xs text-muted-foreground">Abonnement requis pour ouvrir le contenu.</span>
    </div>
  )
}

function IconeEtape({ type, ouverte }: { type: EtapeSeance["type"]; ouverte: boolean }) {
  // Cochée dès qu'ouverte : elle dit "déjà passé par là", pas "compris" - la séance,
  // elle, ne se valide qu'avec le quiz.
  const Icone = ouverte ? Check : type === "cours" ? BookOpen : type === "exercice" ? PenLine : Sparkles
  return (
    <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
      <Icone className="size-4" />
    </span>
  )
}

/** Le thème travaillé, ou à défaut ce que la séance propose de faire. */
function titreDeLaSeance(seance: Seance): string {
  if (seance.theme) return seance.theme.name
  if (seance.savoir) return seance.savoir.intitule
  if (seance.origine === "DIAGNOSTIC") return "on situe ton niveau"
  return seance.origine_display
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

/**
 * "Combien de temps as-tu ?" - trois budgets, un clic.
 *
 * Un plan qui impose 25 minutes ne sert à rien les jours où l'élève en a dix : il ne
 * fait alors rien du tout plutôt que moins. Le thème ne change pas, seule sa mise en
 * œuvre se resserre (10 min : on passe directement aux questions) ou s'étire (45 min :
 * un second exercice d'examen, et un quiz plus long).
 *
 * Les libellés sont des PLAFONDS, jamais des promesses : la durée réelle affichée
 * au-dessus peut être inférieure quand le contenu manque - un "45 min" qui donne 42
 * minutes reste honnête, un "45 min" qui en donne 45 par construction ne le serait pas.
 */
function ChoixDuree({
  seance, onChoisir, enCours,
}: {
  seance: Seance
  onChoisir: (minutes: number) => void
  enCours: boolean
}) {
  if (seance.budgets_possibles.length < 2) return null
  return (
    <div className="mt-5 flex flex-wrap items-center gap-x-3 gap-y-2">
      <span className="text-xs text-muted-foreground">Combien de temps as-tu ?</span>
      <div role="group" className="inline-flex rounded-full border border-border/80 bg-muted/60 p-1">
        {seance.budgets_possibles.map((minutes) => (
          <button
            key={minutes}
            type="button"
            disabled={enCours}
            aria-pressed={minutes === seance.budget_minutes}
            onClick={() => onChoisir(minutes)}
            className={cn(
              "rounded-full px-3.5 py-1 text-xs font-medium tabular-nums transition-all disabled:opacity-60",
              minutes === seance.budget_minutes
                ? "bg-background text-primary shadow-sm ring-1 ring-primary/25"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {minutes} min
          </button>
        ))}
      </div>
    </div>
  )
}

/**
 * Les étapes groupées par phase : Comprendre, S'entraîner, Vérifier.
 *
 * La liste plate ("Relire la méthode", "Exercice 1", "5 questions") disait CE QU'ON
 * FAIT sans dire À QUOI ÇA SERT - or c'est la seule chose qui distingue une séance
 * d'une pile de liens. Nommer les phases rend le trajet lisible d'un coup d'œil, et
 * rend visible ce qui manque : une séance sans "Comprendre" se lit alors comme une
 * étape sautée à dessein (thème déjà maîtrisé) plutôt que comme un contenu absent.
 *
 * Les phases se déduisent du type de l'étape, sans donnée supplémentaire côté serveur -
 * cours/exercice/quiz correspondent exactement à comprendre/s'entraîner/vérifier.
 * Deux exercices tombent donc naturellement sous la même phase, au lieu de produire
 * deux numéros identiques.
 *
 * En dessous de deux phases (séance express : un seul quiz), les en-têtes sont tus :
 * intituler "Vérifier" une liste d'un seul élément est du bruit, pas de la structure.
 */
const PHASES = [
  { cle: "cours", titre: "Comprendre" },
  { cle: "exercice", titre: "S'entraîner" },
  { cle: "quiz", titre: "Vérifier" },
] as const

function EtapesParPhase({
  seance, country, plan, onOuvrirEtape,
}: { seance: Seance; country: string; plan: PlanDuJour; onOuvrirEtape: (etape: EtapeSeance) => void }) {
  // La page des exercices d'un thème exige la matière ET le cursus (voir
  // ThemeExercicesView) : sans eux le lien mène à une erreur 400, donc on ne l'affiche
  // pas plutôt que de proposer une impasse.
  const lienExercices =
    seance.theme && seance.subject && plan.cursus
      ? `${themeExercicesPath(country, seance.theme.id)}?subject=${seance.subject.code}&cursus=${plan.cursus.id}`
      : null
  const groupes = PHASES
    .map((phase) => ({ ...phase, etapes: seance.etapes.filter((e) => e.type === phase.cle) }))
    .filter((phase) => phase.etapes.length > 0)
  const avecTitres = groupes.length > 1

  return (
    <div className="self-start rounded-2xl border border-border/70 bg-background/70 p-4 backdrop-blur-sm sm:p-5">
      <p className="flex items-baseline justify-between gap-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
        Ton parcours
        <span className="font-sans normal-case tracking-normal tabular-nums">{seance.duree_estimee_min} min</span>
      </p>
      <ol className="mt-4 flex flex-col">
        {groupes.map((phase, index) => (
          // La frise : un fil vertical relie les phases, coupé après la dernière pour
          // que le trajet se lise comme un chemin qui aboutit, pas comme une liste.
          <li key={phase.cle} className={cn("relative", avecTitres && "pl-9 pb-4 last:pb-0")}>
            {avecTitres && (
              <>
                {index < groupes.length - 1 && (
                  <span aria-hidden className="absolute bottom-0 left-[11px] top-7 w-px bg-gradient-to-b from-primary/40 to-border" />
                )}
                <span className="absolute left-0 top-0 flex size-6 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground shadow-sm shadow-primary/30 ring-4 ring-primary/10">
                  {index + 1}
                </span>
                <p className="flex h-6 items-center text-xs font-semibold uppercase tracking-wide text-foreground/80">
                  {phase.titre}
                  {phase.cle === "quiz" && (
                    <span className="ml-2 font-medium normal-case tracking-normal text-primary">
                      · valide la séance
                    </span>
                  )}
                </p>
              </>
            )}
            <div className={cn("flex flex-col gap-1", avecTitres && "mt-1.5 -ml-2")}>
              {/* La profondeur, à un clic, sans jamais déverser 33 liens dans la carte :
                  la promesse de la séance est "une seule chose à faire", et un élève qui
                  voit 33 items n'en fait généralement aucun. Même patron que
                  "Propose-moi autre chose" - accessible, jamais promu. */}
              {phase.cle === "exercice" && seance.exercices_total > phase.etapes.length && lienExercices && (
                <Link
                  to={lienExercices}
                  className="order-last flex items-center gap-1.5 px-2 pt-1 text-xs text-muted-foreground underline underline-offset-4 transition-colors hover:text-primary"
                >
                  Les {seance.exercices_total} exercices sur ce thème
                  <ArrowRight className="size-3" />
                </Link>
              )}
              {phase.etapes.map((etape) => (
                <Link
                  key={etape.libelle}
                  to={lienEtape(etape, country, plan)}
                  onClick={() => onOuvrirEtape(etape)}
                  className="group flex items-center gap-3 rounded-xl border border-transparent px-2 py-1.5 text-sm transition-all hover:border-primary/20 hover:bg-primary/[0.04]"
                >
                  <IconeEtape type={etape.type} ouverte={etape.ouverte} />
                  <span className="line-clamp-2 min-w-0 flex-1 font-medium leading-snug">{etape.libelle}</span>
                  <span className="shrink-0 text-xs tabular-nums text-muted-foreground">{etape.duree_min} min</span>
                  <ChevronRight className="hidden size-4 shrink-0 text-muted-foreground/50 sm:block transition-all group-hover:translate-x-0.5 group-hover:text-primary" />
                </Link>
              ))}
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}
