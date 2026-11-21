import { useEffect, useId, useRef, useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { usePublierContextePage } from "@/lib/guides/contextePage"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ArrowRight, BookOpen, CalendarClock, Check, ChevronDown, Clock, Lock, PenLine, RotateCcw,
  Shuffle, SlidersHorizontal, Sparkles, Target, Zap, type LucideIcon,
} from "lucide-react"

import {
  ajusterDureeSeance, continuerSeanceDuJour, definirObjectifMatiere, getAccueil, listMySubscriptions,
  proposerAutreChose, retirerObjectifMatiere, terminerSeanceDuJour,
} from "@/api/endpoints"
import type { EtapeSeance, EtapeSeanceVerrouillee, PlanDuJour, Seance } from "@/api/types"
import { BoutonParents } from "@/components/BoutonParents"
import { JalonsAtteints } from "@/components/JalonsAtteints"
import { Button } from "@/components/ui/button"
import { themeExercicesPath, themesFrequentsPath } from "@/lib/countryPath"
import { lienEtape, ouvrirEtapeDeSeance, seanceAffichable } from "@/lib/seance"
import { delaiDepuisAffichageAccueil } from "@/lib/accueilChrono"
import { trackEvent } from "@/lib/analytics"
import { FRAICHEUR_ACCUEIL_MS, lireQuizIgnores, useCleQuizEnCours, useQuizEnCours } from "@/lib/quizEnCours"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { PRIX_MOIS_FCFA } from "@/lib/tarifs"
import { cn, formatAmount } from "@/lib/utils"
import { langueCourante, localeCourante, t, tn, useI18n, type CleI18n } from "@/lib/i18n"
import { LienAide } from "@/components/aide/LienAide"
import { AideContextuelle, BoutonAide } from "@/components/guides/AideContextuelle"

/**
 * Séance verrouillée parce que l'abonnement est échu (et non parce qu'on n'a jamais acheté) : l'abonnement le plus
 * récemment terminé, ou null (jamais abonné, abonnement en cours, liste pas encore arrivée). `actif` : la liste n'est
 * demandée que devant une séance verrouillée.
 */
function useAccesEchu(actif: boolean) {
  const { data: abonnements } = useQuery({ queryKey: ["mes-abonnements"], queryFn: listMySubscriptions, enabled: actif })
  if (!actif || !abonnements || abonnements.some((a) => a.is_active)) return null
  return [...abonnements].sort((a, b) => b.expires_at.localeCompare(a.expires_at))[0] ?? null
}

/**
 * L'ancien abonné voyait « Débloquer ma séance » comme un nouvel arrivant et ne savait pas que son accès avait pris
 * fin : on le dit en clair, avec la date. Le message seul : le bouton qui réabonne est le bouton principal de la
 * carte, juste dessous (voir SeanceAFaire). Ce bandeau portait son propre « Se réabonner », en contour, au-dessus
 * d'un « Débloquer ma séance » plein qui menait à la page générique des prix : deux boutons pour la même chose, le
 * moins direct étant le plus visible (audit des accueils, 2026-11-21).
 */
function BandeauAccesTermine({ expiresAt }: { expiresAt: string }) {
  const date = new Date(expiresAt).toLocaleDateString(localeCourante(), {
    day: "numeric", month: "long", year: "numeric",
  })
  return (
    <p role="status" className="mt-5 rounded-lg border border-warning/40 bg-warning/10 p-3.5 text-sm font-medium">
      {t("seance.acces_termine", { date })}
    </p>
  )
}

/**
 * La séance complète du jour, FERMÉE, en version courte : le second étage de l'accueil d'un élève connecté sans
 * abonnement (voir AccueilDecouverte), sous la séance gratuite qu'il peut faire.
 *
 * Avant, cette séance verrouillée était la première chose de sa page, en grand, et ce qu'il pouvait faire gratuitement
 * se trouvait deux écrans plus bas, sous un autre thème (audit des accueils, 2026-11-21). Ici elle dit seulement ce que
 * l'abonnement ajoute, avec les faits qui la rendent crédible (le thème, sa fréquence à l'examen, les trois temps de
 * la séance), le prix, et un seul bouton. Pour un ancien abonné : la date de fin, ce qui l'attend, et le réabonnement
 * du bon profil.
 */
