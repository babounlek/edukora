import { useEffect, useRef, useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ArrowRight, BookOpen, Check, Clock, ListChecks, Lock, PenLine, RotateCcw,
  Shuffle, Sparkles, Target, type LucideIcon,
} from "lucide-react"

import {
  ajusterDureeSeance, continuerSeanceDuJour, definirObjectifMatiere, getPlanDuJour,
  proposerAutreChose, retirerObjectifMatiere, terminerSeanceDuJour,
} from "@/api/endpoints"
import type { EtapeSeance, EtapeSeanceVerrouillee, PlanDuJour, Seance } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { themeExercicesPath, themesFrequentsPath } from "@/lib/countryPath"
import { lienEtape, ouvrirEtapeDeSeance, seanceAffichable } from "@/lib/seance"
import { delaiDepuisAffichageAccueil } from "@/lib/accueilChrono"
import { trackEvent } from "@/lib/analytics"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
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

  const { data } = useQuery({
    queryKey: ["plan-du-jour"],
    queryFn: ({ signal }) => getPlanDuJour(signal),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated || !data || !seanceAffichable(data)) return null

  return (
    <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
      <Ecrin>
        <SeanceCorps plan={data} country={country} />
      </Ecrin>
    </section>
  )
}

/**
 * Le corps de la séance - à faire ou faite, avec ses actions - sans la carte qui
 * l'entoure. Partagé entre la vitrine (SeanceDuJour, ci-dessus, dans son Ecrin) et
 * l'accueil d'un abonné (TeteAccueil, où il vit sous le bandeau du coach) : une seule
 * implémentation des mutations, pour que "Commencer", "Propose-moi autre chose" et
 * "J'ai fini" se comportent pareil des deux côtés.
 *
 * `secondaire` : une action de second rang à côté de "Commencer" (l'annale en
 * conditions d'examen, à un mois du jour J - voir TeteAccueil).
 */
