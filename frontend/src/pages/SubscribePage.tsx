import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { AideContextuelle, BoutonAide } from "@/components/guides/AideContextuelle"
import { AlertCircle, CheckCircle2, Gift, Loader2, ShieldCheck, Sparkles, User, XCircle, Zap } from "lucide-react"

import {
  checkPaymentStatus, initiatePayment, listCursus, listMyInscriptionsInedites, listPlans, listProfils,
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
import { Button } from "@/components/ui/button"
import { ErreurChargement } from "@/components/ErreurChargement"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { BienvenueAbonne } from "@/components/BienvenueAbonne"
import { BilanDePeriode } from "@/components/BilanDePeriode"
import { ContenuDebloque } from "@/components/ContenuDebloque"
import { ManualPaymentPanel } from "@/components/ManualPaymentPanel"
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

/** Le nom d'un plan : en français celui du serveur ; ailleurs, la formule unique « Jusqu'à l'Examen » est traduite. */
function nomPlan(plan: Plan): string {
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
  const profilId = profilParam ? Number(profilParam) : (user?.profil_actif?.id ?? undefined)
  const { country } = useCountry()

  const [cursus, setCursus] = useState<Cursus | null>(null)
  const [profilPrenom, setProfilPrenom] = useState<string | null>(null)
  const [plans, setPlans] = useState<Plan[]>([])
  // `plans` vide veut dire trois choses différentes : pas encore chargé, chargement en échec,
  // ou vraiment aucune offre. Sans ces deux états on affichait « Aucune offre disponible »
  // pendant le chargement ou après une coupure réseau, soit un faux verdict sur le catalogue.
  const [plansPrets, setPlansPrets] = useState(false)
  const [plansErreur, setPlansErreur] = useState(false)
  // Incrémenté par « Réessayer » pour relancer l'effet de chargement des offres.
  const [tentativePlans, setTentativePlans] = useState(0)
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null)
  const [phoneNumber, setPhoneNumber] = useState("")
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("CAMPAY")
  // Replié par défaut - voir la note sur CAMPAY_METHOD/MANUAL_METHODS ci-dessus.
  const [showManualOptions, setShowManualOptions] = useState(false)
  const [declaredPayment, setDeclaredPayment] = useState<ManualPayment | null>(null)
  const [phase, setPhase] = useState<PaymentPhase>("form")
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<number | null>(null)
  const queryClient = useQueryClient()
  // Campay coupé côté serveur (CAMPAY_ACTIVE=0) : seul le paiement manuel reste proposé,
  // directement déplié et présélectionné. `methode` est la méthode réellement affichée -
  // dérivée plutôt que corrigée dans un effet, pour ne jamais montrer Campay un instant.
  const { campayActif, pret: configPrete } = usePaymentConfig()
  const methode: PaymentMethod = !campayActif && paymentMethod === "CAMPAY" ? "ORANGE" : paymentMethod
  const optionsManuellesVisibles = !campayActif || showManualOptions

  useEffect(() => {
    trackEvent("abonnement_ouvert")
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
        },
      })
    }
  }, [isLoading, isAuthenticated, searchParams, navigate])

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
    listPlans(cursusId ? Number(cursusId) : undefined, profilId, true).then((data) => {
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
      const populaire = eligiblePlans.find((p) => p.duration_mode === "JUSQUA_EXAMEN")
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
  }, [cursusId, requireRepetiteur, dureeParam, profilId, tentativePlans])

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
      .then((profils) => {
        // Compte à un seul profil : pas de « pour <prénom> », l'achat ne peut viser personne d'autre.
        const nomme = profilParam || profils.length > 1
        setProfilPrenom(nomme ? (profils.find((p) => p.id === profilId)?.prenom ?? null) : null)
      })
      .catch(() => {
        // Simple confirmation visuelle (« pour Awa ») : l'achat reste possible sans elle.
      })
  }, [profilId, profilParam])

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current)
    }
  }, [])

  function pollTransaction(transactionId: number) {
    let attempts = 0
    pollRef.current = window.setInterval(async () => {
      attempts += 1
      try {
        const result = await checkPaymentStatus(transactionId)
        if (result.status !== "PENDING") {
          if (pollRef.current) window.clearInterval(pollRef.current)
          setPhase(result.status === "SUCCESSFUL" ? "success" : "failed")
          // Le bandeau « reprendre mon paiement » doit refléter ce résultat tout de suite.
          queryClient.invalidateQueries({ queryKey: ["paiement-a-reprendre"] })
          trackEvent(result.status === "SUCCESSFUL" ? "payment_succeeded" : "payment_failed", {
            cursus_id: cursusId ? Number(cursusId) : undefined,
          })
          return
        }
      } catch {
        // on continue de sonder, une erreur ponctuelle du reseau ne doit pas interrompre l'attente
      }
      if (attempts >= MAX_POLL_ATTEMPTS) {
        if (pollRef.current) window.clearInterval(pollRef.current)
        setPhase("timeout")
        trackEvent("payment_timeout", { cursus_id: cursusId ? Number(cursusId) : undefined })
      }
    }, 3000)
  }

  function cancelPending() {
    if (pollRef.current) {
      window.clearInterval(pollRef.current)
      pollRef.current = null
    }
    setPhase("form")
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!selectedPlanId) return

    setError(null)
    if (!/^6\d{8}$/.test(phoneNumber)) {
      setError(t("sb.erreur_numero"))
      return
    }

    setPhase("pending")
    const properties = { cursus_id: cursusId ? Number(cursusId) : undefined, plan_id: selectedPlanId }
    trackEvent("payment_initiated", properties)
    try {
      const response = await initiatePayment({ planId: selectedPlanId, phoneNumber, profilId })
      if (response.status === "FAILED") {
        setPhase("failed")
        trackEvent("payment_failed", properties)
        return
      }
      if (response.status === "SUCCESSFUL") {
        // Crédit parrainage suffisant pour couvrir tout le prix - jamais envoyé à
        // CamPay côté backend (voir TransactionManager.creer_couverte_par_credit),
        // donc rien à sonder ici non plus.
        setPhase("success")
        trackEvent("payment_succeeded", properties)
        return
      }
      pollTransaction(response.transaction_id)
    } catch (err) {
      setPhase("failed")
      setError(err instanceof ApiError ? err.message : t("sb.erreur_initie"))
      trackEvent("payment_failed", properties)
      // Contrairement à response.status === "FAILED" ci-dessus (échec métier déjà
      // remonté côté backend, voir payments/views.py._report_campay_error) : un rejet
      // de la promesse ici est inattendu (réseau, réponse invalide...) - jamais capturé
      // ailleurs, donc explicitement priorisé côté Sentry (voir l'audit UX, reco 5.1).
      Sentry.captureException(err, { tags: { critical_path: "payment" } })
      // Campay a peut-être été coupé depuis le chargement de la page : on relit l'état
      // pour que « Réessayer » ramène un formulaire déjà basculé sur le paiement manuel.
      queryClient.invalidateQueries({ queryKey: PAYMENT_CONFIG_KEY })
    }
  }

  const selectedPlan = plans.find((p) => p.id === selectedPlanId) ?? null

  // Remise appliquée automatiquement côté serveur (voir payments.views.initiate_payment)
  // pour un paiement Campay uniquement - recalculée ici à l'identique (min(prix, solde))
  // seulement pour l'affichage, jamais pour fixer un montant. Le paiement manuel
  // (ManualPaymentPanel) ne consomme pas ce crédit - voir sa portée volontairement
  // limitée côté backend - donc jamais montré comme réduisant son montant à déclarer.
  const creditDisponible = user?.credit_parrainage_disponible ?? 0
  const creditAppliqueSelection = selectedPlan ? Math.min(selectedPlan.effective_price, creditDisponible) : 0
  const netAPayerSelection = (selectedPlan?.effective_price ?? 0) - creditAppliqueSelection

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
  function renderPlanRecap(plan: Plan) {
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
          {plan.duration_mode === "JUSQUA_EXAMEN" && plan.effective_price < plan.price && (
            <span className="text-xs font-medium text-success">
              {t("sb.prix_enfant", { a: formatAmount(plan.price), b: formatAmount(plan.effective_price) })}
            </span>
          )}
        </span>
        <span className="shrink-0 font-display text-base font-semibold text-primary">
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
          </span>
        </span>
        <span className="font-display text-base font-semibold text-primary">
          {formatAmount(plan.effective_price)} FCFA
        </span>
      </label>
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
              {profilPrenom && (
                <p className="flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 px-3.5 py-2.5 text-sm font-medium">
                  <User className="size-4 shrink-0 text-primary" aria-hidden="true" />
                  {t("sb.paiement_pour", { prenom: profilPrenom })}
                </p>
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
                            <span className="text-sm font-semibold">{CAMPAY_METHOD.label}</span>
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

                    {!optionsManuellesVisibles ? (
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

                  <div className="flex flex-col gap-2.5">
                    <StepLabel n={2}>{t("sb.paiement")}</StepLabel>

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
                          />
                        </div>

                        {error && <p className="text-sm text-destructive">{error}</p>}

                        {selectedPlan && creditAppliqueSelection > 0 && (
                          <p className="text-xs text-muted-foreground">
                            {t("sb.credit_ligne", { prix: formatAmount(selectedPlan.effective_price), credit: formatAmount(creditAppliqueSelection) })}
                          </p>
                        )}
                        <Button type="submit" disabled={!selectedPlan} size="lg" className="w-full">
                          {selectedPlan ? t("sb.payer_montant", { montant: formatAmount(netAPayerSelection) }) : t("sb.payer")}
                        </Button>
                      </form>
                    ) : (
                      selectedPlan && (
                        <ManualPaymentPanel
                          plan={selectedPlan}
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
                              operator: methode,
                            })
                          }}
                        />
                      )
                    )}
                  </div>
                </>
              )}
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
              <p className="text-sm text-muted-foreground">
                {t("sb.confirme_texte", { phone: phoneNumber })}
              </p>
              {/* Pas « Annuler » : ce bouton n'annule rien côté opérateur, il arrête seulement
                  de sonder le statut sur cette page. Le dire évite qu'on croie sa demande
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
            </div>
          )}

          {phase === "timeout" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <AlertCircle className="size-10 text-warning" />
              <p className="font-display font-medium">{t("sb.timeout_titre")}</p>
              <p className="text-sm text-muted-foreground">
                {t("sb.timeout_texte")}
              </p>
              <Button variant="outline" onClick={() => setPhase("form")}>
                {t("erreur.reessayer")}
              </Button>
              {campayActif && (
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
              <Button asChild>
                {requireRepetiteur ? (
                  <Link to="/fiches">{t("sb.generer_fiche")}</Link>
                ) : (
                  <Link to={epreuvesListPath(country)}>{t("ed.retour_catalogue")}</Link>
                )}
              </Button>
            </div>
          )}

          {phase === "failed" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <XCircle className="size-10 text-destructive" />
              <p className="font-display font-medium">{t("sb.echec")}</p>
              {error && <p className="text-sm text-muted-foreground">{error}</p>}
              <Button variant="outline" onClick={() => setPhase("form")}>
                {t("erreur.reessayer")}
              </Button>
              {campayActif && (
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
        {t("sb.securise")}
      </p>
    </div>
  )
}