export function SeanceCompleteVerrouillee({ plan }: { plan: PlanDuJour }) {
  useI18n()
  const seance = plan.seance as Seance
  const accesEchu = useAccesEchu(true)
  const libelleDeblocage = accesEchu ? t("seance.reabonner") : t("seance.debloquer")
  const lienDeblocage = accesEchu ? `/abonnement?cursus=${accesEchu.cursus.id}&profil=${accesEchu.profil.id}` : "/tarifs"
  const phases = PHASES.filter((phase) => seance.etapes.some((e) => e.type === phase.cle))

  // Ce que la carte montre, publié pour le tutoriel de ce public (voir lib/guides/textes.ts).
  usePublierContextePage("seance", {
    bouton: libelleDeblocage,
    phases: phases.map((phase) => t(phase.titre)),
    quiz: phases.some((phase) => phase.cle === "quiz"),
    quizExpress: false,
    verrouillee: true,
  })

  return (
    <div>
      <h2 className="font-display">
        <span className="flex flex-wrap items-center gap-x-2 gap-y-0.5 font-sans text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          <Lock className="size-3.5" aria-hidden="true" />
          {t("decouverte.complete")}
          <span className="font-medium normal-case tracking-normal">{t("decouverte.complete_abonnement")}</span>
        </span>
        <span className="mt-1.5 block text-xl font-semibold leading-tight tracking-tight sm:text-2xl">
          {majuscule(titreDeLaSeance(seance))}
        </span>
      </h2>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {seance.subject && <PastilleMatiere code={seance.subject.code} label={seance.subject.label} />}
        <Pastille icone={Clock}>{seance.duree_estimee_min} min</Pastille>
        {seance.frequence && <PastilleFrequence frequence={seance.frequence} onBascule={() => {}} />}
      </div>
      {/* Les trois temps de la séance, sur une ligne : ce que l'abonnement ouvre, sans le parcours détaillé. */}
      {phases.length > 0 && (
        <ol data-guide="seance-parcours" className="mt-3 flex flex-wrap items-center gap-x-1.5 gap-y-1 text-sm text-muted-foreground">
          {phases.map((phase, i) => (
            <li key={phase.cle} className="flex items-center gap-1.5">
              {i > 0 && <ArrowRight className="size-3.5 text-muted-foreground/60" aria-hidden="true" />}
              <span className="font-medium text-foreground">{t(phase.titre)}</span>
            </li>
          ))}
        </ol>
      )}
      <RaisonsSeance seance={seance} sansRaisonsDites={false} />

      {accesEchu && <BandeauAccesTermine expiresAt={accesEchu.expires_at} />}
      {accesEchu && <CeQuiAttend />}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <Button asChild size="lg" className="h-12 rounded-full px-7 text-base">
          <Link data-guide="seance-debloquer" to={lienDeblocage} onClick={() => trackEvent("plan_verrouille_clic")}>
            <Lock className="size-4" />
            {libelleDeblocage}
          </Link>
        </Button>
        <p className="basis-full text-sm text-muted-foreground">
          {t("seance.prix_abonnement", { prix: formatAmount(PRIX_MOIS_FCFA) })}
        </p>
        <BoutonParents contenu={t("parents.contenu_seance")} className="h-11 rounded-full px-5" />
        <LienAide slug="seance-verrouillee">{t("aide.lien.verrouille")}</LienAide>
      </div>
    </div>
  )
}

/**
 * Ce qu'un ancien abonné a construit et retrouve en se réabonnant : ses thèmes en révision, ses thèmes maîtrisés, ses
 * erreurs à refaire. Des faits à lui, jamais un reproche, et rien quand il n'y a rien à dire. Les chiffres sont ceux
 * de l'accueil d'un abonné (voir quiz.accueil), demandés seulement ici.
 */
function CeQuiAttend() {
  const { data } = useQuery({
    queryKey: ["accueil-ancien-abonne"],
    queryFn: ({ signal }) => getAccueil(signal),
    staleTime: 5 * 60_000,
  })
  if (!data) return null
  const somme = (cle: "en_revision" | "maitrises") => data.resume.reduce((total, matiere) => total + matiere[cle], 0)
  const enRevision = somme("en_revision")
  const maitrises = somme("maitrises")
  const erreurs = data.erreurs_total ?? 0
  const elements = [
    enRevision > 0 ? tn("decouverte.attend_revision", enRevision) : null,
    maitrises > 0 ? tn("decouverte.attend_maitrises", maitrises) : null,
    erreurs > 0 ? tn("decouverte.attend_erreurs", erreurs) : null,
  ].filter((element): element is string => element !== null)
  if (elements.length === 0) return null
  return (
    <p className="mt-3 flex items-start gap-2 text-sm">
      <RotateCcw className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
      <span>{t("decouverte.attend", { liste: enumerer(elements) })}</span>
    </p>
  )
}

/** « a », « a et b », « a, b et c » dans la langue de l'interface. */
function enumerer(elements: string[]): string {
  return new Intl.ListFormat(langueCourante(), { style: "long", type: "conjunction" }).format(elements)
}

/**
 * Le corps de la séance - à faire ou faite, avec ses actions - sans la carte qui
 * l'entoure. Rendu par l'accueil d'un abonné (TeteAccueil, où il vit sous le bandeau du
 * coach). Il vivait aussi dans la vitrine, pour un élève connecté sans abonnement, qui a
 * maintenant sa propre carte (voir SeanceCompleteVerrouillee, ci-dessus). La séance peut
 * encore y être verrouillée : un compte abonné à un examen qui en regarde un autre.
 *
 * `secondaire` : une action de second rang à côté de "Commencer" (l'annale en
 * conditions d'examen, à un mois du jour J - voir TeteAccueil).
 *
 * `phraseDuCoach` : la phrase du coach est affichée juste au-dessus (accueil d'un
 * abonné). Elle dit déjà le ratage ou la lecture en cours (voir quiz.accueil.phrase_coach) :
 * la liste de raisons ne les répète pas. La vitrine n'a pas cette phrase, elle les garde.
 *
 * `apresDuree` : un bloc posé sous le choix de durée, avant le parcours - l'objectif d'XP et la
 * semaine de l'accueil, qui poussaient le bouton principal sous le pli quand ils le précédaient.
 */