export function SeanceCorps({
  plan, country, secondaire,
}: { plan: PlanDuJour; country: string; secondaire?: ReactNode }) {
  const queryClient = useQueryClient()
  const data = plan

  // L'accueil agrégé (voir getAccueil) porte la phrase du coach et le delta, qui
  // dépendent de la séance : toute action qui la change le remet en question. Sans
  // accueil monté (vitrine), il n'y a rien d'actif à rafraîchir et l'appel est neutre.
  const rafraichirAccueil = () => queryClient.invalidateQueries({ queryKey: ["accueil"] })

  const terminer = useMutation({
    mutationFn: terminerSeanceDuJour,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] })
      rafraichirAccueil()
    },
  })

  // La réponse de "continuer" a exactement la forme du plan (voir
  // quiz.views._charge_utile_plan) : on l'écrit directement dans le cache plutôt que
  // de réinvalider, pour que la séance suivante s'affiche sans un aller-retour de plus.
  const continuer = useMutation({
    mutationFn: continuerSeanceDuJour,
    onSuccess: (plan) => {
      queryClient.setQueryData(["plan-du-jour"], plan)
      rafraichirAccueil()
    },
  })

  // Même principe : la réponse EST le plan, on l'écrit dans le cache. Un
  // "rien_a_proposer" ne doit surtout pas l'écraser - la séance refusée reste à
  // l'écran, et c'est seulement là qu'on rend la main sur le catalogue.
  const autreChose = useMutation({
    mutationFn: proposerAutreChose,
    onSuccess: (plan) => {
      if (plan.seance) {
        queryClient.setQueryData(["plan-du-jour"], plan)
        rafraichirAccueil()
      }
    },
  })

  // Recomposition de la séance pour le temps disponible - le thème ne change pas,
  // seule sa mise en œuvre se resserre ou s'étire (voir ajuster_duree_seance).
  const duree = useMutation({
    mutationFn: ajusterDureeSeance,
    onSuccess: (plan) => {
      queryClient.setQueryData(["plan-du-jour"], plan)
      rafraichirAccueil()
    },
  })

  // Choisir (ou lâcher) une matière pour la semaine : la réponse est le plan recalculé.
  const objectif = useMutation({
    mutationFn: (subject: number | null) =>
      subject === null ? retirerObjectifMatiere() : definirObjectifMatiere(subject),
    onSuccess: (plan) => {
      queryClient.setQueryData(["plan-du-jour"], plan)
      rafraichirAccueil()
    },
  })

  // "Séance affichée" une seule fois par séance, jamais à chaque rendu : le
  // dénominateur du seul chiffre qui compte (combien reviennent faire une séance) ne
  // vaut rien s'il enfle à chaque re-rendu de React.
  const seanceTracee = useRef<number | null>(null)
  const seanceId = data.seance?.id ?? null
  const verrouillee = data.seance?.verrouillee
  useEffect(() => {
    if (seanceId === null || seanceTracee.current === seanceId) return
    seanceTracee.current = seanceId
    trackEvent("plan_affiche", { verrouillee: Boolean(verrouillee) })
  }, [seanceId, verrouillee])

  if (!seanceAffichable(data)) return null

  // Les deux réglages discrets de la carte - changer de thème, choisir une matière
  // de la semaine - vivaient auparavant à deux endroits différents (l'un juste après
  // la durée, l'autre tout en bas après le parcours). Regroupés dans un seul bloc en
  // fin de carte, ils se lisent comme ce qu'ils sont : des réglages, pas une suite du
  // récit. "Propose-moi autre chose" n'a de sens que devant une séance à faire ; "Me
  // concentrer sur une matière" reste pertinent même la séance du jour terminée,
  // c'est un choix pour la semaine entière.
  const matieresObjectif = data.matieres_objectif ?? []
  const afficherObjectif = matieresObjectif.length >= 2 || Boolean(data.objectif_matiere)
  const afficherSecours = data.etat === "plan_pret"

  return (
    <>
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
          onChoisirDuree={(minutes) => duree.mutate(minutes)}
          ajustementEnCours={duree.isPending}
          secondaire={secondaire}
        />
      )}
      {(afficherSecours || afficherObjectif) && (
        <div className="mt-4 flex flex-col gap-3 border-t border-border/60 pt-3">
          {afficherSecours && (
            <SortieDeSecours
              country={country}
              onAutreChose={() => {
                // L'évènement part du refus lui-même, jamais du succès du
                // remplacement : c'est le refus qui est le contre-indicateur à
                // surveiller (au-delà d'environ 30 % des séances affichées, la
                // sélection n'est pas crédible).
                trackEvent("plan_theme_ignore", { origine: data.seance?.origine })
                autreChose.mutate()
              }}
              remplacementEnCours={autreChose.isPending}
              plusRienAProposer={autreChose.isSuccess && autreChose.data?.etat === "rien_a_proposer"}
              verrouillee={Boolean(data.seance?.verrouillee)}
            />
          )}
          {afficherObjectif && (
            <ObjectifMatiereControle
              plan={data}
              enCours={objectif.isPending}
              onChoisir={(subject) => {
                trackEvent("objectif_matiere", { action: subject === null ? "retire" : "definit" })
                objectif.mutate(subject)
              }}
            />
          )}
        </div>
      )}
    </>
  )
}

