import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Check, Flame } from "lucide-react"

import { listCursus, listPlans } from "@/api/endpoints"
import type { Cursus, Plan } from "@/api/types"
import { formatAmount } from "@/lib/utils"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

// Au-delà de cette fenêtre, "jusqu'à l'examen" ne crée plus d'urgence réelle (ex.
// 300 jours restants) - le pack ne vaut la peine d'être mis en avant que proche de
// la session, sinon un tarif fixe classique est plus adapté.
const URGENCE_MAX_JOURS = 60

function formatDateDansNJours(jours: number): string {
  const cible = new Date(Date.now() + jours * 24 * 60 * 60 * 1000)
  return cible.toLocaleDateString("fr-FR", { day: "numeric", month: "long" })
}

function tierLabel(days: number): string {
  if (days <= 7) return "7 jours"
  if (days <= 31) return "1 mois"
  return "1 an"
}

export function PricingPage() {
  useSeo({
    title: "Tarifs",
    description: `Abonnement ${SITE_NAME} par Mobile Money : 7 jours, 1 mois ou 1 an pour accéder à tous les corrigés et cours de ton cursus.`,
  })

  const navigate = useNavigate()
  const [tiers, setTiers] = useState<Plan[]>([])
  const [allPlans, setAllPlans] = useState<Plan[]>([])
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  const [selectedCursus, setSelectedCursus] = useState("")

  useEffect(() => {
    listPlans().then((plans) => {
      setAllPlans(plans)
      // Le prix est le même pour tous les cursus sur les paliers fixes : on ne garde
      // qu'un exemplaire par durée pour la grille, pas les ~24 offres telles quelles.
      // Le pack "jusqu'à l'examen" est exclu de cette grille - son prix/sa durée
      // dépend du cursus choisi, il est affiché séparément une fois le cursus choisi.
      const fixes = plans.filter((p) => p.duration_mode === "FIXE")
      const seen = new Map<number, Plan>()
      fixes.forEach((plan) => {
        if (!seen.has(plan.duration_days)) seen.set(plan.duration_days, plan)
      })
      setTiers(Array.from(seen.values()).sort((a, b) => a.duration_days - b.duration_days))
    })
    listCursus().then(setCursusList)
  }, [])

  const packExamen = allPlans.find(
    (p) =>
      p.duration_mode === "JUSQUA_EXAMEN" &&
      String(p.cursus.id) === selectedCursus &&
      p.effective_duration_days <= URGENCE_MAX_JOURS,
  )

  function handleSubscribe() {
    if (!selectedCursus) return
    navigate(`/abonnement?cursus=${selectedCursus}`)
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
      <div className="mx-auto max-w-xl animate-fade-up text-center">
        <p className="mb-2 font-display text-sm italic text-primary">Tarifs</p>
        <h1 className="font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
          Un seul prix, <span className="text-primary">le même pour tous les cursus</span>.
        </h1>
        <p className="mt-4 text-muted-foreground">
          Corrigés d'annales, sujets et cours complets - pour la matière et la série de ton choix.
        </p>
      </div>

      <div className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-3">
        {tiers.map((tier) => (
          <Card
            key={tier.duration_days}
            className={tier.duration_days === 30 ? "border-primary shadow-lg shadow-primary/10" : ""}
          >
            <CardHeader>
              <CardTitle className="font-display text-lg">{tierLabel(tier.duration_days)}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <p className="font-display text-3xl font-semibold text-primary">
                {formatAmount(tier.price)}
                <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
              </p>
              <ul className="flex flex-col gap-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <Check className="size-4 shrink-0 text-success" />
                  Corrigés complets en illimité
                </li>
                <li className="flex items-center gap-2">
                  <Check className="size-4 shrink-0 text-success" />
                  Cours et exercices d'application
                </li>
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mx-auto mt-14 max-w-md animate-fade-up rounded-xl border border-border p-6">
        <h2 className="mb-1 font-display text-lg font-semibold">S'abonner</h2>
        <p className="mb-4 text-sm text-muted-foreground">Choisis ton cursus pour continuer.</p>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Select value={selectedCursus} onValueChange={setSelectedCursus}>
            <SelectTrigger className="flex-1">
              <SelectValue placeholder="Choisis ton cursus" />
            </SelectTrigger>
            <SelectContent>
              {cursusList.map((c) => (
                <SelectItem key={c.id} value={String(c.id)}>
                  {c.examen_display}
                  {c.series ? ` - Série ${c.series.code}` : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button onClick={handleSubscribe} disabled={!selectedCursus} size="lg">
            Continuer
          </Button>
        </div>

        {packExamen && (
          <div className="mt-4 flex items-start gap-3 rounded-lg border border-primary/30 bg-primary/5 p-3.5">
            <Flame className="mt-0.5 size-4 shrink-0 text-primary" />
            <p className="text-sm text-foreground">
              Ton {packExamen.cursus.examen_display} commence dans{" "}
              <strong>{packExamen.effective_duration_days} jour{packExamen.effective_duration_days > 1 ? "s" : ""}</strong>{" "}
              (le {formatDateDansNJours(packExamen.effective_duration_days)}). Le pack{" "}
              <strong>{packExamen.name}</strong> à {formatAmount(packExamen.price)} FCFA te donne accès jusqu'à ce
              jour-là.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