export function SeanceCorps({
  plan, country, secondaire, phraseDuCoach, apresDuree,
}: {
  plan: PlanDuJour
  country: string
  secondaire?: ReactNode
  phraseDuCoach?: string
  apresDuree?: ReactNode
}) {
  useI18n()
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
  // Pas verrouillée : le bouton était grisé sans un mot (test élève 2026-11-07, compte libre). Ce qu'on ne peut
  // pas faire ne se montre pas ; ce que l'abonnement ouvre se dit une fois, près du bouton « Débloquer ».
  const afficherSecours = data.etat === "plan_pret" && !data.seance?.verrouillee
  // Séance à faire et ouverte : la durée, « autre chose » et la matière de la semaine se replient sous un seul
  // lien (voir ReglagesSeance). La matière de la semaine, une fois choisie, reste dehors : elle explique pourquoi
  // la séance porte sur cette matière. Séance verrouillée ou déjà faite : rien ne change.
  const replier = afficherSecours
  const objectifChoisi = Boolean(data.objectif_matiere)
  const secours = afficherSecours && (
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
  )
  const controleObjectif = afficherObjectif && (
    <ObjectifMatiereControle
      plan={data}
      enCours={objectif.isPending}
      onChoisir={(subject) => {
        trackEvent("objectif_matiere", { action: subject === null ? "retire" : "definit" })
        objectif.mutate(subject)
      }}
    />
  )

  return (
    <>
      {data.etat === "deja_fait_aujourdhui" ? (
        <SeanceFaite
          plan={data}
          country={country}
          onContinuer={() => continuer.mutate()}
          continuationEnCours={continuer.isPending}
          phraseDuCoach={phraseDuCoach}
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
          phraseDuCoach={phraseDuCoach}
          apresDuree={apresDuree}
          dureeDansLesReglages={replier}
        />
      )}
      {/* Une séance close ICI (« J'ai fini », sans quiz final) peut ouvrir un jalon de régularité : fêté tout de suite, comme
          sur le résultat d'un quiz. Seulement après ce geste : l'accueil ne relit pas « Mes réussites » à chaque ouverture. */}
      {terminer.isSuccess && <JalonsAtteints className="mt-3" />}
      {replier ? (
        <>
          {objectifChoisi && controleObjectif && (
            <div className="mt-4 border-t border-border/60 pt-3">{controleObjectif}</div>
          )}
          <ReglagesSeance sansFilet={objectifChoisi && Boolean(controleObjectif)}>
            {data.seance && (
              <ChoixDuree
                seance={data.seance as Seance}
                onChoisir={(minutes) => duree.mutate(minutes)}
                enCours={duree.isPending}
              />
            )}
            {secours}
            {!objectifChoisi && controleObjectif}
            <BoutonAide guide="seance-du-jour" className="-ml-2.5 self-start" />
          </ReglagesSeance>
        </>
      ) : (
        (afficherSecours || afficherObjectif) && (
          <div className="mt-4 flex flex-col gap-3 border-t border-border/60 pt-3">
            {secours}
            {controleObjectif}
          </div>
        )
      )}
    </>
  )
}

/**
 * « Régler ma séance » : la durée, « propose-moi autre chose » et la matière de la semaine, repliés sous un seul lien
 * en bas de la carte.
 *
 * Ces trois réglages occupaient environ 210 px en permanence sous le bouton, dans une carte qui mesurait 1 057 px sur
 * un téléphone (audit de l'accueil abonné, 2026-11-16 : douze commandes dans la carte). Ils servent à qui veut
 * changer quelque chose, pas à chaque ouverture : le bouton principal, le quiz express, la fréquence et la ligne du
 * jour restent seuls visibles. Fermé au départ, et il reste ouvert tant que l'élève ne le referme pas (changer de
 * durée ou de thème ne le replie pas).
 */
function ReglagesSeance({ children, sansFilet = false }: { children: ReactNode; sansFilet?: boolean }) {
  const [ouvert, setOuvert] = useState(false)
  const id = useId()
  return (
    <div className={cn("mt-4", !sansFilet && "border-t border-border/60 pt-1")}>
      <button
        type="button"
        aria-expanded={ouvert}
        aria-controls={id}
        onClick={() => setOuvert((o) => !o)}
        className="flex min-h-11 w-full flex-wrap items-center gap-x-2 gap-y-0.5 py-1.5 text-left text-sm font-medium transition-colors hover:text-primary"
      >
        <SlidersHorizontal className="size-4 shrink-0 text-primary" aria-hidden="true" />
        {t("seance.regler")}
        <span className="text-xs font-normal text-muted-foreground">{t("seance.regler_detail")}</span>
        <ChevronDown
          className={cn("ml-auto size-4 shrink-0 text-muted-foreground transition-transform", ouvert && "rotate-180")}
          aria-hidden="true"
        />
      </button>
      {ouvert && (
        // Le choix de durée porte sa propre marge haute (mt-5), pensée pour sa place d'avant, sous le bouton.
        <div id={id} className="flex flex-col gap-3 pb-1 [&>*:first-child]:mt-1">
          {children}
        </div>
      )}
    </div>
  )
}

/** Ce que fait l'étape, au verbe : le bouton principal dit où il mène plutôt que « la séance ». */
function actionDeLEtape(etape: EtapeSeance): string {
  if (etape.type === "cours") return t("seance.action_cours")
  if (etape.type === "exercice") return t("seance.action_exercice")
  return t("seance.action_quiz")
}

/** XP maximale d'un quiz : chaque question rapporte au mieux XP_QCM_JUSTE (voir quiz.xp). Un
 * plafond, jamais une promesse - les questions ouvertes rapportent moins. */
const XP_MAX_PAR_QUESTION = 10