function SeanceAFaire({
  plan, country, onOuvrirEtape, onTerminer, terminaisonEnCours, onChoisirDuree, ajustementEnCours, secondaire,
}: {
  plan: PlanDuJour
  country: string
  onOuvrirEtape: (etape: EtapeSeance) => void
  onTerminer: () => void
  terminaisonEnCours: boolean
  onChoisirDuree: (minutes: number) => void
  ajustementEnCours: boolean
  secondaire?: ReactNode
}) {
  const seance = plan.seance as Seance
  // Verrouillée, chaque étape est une EtapeSeanceVerrouillee (voir types.ts) : ni
  // `cle` ni `ouverte`, rien à reprendre - seance.verrouillee dit sans ambiguïté
  // laquelle des deux formes est là, TypeScript ne peut pas le déduire seul.
  const etapes = seance.verrouillee ? [] : (seance.etapes as EtapeSeance[])
  // "Reprendre" plutôt que "Commencer" dès qu'une étape a été ouverte, et on repart de
  // la première qui ne l'est pas - à défaut, de la dernière (le quiz, qui valide).
  const dejaCommencee = etapes.some((e) => e.ouverte)
  const prochaine = etapes.find((e) => !e.ouverte) ?? etapes[etapes.length - 1]
  // Affiché même verrouillé (voir EtapesParPhase) : la structure du parcours fait
  // partie de ce que le paywall doit démontrer, pas cacher.
  const avecParcours = seance.etapes.length > 0
  const avecQuiz = seance.etapes.some((e) => e.type === "quiz")

  const frequence = seance.frequence
  const aDesAnnees = (frequence?.annees.length ?? 0) > 0

  return (
    // Un seul flux vertical, plus jamais deux colonnes qui se comparent : c'est ce
    // qui rendait la carte tantôt penchée à gauche, tantôt à droite, quelle que soit
    // la façon dont on répartissait le contenu entre les deux (voir l'historique de ce
    // fichier). Le parcours, plus bas, utilise la largeur libérée en s'étalant en
    // largeur plutôt qu'en hauteur (voir EtapesParPhase) - la seule vraie sortie du
    // problème étant de ne plus avoir deux voisins de hauteur imprévisible.
    <div>
      {/* Le titre, les pastilles, les raisons, le bouton et la durée d'un côté ; sur
          grand écran, une illustration de l'autre. La disparition de la grille à deux
          colonnes a réglé le déséquilibre de hauteur (voir plus haut), mais a laissé
          ce bloc - naturellement étroit, du texte et un bouton - flotter seul dans une
          carte large. L'illustration ne porte AUCUNE information (voir
          IllustrationSeance : `aria-hidden`) et ne force donc jamais sa hauteur
          contre celle du texte, qui varie d'une séance à l'autre (0 à 4 raisons) -
          seule une décoration peut voisiner un bloc de hauteur imprévisible sans
          recréer le problème qu'on vient de résoudre. Masquée sur téléphone/tablette,
          où l'espace manque déjà pour garder "Commencer" au-dessus du pli. */}
      <div className="lg:flex lg:items-start lg:gap-8">
      <div className="min-w-0 lg:flex-1">
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
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {seance.subject && <PastilleMatiere code={seance.subject.code} label={seance.subject.label} />}
          <Pastille icone={Clock}>{seance.duree_estimee_min} min</Pastille>
          {seance.nb_etapes > 1 && <Pastille icone={ListChecks}>{seance.nb_etapes} étapes</Pastille>}
          {/* La fréquence à l'examen, l'argument le plus fort, au même rang que les
              pastilles matière/durée plutôt que dans sa propre carte : la preuve reste
              visible en permanence (jamais repliée), mais ne pèse plus qu'une pastille
              de plus au lieu d'un second bloc dont la hauteur varie d'une séance à
              l'autre (voir PastilleFrequence). */}
          {frequence && <PastilleFrequence frequence={frequence} />}
        </div>
        {/* Les années concernées, juste sous les pastilles : sans elles, le chiffre de la
            pastille est à croire sur parole. Le "…" dit qu'il y en a d'autres plutôt que
            de laisser croire à une liste complète (voir ANNEES_FREQUENCE_MAX serveur). */}
        {aDesAnnees && frequence && (
          <p className="mt-1.5 text-xs tabular-nums text-muted-foreground">
            {frequence.annees.join(" · ")}
            {frequence.occurrences > frequence.annees.length ? " …" : ""}
          </p>
        )}
        {/* Les autres raisons (coefficient, jamais travaillé, thème déjà raté) - le fait
            qui justifie l'action précède l'action, dans l'ordre où on convaincrait
            quelqu'un à voix haute. */}
        <RaisonsSeance seance={seance} />

        {seance.verrouillee ? (
          <div className="mt-6 flex flex-wrap items-center gap-3">
            {/* La forme exacte du vrai bouton, inerte : ce que ça deviendrait une fois
                abonné, pas un message de remplacement. */}
            <Button
              size="lg"
              variant="outline"
              disabled
              className="h-12 rounded-full px-7 text-base opacity-50"
            >
              Commencer la séance
              <ArrowRight className="size-4" />
            </Button>
            {/* Le seul bouton qui fonctionne reste le plus visible des deux - un
                visiteur qui compare les deux ne doit jamais hésiter sur lequel agit. */}
            <Button
              asChild
              size="lg"
              className="group h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/30"
            >
              <Link to="/tarifs" onClick={() => trackEvent("plan_verrouille_clic")}>
                <Lock className="size-4" />
                Débloquer ma séance
              </Link>
            </Button>
            <Button variant="ghost" size="sm" disabled className="rounded-full text-muted-foreground opacity-50">
              <Check className="size-4" />
              J'ai fini
            </Button>
            {avecQuiz && (
              <p className="basis-full text-xs text-muted-foreground">
                La séance est validée quand tu termines le quiz.
              </p>
            )}
          </div>
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
                    // `delai_s` : secondes entre l'affichage de l'accueil et ce clic - LE
                    // chiffre qui juge la page (voir lib/accueilChrono).
                    if (!dejaCommencee) {
                      trackEvent("plan_seance_demarree", {
                        origine: seance.origine, delai_s: delaiDepuisAffichageAccueil(),
                      })
                    }
                    onOuvrirEtape(prochaine)
                  }}
                >
                  {dejaCommencee ? "Reprendre la séance" : "Commencer la séance"}
                  <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
            )}
            {secondaire}
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

        {/* Le réglage de durée vient APRÈS le bouton : sur téléphone, il repoussait
            "Commencer" sous le pli, et une page dont l'action principale n'est pas
            visible n'a pas d'action principale. */}
        <ChoixDuree
          seance={seance}
          onChoisir={onChoisirDuree}
          enCours={ajustementEnCours}
          desactive={seance.verrouillee}
        />
        </div>
        <IllustrationSeance />
      </div>

      {/* Le parcours en pleine largeur, sous tout le reste : plus une colonne étroite
          à comparer à sa voisine, mais un bandeau qui s'étale sur la largeur libérée
          par la disparition de la grille (voir EtapesParPhase). */}
      {avecParcours && (
        <EtapesParPhase
          seance={seance}
          country={country}
          plan={plan}
          onOuvrirEtape={onOuvrirEtape}
          verrouillee={seance.verrouillee}
        />
      )}
    </div>
  )
}

