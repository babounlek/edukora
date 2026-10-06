import { useEffect, useRef, useState } from "react"
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom"
import { ArrowLeft, Check, Clock, Crown, Gift, GraduationCap, Lock, RotateCcw, Sparkles, Unlock } from "lucide-react"

import { getEpreuveInedite, listPlans, startExamMode, startTentativeInedite } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Epreuve, Plan } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { ParrainageHint } from "@/components/ParrainageHint"
import { BackToTopBar } from "@/components/BackToTopBar"
import { CountryBadge } from "@/components/CountryBadge"
import { ChoixModeEpreuve } from "@/components/inedit/ChoixModeEpreuve"
import { DialogueModeExamen } from "@/components/inedit/DialoguesEpreuve"
import { useAuth } from "@/context/AuthContext"
import { formatCursusGroups } from "@/lib/cursus"
import { useCursusDeclare, useInedites } from "@/lib/cursusAccueil"
import { trackEvent } from "@/lib/analytics"
import { formatAmount } from "@/lib/utils"
import { formatDuration } from "@/lib/duration"
import { formatNote } from "@/lib/notation"
import { choisirCursusPourAchat, lienAbonnement } from "@/lib/retourAchat"
import { useSeo } from "@/lib/seo"
import { coursDetailPath, coursReaderPath, epreuveInediteDetailPath, epreuvesListPath } from "@/lib/countryPath"

/** Fiche détail d'une épreuve inédite - miroir simplifié d'EpreuveDetailPage.tsx : pas
 * de sujet complet en aperçu public (contrairement à previewEpreuve côté classique,
 * tout le contenu reste gated) - seul apercu_enonce_markdown (une unique question)
 * est public, voir sa section plus bas. "Commencer" ouvre (ou reprend) une tentative
 * plutôt que de mener directement à un lecteur. */
