import { useEffect, useMemo, useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query"
import { ArrowRight, BookOpen, ChevronDown, ClipboardCheck, Clock, Crown, ListChecks, Play, RotateCcw } from "lucide-react"

import { getAccueil, listMyTentativesInedites } from "@/api/endpoints"
import type { Accueil, DefiSemaine, TentativeInediteListItem } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { DepuisLaDerniereFois } from "@/components/DepuisLaDerniereFois"
import { CLE_DUES, RangeeCartes, useCartesDues } from "@/components/CartesDeRevision"
import { DefiDeLaSemaine, mentionDefi, useDefiSemaine } from "@/components/DefiDeLaSemaine"
import { Moments } from "@/components/Moments"
import { OuJenSuis } from "@/components/OuJenSuis"
import { ReprendreQuiz } from "@/components/ReprendreQuiz"
import { InviteRappels } from "@/components/RappelsEmail"
import { InvitationMatieres } from "@/components/ChoixMatieres"
import { LigneErreurs } from "@/components/MesErreurs"
import { TeteAccueil } from "@/components/TeteAccueil"
import { ecrireAccueilEnCache, lireAccueilEnCache } from "@/lib/accueilCache"
import { marquerAffichageAccueil } from "@/lib/accueilChrono"
import { coursReaderPath, epreuveInediteDetailPath, epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"
import { formatDuration } from "@/lib/duration"
import { maintenantServeur } from "@/lib/horlogeServeur"
import { cleQuizEnCours, FRAICHEUR_ACCUEIL_MS } from "@/lib/quizEnCours"
import { requeteInedites, useCursusAccueil, useInedites } from "@/lib/cursusAccueil"
import { langueCourante, t, tn, useI18n } from "@/lib/i18n"
import { useSeo } from "@/lib/seo"

/**
 * Dépose les reprises reçues avec l'accueil dans le cache de la route de chacune (voir quiz.views._reprises côté
 * serveur) : la carte « Quiz en cours », la ligne des cartes et le défi de la semaine lisent ces clés et s'affichent
 * donc avec la séance, sans requête à eux. Avant, chacun arrivait un instant après : la carte « Quiz en cours »,
 * placée au-dessus de la séance, faisait descendre « Commencer » de 128 px (audit de l'accueil abonné, 2026-11-16).
 *
 * `seulementSiAbsent` : pour un accueil relu dans le navigateur (version de la dernière visite), on ne remplace
 * jamais une donnée que la page tient déjà du serveur, forcément plus récente.
 */
function deposerReprises(
  queryClient: QueryClient,
  accueil: Accueil,
  profilId: number | null | undefined,
  cursusId: number,
  { seulementSiAbsent = false }: { seulementSiAbsent?: boolean } = {},
) {
  const reprises = accueil.reprises
  if (!reprises) return
  const deposer = (cle: readonly unknown[], valeur: unknown) => {
    if (seulementSiAbsent && queryClient.getQueryData(cle) !== undefined) return
    queryClient.setQueryData(cle, valeur)
  }
  if (profilId != null) deposer(cleQuizEnCours(profilId), reprises.quiz_en_cours)
  deposer(CLE_DUES, reprises.cartes_dues)
  deposer(["defi-semaine", cursusId], { defi: reprises.defi })
}

/** Deux instants tombent-ils le même jour, à l'heure de l'appareil ? */
function memeJour(a: number, b: number): boolean {
  return new Date(a).toDateString() === new Date(b).toDateString()
}

/**
 * L'accueil d'un élève ABONNÉ, en trois zones et pas plus :
 *
 *   1. Aujourd'hui (TeteAccueil) : qui il est, où il en est, une phrase de coach, et
 *      LE bouton - au-dessus du pli, y compris sur téléphone.
 *   2. Depuis la dernière fois (DepuisLaDerniereFois) : ce qui a bougé, puis ce qu'il
 *      y a à reprendre (deux révisions au plus, une lecture ouverte).
 *   3. Où j'en suis (OuJenSuis) : l'anneau pondéré, la trajectoire d'ici le jour J, les
 *      deux matières les plus en retard.
 *
 * Tout vient d'UNE requête (voir getAccueil et quiz.accueil côté backend), rendue en
 * un seul passage : plus de blocs qui apparaissent un à un ni de page qui saute. La
 * dernière version connue est gardée dans le navigateur (voir lib/accueilCache) pour
 * s'afficher avant la réponse - et hors connexion.
 *
 * Un VISITEUR et un élève NON abonné continuent de voir la page vitrine complète (voir
 * CataloguePage) : pour le second, c'est sa page de conversion. La vitrine reste aussi
 * ce que voient les robots d'indexation.
 */
export function AccueilEleve({ country }: { country: string }) {
  useI18n()
  // Seul composant de page sans titre : il gardait celui de la page précédente, ou, au rechargement, le titre français
  // statique d'index.html (même pour un élève GCE sur /en). Page personnelle : jamais indexée (la vitrine reste ce que
  // voient les robots, voir CataloguePage).
  useSeo({ title: t("accueil.seo_eleve"), description: t("accueil.seo_eleve_description"), noindex: true })
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const cursusId = user?.cursus_prepare?.id
  const userId = user?.id
  const profilId = user?.profil_actif?.id

  // Le chrono du seul chiffre qui juge cette page : le délai jusqu'à "Commencer".
  useEffect(() => {
    marquerAffichageAccueil()
  }, [])

  const enCache = useMemo(
    () => {
      const entree = userId && cursusId ? lireAccueilEnCache(userId, cursusId) : null
      // Avant le premier rendu des blocs : ils trouvent leurs données en montant, sans requête.
      if (entree && cursusId) deposerReprises(queryClient, entree.data, profilId, cursusId, { seulementSiAbsent: true })
      return entree
    },
    [userId, cursusId, profilId, queryClient],
  )

  const { data, isError, isFetchedAfterMount, fetchStatus } = useQuery({
    queryKey: ["accueil", cursusId],
    queryFn: async ({ signal }) => {
      const accueil = await getAccueil(signal)
      // Les blocs qui vivent aussi ailleurs lisent leurs clés habituelles : on les
      // alimente ici pour qu'aucun n'ait à refaire sa propre requête (la séance et ses
      // mutations sous "plan-du-jour", le bilan de semaine, le résumé du parcours que
      // la page Ma progression réutilise en arrivant depuis "Voir toute ma progression").
      queryClient.setQueryData(["plan-du-jour"], accueil.plan)
      if (accueil.bilan_semaine) queryClient.setQueryData(["bilan-periode", cursusId, 7], accueil.bilan_semaine)
      queryClient.setQueryData(["parcours-resume", cursusId], accueil.resume)
      if (cursusId) deposerReprises(queryClient, accueil, profilId, cursusId)
      if (userId && cursusId) ecrireAccueilEnCache(userId, cursusId, accueil)
      return accueil
    },
    // La version en cache s'affiche tout de suite, et le serveur est TOUJOURS
    // interrogé au montage (staleTime 0, contre 60 s par défaut) : un accueil rouvert
    // deux minutes après la séance doit déjà dire "Séance faite" - c'est précisément la
    // page dont la donnée bouge entre deux ouvertures.
    initialData: enCache?.data,
    initialDataUpdatedAt: enCache?.date,
    // Un onglet ou une PWA laissé ouvert la veille affichait encore « Séance faite » le lendemain :
    // au retour sur l'onglet, on revérifie si la donnée a plus de 5 minutes (le réglage global
    // coupe cette revérification, pensée pour du contenu qui ne bouge pas).
    refetchOnWindowFocus: (query) => Date.now() - query.state.dataUpdatedAt > 5 * 60_000,
    staleTime: 0,
    enabled: Boolean(cursusId),
  })

  // Les inédites de SON cursus uniquement - même clé de cache que la vitrine. L'examen du compte, quelle que soit
  // la langue de l'interface (voir `toutesLangues` dans useCursusAccueil).
  const cursusAccueil = useCursusAccueil(country, { toutesLangues: true })
  const { data: inedites } = useInedites(country, cursusAccueil)
  // Une épreuve inédite commencée et pas rendue : la seule porte d'entrée vers elle était
  // le menu du compte > Mon historique. La liste arrive avec l'accueil (voir `reprises`), qui est relu à chaque
  // ouverture : l'accueil rouvert après avoir rendu sa copie ne propose donc pas de la reprendre. La requête à part
  // ne sert plus qu'à un accueil gardé en cache d'avant ce champ (staleTime 0, pour la même raison).
  const { data: tentativesSeules } = useQuery({
    queryKey: ["inedit-tentatives"],
    queryFn: () => listMyTentativesInedites(),
    staleTime: 0,
    enabled: Boolean(cursusId) && Boolean(data) && !data?.reprises,
  })
  const tentatives = data?.reprises?.tentatives ?? tentativesSeules
  const enCours = tentatives?.find((t) => t.submitted_at === null)
  // La dernière copie rendue dont il reste des questions à noter (voir questions_a_noter côté serveur).
  const aNoter = tentatives?.find((t) => t.submitted_at !== null && (t.questions_a_noter ?? 0) > 0)

  if (!data || !cursusId) {
    return isError ? <ErreurAccueil /> : <SqueletteAccueil />
  }

  // Une épreuve au chrono lancé ne peut pas attendre : la copie est rendue à zéro à l'échéance. Sur téléphone la
  // tête de page occupe plus d'un écran, et la reprise (sous elle) tombait à ~1 290 px du haut, 1,6 écran
  // (test élève 2026-11-07, chrono de 1 h 59 en cours). Elle passe donc AVANT la séance du jour.
  const chronoEnCours = Boolean(enCours?.echeance)
  // Une lecture ouverte cette semaine : « Lecture en cours » vivait tout en bas, dans « Depuis la dernière fois »,
  // à ~1 380 px du haut (test élève 2026-11-07). Elle remonte sous la séance, avec les autres reprises. Sauf si la
  // séance du jour EST cette lecture : le bouton de la tête de page y mène déjà, un second serait un doublon.
  const lectureAReprendre = data.lecture && data.plan?.seance?.origine !== "LECTURE_EN_COURS" ? data.lecture : null
  // La page de la dernière visite s'affiche avant la réponse du serveur (voir lib/accueilCache). Si cette visite
  // date d'un autre jour, sa carte de séance est fausse : « Séance faite », ou le thème de la veille, le temps du
  // chargement (audit de l'accueil abonné, 2026-11-16). On garde donc le reste de la page et on met la carte en
  // attente tant que le serveur n'a pas répondu. Hors connexion (requête en pause) ou après un échec, la page
  // d'hier vaut mieux que rien : elle reste affichée en entier.
  const seanceEnAttente = enCache != null && !memeJour(enCache.date, Date.now())
    && !isFetchedAfterMount && fetchStatus === "fetching"

  return (
    // `eleve-installe` : repère lu par le tutoriel de bienvenue (voir lib/guides/contenu.ts), posé dès que l'élève a
    // terminé une séance. Sans lui, le tutoriel se rejouait à un abonné de longue date sur chaque nouvel appareil.
    <div className="pb-4" data-guide={data.premiers_pas ? undefined : "eleve-installe"}>
      {/* Le titre de la page, pour les lecteurs d'écran et le plan du document : la salutation visible contient un
          sélecteur d'examen, qui n'a pas sa place dans un titre. */}
      <h1 className="sr-only">{t("seance.aujourdhui")}</h1>
      {enCours && chronoEnCours && <LigneReprise tentative={enCours} country={country} cursusAccueil={cursusAccueil} />}
      {/* Un quiz commencé passe lui aussi avant la tête de page (test élève 2026-11-07, deux testeurs : « Quiz en cours »
          à ~1 180 px du haut, sous le premier écran). Ordre : chrono d'examen, puis quiz, puis la séance du jour. */}
      <ReprendreQuiz enveloppe fraicheurMs={FRAICHEUR_ACCUEIL_MS} />
      {seanceEnAttente ? <SqueletteTete /> : <TeteAccueil accueil={data} country={country} />}
      {/* Ce qui est commencé et pas fini passe juste sous la séance : placé après « Où j'en suis », il se
          trouvait à 2 ou 3 écrans de défilement sur téléphone (test élève 2026-10-24, reprise > 10 s). Tout ce qui
          se reprend ou se fait en plus de la séance tient maintenant dans UN bloc (voir AContinuer). */}
      <AContinuer
        accueil={data}
        country={country}
        cursusAccueil={cursusAccueil}
        inedites={inedites}
        enCours={enCours && !chronoEnCours ? enCours : undefined}
        epreuveEnCours={enCours?.epreuve}
        aNoter={!enCours ? aNoter : undefined}
        lecture={lectureAReprendre}
      />
      {/* GCE seulement, et seulement tant que l'élève n'a pas dit quelles matières il passe. */}
      <InvitationMatieres />
      <Moments accueil={data} userId={userId} />
      {/* Proposé une fois, quand l'élève sait ce qu'on lui rappellerait : après sa
          première séance. */}
      {!data.premiers_pas && <InviteRappels />}
      {/* Ce qui a bougé depuis la dernière visite, et rien d'autre : les thèmes à reprendre et la lecture ouverte
          sont dans « À continuer », plus haut. */}
      <DepuisLaDerniereFois depuis={data.depuis} revisions={[]} lecture={null} />
      <OuJenSuis accueil={data} cursusId={cursusId} country={country} />
    </div>
  )
}

// Nombre de lignes du bloc « À continuer » montrées d'emblée ; le reste est derrière « Voir N de plus ».
const LIGNES_A_CONTINUER = 3

// À partir de ce nombre d'erreurs à refaire, leur ligne passe en tête du bloc, devant la copie entamée : en dessous,
// la deuxième place suffit (une erreur se corrige en une minute, elle ne presse pas plus qu'une copie à finir).
const SEUIL_ERREURS_EN_TETE = 5

/**
 * Le défi de la semaine, quand la copie entamée est la sienne et qu'il n'est pas encore relevé (il l'est une fois la
 * copie rendue, voir inedit.defi côté serveur) ; null sinon.
 */
function defiDeLaCopie(defi: DefiSemaine | null, epreuve: number | undefined): DefiSemaine | null {
  return defi && !defi.releve && epreuve != null && defi.epreuve_id === epreuve ? defi : null
}

const CADRE_RANGEE = "group flex items-center gap-3 px-5 py-3.5 transition-colors hover:bg-muted/40"

/**
 * « À continuer » : tout ce qui se reprend ou se fait en plus de la séance du jour, dans UN bloc.
 *
 * Avant, six blocs se suivaient sous la séance, chacun avec son cadre et son bouton, sans ordre entre eux : lecture en
 * cours, mes erreurs, cartes, défi de la semaine, thèmes à reprendre, prochaine inédite. Sur un téléphone ils
 * occupaient près d'un écran et se disputaient l'attention avec le bouton « Commencer » (audit de l'accueil abonné,
 * 2026-11-16 : dix blocs, 4,6 écrans). Ici trois lignes au plus sont montrées, dans l'ordre de ce qui presse :
 *
 *   1. la copie d'épreuve inédite entamée, ou la copie rendue à finir de noter ;
 *   2. les erreurs à refaire : c'est le geste le plus rentable de la liste et le plus court, il ne doit pas attendre
 *      derrière « Voir N de plus » (décision de l'utilisateur, 2026-11-21 ; il était avant-dernier). Il ne prend pas
 *      la première ligne, pour que l'accueil ne s'ouvre pas sur un reproche, sauf quand les erreurs s'accumulent
 *      (voir SEUIL_ERREURS_EN_TETE) ;
 *   3. la lecture ouverte ;
 *   4. ce qui a une échéance (le défi de la semaine, tant qu'il n'est pas relevé) ;
 *   5. ce qui est neuf (la prochaine épreuve inédite) : c'est le contenu que l'abonné paie pour recevoir, elle reste
 *      devant ce qui s'entretient (décision de l'utilisateur, 2026-11-16) ;
 *   6. ce qui s'entretient (thèmes à reprendre, cartes dues) ;
 *   7. le défi déjà relevé, qui n'appelle plus de geste.
 *
 * Quand la copie entamée EST le défi de la semaine, les deux ne font qu'une ligne : la reprise, qui porte l'échéance
 * du défi (voir mentionDefi). Avant, le même titre se lisait deux fois, à deux lignes d'écart.
 *
 * Le reste est derrière « Voir N de plus », sur place. Une épreuve au chrono lancé et un quiz commencé ne sont pas
 * ici : ils passent AVANT la séance (voir AccueilEleve), parce qu'ils ne peuvent pas attendre.
 */
function AContinuer({
  accueil, country, cursusAccueil, inedites, enCours, epreuveEnCours, aNoter, lecture,
}: {
  accueil: Accueil
  country: string
  cursusAccueil: ReturnType<typeof useCursusAccueil>
  inedites: ReturnType<typeof useInedites>["data"]
  enCours?: TentativeInediteListItem
  /** L'épreuve de la copie entamée, que sa ligne soit ici ou avant la séance (chrono lancé). */
  epreuveEnCours?: number
  aNoter?: TentativeInediteListItem
  lecture: Accueil["lecture"]
}) {
  const [toutVoir, setToutVoir] = useState(false)
  // Mêmes clés de cache que l'accueil vient de remplir (voir deposerReprises) : aucune requête de plus.
  const defi = useDefiSemaine(country, cursusAccueil)
  const cartes = useCartesDues()
  // Le défi est la copie déjà entamée : sa ligne de reprise le dit, il n'a pas de ligne à lui.
  const defiEntame = defiDeLaCopie(defi, epreuveEnCours)

  const erreurs = accueil.erreurs_total ?? 0
  const rangeeErreurs = cursusAccueil != null && erreurs > 0
    ? { cle: "erreurs", rendu: <LigneErreurs total={erreurs} cursusId={cursusAccueil} rangee /> }
    : null
  const erreursEnTete = erreurs >= SEUIL_ERREURS_EN_TETE

  const lignes: { cle: string; rendu: ReactNode }[] = []
  if (rangeeErreurs && erreursEnTete) lignes.push(rangeeErreurs)
  if (enCours) lignes.push({ cle: "copie", rendu: <RangeeReprise tentative={enCours} defi={defiEntame} /> })
  if (aNoter) lignes.push({ cle: "notation", rendu: <RangeeNotation tentative={aNoter} /> })
  if (rangeeErreurs && !erreursEnTete) lignes.push(rangeeErreurs)
  if (lecture) lignes.push({ cle: "lecture", rendu: <RangeeLecture lecture={lecture} /> })
  const rangeeDefi = defi && !defiEntame
    ? { cle: "defi", rendu: <DefiDeLaSemaine country={country} cursusId={cursusAccueil} rangee /> }
    : null
  if (rangeeDefi && !defi?.releve) lignes.push(rangeeDefi)
  if (inedites && inedites.count > 0) {
    lignes.push({
      cle: "inedites",
      rendu: <RangeeInedites country={country} inedites={inedites} cursusAccueil={cursusAccueil} />,
    })
  }
  for (const revision of accueil.revisions) {
    lignes.push({ cle: `revision-${revision.id}`, rendu: <RangeeRevision revision={revision} /> })
  }
  if (cartes && cartes.total > 0) lignes.push({ cle: "cartes", rendu: <RangeeCartes total={cartes.total} /> })
  if (rangeeDefi && defi?.releve) lignes.push(rangeeDefi)

  if (lignes.length === 0) return null
  const enPlus = lignes.length - LIGNES_A_CONTINUER
  const montrees = toutVoir ? lignes : lignes.slice(0, LIGNES_A_CONTINUER)

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-labelledby="a-continuer-titre">
      <div className="overflow-hidden rounded-2xl border border-border bg-card">
        <h2
          id="a-continuer-titre"
          className="flex items-center gap-2 px-5 pt-4 pb-1 text-xs font-semibold uppercase tracking-[0.18em] text-primary"
        >
          <ListChecks className="size-3.5" aria-hidden="true" />
          {t("continuer.titre")}
        </h2>
        <ul className="divide-y divide-border/60">
          {montrees.map((ligne) => (
            <li key={ligne.cle}>{ligne.rendu}</li>
          ))}
        </ul>
        {enPlus > 0 && (
          <button
            type="button"
            aria-expanded={toutVoir}
            onClick={() => setToutVoir((ouvert) => !ouvert)}
            className="flex min-h-11 w-full items-center justify-center gap-1.5 border-t border-border/60 px-5 text-sm font-medium text-primary transition-colors hover:bg-muted/40"
          >
            {toutVoir ? t("continuer.moins") : tn("continuer.plus", enPlus)}
            <ChevronDown className={toutVoir ? "size-4 rotate-180 transition-transform" : "size-4 transition-transform"} aria-hidden="true" />
          </button>
        )}
      </div>
    </section>
  )
}

/** Une copie rendue dont la note n'est pas complète : l'élève se note lui-même, un rappel finit le travail. */
function RangeeNotation({ tentative }: { tentative: TentativeInediteListItem }) {
  return (
    <Link to={`/inedit/tentative/${tentative.id}`} className={CADRE_RANGEE}>
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
        <ClipboardCheck className="size-4" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {tn("abonne.a_noter", tentative.questions_a_noter ?? 0)}
        </span>
        <span className="line-clamp-2 text-sm font-medium">{tentative.epreuve_titre}</span>
      </span>
      <span className="shrink-0 text-sm font-medium text-gold-text">{t("abonne.finir_notation")}</span>
      <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
    </Link>
  )
}

/** La lecture ouverte cette semaine (cours ou épreuve), à reprendre là où l'élève s'est arrêté. */
function RangeeLecture({ lecture }: { lecture: NonNullable<Accueil["lecture"]> }) {
  return (
    <Link
      to={lecture.type === "cours" ? coursReaderPath(lecture.slug) : epreuveReaderPath(lecture.country, lecture.slug)}
      className={CADRE_RANGEE}
    >
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
        <BookOpen className="size-4" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {t("depuis.lecture_en_cours")}
        </span>
        {/* Deux lignes plutôt qu'une coupe : à 375 px, « Allemand BEPC 20… » perdait l'année. */}
        <span className="line-clamp-2 text-sm font-medium">{lecture.title}</span>
      </span>
      <span className="shrink-0 text-sm font-medium text-primary">{t("seance.reprendre")}</span>
      <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
    </Link>
  )
}

/**
 * Une épreuve inédite entamée, sans chrono lancé : à reprendre quand l'élève veut. `defi` : cette copie est le défi de
 * la semaine, la ligne en porte l'échéance à la place d'une seconde ligne au même titre.
 */
function RangeeReprise({ tentative, defi }: { tentative: TentativeInediteListItem; defi?: DefiSemaine | null }) {
  return (
    <Link to={`/inedit/tentative/${tentative.id}`} className={CADRE_RANGEE}>
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">
        <Play className="size-4" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {t("abonne.inedite_en_cours")}
        </span>
        <span className="line-clamp-2 text-sm font-medium">{tentative.epreuve_titre}</span>
        {defi && <span className="block text-xs text-muted-foreground">{mentionDefi(defi)}</span>}
      </span>
      <span className="shrink-0 text-sm font-medium text-primary">{t("seance.reprendre")}</span>
      <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
    </Link>
  )
}

/** Un thème dont la révision est due (répétition espacée) : un quiz sur ce thème, en un geste. */
function RangeeRevision({ revision }: { revision: Accueil["revisions"][number] }) {
  const theme = revision.theme.charAt(0).toLocaleUpperCase(langueCourante()) + revision.theme.slice(1)
  return (
    <Link to={`/quiz?cursus=${revision.cursus}&theme=${revision.theme_id}`} className={CADRE_RANGEE}>
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
        <RotateCcw className="size-4" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {t("depuis.a_reprendre")} · {revision.subject_label}
        </span>
        <span className="line-clamp-2 text-sm font-medium">{theme}</span>
        {/* Un retard se dit, il ne se reproche pas : gris, jamais rouge. */}
        {revision.jours_retard > 0 && (
          <span className="block text-xs text-muted-foreground">{t("depuis.jours_retard", { n: revision.jours_retard })}</span>
        )}
      </span>
      <span className="shrink-0 text-sm font-medium text-primary">{t("continuer.reviser")}</span>
      <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
    </Link>
  )
}

/**
 * « Reprendre » : l'épreuve inédite entamée AU CHRONO LANCÉ, seule ligne qui passe avant la séance du jour (voir
 * AccueilEleve) : la copie est rendue à zéro à l'échéance, on dit donc ce qu'il reste. Quand cette copie est le défi de
 * la semaine, la ligne le dit aussi : le défi n'a alors plus de ligne à lui dans « À continuer ».
 */
function LigneReprise({
  tentative, country, cursusAccueil,
}: {
  tentative: TentativeInediteListItem
  country: string
  cursusAccueil: ReturnType<typeof useCursusAccueil>
}) {
  // Même clé de cache que l'accueil vient de remplir (voir deposerReprises) : aucune requête de plus.
  const defi = defiDeLaCopie(useDefiSemaine(country, cursusAccueil), tentative.epreuve)
  const reste = tentative.echeance
    ? Math.max(0, Math.round((new Date(tentative.echeance).getTime() - maintenantServeur()) / 1000))
    : null
  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("abonne.inedite_en_cours")}>
      <Link
        to={`/inedit/tentative/${tentative.id}`}
        className="group flex items-center gap-3 rounded-2xl border border-primary/40 bg-primary/5 px-5 py-3.5 transition-colors hover:border-primary"
      >
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">
          <Play className="size-4" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {reste !== null ? t("abonne.chrono_en_cours", { duree: formatDuration(reste) }) : t("abonne.inedite_en_cours")}
          </span>
          <span className="block truncate text-sm font-medium">{tentative.epreuve_titre}</span>
          {defi && <span className="block text-xs text-muted-foreground">{mentionDefi(defi)}</span>}
        </span>
        <span className="shrink-0 text-sm font-medium text-primary">{t("seance.reprendre")}</span>
        <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
      </Link>
    </section>
  )
}

