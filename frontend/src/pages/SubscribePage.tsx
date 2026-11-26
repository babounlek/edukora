import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react"
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom"
import { AideContextuelle, BoutonAide } from "@/components/guides/AideContextuelle"
import { AlertCircle, CheckCircle2, Gift, Loader2, MessageCircle, ShieldCheck, Smartphone, Sparkles, User, XCircle, Zap } from "lucide-react"

import {
  checkPaymentStatus, getPaiementEnCours, initiatePayment, listCursus, listMyInscriptionsInedites, listMySubscriptions, listPlans,
  listProfils,
} from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cursus, ManualPayment, MobileMoneyOperator, Plan } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { useQueryClient } from "@tanstack/react-query"
import { trackEvent } from "@/lib/analytics"
import { Sentry } from "@/lib/sentry"
import { cn, formatAmount } from "@/lib/utils"
import { useSeo } from "@/lib/seo"
import { epreuvesListPath } from "@/lib/countryPath"
import { cheminRetourSur } from "@/lib/retourAchat"
import { PAYMENT_CONFIG_KEY, usePaymentConfig } from "@/lib/paymentConfig"
import { dateLimiteCampagne, nomCampagne } from "@/lib/campagne"
import { MOIS_PAR_DEFAUT, estAuMois, moisValides, prixTotal } from "@/lib/tarifs"
import { RecapDuree, SelecteurDuree } from "@/components/SelecteurDuree"
import { Button } from "@/components/ui/button"
import { CodeRevendeur } from "@/components/CodeRevendeur"
import { ErreurChargement } from "@/components/ErreurChargement"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { BienvenueAbonne } from "@/components/BienvenueAbonne"
import { BilanDePeriode } from "@/components/BilanDePeriode"
import { ContenuDebloque } from "@/components/ContenuDebloque"
import { InviteAvis } from "@/components/InviteAvis"
import { ManualPaymentPanel } from "@/components/ManualPaymentPanel"
import { LienAide } from "@/components/aide/LienAide"
import { lienContactAide } from "@/lib/aide/contact"
import { delaiVerificationPaiementAffiche } from "@/lib/delaiVerificationPaiement"
import { langueCourante, t, tn, useI18n } from "@/lib/i18n"
import { chiffresNumeroLocal } from "@/lib/telephone"

type PaymentPhase = "form" | "pending" | "success" | "failed" | "timeout" | "manual_submitted"
type PaymentMethod = "CAMPAY" | MobileMoneyOperator

// ~2 minutes à 3s d'intervalle - au-delà, on suppose que la confirmation opérateur
// bloque quelque part plutôt que de laisser un spinner tourner indéfiniment sans
// aucune échappatoire (source de tickets support : l'utilisateur ne sait pas s'il
// doit attendre, réessayer, ou si son argent est parti).
const MAX_POLL_ATTEMPTS = 40
const SONDAGE_RAPIDE_MS = 3000
// Passé ces deux minutes, la page ne s'arrête plus de regarder : elle sonde plus lentement pendant dix minutes de plus.
// Qui validait à 2 min 30 restait devant « prend plus de temps que prévu » jusqu'au rattrapage horaire du serveur
// (audit du tunnel de paiement, 2026-11-26).
const SONDAGE_LENT_MS = 10_000
const MAX_SONDAGES_LENTS = 60

/**
 * Le code à composer pour retrouver et valider une demande de paiement en attente, par opérateur : la demande
 * n'apparaît pas toujours d'elle-même sur le téléphone. Codes donnés par l'agrégateur avec chaque demande
 * (documentation du SDK CamPay) ; à corriger ici si un opérateur change le sien.
 */
const CODE_VALIDATION: Record<MobileMoneyOperator, string> = { MTN: "*126#", ORANGE: "#150*50#" }
const NOM_OPERATEUR: Record<MobileMoneyOperator, string> = { MTN: "MTN MoMo", ORANGE: "Orange Money" }

/** La demande envoyée au téléphone du payeur, telle que l'écran d'attente la décrit. */
interface DemandeEnAttente {
  transactionId: number
  operator: MobileMoneyOperator | ""
  montant: number
  /** Le serveur a rendu une demande déjà envoyée plutôt que d'en envoyer une deuxième. */
  dejaEnAttente: boolean
}

/** Les erreurs de paiement que le serveur nomme par un code : dites dans la langue de la page, jamais en texte technique. */
function messageErreurPaiement(err: unknown): string {
  if (!(err instanceof ApiError)) return t("sb.erreur_initie")
  if (err.code === "paiement_indisponible") return t("sb.err_indisponible")
  if (err.code === "numero_refuse") return t("sb.err_numero_refuse")
  if (err.code === "numero_invalide") return t("sb.erreur_numero")
  return err.message
}

/**
 * « Rien ne s'affiche sur ton téléphone ? » : le code à composer pour retrouver la demande et la valider. L'opérateur
 * vient de l'agrégateur ; tant qu'il ne l'a pas dit, les deux codes sont donnés. Sur un téléphone, un toucher compose
 * le code (le menu de l'opérateur seulement : rien n'est validé sans le code secret du payeur).
 */
function AideValidation({ operator }: { operator: MobileMoneyOperator | "" }) {
  const operateurs: MobileMoneyOperator[] = operator ? [operator] : ["MTN", "ORANGE"]
  return (
    <div className="w-full rounded-lg border border-border bg-muted/40 px-3.5 py-3 text-left text-sm">
      <p className="font-medium">{t("sb.ussd_titre")}</p>
      <p className="mt-1 text-muted-foreground">
        {operator
          ? t("sb.ussd_un", { code: CODE_VALIDATION[operator], operateur: NOM_OPERATEUR[operator] })
          : t("sb.ussd_deux", { mtn: CODE_VALIDATION.MTN, orange: CODE_VALIDATION.ORANGE })}
      </p>
      <div className="mt-2.5 flex flex-wrap gap-2 sm:hidden">
        {operateurs.map((op) => (
          <Button key={op} asChild variant="secondary" size="sm">
            <a href={`tel:${encodeURIComponent(CODE_VALIDATION[op])}`}>
              <Smartphone className="size-3.5" aria-hidden="true" />
              {t("sb.ussd_bouton", { code: CODE_VALIDATION[op], operateur: NOM_OPERATEUR[op] })}
            </a>
          </Button>
        ))}
      </div>
    </div>
  )
}

interface PaymentMethodOption {
  value: PaymentMethod
  label: string
  badgeClass: string
  content: ReactNode
}

// Couleurs de marque des opérateurs (pas des tokens du thème) : ce sont les seules
// couleurs de toute l'app qui doivent rester reconnaissables telles quelles - un
// utilisateur repère "orange = Orange Money" au premier coup d'oeil, un badge dans
// la couleur primaire de l'app casserait ce repère.
//
// Campay est isolé du reste (pas dans un tableau plat des 3 méthodes) : c'est le
// mode recommandé - activation immédiate, aucune vérification manuelle côté équipe -
// donc il occupe seul la carte visible par défaut. Orange/MTN restent le plan B pour
// qui n'arrive pas à payer avec Campay, repliés derrière un lien plutôt qu'affichés
// à poids égal (voir showManualOptions plus bas) : moins de paiements manuels à
// vérifier à la main, moins de choix à faire pour la majorité des visiteurs.
const CAMPAY_METHOD: PaymentMethodOption = {
  value: "CAMPAY",
  label: "Campay",
  badgeClass: "bg-primary text-primary-foreground",
  content: <Zap className="size-4" fill="currentColor" />,
}