export function EpreuveInediteDetailPage() {
  const { country: countryParam, id } = useParams<{ country?: string; id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const { isAuthenticated } = useAuth()
  const cursusDeclare = useCursusDeclare()

  const [epreuve, setEpreuve] = useState<Epreuve | null>(null)
  const [error, setError] = useState("")
  const [starting, setStarting] = useState(false)
  // La formule la moins chère qui débloque réellement les inédites (voir l'effet plus bas).
  const [offre, setOffre] = useState<Plan | null>(null)
  const [confirmerRecommencer, setConfirmerRecommencer] = useState(false)
  // Mode chronométré à confirmer avant de lancer le chrono (jamais lancé d'un simple clic).
  const [modeAConfirmer, setModeAConfirmer] = useState<"examen" | "papier" | null>(null)
  // Le bloc d'action est-il à l'écran ? Sinon, sur téléphone, sa copie collée en bas prend
  // le relais (voir plus bas) : l'élève n'a jamais à redescendre ou remonter pour agir.
  const actionsRef = useRef<HTMLDivElement>(null)
  const [actionsVisibles, setActionsVisibles] = useState(true)

  useSeo({
    title: epreuve?.title ?? "Épreuve inédite",
    description: epreuve
      ? `${epreuve.subject.label} - épreuve inédite originale conçue par Edukora, jamais tirée des annales.`
      : undefined,
  })

  useEffect(() => {
    if (!id) return
    getEpreuveInedite(id)
      .then(setEpreuve)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Impossible de charger cette épreuve."))
  }, [id])

  useEffect(() => {
    // ?ref=pdf_sujet_inedit : posé par le PDF du sujet (voir backend
    // inedit.sujet_pdf._epreuve_deep_link) - même mécanique que EpreuveDetailPage.tsx,
    // mais ce lecteur est déjà abonné (ce PDF est privé, voir la note de partage
    // affichée dessus) : on mesure ici un retour vers l'appli depuis un sujet
    // imprimé, pas une acquisition.
    if (!epreuve) return
    if (searchParams.get("ref") !== "pdf_sujet_inedit") return
    trackEvent("pdf_sujet_inedit_landing", { subject_code: epreuve.subject.code })
  }, [epreuve, searchParams])

  useEffect(() => {
    // Recanonicalise vers /{pays}/epreuves-inedites/{slug} dès que l'épreuve réelle
    // est connue - même principe que EpreuveDetailPage.tsx (préfixe pays), étendu au
    // slug lui-même : un ancien lien par id (voir EpreuveInedite.slug, résolu en
    // lecture côté backend pour compat) ne doit jamais rester l'URL affichée/indexée
    // une fois le slug connu - jamais deux URLs différentes pour le même contenu.
    if (!epreuve || !epreuve.slug) return
    const canonicalCountry = epreuve.subject.country.code.toLowerCase()
    if (countryParam !== canonicalCountry || id !== epreuve.slug) {
      navigate(epreuveInediteDetailPath(canonicalCountry, epreuve.slug), { replace: true })
    }
  }, [epreuve, countryParam, id, navigate])

  // Le cursus à acheter : celui que l'élève a déclaré quand l'épreuve le couvre (une épreuve
  // « BAC D et TI » ne doit pas envoyer un élève de TI acheter le BAC D), sinon le premier.
  const cursusAchat = epreuve ? choisirCursusPourAchat(epreuve.cursus, cursusDeclare) : undefined
  const cursusAchatId = cursusAchat?.id

  useEffect(() => {
    // Prix d'appel affiché sur le mur payant (voir plus bas) - inutile si l'élève a
    // déjà accès. Formule la moins chère qui débloque réellement l'add-on (inclut_inedit),
    // jamais le prix de Mensuel qui ne débloquerait pas cette épreuve. effective_price
    // (pas price, qui n'est qu'un plafond pour Jusqu'à l'Examen) - voir
    // subscriptions.models.Plan.effective_price.
    if (!epreuve || epreuve.has_access || !cursusAchatId) return
    listPlans(cursusAchatId).then((plans) => {
      const eligibles = plans.filter((p) => p.inclut_inedit)
      if (eligibles.length === 0) return
      setOffre(eligibles.reduce((moins, p) => (p.effective_price < moins.effective_price ? p : moins)))
    })
  }, [epreuve, cursusAchatId])

  // Combien d'inédites l'abonnement ouvre sur ce cursus : l'argument du mur payant, chiffré.
  const paysEpreuve = epreuve?.subject.country.code.toLowerCase() ?? ""
  const { data: ineditesDuCursus } = useInedites(paysEpreuve, cursusAchatId ?? null, Boolean(epreuve && (!epreuve.has_access || epreuve.est_vitrine) && cursusAchatId))

  const epreuveChargee = epreuve !== null
  useEffect(() => {
    const bloc = actionsRef.current
    if (!bloc || typeof IntersectionObserver === "undefined") return
    const observateur = new IntersectionObserver(([entree]) => setActionsVisibles(entree.isIntersecting))
    observateur.observe(bloc)
    return () => observateur.disconnect()
  }, [epreuveChargee])

  async function handleStart(options: { nouvelle?: boolean } = {}) {
    if (!epreuve || starting) return
    setStarting(true)
    setError("")
    try {
      const tentative = await startTentativeInedite(epreuve.id, options)
      navigate(`/inedit/tentative/${tentative.id}`)
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Impossible de démarrer cette épreuve pour le moment. Réessaie plus tard.",
      )
      setStarting(false)
      setConfirmerRecommencer(false)
    }
  }

  /** Ouvre (ou reprend) la copie ET applique le mode choisi, d'un seul geste : le choix se fait
   * sur la fiche, plus sur une seconde page intermédiaire. Le chrono, lui, ne démarre qu'après
   * la confirmation (voir DialogueModeExamen). */
  async function lancer(mode: "libre" | "examen" | "papier") {
    if (!epreuve || starting) return
    setStarting(true)
    setError("")
    try {
      const tentative = await startTentativeInedite(epreuve.id)
      if (mode === "libre") {
        // Même repère que le briefing de la page de tentative (voir InediteTentativePage) :
        // le choix est fait, on ne le lui repropose pas.
        try {
          sessionStorage.setItem(`inedit-libre-${tentative.id}`, "1")
        } catch {
          // stockage indisponible : le briefing se reproposera, sans gravité
        }
      } else {
        await startExamMode(tentative.id, { papier: mode === "papier" })
      }
      navigate(`/inedit/tentative/${tentative.id}`)
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Impossible de démarrer cette épreuve pour le moment. Réessaie plus tard.",
      )
      setStarting(false)
      setModeAConfirmer(null)
    }
  }

  if (error && !epreuve) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <p className="text-destructive">{error}</p>
        <Link to="/" className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour au catalogue
        </Link>
      </div>
    )
  }

  if (!epreuve) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-3">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-5 w-1/2" />
          <Skeleton className="h-10 w-40" />
        </div>
      </div>
    )
  }

  const country = epreuve.subject.country.code.toLowerCase()
  const cheminFiche = epreuveInediteDetailPath(country, epreuve.slug ?? epreuve.id)
  // Un seul abonnement existe par cursus (Jusqu'à l'Examen) et inclut toujours les épreuves
  // inédites. `retour` : l'épreuve qui a motivé l'achat, pour y revenir après la connexion
  // et le paiement plutôt que d'atterrir sur un diagnostic sans rapport.
  const lienAchat = cursusAchatId ? lienAbonnement(cursusAchatId, cheminFiche) : "/abonnement"
  // Certains énoncés (voir correction-experte) commencent déjà par leur propre en-tête
  // "Exercice N" en gras (ex. "**Exercice 1 (5 points)**") - l'ajouter une seconde fois
  // au-dessus ferait doublon. On ne l'affiche donc que si l'énoncé ne le contient pas
  // déjà en tête.
  const apercuDejaTitre = /^[\s#*]*exercice\s+\S/i.test(epreuve.apercu_enonce_markdown ?? "")

  // Copie déjà entamée : « Reprendre » plutôt que « Commencer ». Une copie encore vierge
  // (ouverte puis abandonnée au briefing) n'est pas une reprise : le serveur la réutilise.
  const enCours = epreuve.tentative_en_cours ?? null
  const chronoLance = enCours?.exam_mode_started_at != null
  const reprise = enCours !== null && (chronoLance || enCours.traitees > 0)
  const resteSecondes =
    enCours?.echeance ? Math.max(0, Math.round((new Date(enCours.echeance).getTime() - Date.now()) / 1000)) : null
  const avancement = enCours
    ? resteSecondes !== null
      ? `Chrono en cours : il te reste ${formatDuration(resteSecondes)}.`
      : `${enCours.traitees} sur ${enCours.total} traitées : ta copie t'attend.`
    : null

  // Ce que le visiteur gagne, dit avec des chiffres : la formule la moins chère qui ouvre
  // réellement les inédites, sa durée, et combien d'épreuves elle ouvre sur ce cursus.
  const libelleCursus = cursusAchat
    ? `${cursusAchat.examen_display}${cursusAchat.series ? ` - Série ${cursusAchat.series.code}` : ""}`
    : "ce cursus"
  const nbInedites = ineditesDuCursus?.count ?? null
  const validite = offre
    ? offre.duration_mode === "JUSQUA_EXAMEN"
      ? "paiement unique, valable jusqu'à ton examen"
      : `valable ${offre.effective_duration_days} jours`
    : null
  const mes = epreuve.mes_tentatives ?? null
  const dejaRendue =
    mes && mes.nb_terminees > 0
      ? `Déjà rendue ${mes.nb_terminees === 1 ? "une fois" : `${mes.nb_terminees} fois`}${
          mes.meilleure_note !== null && mes.bareme !== null
            ? ` · meilleure note ${formatNote(mes.meilleure_note, mes.bareme)}`
            : ""
        }.`
      : null

  /** Le geste principal, sans le choix du mode : sur la fiche il est intégré au bloc d'action
   * (voir ChoixModeEpreuve) ; la barre fixe du téléphone, elle, n'a la place que d'un bouton. */
  function boutonPrincipal(classe?: string) {
    if (!epreuve) return null
    if (!epreuve.has_access && epreuve.est_vitrine) {
      // Épreuve offerte, mais un compte est requis (la copie est rattachée à un profil) : le
      // visiteur crée le sien et revient ICI, prêt à choisir son mode.
      return (
        <Button asChild size="lg" className={classe}>
          <Link to="/connexion" state={{ from: cheminFiche }}>
            <Gift />
            Essayer gratuitement
          </Link>
        </Button>
      )
    }
    if (!epreuve.has_access) {
      return (
        <Button asChild size="lg" className={classe}>
          <Link to={lienAchat}>Débloquer l'accès</Link>
        </Button>
      )
    }
    if (reprise && enCours) {
      return (
        <Button size="lg" className={classe} onClick={() => navigate(`/inedit/tentative/${enCours.id}`)}>
          <Sparkles />
          Reprendre cette épreuve
        </Button>
      )
    }
    if (epreuve.duree_minutes) {
      // Plusieurs façons de la passer : on ramène au choix plutôt que d'en imposer une.
      return (
        <Button
          size="lg"
          className={classe}
          onClick={() => actionsRef.current?.scrollIntoView({ behavior: "smooth", block: "center" })}
        >
          <Sparkles />
          Choisir comment la passer
        </Button>
      )
    }
    return (
      <Button size="lg" className={classe} onClick={() => lancer("libre")} disabled={starting}>
        <Sparkles />
        {starting ? "Préparation..." : "Commencer cette épreuve"}
      </Button>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 max-sm:pb-24 sm:px-6">
      <Link
        to={epreuvesListPath(country)}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour au catalogue
      </Link>

      <div className="flex animate-fade-up flex-col gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold leading-tight sm:text-3xl">{epreuve.title}</h1>
          <div className="mt-3 flex flex-wrap gap-1.5">
            <CountryBadge code={epreuve.subject.country.code} label={epreuve.subject.country.label} />
            <Badge variant="gold" className="gap-1">
              <Crown className="size-3" />
              Épreuve inédite
            </Badge>
            {epreuve.est_vitrine && (
              <Badge variant="success" className="gap-1">
                <Gift className="size-3" />
                Gratuite
              </Badge>
            )}
            <Badge variant="secondary">{epreuve.subject.label}</Badge>
            {formatCursusGroups(epreuve.cursus).map((group) => (
              <Badge key={group.key} variant="outline">{group.label}</Badge>
            ))}
            {epreuve.duree_minutes && (
              <Badge variant="outline">
                <Clock className="mr-1 size-3" />
                Durée indicative : {epreuve.duree_minutes} min
              </Badge>
            )}
            {epreuve.exercises_count > 0 && (
              <Badge variant="outline">
                {epreuve.exercises_count} exercice{epreuve.exercises_count > 1 ? "s" : ""}
              </Badge>
            )}
          </div>
        </div>

        <p className="text-sm text-muted-foreground">
          Une épreuve originale conçue par Edukora, jamais tirée des annales - même niveau, même structure, même
          barème que l'examen réel. Le seul moyen de te tester en conditions réelles sans déjà connaître les
          réponses.
        </p>

        {/* Les actions AVANT l'aperçu : placées après lui, le bouton d'accès se trouvait à
            près de 1 000 px du haut sur ordinateur et 1 400 px sur téléphone - un visiteur
            convaincu devait deviner qu'il fallait descendre. */}
        <div ref={actionsRef} className="flex flex-wrap gap-2">
          {epreuve.has_access ? (
            <div className="flex w-full flex-col gap-3">
              {reprise ? (
                <div className="flex flex-col gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    {boutonPrincipal()}
                    {/* Recommencer n'a de sens que sur une copie entamée en mode libre : tant que le
                        chrono tourne, une seconde copie ouvrirait le corrigé en plein examen (le
                        serveur la refuse de toute façon). */}
                    {!chronoLance && (
                      <Button size="lg" variant="outline" disabled={starting} onClick={() => setConfirmerRecommencer(true)}>
                        <RotateCcw />
                        Recommencer à zéro
                      </Button>
                    )}
                  </div>
                  {avancement && <p className="text-sm text-muted-foreground">{avancement}</p>}
                </div>
              ) : epreuve.duree_minutes ? (
                /* Le choix du mode, ICI : il vivait sur une seconde page (le briefing de la
                   tentative), après un « Commencer » qui ne choisissait rien. */
                <ChoixModeEpreuve
                  entete={false}
                  titre={epreuve.title}
                  dureeMinutes={epreuve.duree_minutes}
                  bareme={null}
                  nbExercices={epreuve.exercises_count}
                  nbQuestions={0}
                  papierDisponible={epreuve.sujet_pdf_disponible}
                  onExamen={() => setModeAConfirmer("examen")}
                  onPapier={() => setModeAConfirmer("papier")}
                  onLibre={() => lancer("libre")}
                />
              ) : (
                boutonPrincipal()
              )}
              {dejaRendue && (
                <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  <Check className="size-4 shrink-0 text-success" aria-hidden="true" />
                  {dejaRendue}
                </p>
              )}
            </div>
          ) : epreuve.est_vitrine ? (
            /* La vitrine : on ne vend pas un chrono qu'on n'a jamais laissé lancer. */
            <div className="flex w-full flex-col gap-3 rounded-lg border border-success/40 bg-success/5 p-4">
              <p className="flex items-center gap-1.5 text-sm font-medium">
                <Gift className="size-4 shrink-0 text-success" />
                Cette épreuve est offerte : passe-la en entier, gratuitement
              </p>
              <ul className="flex list-disc flex-col gap-1 pl-9 text-sm text-muted-foreground">
                <li>Le chrono, la notation et le rapport de fin d'une vraie épreuve inédite</li>
                <li>Un compte suffit (une minute) : pas d'abonnement, pas de paiement</li>
              </ul>
              <div className="flex flex-wrap items-center gap-3">
                {boutonPrincipal("w-fit")}
                <Link
                  to={lienAchat}
                  className="text-sm font-medium text-primary underline-offset-2 hover:underline"
                >
                  {nbInedites !== null && nbInedites > 1
                    ? `Voir l'abonnement : les ${nbInedites} épreuves inédites`
                    : "Voir l'abonnement"}
                </Link>
              </div>
              {!isAuthenticated && (
                <p className="text-sm text-muted-foreground">
                  Déjà un compte ?{" "}
                  <Link
                    to="/connexion"
                    state={{ from: `${location.pathname}${location.search}` }}
                    className="font-medium text-primary underline-offset-2 hover:underline"
                  >
                    Te connecter
                  </Link>
                </p>
              )}
            </div>
          ) : (
            <div className="flex w-full flex-col gap-3 rounded-lg border border-dashed border-border bg-muted/40 p-4">
              <p className="flex items-center gap-1.5 text-sm font-medium">
                <Lock className="size-4 shrink-0" />
                Incluse dans l'abonnement {libelleCursus}
              </p>
              <ul className="flex list-disc flex-col gap-1 pl-9 text-sm text-muted-foreground">
                <li>
                  {nbInedites !== null && nbInedites > 1 ? `Les ${nbInedites} épreuves inédites` : "Les épreuves inédites"}{" "}
                  de ce cursus, chronométrées, avec grille de notation et rapport de fin
                </li>
                <li>Tous les corrigés d'annales et les cours de méthode</li>
                <li>La séance du jour et les quiz, jusqu'à ton examen</li>
              </ul>
              <div className="flex flex-wrap items-center gap-3">
                {boutonPrincipal("w-fit")}
                {offre && (
                  <span className="text-sm text-muted-foreground">
                    <strong className="font-semibold text-foreground">{formatAmount(offre.effective_price)} FCFA</strong>
                    {validite ? ` · ${validite}` : ""}
                  </span>
                )}
              </div>
              {/* Un abonné dont la session a expiré arrive ici comme un visiteur : sans ce lien,
                  son seul chemin visible était l'achat. */}
              {!isAuthenticated && (
                <p className="text-sm text-muted-foreground">
                  Déjà abonné ?{" "}
                  <Link
                    to="/connexion"
                    state={{ from: `${location.pathname}${location.search}` }}
                    className="font-medium text-primary underline-offset-2 hover:underline"
                  >
                    Te connecter
                  </Link>
                </p>
              )}
              <ParrainageHint />
            </div>
          )}
        </div>

        {/* Aperçu public minimal : une seule question, jamais le sujet entier (voir
            catalog.inedit_bridge._apercu_enonce_markdown côté backend) - donner le
            niveau sans dévoiler l'épreuve ni compromettre les conditions d'examen. */}
        {epreuve.apercu_enonce_markdown && (
          <div className="border-t border-border pt-5">
            <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">Aperçu</h2>
            {epreuve.apercu_numero_exercice && !apercuDejaTitre && (
              <p className="mb-2 text-sm font-medium">Exercice {epreuve.apercu_numero_exercice}</p>
            )}
            <article className="prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display">
              <EpreuveMarkdown markdown={epreuve.apercu_enonce_markdown} />
            </article>
            <p className="mt-3 text-xs text-muted-foreground">
              Le reste de l'épreuve reste inédit jusqu'à ce que tu la commences.
            </p>
          </div>
        )}

        {epreuve.related_cours.length > 0 && (
          <div className="mt-2 border-t border-border pt-5">
            <h2 className="mb-3 font-display text-sm font-semibold text-muted-foreground">Cours associés</h2>
            <div className="flex flex-col gap-2">
              {epreuve.related_cours.map((cours) => (
                <Link
                  key={cours.id}
                  to={cours.has_access ? coursReaderPath(cours.slug) : coursDetailPath(cours.slug)}
                  className="flex items-center justify-between gap-2 rounded-lg border border-border px-3.5 py-2.5 text-sm transition-colors hover:border-primary/50 hover:bg-accent"
                >
                  <span className="flex items-center gap-2">
                    <GraduationCap className="size-4 text-primary" />
                    {cours.titre}
                  </span>
                  {cours.has_access ? (
                    <Unlock className="size-3.5 shrink-0 text-success" />
                  ) : (
                    <Lock className="size-3.5 shrink-0 text-muted-foreground" />
                  )}
                </Link>
              ))}
            </div>
          </div>
        )}

        {error && <p className="text-sm text-destructive">{error}</p>}

        <BackToTopBar links={[{ to: epreuvesListPath(country), label: "Retour au catalogue" }]} />
      </div>

      {/* Sur téléphone, l'action reste sous le pouce dès que son bloc d'origine a défilé hors
          de l'écran. Posée au-dessus de la barre d'onglets quand elle existe (sa hauteur est
          publiée dans --bottom-tab-bar par BottomTabBar, comptage à rebours compris). */}
      {!actionsVisibles && (
        <div className="fixed inset-x-0 bottom-[var(--bottom-tab-bar,0px)] z-30 border-t border-border bg-background/95 px-4 py-3 backdrop-blur sm:hidden">
          <div className="flex items-center gap-3">
            {!epreuve.has_access && !epreuve.est_vitrine && offre && (
              <span className="shrink-0 text-sm font-medium tabular-nums">{formatAmount(offre.effective_price)} FCFA</span>
            )}
            {boutonPrincipal("min-w-0 flex-1")}
          </div>
        </div>
      )}

      {epreuve.duree_minutes && (
        <DialogueModeExamen
          open={modeAConfirmer !== null}
          onOpenChange={(ouvert) => !ouvert && setModeAConfirmer(null)}
          dureeMinutes={epreuve.duree_minutes}
          papier={modeAConfirmer === "papier"}
          enCours={starting}
          onConfirmer={() => modeAConfirmer && lancer(modeAConfirmer)}
        />
      )}

      <Dialog open={confirmerRecommencer} onOpenChange={setConfirmerRecommencer}>
        <DialogContent>
          <DialogTitle>Recommencer à zéro ?</DialogTitle>
          <DialogDescription>
            Tu repars d'une copie vierge. Celle que tu as entamée reste dans ton historique, avec ce que tu y avais
            traité.
          </DialogDescription>
          <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button variant="outline" onClick={() => setConfirmerRecommencer(false)}>
              Garder ma copie
            </Button>
            <Button disabled={starting} onClick={() => handleStart({ nouvelle: true })}>
              {starting ? "Préparation..." : "Recommencer"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