/**
 * "Ce n'est pas ce que tu veux réviser ?" - remontée par SeanceCorps et affichée aux
 * côtés d'ObjectifMatiereControle dans un seul bloc de réglages en bas de carte (voir
 * SeanceCorps) : les deux étaient auparavant à deux endroits différents de la carte,
 * l'un juste après le sélecteur de durée, l'autre tout en bas après "Ton parcours" -
 * regroupés, ils se lisent comme ce qu'ils sont, deux réglages discrets de la même
 * séance, plutôt que comme deux préoccupations séparées.
 *
 * Volontairement discrète : un plan qu'on ne peut pas contourner est vécu comme une
 * contrainte, mais la remonter au même niveau que "Commencer" rendrait à l'élève la
 * charge de choisir - exactement ce dont ce bloc le décharge.
 *
 * Propose une AUTRE séance, jamais le catalogue : quand l'élève dit "pas ça", un coach
 * propose autre chose, il ne tend pas le sommaire. Le catalogue ne réapparaît que
 * lorsqu'on a réellement épuisé ce qu'on sait proposer.
 */
function SortieDeSecours({
  country, onAutreChose, remplacementEnCours, plusRienAProposer, verrouillee,
}: {
  country: string
  onAutreChose: () => void
  remplacementEnCours: boolean
  plusRienAProposer: boolean
  verrouillee: boolean
}) {
  return (
    <div>
      <p className="flex flex-wrap items-center gap-x-1.5 text-xs text-muted-foreground">
        <Shuffle className="size-3 shrink-0" />
        Ce n'est pas ce que tu veux réviser ?
        <button
          type="button"
          onClick={onAutreChose}
          disabled={remplacementEnCours || verrouillee}
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
 *
 * Sans marge ni bordure propres : rendu par SeanceCorps dans le même bloc de réglages
 * que SortieDeSecours, qui porte la bordure haute partagée par les deux.
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
      <p className="flex flex-wrap items-center gap-x-1.5 text-xs text-muted-foreground">
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
      <p className="flex flex-wrap items-center gap-x-1.5 text-xs text-muted-foreground">
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
    <div>
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
 * Meuble l'espace à droite du titre et du bouton, sur grand écran, laissé vide par la
 * disparition de la grille à deux colonnes (voir SeanceAFaire) : contrairement au
 * bandeau du coach (voir TeteAccueil.IllustrationAujourdhui, qui ne comble qu'un
 * manque de donnée au tout premier passage), rien ici ne dépend de l'historique de
 * l'élève - ce bloc reste étroit tous les jours, pour tout le monde, dès que l'écran
 * est large.
 *
 * Un livre qui ouvre sur une courbe montante, plutôt qu'une icône de bibliothèque
 * agrandie : la première version (un BookOpen générique) se lisait comme un
 * bouche-trou, pas comme quelque chose de dessiné pour cette page. La deuxième
 * version (deux arcs sans détail) allait trop loin dans l'autre sens : sans reliure
 * ni lignes de texte, la forme ne se lisait plus comme un livre du tout. Celle-ci a
 * les deux repères qui font reconnaître un livre d'un coup d'œil - la reliure
 * centrale et quelques lignes de texte sur chaque page - avant de laisser partir la
 * courbe, nettement séparée, vers l'étincelle dorée. La courbe fait le lien avec ce
 * que la séance montre déjà (une fréquence, un tableau de variation en maths) - deux
 * points marquent sa progression, l'étincelle reprend le même or que la pastille de
 * fréquence et les jalons de la semaine.
 *
 * Purement décorative (`aria-hidden`), donc jamais tenue d'égaler la hauteur du texte
 * voisin, qui varie d'une séance à l'autre (0 à 4 raisons) - la recréer avec un
 * second bloc de CONTENU aurait juste redonné deux colonnes à comparer. Masquée en
 * dessous de `lg` : sur téléphone et tablette, l'espace manque déjà pour garder
 * "Commencer" au-dessus du pli, la décoration cède toujours la place à l'action.
 */
function IllustrationSeance() {
  return (
    <div
      aria-hidden="true"
      className="relative mt-8 hidden shrink-0 items-center justify-center overflow-hidden lg:mt-0 lg:flex lg:size-48 xl:size-56"
    >
      <div className="absolute -right-4 -top-4 size-24 rounded-full bg-gold/20 blur-2xl xl:size-28" />
      <div className="absolute -bottom-6 -left-2 size-24 rounded-full bg-primary/10 blur-2xl xl:size-28" />
      <svg viewBox="0 0 200 200" fill="none" className="relative size-32 xl:size-40">
        {/* Le livre : page gauche et page droite, réunies par une reliure centrale -
            sans elle, deux arcs isolés ne se lisent plus comme un livre du tout. */}
        <path
          d="M20 138C20 106 46 94 82 100L82 152C46 146 20 170 20 138Z
             M160 138C160 106 134 94 98 100L98 152C134 146 160 170 160 138Z
             M90 97L90 151"
          className="stroke-primary/45"
          strokeWidth="4"
          strokeLinejoin="round"
        />
        {/* Les lignes de texte sur chaque page - le détail qui achève de dire "livre"
            plutôt que "forme arrondie". Plus fines que le contour, en retrait. */}
        <path
          d="M32 118L58 114M32 128L62 124M32 138L60 135
             M148 118L122 114M148 128L118 124M148 138L120 135"
          className="stroke-primary/30"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        {/* La courbe : ce que la séance promet - une progression qui se lit de gauche
            à droite, comme un tableau de variation ou une fréquence qui monte.
            Nettement séparée du livre (part au-dessus de la reliure, jamais collée à
            elle) pour ne jamais se confondre avec son contour. */}
        <path
          d="M100 82C112 68 122 78 130 55C138 32 152 36 162 14"
          className="stroke-primary/35"
          strokeWidth="4"
          strokeLinecap="round"
        />
        <circle cx="130" cy="55" r="4" className="fill-primary/45" />
        <circle cx="162" cy="14" r="4" className="fill-primary/45" />
        {/* L'étincelle dorée, au bout du trait - le même or que la pastille de
            fréquence et les jalons de la semaine (voir PastilleFrequence, jalons.ts). */}
        <path d="M180 4V20M171 12H189" className="stroke-gold" strokeWidth="3.5" strokeLinecap="round" />
      </svg>
    </div>
  )
}

/**
 * La fréquence à l'examen, en pastille : "35 sur 41 épreuves", au même rang que les
 * pastilles matière/durée/étapes plutôt que dans sa propre carte.
 *
 * Tout le produit repose sur la crédibilité de sa recommandation : un élève qui ne
 * comprend pas pourquoi on lui propose ce thème n'a aucune raison de nous croire
 * plutôt que de retourner choisir lui-même. Le chiffre reste donc affiché en
 * permanence, jamais replié derrière un "voir pourquoi" - cacher l'argument, c'est le
 * perdre. Ce qui a changé, c'est sa PRÉSENTATION : une carte à part avec sa propre
 * jauge de progression pesait, seule, plus que le reste de la carte réuni, et sa
 * hauteur variait trop (0 à 6 années citées juste en dessous) pour ne jamais
 * déséquilibrer un voisin. Une pastille a une hauteur fixe, quel que soit le chiffre.
 */
function PastilleFrequence({ frequence }: { frequence: NonNullable<Seance["frequence"]> }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-gold/15 px-3 py-1 text-xs font-medium text-gold-foreground dark:text-gold-text">
      <Target className="size-3.5 shrink-0" />
      {frequence.occurrences} sur {frequence.epreuves_total} épreuves
    </span>
  )
}

/** Les raisons autres que la fréquence - coefficient, ratage précédent, thème jamais
 * travaillé. Chacune est un fait déjà en base (voir raisons_de_la_seance), affichée
 * juste avant le bouton : le fait qui justifie l'action précède l'action, comme dans
 * un argumentaire dit à voix haute. */
function RaisonsSeance({ seance }: { seance: Seance }) {
  if (seance.raisons.length === 0) return null
  return (
    <ul className="mt-3 flex flex-col gap-1">
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

function IconeEtape({ type, ouverte }: { type: EtapeSeance["type"] | EtapeSeanceVerrouillee["type"]; ouverte: boolean }) {
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
  seance, onChoisir, enCours, desactive = false,
}: {
  seance: Seance
  onChoisir: (minutes: number) => void
  enCours: boolean
  // Verrouillée, la séance montre ce sélecteur mais ne le laisse pas agir - changer de
  // budget de temps ne sert à rien tant qu'on ne peut rien ouvrir.
  desactive?: boolean
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
            disabled={enCours || desactive}
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
 * Les étapes groupées par phase : Comprendre, S'entraîner, Vérifier - en bandeau
 * horizontal, une carte par phase, plutôt qu'une frise verticale unique.
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
 *
 * Horizontal plutôt que vertical : la mise en page à deux colonnes précédente
 * enfermait ce parcours dans une colonne étroite dont la hauteur était comparée à sa
 * voisine, avec un fil vertical qui ne cousait que trois étapes au maximum. En
 * bandeau, chaque phase devient sa propre carte, le nombre de colonnes suit le
 * nombre de phases réellement présentes (jamais de case vide), et la largeur libérée
 * par la disparition de la grille sert enfin à quelque chose.
 */
const PHASES = [
  { cle: "cours", titre: "Comprendre" },
  { cle: "exercice", titre: "S'entraîner" },
  { cle: "quiz", titre: "Vérifier" },
] as const

function EtapesParPhase({
  seance, country, plan, onOuvrirEtape, verrouillee,
}: {
  seance: Seance
  country: string
  plan: PlanDuJour
  onOuvrirEtape: (etape: EtapeSeance) => void
  // Le parcours entier s'affiche verrouillé ou non (voir SeanceAFaire) - lui seul
  // décide si ses lignes ouvrent vraiment quelque chose ou n'en montrent que la forme.
  verrouillee: boolean
}) {
  // La page des exercices d'un thème exige la matière ET le cursus (voir
  // ThemeExercicesView) : sans eux le lien mène à une erreur 400, donc on ne l'affiche
  // pas plutôt que de proposer une impasse. Absente aussi verrouillée : c'est déjà du
  // contenu gated, pas seulement une profondeur supplémentaire de la séance du jour.
  const lienExercices =
    !verrouillee && seance.theme && seance.subject && plan.cursus
      ? `${themeExercicesPath(country, seance.theme.id)}?subject=${seance.subject.code}&cursus=${plan.cursus.id}`
      : null
  const groupes = PHASES
    .map((phase) => ({ ...phase, etapes: seance.etapes.filter((e) => e.type === phase.cle) }))
    .filter((phase) => phase.etapes.length > 0)
  const avecTitres = groupes.length > 1

  return (
    <div className="mt-6 rounded-2xl border border-border/70 bg-background/70 p-4 backdrop-blur-sm sm:p-5">
      <p className="flex items-baseline justify-between gap-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
        Ton parcours
        <span className="font-sans normal-case tracking-normal tabular-nums">{seance.duree_estimee_min} min</span>
      </p>
      {/* Une colonne par phase réellement présente (une à trois), empilées sur
          téléphone : le nombre de classes possibles est fini (1 à 3 phases), autant
          les nommer plutôt que calculer une valeur arbitraire côté style. */}
      <ol
        className={cn(
          "mt-4 grid grid-cols-1 gap-3",
          groupes.length === 2 && "sm:grid-cols-2",
          groupes.length >= 3 && "sm:grid-cols-3",
        )}
      >
        {groupes.map((phase, index) => (
          <li key={phase.cle} className="rounded-xl border border-border/60 bg-background/60 p-3">
            {avecTitres && (
              <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-foreground/80">
                <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-primary text-[0.65rem] font-semibold text-primary-foreground shadow-sm shadow-primary/30">
                  {index + 1}
                </span>
                {phase.titre}
                {phase.cle === "quiz" && (
                  <span className="font-medium normal-case tracking-normal text-primary">· valide</span>
                )}
              </p>
            )}
            <div className={cn("flex flex-col gap-1", avecTitres && "mt-2")}>
              {verrouillee
                ? (phase.etapes as EtapeSeanceVerrouillee[]).map((etape, index) => (
                    <div
                      key={`${etape.type}-${index}`}
                      className="flex items-center gap-2.5 rounded-lg px-1.5 py-1 text-sm opacity-60"
                    >
                      <IconeEtape type={etape.type} ouverte={false} />
                      <span className="line-clamp-2 min-w-0 flex-1 font-medium leading-snug">{etape.libelle}</span>
                      <Lock className="hidden size-3.5 shrink-0 text-muted-foreground sm:block" aria-hidden="true" />
                    </div>
                  ))
                : (phase.etapes as EtapeSeance[]).map((etape) => (
                    <Link
                      key={etape.cle}
                      to={lienEtape(etape, country, plan)}
                      onClick={() => onOuvrirEtape(etape)}
                      className="group flex items-center gap-2.5 rounded-lg border border-transparent px-1.5 py-1 text-sm transition-all hover:border-primary/20 hover:bg-primary/[0.04]"
                    >
                      <IconeEtape type={etape.type} ouverte={etape.ouverte} />
                      <span className="line-clamp-2 min-w-0 flex-1 font-medium leading-snug">{etape.libelle}</span>
                      <span className="shrink-0 text-xs tabular-nums text-muted-foreground">{etape.duree_min} min</span>
                    </Link>
                  ))}
              {/* La profondeur, à un clic, sans jamais déverser 33 liens dans la carte :
                  la promesse de la séance est "une seule chose à faire", et un élève qui
                  voit 33 items n'en fait généralement aucun. Même patron que
                  "Propose-moi autre chose" - accessible, jamais promu. */}
              {phase.cle === "exercice" && seance.exercices_total > phase.etapes.length && lienExercices && (
                <Link
                  to={lienExercices}
                  className="flex items-center gap-1.5 px-1.5 pt-0.5 text-xs text-muted-foreground underline underline-offset-4 transition-colors hover:text-primary"
                >
                  Les {seance.exercices_total} exercices sur ce thème
                  <ArrowRight className="size-3" />
                </Link>
              )}
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}
