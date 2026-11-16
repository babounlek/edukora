import { useEffect, useMemo } from "react"
import { Link } from "react-router-dom"
import { useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query"
import { ArrowRight, BookOpen, ClipboardCheck, Clock, Crown, Play } from "lucide-react"

import { getAccueil, listMyTentativesInedites } from "@/api/endpoints"
import type { Accueil, TentativeInediteListItem } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { DepuisLaDerniereFois } from "@/components/DepuisLaDerniereFois"
import { CLE_DUES, LigneCartes } from "@/components/CartesDeRevision"
import { DefiDeLaSemaine } from "@/components/DefiDeLaSemaine"
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
import { t, tn, useI18n } from "@/lib/i18n"
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
      {enCours && chronoEnCours && <LigneReprise tentative={enCours} />}
      {/* Un quiz commencé passe lui aussi avant la tête de page (test élève 2026-11-07, deux testeurs : « Quiz en cours »
          à ~1 180 px du haut, sous le premier écran). Ordre : chrono d'examen, puis quiz, puis la séance du jour. */}
      <ReprendreQuiz enveloppe fraicheurMs={FRAICHEUR_ACCUEIL_MS} />
      {seanceEnAttente ? <SqueletteTete /> : <TeteAccueil accueil={data} country={country} />}
      {/* Ce qui est commencé et pas fini passe juste sous la séance : placé après « Où j'en suis », il se
          trouvait à 2 ou 3 écrans de défilement sur téléphone (test élève 2026-10-24, reprise > 10 s). */}
      {enCours && !chronoEnCours && <LigneReprise tentative={enCours} />}
      {lectureAReprendre && <LigneLecture lecture={lectureAReprendre} />}
      {!enCours && aNoter && <LigneNotation tentative={aNoter} />}
      {/* Les questions ratées et pas encore réussies : un geste pour en refaire un paquet (voir quiz.erreurs). */}
      {cursusAccueil != null && <LigneErreurs total={data.erreurs_total ?? 0} cursusId={cursusAccueil} />}
      {/* GCE seulement, et seulement tant que l'élève n'a pas dit quelles matières il passe. */}
      <InvitationMatieres />
      <Moments accueil={data} userId={userId} />
      <LigneCartes />
      <DefiDeLaSemaine country={country} cursusId={cursusAccueil} />
      {/* Proposé une fois, quand l'élève sait ce qu'on lui rappellerait : après sa
          première séance. */}
      {!data.premiers_pas && <InviteRappels />}
      <DepuisLaDerniereFois
        depuis={data.depuis}
        revisions={data.revisions}
        lecture={lectureAReprendre ? null : data.lecture}
      />
      <OuJenSuis accueil={data} cursusId={cursusId} country={country} />
      <LigneInedites accueil={data} country={country} inedites={inedites} cursusAccueil={cursusAccueil} />
    </div>
  )
}

/** Une copie rendue dont la note n'est pas complète : l'élève se note lui-même, un rappel finit le travail. */
function LigneNotation({ tentative }: { tentative: TentativeInediteListItem }) {
  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("abonne.section_notation")}>
      <Link
        to={`/inedit/tentative/${tentative.id}`}
        className="group flex items-center gap-3 rounded-2xl border border-gold/40 bg-gold/5 px-5 py-3.5 transition-colors hover:border-gold"
      >
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
          <ClipboardCheck className="size-4" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {tn("abonne.a_noter", tentative.questions_a_noter ?? 0)}
          </span>
          <span className="block truncate text-sm font-medium">{tentative.epreuve_titre}</span>
        </span>
        <span className="shrink-0 text-sm font-medium text-gold-text">{t("abonne.finir_notation")}</span>
        <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" />
      </Link>
    </section>
  )
}

/** La lecture ouverte cette semaine (cours ou épreuve), à reprendre là où l'élève s'est arrêté. */
function LigneLecture({ lecture }: { lecture: NonNullable<Accueil["lecture"]> }) {
  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("depuis.lecture_en_cours")}>
      <Link
        to={lecture.type === "cours" ? coursReaderPath(lecture.slug) : epreuveReaderPath(lecture.country, lecture.slug)}
        className="group flex items-center gap-3 rounded-2xl border border-border bg-card px-5 py-3.5 transition-colors hover:border-primary/40"
      >
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <BookOpen className="size-4" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {t("depuis.lecture_en_cours")}
          </span>
          <span className="block truncate text-sm font-medium">{lecture.title}</span>
        </span>
        <span className="shrink-0 text-sm font-medium text-primary">{t("seance.reprendre")}</span>
        <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
      </Link>
    </section>
  )
}

/**
 * « Reprendre » : l'épreuve inédite entamée passe avant toute proposition d'en commencer une
 * autre. Avec un chrono lancé, on dit ce qu'il reste - c'est l'urgence qui compte ici.
 */
function LigneReprise({ tentative }: { tentative: TentativeInediteListItem }) {
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
        </span>
        <span className="shrink-0 text-sm font-medium text-primary">{t("seance.reprendre")}</span>
        <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
      </Link>
    </section>
  )
}

/**
 * Le seul bloc "produit" conservé, réduit à une ligne : une inédite n'est pas un
 * argumentaire, c'est du contenu neuf que l'abonné a payé pour recevoir - sans ça, il
 * ne sait pas qu'il est arrivé.
 */
function LigneInedites({
  country, inedites, cursusAccueil,
}: {
  accueil: Accueil
  country: string
  inedites: ReturnType<typeof useInedites>["data"]
  cursusAccueil: ReturnType<typeof useCursusAccueil>
}) {
  if (!inedites || inedites.count === 0) return null
  const liste = `${epreuvesListPath(country)}?${requeteInedites(cursusAccueil)}`
  // La prochaine à FAIRE (accessible, jamais rendue), pas toujours la plus récente : une
  // ligne qui remontait l'épreuve déjà passée n'invitait à rien. Elle mène droit à sa fiche.
  const suivante = inedites.results.find((e) => e.has_access && !e.is_read)
  const fiche = suivante ? epreuveInediteDetailPath(country, suivante.slug ?? suivante.id) : null
  const intitule = suivante?.title ?? inedites.results[0]?.title ?? t("abonne.inedites_generique")
  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label={t("abonne.section_inedites")}>
      <div className="flex items-center gap-3 rounded-2xl border border-gold/30 bg-gold/5 px-5 py-3.5 transition-colors hover:border-gold/60">
        <Link to={fiche ?? liste} className="group flex min-w-0 flex-1 items-center gap-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
            <Crown className="size-4" />
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
        {fiche && (
          <Link to={liste} className="flex min-h-11 shrink-0 items-center text-xs font-medium text-gold-text underline-offset-2 hover:underline">
            {t("abonne.inedites_toutes", { n: inedites.count })}
          </Link>
        )}
      </div>
    </section>
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