function SeanceAFaire({
  plan, country, onOuvrirEtape, onTerminer, terminaisonEnCours, onChoisirDuree, ajustementEnCours, secondaire,
  phraseDuCoach, apresDuree, dureeDansLesReglages = false,
}: {
  plan: PlanDuJour
  country: string
  onOuvrirEtape: (etape: EtapeSeance) => void
  onTerminer: () => void
  terminaisonEnCours: boolean
  onChoisirDuree: (minutes: number) => void
  ajustementEnCours: boolean
  secondaire?: ReactNode
  phraseDuCoach?: string
  apresDuree?: ReactNode
  /** Le choix de durée est rendu plus bas, replié avec les autres réglages (voir ReglagesSeance). */
  dureeDansLesReglages?: boolean
}) {
  const seance = plan.seance as Seance
  // Les années derrière la pastille de fréquence : la preuve est un clic, pas une ligne
  // de plus en permanence (voir PastilleFrequence).
  const [anneesOuvertes, setAnneesOuvertes] = useState(false)
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
  // Le quiz est aussi une porte d'ENTRÉE, pas seulement la dernière marche : c'est lui qui
  // rapporte l'XP, fait avancer la série et valide la séance. Tant qu'il n'est pas ouvert et que
  // le bouton principal mène ailleurs (cours, exercice), on le propose en direct.
  const etapeQuiz = etapes.find((e) => e.type === "quiz")
  const quizExpress = etapeQuiz && !etapeQuiz.ouverte && prochaine && prochaine.type !== "quiz" ? etapeQuiz : null

  // Un quiz déjà commencé : « Reprendre : faire le quiz » doit le rouvrir à la question où l'élève s'est arrêté,
  // pas lancer une nouvelle série à la question 1 (passe Guyguy 2026-11-07 : la vraie reprise était une carte plus
  // bas, retrouvée en 25 à 30 s). Même liste que la carte « en cours » (le serveur la tient à jour), mêmes quiz
  // écartés par l'élève ; ni test de niveau, ni rejeu, ni chrono écoulé, et seulement dans l'examen de la séance.
  const cleQuizEnCours = useCleQuizEnCours()
  const { data: quizEnCours } = useQuizEnCours({ fraicheurMs: FRAICHEUR_ACCUEIL_MS })
  const ignores = cleQuizEnCours ? lireQuizIgnores(cleQuizEnCours) : []
  const quizAReprendre = quizEnCours?.find(
    (s) => !ignores.includes(s.id) && s.mode !== "DIAGNOSTIC" && s.rejeu_de === null && !s.chrono_ecoule
      && s.cursus === plan.cursus?.id
      // Le quiz de CETTE séance : même thème, sinon « Quiz express » rouvrait un quiz en cours d'une autre
      // matière ou d'un autre thème (signalé 2026-11-15 : Effet photoélectrique renvoyait ailleurs).
      && (!seance.theme || s.theme_id === seance.theme.id),
  )
  const lienDeLEtape = (etape: EtapeSeance) =>
    etape.type === "quiz" && quizAReprendre ? `/quiz/session/${quizAReprendre.id}` : lienEtape(etape, country, plan)

  // Séance verrouillée : un seul bouton plein. Pour un ancien abonné il réabonne le bon profil au bon examen, d'un
  // toucher ; pour qui n'a jamais payé il mène aux prix.
  const accesEchu = useAccesEchu(seance.verrouillee)
  const libelleDeblocage = accesEchu ? t("seance.reabonner") : t("seance.debloquer")
  const lienDeblocage = accesEchu ? `/abonnement?cursus=${accesEchu.cursus.id}&profil=${accesEchu.profil.id}` : "/tarifs"

  // Ce que cette séance montre vraiment, publié pour les guides (bienvenue, aide de la séance) : le libellé
  // du bouton, les étapes dans leur ordre, le quiz express. Une aide qui décrit une séance à trois étapes
  // devant une séance à deux ne correspond à rien de visible.
  usePublierContextePage("seance", {
    bouton: seance.verrouillee
      ? libelleDeblocage
      : prochaine
        ? t("seance.bouton_etape", { verbe: dejaCommencee ? t("seance.reprendre") : t("seance.commencer"), action: actionDeLEtape(prochaine) })
        : undefined,
    phases: PHASES.filter((phase) => seance.etapes.some((e) => e.type === phase.cle)).map((phase) => t(phase.titre)),
    quiz: avecQuiz,
    quizExpress: Boolean(quizExpress),
    verrouillee: seance.verrouillee,
  })

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
      {/* Le titre, les pastilles, les raisons, les boutons et la durée. L'illustration
          décorative qui occupait la colonne de droite a été retirée : elle ne portait aucune
          information, et la place sert mieux le bouton principal et le quiz express. */}
      <div className="lg:flex lg:items-start lg:gap-8">
      <div className="min-w-0 lg:flex-1">
        {/* "Aujourd'hui" en surtitre et le thème en grand : le thème est ce que l'élève
            doit retenir d'un coup d'œil, le jour n'est que le cadre. Un seul <h2> pour
            que les lecteurs d'écran lisent toujours "Aujourd'hui, concentration
            molaire" d'une traite. */}
        <h2 className="font-display">
          <span className="flex items-center gap-2 font-sans text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            <Sparkles className="size-3.5" />
            {t("seance.aujourdhui")}
          </span>
          <span className="mt-2 block text-3xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-4xl">
            {majuscule(titreDeLaSeance(seance))}
          </span>
        </h2>
        {/* Le mot du coach, juste sous le thème qu'il commente : « Ce thème tombe presque à
            chaque examen » ne désigne rien tant que le titre n'est pas à côté. */}
        {phraseDuCoach && (
          // max-w-4xl et non max-w-prose (65 caractères), et 16 px partout : la phrase de
          // fréquence fait environ 80 caractères, 650 à 716 px à 16 px (732 à 806 px à 18 px,
          // mesurés) ; elle se coupait en deux après les deux-points alors que la carte avait
          // la place. text-balance reste : si la variante la plus longue doit passer à la
          // ligne, les deux lignes sont équilibrées au lieu de laisser un mot seul.
          // Une bande teintée (paire accent / accent-foreground du thème, définie en clair et en
          // sombre) avec une barre d'appui : le mot du coach se détache de la carte au lieu de se
          // fondre dans le texte gris, et le contraste reste fort (vert foncé sur menthe).
          <p className="mt-3 max-w-4xl rounded-lg border-l-4 border-primary bg-accent px-3 py-2.5 text-base leading-snug font-medium text-balance text-accent-foreground">{phraseDuCoach}</p>
        )}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {seance.subject && <PastilleMatiere code={seance.subject.code} label={seance.subject.label} />}
          <Pastille icone={Clock}>{seance.duree_estimee_min} min</Pastille>
          {/* La fréquence à l'examen, l'argument le plus fort, au même rang que les
              pastilles matière/durée plutôt que dans sa propre carte : le chiffre reste
              visible en permanence, jamais replié. Seules les années, qui le détaillent,
              s'ouvrent au clic (voir PastilleFrequence). */}
          {frequence && (
            <PastilleFrequence
              frequence={frequence}
              ouvert={aDesAnnees ? anneesOuvertes : undefined}
              onBascule={() => setAnneesOuvertes((ouvert) => !ouvert)}
            />
          )}
          {/* Pas pour la séance verrouillée : ses étapes ne s'ouvrent pas, l'aide parlerait d'un bouton absent. Ni ici
              quand les réglages sont repliés sous la carte (voir SeanceCorps) : « Revoir cette aide » y est rangé avec eux.
              À cette place il prenait une ligne de 44 px entre les pastilles et « Commencer », à chaque ouverture, pour
              un élève qui a dix séances derrière lui (audit des accueils, 2026-11-21). */}
          {!seance.verrouillee && !dureeDansLesReglages && <BoutonAide guide="seance-du-jour" className="-ml-1" />}
        </div>
        {/* Les années concernées, sous les pastilles quand on les demande : sans elles, le
            chiffre de la pastille est à croire sur parole, mais elles n'ont pas à peser sur
            l'écran de qui lui fait confiance. Le "…" dit qu'il y en a d'autres plutôt que
            de laisser croire à une liste complète (voir ANNEES_FREQUENCE_MAX serveur). */}
        {aDesAnnees && anneesOuvertes && frequence && (
          <p className="mt-1.5 text-xs tabular-nums text-muted-foreground">
            {frequence.annees.join(" · ")}
            {frequence.occurrences > frequence.annees.length ? " …" : ""}
          </p>
        )}
        {/* Les autres raisons (coefficient, jamais travaillé, thème déjà raté). Séance verrouillée :
            elles restent AVANT le bouton, elles font partie de ce qui convainc de débloquer. Séance
            ouverte : elles passent SOUS les boutons (voir plus bas) - le mot du coach et la pastille
            de fréquence ont déjà dit pourquoi ce thème, et ces deux lignes de plus repoussaient
            « Commencer » sous le pli d'un petit téléphone (audit du 2026-11-13 : bouton à 662 px). */}
        {seance.verrouillee && <RaisonsSeance seance={seance} sansRaisonsDites={Boolean(phraseDuCoach)} />}

        {seance.verrouillee && accesEchu && <BandeauAccesTermine expiresAt={accesEchu.expires_at} />}

        {seance.verrouillee ? (
          <div className="mt-6 flex flex-wrap items-center gap-3">
            {/* Un seul bouton, celui qui agit. Il y avait au-dessus un « Commencer la
                séance » inerte, la forme du vrai bouton une fois abonné : placé en premier,
                il se lisait comme un bouton cassé et reléguait la seule action possible en
                deuxième position. Le parcours en dessous montre déjà ce que l'abonnement ouvre. */}
            <Button
              asChild
              size="lg"
              className="group h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/30"
            >
              <Link data-guide="seance-debloquer" to={lienDeblocage} onClick={() => trackEvent("plan_verrouille_clic")}>
                <Lock className="size-4" />
                {libelleDeblocage}
              </Link>
            </Button>
            {/* Le prix juste sous le bouton qui vend : il n'apparaissait qu'à 1 775 px du haut sur un téléphone, 2,2 écrans
                plus bas, dans le texte écrit pour le visiteur (audit des accueils, 2026-11-21). */}
            <p className="basis-full text-sm text-muted-foreground">
              {t("seance.prix_abonnement", { prix: formatAmount(PRIX_MOIS_FCFA) })}
            </p>
            {/* Ce sont les parents qui paient : de la séance verrouillée, l'élève leur envoie le prix et le moyen de payer. */}
            <BoutonParents contenu={t("parents.contenu_seance")} className="h-12 rounded-full px-5" />
            <LienAide slug="seance-verrouillee">{t("aide.lien.verrouille")}</LienAide>
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
                  data-guide="seance-commencer"
                  to={lienDeLEtape(prochaine)}
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
                  {t("seance.bouton_etape", {
                    verbe: dejaCommencee || (prochaine.type === "quiz" && quizAReprendre) ? t("seance.reprendre") : t("seance.commencer"),
                    action: actionDeLEtape(prochaine),
                  })}
                  <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
            )}
            {quizExpress && (
              <Button
                asChild
                size="lg"
                variant="outline"
                // `h-auto` + retour à la ligne : à 375 px, « Quiz express » et son détail
                // débordaient du bord de l'écran (le détail passe dessous plutôt que dehors).
                className="h-auto min-h-11 max-w-full flex-wrap justify-start gap-x-2 gap-y-0.5 whitespace-normal rounded-full border-gold/50 bg-gold/10 px-5 py-2 text-left text-sm text-gold-foreground hover:bg-gold/20 dark:text-gold-text"
              >
                <Link
                  to={lienDeLEtape(quizExpress)}
                  onClick={() => {
                    if (!dejaCommencee) {
                      trackEvent("plan_seance_demarree", {
                        origine: seance.origine, delai_s: delaiDepuisAffichageAccueil(), entree: "quiz_express",
                      })
                    }
                    onOuvrirEtape(quizExpress)
                  }}
                >
                  <Zap className="size-4" aria-hidden="true" />
                  {t("seance.quiz_express")}
                  <span className="text-xs font-normal">
                    {t("seance.quiz_express_detail", { n: quizExpress.n, points: quizExpress.n * XP_MAX_PAR_QUESTION })}
                  </span>
                </Link>
              </Button>
            )}
            {secondaire}
            {/* Marquer la séance faite : seulement pour une séance SANS quiz (un cours, un
                exercice : rien ne dit quand on a fini de lire). Avec un quiz, c'est lui qui
                valide - le bouton laissait déclarer « fini » sans avoir rien répondu, ce que
                la phrase juste dessous contredisait, et faussait le seul chiffre qui dira si
                ce plan marche. */}
            {!avecQuiz && (
              <Button
                variant="ghost"
                size="sm"
                className="rounded-full text-muted-foreground"
                onClick={onTerminer}
                disabled={terminaisonEnCours}
              >
                <Check className="size-4" />
                {t("seance.jai_fini")}
              </Button>
            )}
            {/* Ce qui valide la séance, dit une fois près de l'action : sans ça, un
                élève qui lit le cours se croit quitte et la séance reste "à faire". */}
            {avecQuiz && (
              <p className="basis-full text-xs text-muted-foreground">
                {t("seance.validee_par_quiz")}
              </p>
            )}
          </div>
        )}

        {/* Sous les boutons, pour la même raison que le réglage de durée : les raisons secondaires,
            puis l'aide « Comment marche ta séance ? ». Ouverte d'elle-même à la première visite,
            l'aide occupait à elle seule 250 px AVANT le bouton dont elle parle. */}
        {!seance.verrouillee && <RaisonsSeance seance={seance} sansRaisonsDites={Boolean(phraseDuCoach)} />}
        {!seance.verrouillee && <AideContextuelle guide="seance-du-jour" />}

        {/* Le réglage de durée vient APRÈS le bouton : sur téléphone, il repoussait
            "Commencer" sous le pli, et une page dont l'action principale n'est pas
            visible n'a pas d'action principale. */}
        {!dureeDansLesReglages && (
          <ChoixDuree
            seance={seance}
            onChoisir={onChoisirDuree}
            enCours={ajustementEnCours}
            desactive={seance.verrouillee}
          />
        )}
        {apresDuree && <div className="mt-5 [&>div]:mb-0">{apresDuree}</div>}
        </div>
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
        {t("seance.pas_ca")}
        <button
          type="button"
          onClick={onAutreChose}
          disabled={remplacementEnCours || verrouillee}
          // Zone de toucher agrandie sans déplacer le texte : le lien faisait 18 px de haut (audit du 2026-11-16).
          className="relative after:absolute after:inset-x-0 after:-inset-y-2.5 after:content-[''] underline underline-offset-4 transition-colors hover:text-primary disabled:opacity-60"
        >
          {remplacementEnCours ? t("seance.je_cherche") : t("seance.autre_chose")}
        </button>
      </p>
      {plusRienAProposer && (
        <p className="mt-1 text-xs text-muted-foreground">
          {t("seance.pas_mieux")}{" "}
          <Link to={themesFrequentsPath(country)} className="underline underline-offset-4 hover:text-primary">
            {t("seance.choisir_theme")}
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
          {t("seance.concentre_avant")} <strong className="font-semibold text-foreground">{choisi.label}</strong>{" "}
          {t("seance.concentre_apres", { date: formaterJourMois(choisi.jusqu_au) })}
        </span>
        <button
          type="button"
          onClick={() => onChoisir(null)}
          disabled={enCours}
          className="underline underline-offset-4 transition-colors hover:text-primary disabled:opacity-60"
        >
          {t("seance.retour_auto")}
        </button>
        <button
          type="button"
          onClick={() => setOuvert(true)}
          className="relative after:absolute after:inset-x-0 after:-inset-y-2.5 after:content-[''] underline underline-offset-4 transition-colors hover:text-primary"
        >
          {t("seance.changer")}
        </button>
      </p>
    )
  }

  if (!ouvert) {
    return (
      <p className="flex flex-wrap items-center gap-x-1.5 text-xs text-muted-foreground">
        <Target className="size-3 shrink-0" />
        {t("seance.devoir_bientot")}
        <button
          type="button"
          onClick={() => setOuvert(true)}
          className="relative after:absolute after:inset-x-0 after:-inset-y-2.5 after:content-[''] underline underline-offset-4 transition-colors hover:text-primary"
        >
          {t("seance.me_concentrer")}
        </button>
      </p>
    )
  }

  return (
    <div>
      <p className="text-xs text-muted-foreground">{t("seance.je_me_concentre")}</p>
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
          {t("seance.annuler")}
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
  return texte.charAt(0).toLocaleUpperCase(langueCourante()) + texte.slice(1)
}