/**
 * La prochaine épreuve inédite à FAIRE (accessible, jamais rendue), pas toujours la plus récente : une ligne qui
 * remontait l'épreuve déjà passée n'invitait à rien. Elle mène droit à sa fiche ; quand tout est fait, à la liste.
 * Une inédite n'est pas un argumentaire, c'est du contenu neuf que l'abonné a payé pour recevoir - sans cette ligne,
 * il ne sait pas qu'il est arrivé.
 */
function RangeeInedites({
  country, inedites, cursusAccueil,
}: {
  country: string
  inedites: NonNullable<ReturnType<typeof useInedites>["data"]>
  cursusAccueil: ReturnType<typeof useCursusAccueil>
}) {
  const liste = `${epreuvesListPath(country)}?${requeteInedites(cursusAccueil)}`
  const suivante = inedites.results.find((e) => e.has_access && !e.is_read)
  const fiche = suivante ? epreuveInediteDetailPath(country, suivante.slug ?? suivante.id) : null
  const intitule = suivante?.title ?? inedites.results[0]?.title ?? t("abonne.inedites_generique")
  return (
    <Link to={fiche ?? liste} className={CADRE_RANGEE}>
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
        <Crown className="size-4" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {fiche ? t("abonne.prochaine_inedite") : tn("abonne.inedites_nombre", inedites.count)}
        </span>
        {/* Deux lignes plutôt qu'une coupe : à 375 px, « Mini-inédite Franç… » perdait la matière, le mot utile. */}
        <span className="line-clamp-2 text-sm font-medium">{intitule}</span>
      </span>
      <Clock className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
      <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
    </Link>
  )
}

