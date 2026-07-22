import { useEffect, useRef, useState, type FormEvent } from "react"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import { CheckCircle2, Loader2, XCircle } from "lucide-react"

import { checkPaymentStatus, initiatePayment, listCursus, listPlans } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { Cursus, Plan } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { formatAmount } from "@/lib/utils"
import { useSeo } from "@/lib/seo"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

type PaymentPhase = "form" | "pending" | "success" | "failed"

export function SubscribePage() {
  useSeo({ title: "Abonnement" })

  const [searchParams] = useSearchParams()
  const cursusId = searchParams.get("cursus")
  const navigate = useNavigate()
  const { isAuthenticated, isLoading, user } = useAuth()

  const [cursus, setCursus] = useState<Cursus | null>(null)
  const [plans, setPlans] = useState<Plan[]>([])
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null)
  const [phoneNumber, setPhoneNumber] = useState("")
  const [phase, setPhase] = useState<PaymentPhase>("form")
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: `/abonnement?cursus=${cursusId ?? ""}` } })
    }
  }, [isLoading, isAuthenticated, cursusId, navigate])

  useEffect(() => {
    if (user) setPhoneNumber(user.phone_number)
  }, [user])

  useEffect(() => {
    listPlans(cursusId ? Number(cursusId) : undefined).then((data) => {
      setPlans(data)
      if (data.length > 0) setSelectedPlanId(data[0].id)
    })
    if (cursusId) {
      listCursus().then((all) => {
        setCursus(all.find((c) => c.id === Number(cursusId)) ?? null)
      })
    }
  }, [cursusId])

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current)
    }
  }, [])

  function pollTransaction(transactionId: number) {
    pollRef.current = window.setInterval(async () => {
      try {
        const result = await checkPaymentStatus(transactionId)
        if (result.status !== "PENDING") {
          if (pollRef.current) window.clearInterval(pollRef.current)
          setPhase(result.status === "SUCCESSFUL" ? "success" : "failed")
        }
      } catch {
        // on continue de sonder, une erreur ponctuelle du reseau ne doit pas interrompre l'attente
      }
    }, 3000)
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!selectedPlanId) return

    setError(null)
    if (!/^6\d{8}$/.test(phoneNumber)) {
      setError("Entre un numéro Mobile Money valide (9 chiffres, commence par 6).")
      return
    }

    setPhase("pending")
    try {
      const response = await initiatePayment({ planId: selectedPlanId, phoneNumber })
      if (response.status === "FAILED") {
        setPhase("failed")
        return
      }
      pollTransaction(response.transaction_id)
    } catch (err) {
      setPhase("failed")
      setError(err instanceof ApiError ? err.message : "Le paiement n'a pas pu être initié.")
    }
  }

  const selectedPlan = plans.find((p) => p.id === selectedPlanId) ?? null

  return (
    <div className="mx-auto max-w-md px-4 py-12">
      <Card className="animate-fade-up shadow-lg shadow-primary/5">
        <CardHeader>
          <CardTitle className="font-display text-2xl">S'abonner</CardTitle>
          <CardDescription>
            {cursus
              ? `${cursus.examen_display}${cursus.series ? ` - Série ${cursus.series.code}` : ""}`
              : "Choisis une offre pour débloquer l'accès."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {phase === "form" && (
            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
              <div className="flex flex-col gap-2">
                <Label>Offre</Label>
                <div className="flex flex-col gap-2">
                  {plans.map((plan) => (
                    <label
                      key={plan.id}
                      className="flex cursor-pointer items-center justify-between rounded-lg border border-input px-3.5 py-3 text-sm transition-colors has-[:checked]:border-primary has-[:checked]:bg-accent"
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
                              Accès jusqu'à ton examen - {plan.effective_duration_days} jour{plan.effective_duration_days > 1 ? "s" : ""} restant{plan.effective_duration_days > 1 ? "s" : ""}
                            </span>
                          )}
                        </span>
                      </span>
                      <span className="font-display font-semibold text-primary">
                        {formatAmount(plan.price)} FCFA
                      </span>
                    </label>
                  ))}
                  {plans.length === 0 && (
                    <p className="text-sm text-muted-foreground">
                      Aucune offre disponible pour ce cursus actuellement.
                    </p>
                  )}
                </div>
              </div>

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

              <Button type="submit" disabled={!selectedPlan} size="lg" className="w-full">
                Payer {selectedPlan ? `${formatAmount(selectedPlan.price)} FCFA` : ""}
              </Button>
            </form>
          )}

          {phase === "pending" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <Loader2 className="size-8 animate-spin text-primary" />
              <p className="font-display font-medium">Confirme le paiement sur ton téléphone</p>
              <p className="text-sm text-muted-foreground">
                Une demande Mobile Money a été envoyée au {phoneNumber}. Cette page se met à jour automatiquement.
              </p>
            </div>
          )}

          {phase === "success" && (
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <CheckCircle2 className="size-10 text-success" />
              <p className="font-display font-medium">Abonnement activé !</p>
              <Button asChild>
                <Link to="/">Retour au catalogue</Link>
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
    </div>
  )
}