/** « Demain : "Dérivation" revient en révision, avec 4 cartes. » - ou rien, quand aucune échéance ne tombe demain. */
export function phraseDeDemain(demain: PlanDuJour["demain"]): string | null {
  if (!demain) return null
  const premier = demain.themes[0]
  const cartes = demain.cartes > 0 ? tn("seance.demain_cartes", demain.cartes) : ""
  if (!premier) return cartes ? t("seance.demain_cartes_seules", { cartes }) : null
  const themes =
    demain.themes_total > 1
      ? t("seance.demain_themes", { n: demain.themes_total, theme: majuscule(premier.theme) })
      : t("seance.demain_theme", { theme: majuscule(premier.theme) })
  return cartes ? t("seance.demain_avec_cartes", { themes, cartes }) : `${themes}.`
}

function SeanceFaite({
  plan, country, onContinuer, continuationEnCours, plusRienAProposer, phraseDuCoach,
}: {
  plan: PlanDuJour
  country: string
  onContinuer: () => void
  continuationEnCours: boolean
  plusRienAProposer: boolean
  phraseDuCoach?: string
}) {
  useI18n()
  const seance = plan.seance as Seance
  return (
    <>
      <h2 className="flex items-center gap-3 font-display text-2xl font-semibold sm:text-3xl">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/25 ring-4 ring-primary/10">
          <Check className="size-5" strokeWidth={3} />
        </span>
        {t("seance.faite")}
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
          <> · {tn("seance.cette_semaine", plan.seances_cette_semaine)}</>
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
          {t("seance.repropose", { quand: formatEcheance(seance.prochaine_revision) })}
        </p>
      )}

      {/* Une raison précise de revenir demain : ce qui sera réellement dû (voir quiz.services.apercu_de_demain), jamais
          une promesse de séance. Rien quand rien n'est dû : « Prochaine séance demain » suffit. */}
      {(() => {
        const phrase = phraseDeDemain(plan.demain)
        return phrase ? (
          <p className="mt-3 flex items-start gap-2 rounded-xl bg-primary/5 px-3 py-2 text-sm">
            <CalendarClock className="mt-0.5 size-4 shrink-0 text-primary" aria-hidden="true" />
            <span>{phrase}</span>
          </p>
        ) : null
      })()}

      {/* "Continuer" enchaîne sur une VRAIE séance suivante, jamais sur la liste des
          thèmes : renvoyer au catalogue quelqu'un qui vient de faire ce qu'on lui a
          demandé, c'est lui rendre la charge de choisir au moment précis où il
          méritait qu'on continue à le guider. */}
      <div className="mt-5 flex flex-wrap items-center gap-3">
        {/* La phrase du coach, juste au-dessus, dit déjà « Demain, on continue » : la
            redire ici ferait trois fois la même chose avec le titre « Séance faite ». */}
        {!phraseDuCoach && <span className="text-sm text-muted-foreground">{t("seance.prochaine_demain")}</span>}
        <Button variant="outline" size="sm" className="rounded-full" onClick={onContinuer} disabled={continuationEnCours}>
          {continuationEnCours ? t("seance.je_cherche") : t("seance.continuer")}
          <ArrowRight className="size-4" />
        </Button>
      </div>
      {/* Il n'y avait plus rien à proposer - dit franchement plutôt que par un bouton
          qui ne fait rien. */}
      {plusRienAProposer && (
        <p className="mt-2 text-xs text-muted-foreground">
          {t("seance.tour_fait")}{" "}
          <Link to={themesFrequentsPath(country)} className="underline underline-offset-4 hover:text-primary">
            {t("seance.choisir_theme")}
          </Link>
        </p>
      )}
    </>
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
 *
 * Seul le détail (les années, qui rendent le chiffre vérifiable) est derrière un clic sur
 * la pastille : le chiffre, lui, reste toujours à l'écran.
 */