const MANUAL_METHODS: PaymentMethodOption[] = [
  {
    value: "ORANGE",
    label: "Orange Money",
    badgeClass: "bg-[#FF7900] text-white",
    content: "OM",
  },
  {
    value: "MTN",
    label: "MTN MoMo",
    badgeClass: "bg-[#FFCC08] text-black",
    content: "MTN",
  },
]

/** Le nom d'un plan : « Abonnement au mois » pour la formule vendue ; en français celui du serveur pour le reste ; ailleurs, l'ancienne formule « Jusqu'à l'Examen » est traduite. */
function nomPlan(plan: Plan): string {
  if (plan.product_type === "ABONNEMENT" && plan.duration_mode === "MENSUEL") return t("sb.formule_mois")
  if (langueCourante() !== "fr" && plan.product_type === "ABONNEMENT" && plan.duration_mode === "JUSQUA_EXAMEN") return t("prix.formule")
  return plan.name
}

function StepLabel({ n, children }: { n: number; children: ReactNode }) {
  return (
    <div className="flex items-center gap-2">
      <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
        {n}
      </span>
      <Label className="text-sm">{children}</Label>
    </div>
  )
}

export function SubscribePage() {
  useI18n()
  useSeo({ title: t("sb.seo") })

  const [searchParams] = useSearchParams()
  const recapChoix = (useLocation().state as { recap?: string } | null)?.recap
  const cursusId = searchParams.get("cursus")
  // Garde-fou pour le CTA "Débloquer l'add-on Fiches" (voir FichesPage.tsx) -
  // ADDON_REPETITEUR est un product_type à part entière (pas un booléen sur un Plan
  // ABONNEMENT comme inclut_inedit), donc le filtre porte directement sur
  // product_type plutôt que sur un champ dédié. Seul point d'entrée qui affiche
  // encore cet add-on : le flux par défaut (sans `require`) ne propose plus jamais
  // que l'abonnement de base, qui inclut désormais toujours les épreuves inédites
  // (voir Plan.inclut_inedit, systématiquement vrai sur Jusqu'à l'Examen depuis la
  // grille à un seul palier) - il n'existe donc plus d'add-on Inédites séparé à
  // proposer ici.
  const requireRepetiteur = searchParams.get("require") === "repetiteur"
  // Formule déjà choisie sur la page Prix (nombre de jours, ou "examen" pour le
  // Pack Examen dont la durée n'est pas fixe) : la sélection arrive ici présélectionnée
  // sur CETTE formule. Sans ce relais, cliquer "Choisir Essentiel" atterrissait sur un
  // formulaire présélectionné sur une autre formule - le choix venait d'être fait, la
  // page suivante le perdait.
  const dureeParam = searchParams.get("duree")
  // Durée déjà choisie sur la page Tarifs (`?mois=5`) : le choix arrive ici présélectionné, jamais perdu.
  // `duree=examen` (anciens liens) vaut « tous les mois qui restent ».
  const moisParam = Number(searchParams.get("mois"))
  // Le contenu verrouillé qui a motivé l'achat (une épreuve inédite) : on y ramène l'élève
  // une fois abonné, au lieu de le laisser sur un diagnostic sans rapport. Voir retourAchat.ts.
  const retour = cheminRetourSur(searchParams.get("retour"))
  // L'enfant pour qui cet achat est fait ("Ajouter un enfant", AccesPage.tsx) -
  // absent pour l'immense majorité des achats (compte à un seul profil), relayé tel
  // quel à initiatePayment/declareManualPayment (voir payments.views._resoudre_profil).
  const profilParam = searchParams.get("profil")
  const navigate = useNavigate()
  const { isAuthenticated, isLoading, user } = useAuth()
  // Sans `profil=`, le serveur retombe sur le PREMIER profil du compte : un parent qui paie depuis le profil du
  // cadet abonnait l'aîné. Le profil actif est donc relayé par défaut (test élève 10-24, parent à deux enfants).
  // Un parent à plusieurs enfants peut changer ici l'enfant pour qui il paie (sélecteur ci-dessous) : sans lui, le
  // bouton « Continuer » de /tarifs abonnait le profil actif, souvent celui qui l'est déjà (audit du 2026-11-12).
  const [profilChoisi, setProfilChoisi] = useState<number | null>(null)
  const profilId = profilChoisi ?? (profilParam ? Number(profilParam) : (user?.profil_actif?.id ?? undefined))
  const { country } = useCountry()

  const [cursus, setCursus] = useState<Cursus | null>(null)
  const [profilPrenom, setProfilPrenom] = useState<string | null>(null)
  const [profils, setProfils] = useState<{ id: number; prenom: string }[]>([])
  const [plans, setPlans] = useState<Plan[]>([])
  // `plans` vide veut dire trois choses différentes : pas encore chargé, chargement en échec,
  // ou vraiment aucune offre. Sans ces deux états on affichait « Aucune offre disponible »
  // pendant le chargement ou après une coupure réseau, soit un faux verdict sur le catalogue.
  const [plansPrets, setPlansPrets] = useState(false)
  const [plansErreur, setPlansErreur] = useState(false)
  // Incrémenté par « Réessayer » pour relancer l'effet de chargement des offres.
  const [tentativePlans, setTentativePlans] = useState(0)
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null)
  // La fin de l'accès en cours de cet enfant sur ce cursus (un renouvellement) : les nouveaux mois s'y ajoutent.
  const [accesActuelJusqua, setAccesActuelJusqua] = useState<Date | null>(null)
  // Le nombre de mois que l'élève a choisi lui-même (null : il n'a encore rien touché, voir `mois` plus bas).
  const [moisChoisi, setMoisChoisi] = useState<number | null>(null)
  // Le lien porte déjà une durée (choisie sur /tarifs, ou « jusqu'à l'examen ») : l'écran la rappelle au lieu de la redemander.
  const dureeVenueDuLien = moisParam > 0 || dureeParam === "examen"
  const [choixDureeOuvert, setChoixDureeOuvert] = useState(false)
  const [phoneNumber, setPhoneNumber] = useState("")
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("CAMPAY")
  // Replié par défaut - voir la note sur CAMPAY_METHOD/MANUAL_METHODS ci-dessus.
  const [showManualOptions, setShowManualOptions] = useState(false)
  const [declaredPayment, setDeclaredPayment] = useState<ManualPayment | null>(null)
  const [phase, setPhase] = useState<PaymentPhase>("form")
  const [error, setError] = useState<string | null>(null)
  const [attente, setAttente] = useState<DemandeEnAttente | null>(null)
  const pollRef = useRef<number | null>(null)
  // Le sondage en cours : incrémenté pour abandonner le précédent (nouvelle demande, page quittée), y compris
  // la réponse d'une requête déjà partie.
  const sondageRef = useRef(0)
  // La phase lue depuis le sondage, qui court sur plusieurs rendus.
  const phaseRef = useRef<PaymentPhase>("form")
  phaseRef.current = phase
  const queryClient = useQueryClient()
  // Campay coupé côté serveur (CAMPAY_ACTIVE=0) : seul le paiement manuel reste proposé,
  // directement déplié et présélectionné. `methode` est la méthode réellement affichée -
  // dérivée plutôt que corrigée dans un effet, pour ne jamais montrer Campay un instant.
  const { campayActif, manuelActif, pret: configPrete } = usePaymentConfig()
  const methode: PaymentMethod = !campayActif && paymentMethod === "CAMPAY" ? "ORANGE" : paymentMethod
  const optionsManuellesVisibles = manuelActif && (!campayActif || showManualOptions)
  const aucunMoyen = !campayActif && !manuelActif

  useEffect(() => {
    // `cursus_id` : la relance de l'inscrit qui n'a pas payé (relances.inscrit_sans_paiement) y lit l'examen visé.
    trackEvent("abonnement_ouvert", { cursus_id: cursusId ? Number(cursusId) : undefined })
    // Une fois, à l'ouverture de l'écran : l'examen ne change pas sans changer de page.
  }, [])

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      // searchParams.toString() plutôt que reconstruire juste "cursus" à la main :
      // préserve aussi require=repetiteur au retour de connexion, sinon le filtre
      // ci-dessus se perdait silencieusement pour quiconque n'était pas déjà connecté.
      // `intent` : sans lui, l'élève arrive sur la connexion sans savoir pourquoi on la lui demande.
      // `replace` : sans lui, « retour » depuis la connexion retombait sur /abonnement, qui renvoyait
      // aussitôt vers la connexion - l'élève ne pouvait plus revenir à l'épreuve qu'en repartant de l'accueil.
      navigate("/connexion", {
        replace: true,
        state: {
          from: `/abonnement?${searchParams.toString()}`,
          intent: t("sb.intent"),
          // Le choix fait sur /tarifs (« BEPC · 3 mois · 6 000 FCFA »), s'il vient de là : voir PricingPage.
          recap: recapChoix,
        },
      })
    }
  }, [isLoading, isAuthenticated, searchParams, navigate, recapChoix])

  useEffect(() => {
    // Le numéro du compte peut être stocké avec l'indicatif : le champ attend les 9 chiffres locaux.
    if (user) setPhoneNumber(chiffresNumeroLocal(user.phone_number))
  }, [user])

  // Déjà abonné à ce cursus (typiquement : session expirée sur la fiche d'une épreuve, vue
  // comme verrouillée, puis reconnexion) : rien à acheter, on rend l'épreuve. Jamais sans
  // `retour` : un abonné qui ouvre /abonnement de lui-même veut peut-être prolonger.
  // N'écoute volontairement ni la phase ni le paiement : un achat qui vient d'aboutir ici
  // doit afficher son écran de bienvenue, pas être redirigé.
  useEffect(() => {
    if (isLoading || !isAuthenticated || !retour || !cursusId) return
    let annule = false
    listMyInscriptionsInedites()
      .then((inscriptions) => {
        if (annule) return
        if (inscriptions.some((i) => i.is_active && i.cursus.id === Number(cursusId))) {
          navigate(retour, { replace: true })
        }
      })
      .catch(() => {
        // Sans réponse on reste sur le formulaire : au pire l'abonné voit une offre qu'il a déjà.
      })
    return () => {
      annule = true
    }
  }, [isLoading, isAuthenticated, retour, cursusId, navigate])

  useEffect(() => {
    // Les réponses d'une page déjà quittée (changement de cursus, retour) ne doivent pas écraser la courante.
    let annule = false
    listPlans(cursusId ? Number(cursusId) : undefined).then((data) => {
      if (annule) return
      // require=repetiteur : ne garder que l'add-on Fiches, seul point d'entrée qui
      // le propose encore (voir FichesPage.tsx). Par défaut, l'abonnement de base
      // uniquement - un seul palier existe par cursus (Jusqu'à l'Examen), il inclut
      // toujours les épreuves inédites (voir Plan.inclut_inedit).
      const eligiblePlans = requireRepetiteur
        ? data.filter((p) => p.product_type === "ADDON_REPETITEUR")
        : data.filter((p) => p.product_type === "ABONNEMENT")
      setPlans(eligiblePlans)
      // À défaut de formule explicitement demandée (`duree`, voir plus haut),
      // présélectionne Jusqu'à l'Examen plutôt que la première de la liste (la moins
      // chère, `Plan.Meta.ordering` trie par prix croissant) - repli sur la première
      // pour require=repetiteur, qui n'a aucun palier JUSQUA_EXAMEN dans ses
      // résultats : sélectionne alors le palier le moins cher, décision volontaire
      // pour un add-on encore sans historique d'usage, cohérente avec "démarrer
      // petit" plutôt que pousser l'engagement le plus long d'emblée.
      const demande = dureeParam
        ? eligiblePlans.find((p) =>
            dureeParam === "examen"
              ? p.duration_mode === "JUSQUA_EXAMEN"
              : p.duration_mode === "FIXE" && p.duration_days === Number(dureeParam),
          )
        : undefined
      const populaire =
        eligiblePlans.find((p) => p.duration_mode === "MENSUEL") ??
        eligiblePlans.find((p) => p.duration_mode === "JUSQUA_EXAMEN")
      setSelectedPlanId((demande ?? populaire ?? eligiblePlans[0])?.id ?? null)
      setPlansPrets(true)
    }).catch(() => {
      if (annule) return
      setPlansErreur(true)
      setPlansPrets(true)
    })
    if (cursusId) {
      listCursus()
        .then((all) => {
          if (!annule) setCursus(all.find((c) => c.id === Number(cursusId)) ?? null)
        })
        .catch(() => {
          // Le cursus ne sert qu'au titre : sans lui la page garde son titre générique « S'abonner ».
        })
    }
    return () => {
      annule = true
    }
  }, [cursusId, requireRepetiteur, dureeParam, tentativePlans])

  // Seulement un confort d'affichage (la date de fin annoncée) : sans réponse, on part d'aujourd'hui.
  useEffect(() => {
    if (!isAuthenticated || !cursusId) return
    let annule = false
    listMySubscriptions()
      .then((abonnements) => {
        if (annule) return
        const courant = abonnements.find(
          (a) => a.is_active && a.cursus.id === Number(cursusId) && (profilId === undefined || a.profil.id === profilId),
        )
        setAccesActuelJusqua(courant ? new Date(courant.expires_at) : null)
      })
      .catch(() => {})
    return () => {
      annule = true
    }
  }, [isAuthenticated, cursusId, profilId])

  function reessayerPlans() {
    setPlansErreur(false)
    setPlansPrets(false)
    setTentativePlans((n) => n + 1)
  }

  // Confirmation visuelle qu'on achète pour le bon enfant ("Abonnement pour Awa") -
  // uniquement quand la page arrive avec un profil explicite (voir "Ajouter un
  // enfant", AccesPage.tsx) ; silencieux sinon, pas de requête en plus pour
  // l'immense majorité des achats.
  useEffect(() => {
    if (!profilId) return
    listProfils()
      .then((liste) => {
        setProfils(liste.map((p) => ({ id: p.id, prenom: p.prenom })))
        // Compte à un seul profil : pas de « pour <prénom> », l'achat ne peut viser personne d'autre.
        const nomme = profilParam || liste.length > 1
        setProfilPrenom(nomme ? (liste.find((p) => p.id === profilId)?.prenom ?? null) : null)
      })
      .catch(() => {
        // Simple confirmation visuelle (« pour Awa ») : l'achat reste possible sans elle.
      })
  }, [profilId, profilParam])

  function arreterSondage() {
    sondageRef.current += 1
    if (pollRef.current) {
      window.clearTimeout(pollRef.current)
      pollRef.current = null
    }
  }

  useEffect(() => arreterSondage, [])

  /**
   * Suit une demande jusqu'à son dénouement : toutes les 3 secondes pendant deux minutes, puis toutes les 10 secondes
   * pendant dix minutes. Le passage au rythme lent affiche « prend plus de temps que prévu » sans cesser de regarder.
   * Le sondage survit au retour sur le formulaire : un succès s'affiche où que soit le payeur (il a payé) ; un échec
   * ne s'affiche que s'il attendait encore, pour ne pas lui retirer le formulaire des mains.
   */
  function pollTransaction(transactionId: number) {
    arreterSondage()
    const moi = sondageRef.current
    const suivi = { cursus_id: cursusId ? Number(cursusId) : undefined }
    let attempts = 0
    const sonder = async () => {
      attempts += 1
      try {
        const result = await checkPaymentStatus(transactionId)
        if (sondageRef.current !== moi) return
        if (result.operator) {
          // L'opérateur n'est parfois connu qu'au premier statut : la consigne de l'écran d'attente se précise alors.
          const operator = result.operator
          setAttente((a) => (a && a.transactionId === transactionId && !a.operator ? { ...a, operator } : a))
        }
        if (result.status !== "PENDING") {
          pollRef.current = null
          const enAttente = phaseRef.current === "pending" || phaseRef.current === "timeout"
          if (result.status === "SUCCESSFUL") setPhase("success")
          else if (enAttente) setPhase("failed")
          // Le bandeau « reprendre mon paiement » doit refléter ce résultat tout de suite.
          queryClient.invalidateQueries({ queryKey: ["paiement-a-reprendre"] })
          trackEvent(result.status === "SUCCESSFUL" ? "payment_succeeded" : "payment_failed", suivi)
          return
        }
      } catch {
        // on continue de sonder, une erreur ponctuelle du reseau ne doit pas interrompre l'attente
        if (sondageRef.current !== moi) return
      }
      if (attempts === MAX_POLL_ATTEMPTS) {
        if (phaseRef.current === "pending") setPhase("timeout")
        trackEvent("payment_timeout", suivi)
      }
      if (attempts >= MAX_POLL_ATTEMPTS + MAX_SONDAGES_LENTS) {
        pollRef.current = null
        return
      }
      pollRef.current = window.setTimeout(sonder, attempts < MAX_POLL_ATTEMPTS ? SONDAGE_RAPIDE_MS : SONDAGE_LENT_MS)
    }
    pollRef.current = window.setTimeout(sonder, SONDAGE_RAPIDE_MS)
  }

  // Ne coupe pas le sondage : ce bouton n'annule rien chez l'opérateur, et qui a validé entre-temps doit voir son accès.
  function cancelPending() {
    setPhase("form")
  }

  function suivreDemande(response: { transaction_id: number; operator?: MobileMoneyOperator | ""; amount: number; deja_en_attente?: boolean }) {
    setAttente({
      transactionId: response.transaction_id,
      operator: response.operator || "",
      montant: response.amount,
      dejaEnAttente: Boolean(response.deja_en_attente),
    })
    setPhase("pending")
    pollTransaction(response.transaction_id)
  }

  // Écran rouvert ou rechargé pendant qu'une demande attend encore sur le téléphone : on reprend l'attente, au lieu de
  // présenter un formulaire vierge qui invite à payer une deuxième fois.
  useEffect(() => {
    if (!isAuthenticated || !configPrete || !campayActif) return
    let annule = false
    getPaiementEnCours(cursusId ? Number(cursusId) : undefined)
      .then((demande) => {
        if (annule || !demande?.en_cours || phaseRef.current !== "form") return
        if (demande.phone_number) setPhoneNumber(demande.phone_number)
        suivreDemande(demande)
      })
      .catch(() => {
        // Sans réponse on reste sur le formulaire : le serveur refuse de toute façon de doubler une demande en attente.
      })
    return () => {
      annule = true
    }
    // Une fois la session et les moyens de paiement connus ; `suivreDemande` ne dépend que de l'examen affiché.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, configPrete, campayActif, cursusId])

  /** `nouvelleDemande` : le payeur demande lui-même une demande neuve alors qu'une autre attend encore. */
  async function lancerPaiement(nouvelleDemande = false) {
    if (!selectedPlanId) return

    setError(null)
    if (!/^6\d{8}$/.test(phoneNumber)) {
      setError(t("sb.erreur_numero"))
      return
    }

    arreterSondage()
    setAttente(null)
    setPhase("pending")
    const properties = { cursus_id: cursusId ? Number(cursusId) : undefined, plan_id: selectedPlanId, mois }
    trackEvent("payment_initiated", properties)
    try {
      const response = await initiatePayment({ planId: selectedPlanId, phoneNumber, profilId, mois, nouvelleDemande })
      if (response.status === "FAILED") {
        setPhase("failed")
        trackEvent("payment_failed", properties)
        return
      }
      if (response.status === "SUCCESSFUL") {
        // Crédit parrainage suffisant pour couvrir tout le prix - jamais envoyé à
        // CamPay côté backend (voir TransactionManager.creer_couverte_par_credit),
        // donc rien à sonder ici non plus. Ou une demande précédente, validée entre-temps.
        setPhase("success")
        trackEvent("payment_succeeded", properties)
        return
      }
      suivreDemande(response)
    } catch (err) {
      const numeroEnCause = err instanceof ApiError && (err.code === "numero_refuse" || err.code === "numero_invalide")
      // Un numéro refusé se corrige dans le formulaire : on y revient, le message sous le champ.
      setPhase(numeroEnCause ? "form" : "failed")
      setError(messageErreurPaiement(err))
      trackEvent("payment_failed", properties)
      // Contrairement à response.status === "FAILED" ci-dessus (échec métier déjà
      // remonté côté backend, voir payments/views.py._report_campay_error) : un rejet
      // de la promesse ici est inattendu (réseau, réponse invalide...) - jamais capturé
      // ailleurs, donc explicitement priorisé côté Sentry (voir l'audit UX, reco 5.1).
      if (!numeroEnCause) Sentry.captureException(err, { tags: { critical_path: "payment" } })
      // Campay a peut-être été coupé depuis le chargement de la page : on relit l'état
      // pour que « Réessayer » ramène un formulaire déjà basculé sur le paiement manuel.
      queryClient.invalidateQueries({ queryKey: PAYMENT_CONFIG_KEY })
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void lancerPaiement()
  }

  const selectedPlan = plans.find((p) => p.id === selectedPlanId) ?? null

  // Le nombre de mois à payer : le choix de l'élève, sinon celui de la page Tarifs, sinon un trimestre - toujours
  // ramené à ce que le plan autorise (1 à mois_max : au-delà, l'examen serait déjà passé). Dérivé plutôt que stocké :
  // il suit le plan sélectionné et ne peut jamais sortir de la plage.
  const moisSouhaite =
    moisChoisi ?? (dureeParam === "examen" ? Number.POSITIVE_INFINITY : moisParam > 0 ? moisParam : MOIS_PAR_DEFAUT)
  const mois = selectedPlan ? moisValides(selectedPlan, moisSouhaite) : 1
  const totalSelection = selectedPlan ? prixTotal(selectedPlan, mois) : 0

  // Remise appliquée automatiquement côté serveur (voir payments.views.initiate_payment)
  // pour un paiement Campay uniquement - recalculée ici à l'identique (min(prix, solde))
  // seulement pour l'affichage, jamais pour fixer un montant. Le paiement manuel
  // (ManualPaymentPanel) ne consomme pas ce crédit - voir sa portée volontairement
  // limitée côté backend - donc jamais montré comme réduisant son montant à déclarer.
  const creditDisponible = user?.credit_parrainage_disponible ?? 0
  const creditAppliqueSelection = Math.min(totalSelection, creditDisponible)
  const netAPayerSelection = totalSelection - creditAppliqueSelection

  // Plan B proposé directement depuis l'écran d'échec / de délai dépassé : retour au
  // formulaire avec le paiement manuel déjà déplié, plutôt que de laisser l'élève
  // retrouver le petit lien « Des difficultés avec Campay ? ».
  function passerAuPaiementManuel() {
    setError(null)
    setShowManualOptions(true)
    setPaymentMethod("ORANGE")
    setPhase("form")
  }

  // Une seule offre à choisir : un bouton radio à valider ne servirait à rien, on montre
  // un récapitulatif (pour qui, quoi, combien) plutôt qu'un choix. Le choix par radio
  // reste pour plusieurs offres (ex. l'add-on Fiches).
  // Le choix de la durée (abonnement au mois) : voir SelecteurDuree, partagé avec la page Tarifs.
  function renderSelecteurDuree(plan: Plan) {
    function choisir(n: number) {
      if (n === mois) return
      setMoisChoisi(n)
      trackEvent("tarifs_duree_choisie", { mois: n, mois_max: plan.mois_max, cursus_id: cursusId ? Number(cursusId) : undefined })
    }
    return (
      <div key={plan.id} className="flex flex-col gap-4">
        <div>
          <p className="font-display font-medium">
            {profilPrenom ? t("sb.plan_pour", { plan: nomPlan(plan), prenom: profilPrenom }) : nomPlan(plan)}
          </p>
          <span className="flex items-center gap-1 text-xs font-medium text-gold-text">
            <Sparkles className="size-3" aria-hidden />
            {t("sb.tout_inclus")}
          </span>
        </div>
        {/* La durée a déjà été choisie sur la page des prix : on ne la redemande pas, on la rappelle, et un bouton
            rouvre le choix. Sur un téléphone, la grille des mois repoussait le numéro à créditer à plus de deux écrans
            du haut (audit du tunnel visiteur → abonné, 2026-11-21). Lien direct sans durée : le choix reste ouvert. */}
        {dureeVenueDuLien && !choixDureeOuvert ? (
          <>
            <RecapDuree plan={plan} mois={mois} accesActuelJusqua={accesActuelJusqua} />
            <Button type="button" variant="ghost" size="sm" className="-mt-2 self-start" onClick={() => setChoixDureeOuvert(true)}>
              {t("sb.changer_duree")}
            </Button>
          </>
        ) : (
          <SelecteurDuree plan={plan} mois={mois} onChoisir={choisir} accesActuelJusqua={accesActuelJusqua} />
        )}
      </div>
    )
  }

  function renderPlanRecap(plan: Plan) {
    if (estAuMois(plan)) return renderSelecteurDuree(plan)
    return (
      <div key={plan.id} className="flex items-center justify-between gap-3 rounded-xl border-2 border-primary bg-accent px-4 py-3.5 text-sm ring-1 ring-primary">
        <span className="flex flex-col gap-1">
          <span className="font-display font-medium">
            {profilPrenom ? t("sb.plan_pour", { plan: nomPlan(plan), prenom: profilPrenom }) : nomPlan(plan)}
          </span>
          {plan.duration_mode === "JUSQUA_EXAMEN" && (
            <span className="text-xs font-normal text-muted-foreground">
              {tn("sb.acces_jusqua", plan.effective_duration_days)}
            </span>
          )}
          {plan.inclut_inedit && (
            <span className="flex items-center gap-1 text-xs font-medium text-gold-text">
              <Sparkles className="size-3" />
              {t("ac.inedites_incluses")}
            </span>
          )}
          {plan.campagne && (
            <span className="text-xs font-medium text-success">
              {t("camp.prix_ligne", {
                nom: nomCampagne(plan.campagne),
                pct: plan.campagne.pourcentage,
                a: formatAmount(plan.prix_reference),
                b: formatAmount(plan.effective_price),
                date: dateLimiteCampagne(plan.campagne.fin),
              })}
            </span>
          )}
        </span>
        <span className="shrink-0 font-display text-base font-semibold text-primary">
          {plan.campagne && (
            <s className="mr-1.5 text-sm font-normal text-muted-foreground">{formatAmount(plan.prix_reference)}</s>
          )}
          {formatAmount(plan.effective_price)} FCFA
        </span>
      </div>
    )
  }

  function renderPlanOption(plan: Plan) {
    return (
      <label
        key={plan.id}
        className="flex cursor-pointer items-center justify-between rounded-xl border-2 border-input px-4 py-3.5 text-sm transition-all has-[:checked]:border-primary has-[:checked]:bg-accent has-[:checked]:ring-1 has-[:checked]:ring-primary"
      >
        <span className="flex items-center gap-2.5">
          <input
            type="radio"
            name="plan"
            checked={selectedPlanId === plan.id}
            onChange={() => setSelectedPlanId(plan.id)}
            className="accent-primary"
          />
          <span className="flex flex-col gap-1">
            <span className="font-display font-medium">{nomPlan(plan)}</span>
            {plan.duration_mode === "JUSQUA_EXAMEN" && (
              <span className="text-xs font-normal text-muted-foreground">
                {tn("sb.acces_jusqua", plan.effective_duration_days)}
              </span>
            )}
            {plan.inclut_inedit && (
              <span className="flex items-center gap-1 text-xs font-medium text-gold-text">
                <Sparkles className="size-3" />
                {t("ac.inedites_incluses")}
              </span>
            )}
            {plan.campagne && (
              <span className="text-xs font-medium text-success">
                {t("camp.prix_promo_jusqu_au", { date: dateLimiteCampagne(plan.campagne.fin) })}
              </span>
            )}
          </span>
        </span>
        <span className="font-display text-base font-semibold text-primary">
          {plan.campagne && (
            <s className="mr-1.5 text-sm font-normal text-muted-foreground">{formatAmount(plan.prix_reference)}</s>
          )}
          {formatAmount(plan.effective_price)} FCFA
        </span>
      </label>
    )
  }

  // Rien de cette page n'est monté tant que la session n'est pas établie. Ses blocs (code revendeur, moyens de
  // paiement manuel) appellent des routes réservées aux comptes : sans session, leur 401 faisait afficher
  // « Session expirée » à un visiteur qui n'en a jamais eu, juste avant l'écran de connexion où l'effet plus haut
  // l'envoie (vu chez trois visiteurs le 2026-11-21, au clic sur « Continuer » de /tarifs).
  if (!isAuthenticated) {
    if (!isLoading) return null
    return (
      <div className="mx-auto flex max-w-5xl justify-center px-4 py-24 sm:px-6">
        <Loader2 className="size-6 animate-spin text-primary" aria-label={t("sb.chargement_offre")} />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16">
      {/* Même gabarit de hero que /tarifs (voir PricingPage.tsx) : fond dégradé, trame
          de points discrète, halo doré décentré - cette page reste le point d'entrée
          d'un paiement réel, elle doit inspirer la même confiance que la page qui y
          mène. */}
      <div className="relative mb-8 animate-fade-up overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.08] via-transparent to-transparent p-6 text-center sm:p-8">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div
          className="pointer-events-none absolute -right-16 -top-16 size-56 rounded-full bg-gold/10 blur-3xl"
          aria-hidden
        />
        <div className="relative">
          <div className="mx-auto mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Sparkles className="size-5" />
          </div>
          <p className="mb-1 font-display text-sm italic text-primary">
            {profilPrenom ? t("sb.abonnement_pour", { prenom: profilPrenom }) : t("sb.seo")}
          </p>
          <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
            {cursus
              ? `${cursus.examen_display}${cursus.series ? ` - ${t("prix.serie", { code: cursus.series.code })}` : ""}`
              : t("prix.sabonner")}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">
            {requireRepetiteur
              ? t("sb.sous_titre_fiches")
              : t("sb.sous_titre")}
          </p>
        </div>
      </div>

      {/* Aide à la demande seulement (guide « paiement » : jamais automatique dans un tunnel de paiement). */}
      <div className="mb-4">
        <BoutonAide guide="paiement" className="-ml-2.5" />
        <AideContextuelle guide="paiement" className="mt-1" />
      </div>

      {/* Renouvellement : ce que l'abonnement a déjà apporté, juste avant de repayer. Silencieux
          pour un premier achat (404) ou sans activité. */}
      {phase === "form" && cursus && <BilanDePeriode cursusId={cursus.id} className="mb-6" />}

      {/* Deux colonnes dès `lg` pour le formulaire : l'offre (récapitulatif, collé en haut au
          défilement) à droite, le paiement à gauche. Sous `lg`, une seule colonne avec l'offre
          d'abord (ordre du DOM), comme avant. Les autres phases (attente, succès, échec...) restent
          une colonne étroite centrée : rien à comparer, juste un message. */}
      <div className={cn("grid gap-6", phase === "form" && "lg:grid-cols-[minmax(0,1fr)_24rem] lg:items-start")}>
        {phase === "form" && (
          <div className="flex flex-col gap-6 lg:sticky lg:top-24 lg:col-start-2 lg:row-start-1">
          <Card className="animate-fade-up overflow-hidden shadow-lg shadow-primary/5">
            <div className="h-1 bg-gradient-to-r from-gold via-primary to-gold" aria-hidden />
            <CardContent className="flex flex-col gap-2.5 p-6">
              <Label className="text-sm font-semibold">{t("sb.ton_offre")}</Label>
              {!plansPrets ? (
                <div className="flex flex-col gap-2" aria-busy="true" aria-label={t("sb.chargement_offre")}>
                  <div className="h-16 w-full animate-pulse rounded-xl bg-muted" />
                </div>
              ) : plansErreur ? (
                <ErreurChargement compact objet={t("sb.objet_offre")} onRetry={reessayerPlans} />
              ) : (
                <div className="flex flex-col gap-2">
                  {plans.length === 1 ? renderPlanRecap(plans[0]) : plans.map(renderPlanOption)}
                  {plans.length > 1 && selectedPlan && estAuMois(selectedPlan) && renderSelecteurDuree(selectedPlan)}
                  {plans.length === 0 && (
                    <p className="text-sm text-muted-foreground">
                      {requireRepetiteur
                        ? t("sb.fiches_indisponible")
                        : t("sb.aucune_offre")}
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
          {cursus && !requireRepetiteur && (
            <ContenuDebloque
              cursusId={cursus.id}
              inclutInedit={plans.find((p) => p.id === selectedPlanId)?.inclut_inedit ?? false}
            />
          )}
          </div>
        )}

      <Card
        className={cn(
          "animate-fade-up overflow-hidden shadow-lg shadow-primary/5",
          phase === "form" ? "lg:col-start-1 lg:row-start-1" : "mx-auto w-full max-w-lg",
        )}
      >
        <div className="h-1 bg-gradient-to-r from-gold via-primary to-gold" aria-hidden />
        <CardContent className="p-6 sm:p-7">
          {phase === "form" && (
            <div className="flex flex-col gap-6">
              {/* Pour qui l'argent part : rappelé AU-DESSUS du formulaire de paiement, là où l'on décide de payer, et pas
                  seulement dans l'en-tête de la page (test élève 2026-10-24, parent de deux enfants). */}
              {profils.length > 1 ? (
                <div role="radiogroup" aria-label={t("sb.choisir_enfant")} className="flex flex-col gap-2 rounded-lg border border-primary/30 bg-primary/5 px-3.5 py-2.5">
                  <p className="flex items-center gap-2 text-sm font-medium">
                    <User className="size-4 shrink-0 text-primary" aria-hidden="true" />
                    {t("sb.choisir_enfant")}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {profils.map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        role="radio"
                        aria-checked={p.id === profilId}
                        onClick={() => setProfilChoisi(p.id)}
                        className={cn(
                          "min-h-10 rounded-full border px-4 text-sm font-medium transition-colors",
                          p.id === profilId
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-border bg-background hover:border-primary/50",
                        )}
                      >
                        {p.prenom}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                profilPrenom && (
                  <p className="flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 px-3.5 py-2.5 text-sm font-medium">
                    <User className="size-4 shrink-0 text-primary" aria-hidden="true" />
                    {t("sb.paiement_pour", { prenom: profilPrenom })}
                  </p>
                )
              )}
              {campayActif && creditDisponible > 0 && (
                <div className="flex items-center gap-2.5 rounded-lg border border-gold/30 bg-gold/[0.06] px-3.5 py-2.5 text-sm">
                  <Gift className="size-4 shrink-0 text-gold-text" />
                  <span>
                    {t("sb.credit_avant")} <strong className="text-foreground">{formatAmount(creditDisponible)} FCFA</strong>{" "}
                    {t("sb.credit_apres")}
                  </span>
                </div>
              )}

              {!configPrete ? (
                <Loader2 className="mx-auto size-6 animate-spin text-primary" aria-label={t("sb.chargement_moyens")} />
              ) : (
                <>
                  {/* Un seul moyen proposé (la demande sur le téléphone) : pas d'étape « choisis ton moyen » à option
                      unique, ni de carte au nom du prestataire, inconnu de qui paie. Les deux opérateurs acceptés,
                      et ce qui va se passer. */}
                  {campayActif && !manuelActif ? (
                    <div className="flex items-start gap-3">
                      <span className="mt-0.5 flex shrink-0 -space-x-1.5">
                        {MANUAL_METHODS.map((method) => (
                          <span
                            key={method.value}
                            className={cn("flex size-8 items-center justify-center rounded-full text-[0.65rem] font-bold ring-2 ring-card", method.badgeClass)}
                            aria-hidden="true"
                          >
                            {method.content}
                          </span>
                        ))}
                      </span>
                      <span className="flex flex-col gap-0.5">
                        <span className="text-sm font-semibold">{t("sb.direct_seul_titre")}</span>
                        <span className="text-xs text-muted-foreground">{t("sb.direct_seul_texte")}</span>
                      </span>
                    </div>
                  ) : (
                  <div className="flex flex-col gap-2.5">
                    <StepLabel n={1}>{t("sb.moyen")}</StepLabel>

                    {campayActif && (
                      <label
                        className={cn(
                          "flex cursor-pointer items-start gap-3 rounded-xl border-2 px-4 py-3.5 transition-all",
                          methode === "CAMPAY" ? "border-primary bg-accent ring-1 ring-primary" : "border-input",
                        )}
                      >
                        <input
                          type="radio"
                          name="payment-method"
                          checked={methode === "CAMPAY"}
                          onChange={() => setPaymentMethod("CAMPAY")}
                          className="sr-only"
                        />
                        <span
                          className={cn(
                            "mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-full text-xs font-bold",
                            CAMPAY_METHOD.badgeClass,
                          )}
                        >
                          {CAMPAY_METHOD.content}
                        </span>
                        <span className="flex flex-col gap-0.5">
                          <span className="flex items-center gap-1.5">
                            <span className="text-sm font-semibold">{t("sb.direct_label")}</span>
                            <span className="rounded-full bg-success/15 px-1.5 py-0.5 text-xs font-semibold uppercase tracking-wide text-success">
                              {t("sb.recommande")}
                            </span>
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {t("sb.campay_texte")}
                          </span>
                        </span>
                      </label>
                    )}

                    {aucunMoyen ? (
                      <p className="text-sm text-muted-foreground">{t("sb.aucun_moyen")}</p>
                    ) : !manuelActif ? null : !optionsManuellesVisibles ? (
                      <button
                        type="button"
                        onClick={() => setShowManualOptions(true)}
                        className="min-h-11 self-start text-left text-xs text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
                      >
                        {t("sb.difficultes")}
                      </button>
                    ) : (
                      <div className="flex flex-col gap-2.5 rounded-lg border border-dashed border-input p-3">
                        <p className="text-xs text-muted-foreground">
                          {!campayActif && t("sb.auto_indisponible")}
                          {t("sb.manuel_info", { delai: delaiVerificationPaiementAffiche() })}
                        </p>
                        <div className="grid grid-cols-2 gap-2">
                          {MANUAL_METHODS.map((method) => (
                            <label
                              key={method.value}
                              className="flex cursor-pointer items-center gap-2.5 rounded-xl border border-input px-3 py-2.5 transition-all has-[:checked]:border-primary has-[:checked]:bg-accent has-[:checked]:ring-1 has-[:checked]:ring-primary"
                            >
                              <input
                                type="radio"
                                name="payment-method"
                                checked={methode === method.value}
                                onChange={() => setPaymentMethod(method.value)}
                                className="sr-only"
                              />
                              <span
                                className={cn(
                                  "flex size-8 shrink-0 items-center justify-center rounded-full text-xs font-bold",
                                  method.badgeClass,
                                )}
                              >
                                {method.content}
                              </span>
                              <span className="text-xs font-semibold leading-tight">{method.label}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  )}

                  {!aucunMoyen && (
                  <div className="flex flex-col gap-2.5">
                    {!(campayActif && !manuelActif) && <StepLabel n={2}>{t("sb.paiement")}</StepLabel>}

                    {methode === "CAMPAY" ? (
                      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                        <div className="flex flex-col gap-2">
                          <Label htmlFor="momo-phone">{t("sb.numero_momo")}</Label>
                          <Input
                            id="momo-phone"
                            inputMode="numeric"
                            placeholder="677123456"
                            value={phoneNumber}
                            // Pas de maxLength : il tronquait un collage « +237 6… » ; le helper
                            // retire l'indicatif et ramène à 9 chiffres.
                            onChange={(e) => setPhoneNumber(chiffresNumeroLocal(e.target.value))}
                            type="tel"
                            autoComplete="tel-national"
                            aria-describedby="momo-phone-aide"
                          />
                          <p id="momo-phone-aide" className="text-xs text-muted-foreground">{t("sb.numero_aide")}</p>
                        </div>

                        {error && <p role="alert" className="text-sm text-destructive">{error}</p>}

                        {selectedPlan && creditAppliqueSelection > 0 && (
                          <p className="text-xs text-muted-foreground">
                            {t("sb.credit_ligne", { prix: formatAmount(totalSelection), credit: formatAmount(creditAppliqueSelection) })}
                          </p>
                        )}
                        <Button type="submit" disabled={!selectedPlan} size="lg" className="w-full">
                          {selectedPlan ? t("sb.payer_montant", { montant: formatAmount(netAPayerSelection) }) : t("sb.payer")}
                        </Button>
                        {selectedPlan?.campagne && (
                          <p className="text-center text-xs font-medium text-success">
                            {t("camp.prix_promo_jusqu_au", { date: dateLimiteCampagne(selectedPlan.campagne.fin) })}
                          </p>
                        )}
                      </form>
                    ) : (
                      selectedPlan && (
                        <ManualPaymentPanel
                          plan={selectedPlan}
                          mois={mois}
                          montant={totalSelection}
                          operator={methode}
                          profilId={profilId}
                          defaultPayerPhone={phoneNumber}
                          onDeclared={(payment) => {
                            setDeclaredPayment(payment)
                            setPhase("manual_submitted")
                            // Pas d'évènement dédié côté vocabulaire fermé (voir analytics.models.EventName) -
                            // une déclaration manuelle est la même intention qu'un paiement Campay initié,
                            // juste sur un autre canal (voir `operator` dans les properties pour les distinguer).
                            trackEvent("payment_initiated", {
                              cursus_id: cursusId ? Number(cursusId) : undefined,
                              plan_id: selectedPlan.id,
                              mois,
                              operator: methode,
                            })
                          }}
                        />
                      )
                    )}
                  </div>
                  )}
                </>
              )}

              {/* Le code revendeur vient APRÈS le paiement : facultatif, il passait avant le numéro à créditer et le
                  repoussait d'autant sur un téléphone. Il reste valable tant que le paiement n'est pas validé. */}
              <CodeRevendeur />
            </div>
          )}

          {phase === "manual_submitted" && declaredPayment && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <CheckCircle2 className="size-10 text-success" />
              <p className="font-display font-medium">{t("sb.declaration_titre")}</p>
              {profilPrenom && <p className="text-sm font-medium">{t("sb.paiement_pour", { prenom: profilPrenom })}</p>}
              <p className="text-sm text-muted-foreground">
                {t("sb.declaration_texte", { delai: delaiVerificationPaiementAffiche(), id: declaredPayment.id })}
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                <Button asChild>
                  <Link to="/mes-paiements">{t("sb.suivre")}</Link>
                </Button>
                <Button asChild variant="outline">
                  <Link to={epreuvesListPath(country)}>{t("ed.retour_catalogue")}</Link>
                </Button>
              </div>
            </div>
          )}

          {phase === "pending" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <Loader2 className="size-8 animate-spin text-primary" />
              <p className="font-display font-medium">{t("sb.confirme")}</p>
              {profilPrenom && <p className="text-sm font-medium">{t("sb.paiement_pour", { prenom: profilPrenom })}</p>}
              {/* Une demande précédente attend encore sur ce numéro : le serveur l'a rendue au lieu d'en envoyer une
                  deuxième. Le dire, sinon le payeur attend une demande neuve qui ne viendra pas. */}
              {attente?.dejaEnAttente && (
                <p role="status" className="w-full rounded-lg border border-warning/40 bg-warning/10 px-3.5 py-2.5 text-left text-sm">
                  {t("sb.deja_attente")}
                </p>
              )}
              <p className="text-sm text-muted-foreground">
                {attente
                  ? t("sb.confirme_texte", { phone: phoneNumber, montant: formatAmount(attente.montant) })
                  : t("sb.envoi_demande", { phone: phoneNumber })}
              </p>
              {attente && <AideValidation operator={attente.operator} />}
              {/* Pas « Annuler » : ce bouton n'annule rien côté opérateur. Le dire évite qu'on croie sa demande
                  retirée, puis qu'on repaie une deuxième fois. */}
              <button
                type="button"
                onClick={cancelPending}
                className="min-h-11 text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
              >
                {t("sb.revenir_formulaire")}
              </button>
              <p className="text-xs text-muted-foreground">
                {t("sb.deja_valide")}
              </p>
              {attente?.dejaEnAttente && (
                <div className="flex flex-col items-center gap-1 border-t border-border/60 pt-3">
                  <Button type="button" variant="outline" size="sm" onClick={() => void lancerPaiement(true)}>
                    {t("sb.nouvelle_demande")}
                  </Button>
                  <p className="text-xs text-muted-foreground">{t("sb.nouvelle_demande_aide")}</p>
                </div>
              )}
            </div>
          )}

          {phase === "timeout" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <AlertCircle className="size-10 text-warning" />
              <p className="font-display font-medium">{t("sb.timeout_titre")}</p>
              <p className="text-sm text-muted-foreground">
                {t("sb.timeout_texte")}
              </p>
              {attente && <AideValidation operator={attente.operator} />}
              <Button variant="outline" onClick={() => setPhase("form")}>
                {t("erreur.reessayer")}
              </Button>
              {campayActif && manuelActif && (
                <button
                  type="button"
                  onClick={passerAuPaiementManuel}
                  className="min-h-11 text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
                >
                  {t("sb.payer_manuel")}
                </button>
              )}
            </div>
          )}

          {/* Un abonnement de base, pas un add-on : l'accueil guide vers le diagnostic. */}
          {phase === "success" && cursus && plans.find((p) => p.id === selectedPlanId)?.product_type === "ABONNEMENT" && (
            <BienvenueAbonne
              cursusId={cursus.id}
              country={country}
              inclutInedit={Boolean(plans.find((p) => p.id === selectedPlanId)?.inclut_inedit)}
              retour={retour}
            />
          )}

          {phase === "success" && !(cursus && plans.find((p) => p.id === selectedPlanId)?.product_type === "ABONNEMENT") && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <CheckCircle2 className="size-10 text-success" />
              <p className="font-display font-medium">
                {requireRepetiteur ? t("sb.fiches_active") : t("sb.abonnement_active")}
              </p>
              {/* Plus de lien vers /fiches : la page des fiches est en veille (la route redirige vers l'accueil,
                  voir App.tsx), le bouton « Générer une fiche » menait donc nulle part. */}
              <Button asChild>
                <Link to={epreuvesListPath(country)}>{t("ed.retour_catalogue")}</Link>
              </Button>
            </div>
          )}

          {/* L'avis du parent, quand le compte a déjà servi (trois quiz terminés, le serveur en décide) : un premier
              paiement n'y a donc pas droit, et l'accueil du nouvel abonné reste seul à l'écran. Voir InviteAvis. */}
          {phase === "success" && <InviteAvis role="parent" className="mt-2 text-left" />}

          {phase === "failed" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <XCircle className="size-10 text-destructive" />
              <p className="font-display font-medium">{t("sb.echec")}</p>
              {/* Jamais un titre seul : soit le serveur dit ce qui s'est passé, soit l'opérateur a refusé sans dire
                  pourquoi, et l'on donne les trois causes qui expliquent presque tous les refus. */}
              {error ? (
                <p className="text-sm text-muted-foreground">{error}</p>
              ) : (
                <div className="w-full rounded-lg border border-border bg-muted/40 px-3.5 py-3 text-left text-sm">
                  <p className="font-medium">{t("sb.echec_verifs_titre")}</p>
                  <ul className="mt-1 list-disc space-y-0.5 pl-5 text-muted-foreground">
                    <li>{t("sb.echec_solde", { montant: formatAmount(attente?.montant ?? netAPayerSelection) })}</li>
                    <li>{t("sb.echec_code")}</li>
                    <li>{t("sb.echec_delai")}</li>
                  </ul>
                  <p className="mt-2 text-xs text-muted-foreground">{t("sb.echec_rien_debite")}</p>
                </div>
              )}
              <Button onClick={() => setPhase("form")}>
                {t("erreur.reessayer")}
              </Button>
              {/* Le paiement manuel peut être coupé : sans cette porte, l'écran d'échec n'offrait que « Réessayer ». */}
              <Button asChild variant="outline" size="sm">
                <a href={lienContactAide({ page: "/abonnement" })} target="_blank" rel="noopener noreferrer">
                  <MessageCircle className="size-3.5" aria-hidden="true" />
                  {t("aide.contact.bouton")}
                </a>
              </Button>
              <LienAide slug="paiement-refuse">{t("aide.lien.refuse")}</LienAide>
              {campayActif && manuelActif && (
                <button
                  type="button"
                  onClick={passerAuPaiementManuel}
                  className="min-h-11 text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
                >
                  {t("sb.payer_manuel")}
                </button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
      </div>

      <p className="mt-6 flex items-center justify-center gap-1.5 text-center text-xs text-muted-foreground">
        <ShieldCheck className="size-3.5 shrink-0" />
        {/* Une seule phrase sur le délai, celle du mode réellement choisi : « dès la confirmation » sous un transfert
            vérifié à la main contredisait « sous 3 heures », écrit plus haut sur le même écran. */}
        {methode === "CAMPAY" ? t("sb.securise") : t("sb.securise_manuel", { delai: delaiVerificationPaiementAffiche() })}
      </p>
    </div>
  )
}
