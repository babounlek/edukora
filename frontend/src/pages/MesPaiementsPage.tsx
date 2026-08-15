import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { CheckCircle2, Clock, Loader2, Receipt, XCircle } from "lucide-react"

import { listMyManualPayments } from "@/api/endpoints"
import type { ManualPayment } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useSeo } from "@/lib/seo"
import { cn, formatAmount } from "@/lib/utils"

const STATUS_META: Record<ManualPayment["status"], { badge: "success" | "warning" | "outline"; icon: typeof Clock; borderClass: string }> = {
  PENDING: { badge: "outline", icon: Clock, borderClass: "border-l-muted-foreground/40" },
  APPROVED: { badge: "success", icon: CheckCircle2, borderClass: "border-l-success" },
  REJECTED: { badge: "warning", icon: XCircle, borderClass: "border-l-destructive" },
}

export function MesPaiementsPage() {
  useSeo({ title: "Mes paiements" })

  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()
  const [payments, setPayments] = useState<ManualPayment[] | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/mes-paiements" } })
      return
    }
    listMyManualPayments().then(setPayments)
  }, [isLoading, isAuthenticated, navigate])

  if (isLoading) return null

  return (
    <div className="mx-auto max-w-2xl animate-fade-up px-4 py-10 sm:py-14">
      <div className="mb-8">
        <p className="mb-2 font-display text-sm italic text-primary">Suivi</p>
        <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">Mes paiements</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Statut de tes déclarations Mobile Money (Orange Money, MTN MoMo).
        </p>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="font-display text-lg">Déclarations Mobile Money</CardTitle>
        </CardHeader>
        <CardContent>
          {payments === null ? (
            <div className="flex justify-center py-8">
              <Loader2 className="size-6 animate-spin text-primary" />
            </div>
          ) : payments.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-8 text-center">
              <Receipt className="size-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Aucun paiement Mobile Money déclaré pour le moment.
              </p>
              <Button asChild variant="outline" size="sm">
                <Link to="/tarifs">Voir les tarifs</Link>
              </Button>
            </div>
          ) : (
            <ul className="flex flex-col gap-3">
              {payments.map((payment) => {
                const meta = STATUS_META[payment.status]
                const StatusIcon = meta.icon
                return (
                  <li
                    key={payment.id}
                    className={cn(
                      "rounded-md border border-l-4 border-border px-3.5 py-3 text-sm",
                      meta.borderClass,
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium">
                        {payment.plan.cursus.examen_display}
                        {payment.plan.cursus.series ? ` - Série ${payment.plan.cursus.series.code}` : ""}
                      </span>
                      <Badge variant={meta.badge} className="flex items-center gap-1">
                        <StatusIcon className="size-3" />
                        {payment.status_display}
                      </Badge>
                    </div>
                    <div className="mt-2 flex flex-col gap-1 text-xs text-muted-foreground">
                      <span>
                        {payment.operator_display} - {formatAmount(payment.amount_declared)} FCFA
                      </span>
                      <span className="font-mono">Réf. {payment.transaction_reference}</span>
                      <span>Déclaré le {new Date(payment.created_at).toLocaleDateString("fr-FR")}</span>
                      {payment.status === "PENDING" && (
                        <span>Vérification manuelle par notre équipe, généralement en quelques heures.</span>
                      )}
                      {payment.status === "REJECTED" && payment.rejection_reason_display && (
                        <span className="font-medium text-destructive">
                          Motif : {payment.rejection_reason_display}
                        </span>
                      )}
                    </div>
                  </li>
                )
              })}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