function PastilleFrequence({
  frequence, ouvert, onBascule,
}: {
  frequence: NonNullable<Seance["frequence"]>
  // Défini seulement quand il y a des années à montrer : la pastille devient alors le
  // bouton qui les ouvre. Sans années, elle reste un simple texte.
  ouvert?: boolean
  onBascule: () => void
}) {
  useI18n()
  const classes = "inline-flex items-center gap-1.5 rounded-full bg-gold/15 px-3 py-1 text-xs font-medium text-gold-foreground dark:text-gold-text"
  const contenu = (
    <>
      <Target className="size-3.5 shrink-0" />
      {tn("seance.frequence", frequence.occurrences, { total: frequence.epreuves_total })}
    </>
  )
  if (ouvert === undefined) return <span className={classes}>{contenu}</span>
  return (
    <button
      type="button"
      aria-expanded={ouvert}
      onClick={onBascule}
      className={cn(classes, "transition-colors hover:bg-gold/25")}
    >
      {contenu}
      <ChevronDown className={cn("size-3 shrink-0 transition-transform", ouvert && "rotate-180")} aria-hidden="true" />
    </button>
  )
}

/** Les codes que la phrase du coach énonce elle-même (voir quiz.accueil.phrase_coach). */
const RAISONS_DITES_PAR_LE_COACH = ["echec", "lecture", "calibrage"]

