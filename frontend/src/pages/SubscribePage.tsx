import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { AlertCircle, CheckCircle2, Gift, Loader2, ShieldCheck, XCircle, Zap } from "lucide-react"

import { checkPaymentStatus, initiatePayment, listCursus, listPlans } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cursus, ManualPayment, MobileMoneyOperator, Plan } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { trackEvent } from "@/lib/analytics"
import { Sentry } from "@/lib/sentry"
import { cn, formatAmount } from "@/lib/utils"
import { useSeo } from "@/lib/seo"
import { epreuvesListPath } from "@/lib/countryPath"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { ManualPaymentPanel } from "@/components/ManualPaymentPanel"

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

function StepLabel({ n, children }: { n: number; children: ReactNode }) {
  return (
    <div className="flex items-center gap-2">
      <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-primary text-[11px] font-semibold text-primary-foreground">
        {n}
      </span>
      <Label className="text-sm">{children}</Label>
    </div>
  )
}

export function SubscribePage() {
  useSeo({ title: "Abonnement" })

  const [searchParams] = useSearchParams()
  const cursusId = searchParams.get("cursus")
  // Signal porté par le CTA "Débloquer avec Max" (voir EpreuveInediteDetailPage.tsx) :
  // ne montrer QUE les formules qui débloquent réellement l'add-on Épreuves Inédites -
  // sans ça, rien n'empêchait de repartir avec Essentiel/Performance depuis ce CTA et
  // de ne toujours pas avoir ce qu'on est venu chercher.
  const requireInedit = searchParams.get("require") === "inedit"
  // Même garde-fou que requireInedit, pour le CTA "Débloquer l'add-on Fiches" (voir
  // FichesPage.tsx) - ADDON_REPETITEUR est un product_type à part entière (pas un
  // booléen sur un Plan ABONNEMENT comme inclut_inedit), donc le filtre porte
  // directement sur product_type plutôt que sur un champ dédié.
  const requireRepetiteur = searchParams.get("require") === "repetiteur"
  // Formule déjà choisie sur la page Tarifs (nombre de jours, ou "examen" pour le
  // Pack Examen dont la durée n'est pas fixe) : la sélection arrive ici présélectionnée
  // sur CETTE formule. Sans ce relais, cliquer "Choisir Essentiel" atterrissait sur un
  // formulaire présélectionné sur une autre formule - le choix venait d'être fait, la
  // page suivante le perdait.
  const dureeParam = searchParams.get("duree")
  const navigate = useNavigate()
  const { isAuthenticated, isLoading, user } = useAuth()
  const { country } = useCountry()

  const [cursus, setCursus] = useState<Cursus | null>(null)
  const [plans, setPlans] = useState<Plan[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null)
  const [phoneNumber, setPhoneNumber] = useState("")
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("CAMPAY")
  // Replié par défaut - voir la note sur CAMPAY_METHOD/MANUAL_METHODS ci-dessus.
  const [showManualOptions, setShowManualOptions] = useState(false)
  const [declaredPayment, setDeclaredPayment] = useState<ManualPayment | null>(null)
  const [phase, setPhase] = useState<PaymentPhase>("form")
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      // searchParams.toString() plutôt que reconstruire juste "cursus" à la main :
      // préserve aussi require=inedit au retour de connexion, sinon le filtre ci-dessus
      // se perdait silencieusement pour quiconque n'était pas déjà connecté.
      navigate("/connexion", { state: { from: `/abonnement?${searchParams.toString()}` } })
    }
  }, [isLoading, isAuthenticated, searchParams, navigate])

  useEffect(() => {
    if (user) setPhoneNumber(user.phone_number)
  }, [user])

  useEffect(() => {
    listPlans(cursusId ? Number(cursusId) : undefined).then((data) => {
      // require=inedit/require=repetiteur : ne garder que les formules qui débloquent
      // réellement ce qu'on est venu chercher - impossible de repartir avec une
      // formule qui n'active pas l'add-on visé par le CTA d'origine.
      let eligiblePlans = data
      if (requireInedit) eligiblePlans = data.filter((p) => p.inclut_inedit)
      else if (requireRepetiteur) eligiblePlans = data.filter((p) => p.product_type === "ADDON_REPETITEUR")
      setPlans(eligiblePlans)
      // À défaut de formule explicitement demandée (`duree`, voir plus haut),
      // présélectionne la formule la plus populaire (Jusqu'à l'Examen - même
      // convention que la mise en avant ⭐ sur PricingPage, grille à 2 paliers du
      // 2026-08-19) plutôt que la première de la liste (la moins chère,
      // `Plan.Meta.ordering` trie par prix croissant) - repli sur la première.
      // Recherche restreinte aux Plan ABONNEMENT : un visiteur non filtré (ex. "Se
      // réabonner", qui ne passe aucun `require`) ne doit jamais se retrouver avec
      // l'add-on Fiches présélectionné par défaut simplement parce qu'il matche aussi
      // JUSQUA_EXAMEN. Repli sur le premier plan tous types confondus - pour
      // require=repetiteur, qui n'a lui aucun Plan ABONNEMENT dans ses résultats, ça
      // sélectionne le palier le moins cher plutôt que l'engagement le plus long :
      // décision volontaire pour un add-on encore sans historique d'usage, cohérente
      // avec "démarrer petit" plutôt que pousser l'engagement le plus long d'emblée.
      const abonnementEligibles = eligiblePlans.filter((p) => p.product_type === "ABONNEMENT")
      const demande = dureeParam
        ? abonnementEligibles.find((p) =>
            dureeParam === "examen"
              ? p.duration_mode === "JUSQUA_EXAMEN"
              : p.duration_mode === "FIXE" && p.duration_days === Number(dureeParam),
          )
        : undefined
      const populaire = abonnementEligibles.find((p) => p.duration_mode === "JUSQUA_EXAMEN")
      setSelectedPlanId((demande ?? populaire ?? abonnementEligibles[0] ?? eligiblePlans[0])?.id ?? null)
    })
    if (cursusId) {
      listCursus().then((all) => {
        setCursus(all.find((c) => c.id === Number(cursusId)) ?? null)
      })
    }
  }, [cursusId, requireInedit, requireRepetiteur, dureeParam])

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
      setError("Entrez un numéro Mobile Money valide (9 chiffres, commence par 6).")
      return
    }

    setPhase("pending")
    const properties = { cursus_id: cursusId ? Number(cursusId) : undefined, plan_id: selectedPlanId }
    trackEvent("payment_initiated", properties)
    try {
      const response = await initiatePayment({ planId: selectedPlanId, phoneNumber })
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
      setError(err instanceof ApiError ? err.message : "Le paiement n'a pas pu être initié.")
      trackEvent("payment_failed", properties)
      // Contrairement à response.status === "FAILED" ci-dessus (échec métier déjà
      // remonté côté backend, voir payments/views.py._report_campay_error) : un rejet
      // de la promesse ici est inattendu (réseau, réponse invalide...) - jamais capturé
      // ailleurs, donc explicitement priorisé côté Sentry (voir l'audit UX, reco 5.1).
      Sentry.captureException(err, { tags: { critical_path: "payment" } })
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

  // Groupé par product_type plutôt qu'affiché en une liste plate - même hors des cas
  // filtrés (requireInedit/requireRepetiteur), un cursus peut avoir à la fois des Plan
  // ABONNEMENT et ADDON_REPETITEUR (voir l'audit qui a motivé ce chantier : la plupart
  // des points d'entrée vers cette page - "Se réabonner", une fiche de cours/épreuve -
  // ne passent aucun `require`, et Plan.Meta.ordering trie par prix croissant, ce qui
  // entrelace les deux types dans une liste plate). Générique et non conditionné sur
  // requireInedit/requireRepetiteur : quand un seul type est présent (cas filtré, ou
  // cursus sans add-on), un seul groupe existe et aucun en-tête n'est affiché - même
  // rendu qu'avant ce chantier.
  const planGroups: { label: string | null; hint: string | null; plans: Plan[] }[] = [
    { label: "Abonnement", hint: null, plans: plans.filter((p) => p.product_type === "ABONNEMENT") },
    {
      label: "Add-on Épreuves Inédites",
      hint: "Ne débloque pas les corrigés/cours classiques - accès aux épreuves inédites uniquement.",
      plans: plans.filter((p) => p.product_type === "ADDON_INEDIT"),
    },
    {
      label: "Add-on Fiches (répétiteurs)",
      hint: "Ne débloque pas les corrigés/cours classiques - accès à l'outil de génération de fiches uniquement.",
      plans: plans.filter((p) => p.product_type === "ADDON_REPETITEUR"),
    },
  ].filter((group) => group.plans.length > 0)
  const showGroupHeaders = planGroups.length > 1

  function renderPlanOption(plan: Plan) {
    return (
      <label
        key={plan.id}
        className="flex cursor-pointer items-center justify-between rounded-lg border border-input px-3.5 py-3 text-sm transition-colors has-[:checked]:border-primary has-[:checked]:bg-accent has-[:checked]:ring-1 has-[:checked]:ring-primary"
      >
        <span className="flex items-center gap-2.5">
          <input
            type="radio"
            name="plan"
            checked={selectedPlanId === plan.id}
            onChange={() => setSelectedPlanId(plan.id)}
            className="accent-primary"
          />
          <span className="flex flex-col">
            {plan.name}
            {plan.duration_mode === "JUSQUA_EXAMEN" && (
              <span className="text-xs font-normal text-muted-foreground">
                Accès jusqu'à son examen - {plan.effective_duration_days} jour{plan.effective_duration_days > 1 ? "s" : ""} restant{plan.effective_duration_days > 1 ? "s" : ""}
              </span>
            )}
            {plan.inclut_inedit && (
              <span className="text-xs font-normal text-primary">
                Inclut l'accès aux épreuves inédites
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
    <div className="mx-auto max-w-lg px-4 py-12 sm:py-16">
      <div className="mb-8 animate-fade-up text-center">
        <p className="mb-2 font-display text-sm italic text-primary">Abonnement</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
          {cursus
            ? `${cursus.examen_display}${cursus.series ? ` - Série ${cursus.series.code}` : ""}`
            : "S'abonner"}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {requireInedit
            ? "Seules les formules qui débloquent les Épreuves Inédites sur ce cursus sont proposées ici."
            : requireRepetiteur
              ? "Seul l'add-on Fiches (répétiteurs) pour ce cursus est proposé ici - il ne débloque pas les corrigés classiques."
              : "Choisissez votre offre et votre moyen de paiement pour débloquer l'accès."}
        </p>
      </div>

      <Card className="animate-fade-up shadow-lg shadow-primary/5">
        <CardContent className="p-6 sm:p-7">
          {phase === "form" && (
            <div className="flex flex-col gap-6">
              {creditDisponible > 0 && (
                <div className="flex items-center gap-2.5 rounded-lg border border-gold/30 bg-gold/[0.06] px-3.5 py-2.5 text-sm">
                  <Gift className="size-4 shrink-0 text-gold" />
                  <span>
                    Vous avez <strong className="text-foreground">{formatAmount(creditDisponible)} FCFA</strong> de
                    crédit parrainage - appliqué automatiquement pour un paiement Campay.
                  </span>
                </div>
              )}

              <div className="flex flex-col gap-2.5">
                <StepLabel n={1}>Votre offre</StepLabel>
                <div className="flex flex-col gap-4">
                  {planGroups.map((group) => (
                    <div key={group.label} className="flex flex-col gap-2">
                      {showGroupHeaders && (
                        <div>
                          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                            {group.label}
                          </p>
                          {group.hint && <p className="text-xs text-muted-foreground">{group.hint}</p>}
                        </div>
                      )}
                      {group.plans.map(renderPlanOption)}
                    </div>
                  ))}
                  {plans.length === 0 && (
                    <p className="text-sm text-muted-foreground">
                      {requireRepetiteur
                        ? "L'add-on Fiches n'est pas encore disponible à l'achat pour ce cursus - reviens bientôt."
                        : "Aucune offre disponible pour ce cursus actuellement."}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex flex-col gap-2.5">
                <StepLabel n={2}>Moyen de paiement</StepLabel>

                <label
                  className={cn(
                    "flex cursor-pointer items-start gap-3 rounded-xl border-2 px-4 py-3.5 transition-all",
                    paymentMethod === "CAMPAY" ? "border-primary bg-accent ring-1 ring-primary" : "border-input",
                  )}
                >
                  <input
                    type="radio"
                    name="payment-method"
                    checked={paymentMethod === "CAMPAY"}
                    onChange={() => setPaymentMethod("CAMPAY")}
                    className="sr-only"
                  />
                  <span
                    className={cn(
                      "mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-full text-[11px] font-bold",
                      CAMPAY_METHOD.badgeClass,
                    )}
                  >
                    {CAMPAY_METHOD.content}
                  </span>
                  <span className="flex flex-col gap-0.5">
                    <span className="flex items-center gap-1.5">
                      <span className="text-sm font-semibold">{CAMPAY_METHOD.label}</span>
                      <span className="rounded-full bg-success/15 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-success">
                        Recommandé
                      </span>
                    </span>
                    <span className="text-xs text-muted-foreground">
                      Paiement Mobile Money automatique - confirmation en quelques secondes, accès débloqué
                      immédiatement.
                    </span>
                  </span>
                </label>

                {!showManualOptions ? (
                  <button
                    type="button"
                    onClick={() => setShowManualOptions(true)}
                    className="self-start text-xs text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
                  >
                    Des difficultés avec Campay ? Payer manuellement via Orange Money ou MTN MoMo
                  </button>
                ) : (
                  <div className="flex flex-col gap-2.5 rounded-lg border border-dashed border-input p-3">
                    <p className="text-xs text-muted-foreground">
                      Paiement manuel : vous effectuez vous-même le transfert, puis déclarez votre transaction.
                      Vérifiée par notre équipe sous quelques heures.
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
                            checked={paymentMethod === method.value}
                            onChange={() => setPaymentMethod(method.value)}
                            className="sr-only"
                          />
                          <span
                            className={cn(
                              "flex size-8 shrink-0 items-center justify-center rounded-full text-[10px] font-bold",
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
                <StepLabel n={3}>Paiement</StepLabel>

                {paymentMethod === "CAMPAY" ? (
                  <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                    <div className="flex flex-col gap-2">
                      <Label htmlFor="momo-phone">Numéro Mobile Money</Label>
                      <Input
                        id="momo-phone"
                        inputMode="numeric"
                        placeholder="677123456"
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ""))}
                        maxLength={9}
                      />
                    </div>

                    {error && <p className="text-sm text-destructive">{error}</p>}

                    {selectedPlan && creditAppliqueSelection > 0 && (
                      <p className="text-xs text-muted-foreground">
                        {formatAmount(selectedPlan.effective_price)} FCFA − {formatAmount(creditAppliqueSelection)} FCFA
                        de crédit parrainage
                      </p>
                    )}
                    <Button type="submit" disabled={!selectedPlan} size="lg" className="w-full">
                      Payer {selectedPlan ? `${formatAmount(netAPayerSelection)} FCFA` : ""}
                    </Button>
                  </form>
                ) : (
                  selectedPlan && (
                    <ManualPaymentPanel
                      plan={selectedPlan}
                      operator={paymentMethod}
                      onDeclared={(payment) => {
                        setDeclaredPayment(payment)
                        setPhase("manual_submitted")
                        // Pas d'évènement dédié côté vocabulaire fermé (voir analytics.models.EventName) -
                        // une déclaration manuelle est la même intention qu'un paiement Campay initié,
                        // juste sur un autre canal (voir `operator` dans les properties pour les distinguer).
                        trackEvent("payment_initiated", {
                          cursus_id: cursusId ? Number(cursusId) : undefined,
                          plan_id: selectedPlan.id,
                          operator: paymentMethod,
                        })
                      }}
                    />
                  )
                )}
              </div>
            </div>
          )}

          {phase === "manual_submitted" && declaredPayment && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <CheckCircle2 className="size-10 text-success" />
              <p className="font-display font-medium">Votre déclaration a bien été enregistrée</p>
              <p className="text-sm text-muted-foreground">
                Elle est actuellement en cours de vérification par notre équipe, généralement en quelques heures.
                Numéro de demande : #{declaredPayment.id}.
              </p>
              <Button asChild>
                <Link to="/mes-paiements">Suivre mes paiements</Link>
              </Button>
            </div>
          )}

          {phase === "pending" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <Loader2 className="size-8 animate-spin text-primary" />
              <p className="font-display font-medium">Confirmez le paiement sur votre téléphone</p>
              <p className="text-sm text-muted-foreground">
                Une demande Mobile Money a été envoyée au {phoneNumber}. Cette page se met à jour automatiquement.
              </p>
              <button
                type="button"
                onClick={cancelPending}
                className="text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
              >
                Annuler
              </button>
            </div>
          )}

          {phase === "timeout" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <AlertCircle className="size-10 text-warning" />
              <p className="font-display font-medium">La confirmation prend plus de temps que prévu</p>
              <p className="text-sm text-muted-foreground">
                Avez-vous validé la demande sur votre téléphone ? Si le paiement passe malgré tout, votre
                abonnement s'activera automatiquement dès la confirmation de l'opérateur.
              </p>
              <Button variant="outline" onClick={() => setPhase("form")}>
                Réessayer
              </Button>
            </div>
          )}

          {phase === "success" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <CheckCircle2 className="size-10 text-success" />
              <p className="font-display font-medium">
                {requireRepetiteur ? "Add-on Fiches activé !" : "Abonnement activé !"}
              </p>
              <Button asChild>
                {requireRepetiteur ? (
                  <Link to="/fiches">Générer une fiche</Link>
                ) : (
                  <Link to={epreuvesListPath(country)}>Retour au catalogue</Link>
                )}
              </Button>
            </div>
          )}

          {phase === "failed" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <XCircle className="size-10 text-destructive" />
              <p className="font-display font-medium">Le paiement a échoué</p>
              {error && <p className="text-sm text-muted-foreground">{error}</p>}
              <Button variant="outline" onClick={() => setPhase("form")}>
                Réessayer
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <p className="mt-6 flex items-center justify-center gap-1.5 text-center text-xs text-muted-foreground">
        <ShieldCheck className="size-3.5 shrink-0" />
        Paiement sécurisé - votre abonnement s'active dès la confirmation du paiement.
      </p>
    </div>
  )
}