/**
 * Le squelette a la HAUTEUR du contenu qu'il remplace (la tête avec sa bande et son
 * bouton, puis deux blocs) : quand la réponse arrive, rien ne saute. Sans animation
 * de balayage - un téléphone d'entrée de gamme n'a pas besoin de ça pour attendre.
 */
export function SqueletteAccueil() {
  return (
    <div className="pb-4" aria-busy="true" aria-label={t("abonne.chargement")}>
      <SqueletteTete seul={false} />
      <div className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
        <div className="h-36 rounded-3xl border border-border/70 bg-card" />
      </div>
      <div className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
        <div className="h-64 rounded-3xl border border-border/70 bg-card" />
      </div>
    </div>
  )
}

/**
 * La place de la carte de séance, vide. `seul` : affichée à la place de la carte dans une page par ailleurs
 * remplie (accueil d'un autre jour relu dans le navigateur) ; elle s'annonce alors elle-même aux lecteurs d'écran.
 */
function SqueletteTete({ seul = true }: { seul?: boolean }) {
  return (
    <div
      className="mx-auto max-w-5xl px-4 pt-5 sm:px-6 sm:pt-6"
      {...(seul ? { "aria-busy": true, "aria-label": t("abonne.chargement") } : {})}
    >
      <div className="overflow-hidden rounded-3xl border border-border/70 bg-card">
        <div className="h-44 bg-primary/10 sm:h-40" />
        <div className="space-y-4 p-5 sm:p-8">
          <div className="h-4 w-24 rounded bg-muted" />
          <div className="h-9 w-3/4 rounded bg-muted" />
          <div className="flex gap-2">
            <div className="h-7 w-24 rounded-full bg-muted" />
            <div className="h-7 w-16 rounded-full bg-muted" />
          </div>
          <div className="h-12 w-52 rounded-full bg-muted" />
        </div>
      </div>
    </div>
  )
}

function ErreurAccueil() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <p className="text-sm text-muted-foreground">
        {t("abonne.erreur_avant")}{" "}
        <button type="button" onClick={() => window.location.reload()} className="underline underline-offset-4 hover:text-primary">
          {t("abonne.erreur_lien")}
        </button>
        .
      </p>
    </div>
  )
}