const RAISONS_MAX = 2
/** Du plus personnel au plus général (codes de quiz.services.raisons_de_la_seance). */
const ORDRE_RAISONS = ["objectif", "echec", "lecture", "calibrage", "jamais", "maitrise", "coefficient"]
const rangRaison = (code: string) => {
  const rang = ORDRE_RAISONS.indexOf(code)
  return rang === -1 ? ORDRE_RAISONS.length : rang
}

/** Les raisons autres que la fréquence - coefficient, ratage précédent, thème jamais
 * travaillé. Chacune est un fait déjà en base (voir raisons_de_la_seance). Avant le bouton
 * sur une séance verrouillée (l'argumentaire précède l'action), sous les boutons sinon :
 * voir SeanceCorps. */
function RaisonsSeance({ seance, sansRaisonsDites }: { seance: Seance; sansRaisonsDites: boolean }) {
  // Le ratage et la lecture en cours sont déjà nommés par la phrase du coach quand elle
  // est affichée (voir phrase_coach) : les redire ferait la même raison deux fois.
  const restantes = sansRaisonsDites
    ? seance.raisons.filter((raison) => !RAISONS_DITES_PAR_LE_COACH.includes(raison.code))
    : seance.raisons
  // Les plus parlantes d'abord, deux au plus : une liste de cinq faits se lit comme un
  // plaidoyer, deux faits comme une raison. Le coefficient, vrai mais commun à toute la
  // matière, passe après ce qui est propre à l'élève.
  const raisons = [...restantes]
    .sort((a, b) => rangRaison(a.code) - rangRaison(b.code))
    .slice(0, RAISONS_MAX)
  if (raisons.length === 0) return null
  return (
    <ul className="mt-3 flex flex-col gap-1">
      {raisons.map((raison) => {
        // Une coche dit « fait » : devant « Tu ne l'as encore jamais travaillé » elle disait l'inverse (test élève Gogo).
        const Icone = raison.code === "jamais" ? Sparkles : Check
        return (
          <li key={raison.code} className="flex items-start gap-2 text-xs text-muted-foreground">
            <span className="mt-px flex size-4 shrink-0 items-center justify-center rounded-full bg-primary/15">
              <Icone className="size-2.5 text-primary" strokeWidth={3} aria-hidden="true" />
            </span>
            {raison.texte}
          </li>
        )
      })}
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
  if (seance.origine === "DIAGNOSTIC") return t("seance.diagnostic")
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
  if (jours <= 0) return t("seance.echeance_aujourdhui")
  if (jours === 1) return t("seance.echeance_demain")
  return t("seance.echeance_jours", { n: jours })
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
  useI18n()
  // Un calibrage a une longueur fixe (quinze questions) : proposer 10 ou 45 minutes
  // n'aurait aucun effet, ou le dénaturerait (voir ajuster_duree_seance).
  if (seance.origine === "DIAGNOSTIC" || seance.budgets_possibles.length < 2) return null
  // Verrouillée : trois boutons grisés sans explication se lisaient comme une panne. On dit ce que l'abonnement
  // ouvre, en une phrase, au lieu de montrer un réglage qu'on ne peut pas toucher.
  if (desactive) {
    return (
      <p className="mt-5 text-xs text-muted-foreground">
        {t("seance.duree_abonnement", { durees: seance.budgets_possibles.map((m) => `${m} min`).join(", ") })}
      </p>
    )
  }
  return (
    <div className="mt-5 flex flex-wrap items-center gap-x-3 gap-y-2">
      <span className="text-xs text-muted-foreground">{t("seance.combien_temps")}</span>
      <div role="group" className="inline-flex rounded-full border border-border/80 bg-muted/60 p-1">
        {seance.budgets_possibles.map((minutes) => (
          <button
            key={minutes}
            type="button"
            disabled={enCours || desactive}
            aria-pressed={minutes === seance.budget_minutes}
            onClick={() => onChoisir(minutes)}
            className={cn(
              "min-h-11 rounded-full px-3.5 py-1 text-xs font-medium tabular-nums transition-all disabled:opacity-60",
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
  { cle: "cours", titre: "seance.phase_cours" },
  { cle: "exercice", titre: "seance.phase_exercice" },
  { cle: "quiz", titre: "seance.phase_quiz" },
] as const satisfies readonly { cle: string; titre: CleI18n }[]

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
  useI18n()
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
  // Plié par défaut : le bouton principal dit déjà par quelle étape commencer, et une
  // ligne "Comprendre → S'entraîner → Vérifier" suffit à dire où ça mène. Le détail est
  // à un clic. Jamais plié verrouillé (la structure fait partie de ce que le paywall
  // doit montrer) ni avec une seule phase (rien à résumer).
  const [detailOuvert, setDetailOuvert] = useState(false)
  const pliable = !verrouillee && avecTitres

  if (pliable && !detailOuvert) {
    return (
      <div data-guide="seance-parcours" className="mt-6 flex flex-wrap items-center gap-x-2 gap-y-1.5 text-sm">
        <span className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{t("seance.ton_parcours")}</span>
        <ol className="flex flex-wrap items-center gap-x-2 gap-y-1">
          {groupes.map((phase, index) => {
            const faite = (phase.etapes as EtapeSeance[]).every((etape) => etape.ouverte)
            return (
              <li key={phase.cle} className="flex items-center gap-2">
                <span className={cn("inline-flex items-center gap-1 font-medium", faite && "text-primary")}>
                  {faite && <Check className="size-3.5" strokeWidth={3} aria-label={t("seance.fait")} />}
                  {t(phase.titre)}
                </span>
                {index < groupes.length - 1 && <ArrowRight className="size-3 text-muted-foreground" aria-hidden="true" />}
              </li>
            )
          })}
        </ol>
        <span className="text-xs tabular-nums text-muted-foreground">· {seance.duree_estimee_min} min</span>
        <button
          type="button"
          aria-expanded={false}
          onClick={() => setDetailOuvert(true)}
          className="relative after:absolute after:inset-x-0 after:-inset-y-3.5 after:content-[''] ml-auto text-xs text-muted-foreground underline underline-offset-4 transition-colors hover:text-primary"
        >
          {t("seance.voir_detail")}
        </button>
      </div>
    )
  }

  return (
    <div data-guide="seance-parcours" className="mt-6 rounded-2xl border border-border/70 bg-background/70 p-4 backdrop-blur-sm sm:p-5">
      <p className="flex items-baseline justify-between gap-3 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
        {t("seance.ton_parcours")}
        <span className="flex items-baseline gap-3 font-sans normal-case tracking-normal">
          <span className="tabular-nums">{seance.duree_estimee_min} min</span>
          {pliable && (
            <button
              type="button"
              aria-expanded
              onClick={() => setDetailOuvert(false)}
              className="underline underline-offset-4 transition-colors hover:text-primary"
            >
              {t("seance.reduire")}
            </button>
          )}
        </span>
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
          <li
            key={phase.cle}
            className={cn(
              "rounded-xl border p-3",
              // Le quiz est l'étape qui valide la séance ET rapporte l'XP : seule carte du
              // parcours qui sort du rang (voir XP_MAX_PAR_QUESTION pour le chiffre annoncé).
              phase.cle === "quiz" && avecTitres
                ? "border-gold/60 bg-gold/10 shadow-sm"
                : "border-border/60 bg-background/60",
            )}
          >
            {avecTitres && (
              <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-foreground/80">
                <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-primary text-[0.65rem] font-semibold text-primary-foreground shadow-sm shadow-primary/30">
                  {index + 1}
                </span>
                {t(phase.titre)}
                {phase.cle === "quiz" && (
                  <span className="font-medium normal-case tracking-normal text-primary">{t("seance.valide_la_seance")}</span>
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
                      <span className="min-w-0 flex-1">
                        <span className="line-clamp-2 block font-medium leading-snug">{etape.libelle}</span>
                        {etape.type === "quiz" && (
                          <span className="mt-0.5 flex items-center gap-1 text-xs font-medium text-gold-foreground dark:text-gold-text">
                            <Zap className="size-3" aria-hidden="true" />
                            {t("seance.jusqua_points", { points: etape.n * XP_MAX_PAR_QUESTION })}
                          </span>
                        )}
                      </span>
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
                  {t("seance.tous_exercices", { n: seance.exercices_total })}
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
