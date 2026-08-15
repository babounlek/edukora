import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Check, Crown, Flame, Users } from "lucide-react"

import { listCursus, listPlans } from "@/api/endpoints"
import type { Cursus, Plan } from "@/api/types"
import { cn, formatAmount } from "@/lib/utils"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Au-delà de cette fenêtre, "jusqu'à l'examen" ne crée plus d'urgence réelle (ex.
// 300 jours restants) - le pack ne vaut la peine d'être mis en avant que proche de
// la session, sinon un tarif fixe classique est plus adapté.
const URGENCE_MAX_JOURS = 60

function formatDateDansNJours(jours: number): string {
  const cible = new Date(Date.now() + jours * 24 * 60 * 60 * 1000)
  return cible.toLocaleDateString("fr-FR", { day: "numeric", month: "long" })
}

// Noms commerciaux des 3 formules - "Essentiel" (7 jours), "Performance" (1 mois, le
// palier mis en avant ci-dessous), "Max" (1 an). La durée réelle reste affichée en
// sous-titre (voir CardDescription) : le nom seul ne la communique plus.
function formulaName(days: number): string {
  if (days <= 7) return "Essentiel"
  if (days <= 31) return "Performance"
  return "Max"
}

function tierDuration(days: number): string {
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
  const [selectedCursusRepetiteur, setSelectedCursusRepetiteur] = useState("")

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

  // Même dédoublonnage par durée que `tiers` ci-dessus (voir son commentaire) - le prix
  // de l'add-on Fiches est lui aussi pensé comme uniforme par durée, indépendant du
  // cursus. Tant qu'un seul cursus pilote a des Plan ADDON_REPETITEUR (voir le chantier
  // "Outil Fiches"), cette liste ne reflète que son tarif - correct dès qu'un autre
  // cursus recevra les siens, au même prix par convention.
  const repetiteurAddon = allPlans.filter((p) => p.product_type === "ADDON_REPETITEUR" && p.duration_mode === "FIXE")
  const repetiteurTiers = Array.from(
    repetiteurAddon
      .reduce((seen, plan) => (seen.has(plan.duration_days) ? seen : seen.set(plan.duration_days, plan)), new Map<number, Plan>())
      .values(),
  ).sort((a, b) => a.duration_days - b.duration_days)

  function handleSubscribe() {
    if (!selectedCursus) return
    navigate(`/abonnement?cursus=${selectedCursus}`)
  }

  function handleSubscribeRepetiteur() {
    if (!selectedCursusRepetiteur) return
    navigate(`/abonnement?cursus=${selectedCursusRepetiteur}&require=repetiteur`)
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-14 sm:px-6">
      <div className="mx-auto max-w-xl animate-fade-up text-center">
        <p className="mb-2 font-display text-sm italic text-primary">Tarifs</p>
        <h1 className="font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
          Choisis ton profil.
        </h1>
      </div>

      {/* Deux offres commerciales distinctes cohabitent sur cette page (abonnement
          élève classique, add-on Fiches pour répétiteurs/enseignants) - des onglets
          plutôt qu'un simple ancrage de scroll (essayé puis remplacé) : ils ne
          laissent jamais les deux offres se mélanger visuellement, et l'un ou l'autre
          public voit tout de suite qu'il y a bien un onglet "pour lui". */}
      <Tabs defaultValue="eleve" className="mt-8 items-center">
        <TabsList>
          <TabsTrigger value="eleve">Élève</TabsTrigger>
          <TabsTrigger value="repetiteur">Répétiteur ou enseignant</TabsTrigger>
        </TabsList>

        <TabsContent value="eleve" className="w-full animate-fade-up">
          <div className="mx-auto max-w-xl text-center">
            <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
              Un seul prix, <span className="text-primary">le même pour tous les cursus</span>.
            </h2>
            <p className="mt-3 text-muted-foreground">
              Corrigés d'annales, sujets et cours complets - pour la matière et la série de ton choix.
            </p>
          </div>

          <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-3">
            {tiers.map((tier) => {
              const isPopular = tier.duration_days === 365
              return (
                <Card
                  key={tier.duration_days}
                  className={cn(
                    "relative flex flex-col",
                    isPopular && "border-primary shadow-lg shadow-primary/10 sm:-my-2 sm:scale-[1.03]",
                  )}
                >
                  {isPopular && (
                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-1 font-display text-xs font-semibold tracking-wide text-primary-foreground shadow-sm">
                      Le plus populaire
                    </span>
                  )}
                  <CardHeader>
                    <CardTitle className="font-display text-lg">{formulaName(tier.duration_days)}</CardTitle>
                    <CardDescription>{tierDuration(tier.duration_days)}</CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-1 flex-col gap-4">
                    <div>
                      <p className="font-display text-3xl font-semibold text-primary">
                        {formatAmount(tier.price)}
                        <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
                      </p>
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        ≈ {formatAmount(Math.round(tier.price / tier.duration_days))} FCFA/jour
                      </p>
                    </div>
                    <ul className="flex flex-1 flex-col gap-2 text-sm text-muted-foreground">
                      <li className="flex items-center gap-2">
                        <Check className="size-4 shrink-0 text-success" />
                        Corrigés complets en illimité
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="size-4 shrink-0 text-success" />
                        Cours et exercices d'application
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="size-4 shrink-0 text-success" />
                        Quiz qui identifie tes lacunes et cible tes révisions
                      </li>
                      {tier.inclut_inedit && (
                        <li className="flex items-center gap-2 font-medium text-foreground">
                          <Check className="size-4 shrink-0 text-success" />
                          <Crown className="size-3.5 shrink-0 text-gold" />
                          Accès aux épreuves inédites inclus
                        </li>
                      )}
                    </ul>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          <div className="mx-auto mt-12 max-w-md rounded-xl border border-border bg-card p-6 shadow-sm">
            <h3 className="mb-1 font-display text-lg font-semibold">Prêt à t'abonner ?</h3>
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
        </TabsContent>

        <TabsContent value="repetiteur" className="w-full animate-fade-up">
          <div className="mx-auto max-w-xl text-center">
            <h2 className="flex items-center justify-center gap-1.5 font-display text-2xl font-semibold tracking-tight sm:text-3xl">
              <Users className="size-6 shrink-0 text-primary" />
              Génère des fiches d'exercices pour tes élèves
            </h2>
            <p className="mt-3 text-muted-foreground">
              Choisis les compétences à travailler, la difficulté et le nombre de questions - obtiens en quelques
              secondes un PDF énoncé à distribuer à tes élèves et un PDF corrigé pour toi, à ton nom.
            </p>
          </div>

          {repetiteurTiers.length > 0 && (
            <div className="mx-auto mt-8 grid max-w-xs grid-cols-2 gap-3">
              {repetiteurTiers.map((tier) => (
                <div key={tier.duration_days} className="rounded-lg border border-border bg-card px-4 py-3 text-center">
                  <p className="text-xs text-muted-foreground">{tierDuration(tier.duration_days)}</p>
                  <p className="font-display text-lg font-semibold text-primary">
                    {formatAmount(tier.price)}
                    <span className="ml-1 text-xs font-normal text-muted-foreground">FCFA</span>
                  </p>
                </div>
              ))}
            </div>
          )}
          {/* Add-on distinct de l'abonnement classique (voir SubscribePage.tsx) - ne
              débloque jamais, à lui seul, les corrigés/cours de l'onglet Élève.
              Précisé ici plutôt que supposé implicite : même risque de confusion déjà
              identifié pour l'add-on Épreuves Inédites. */}
          <p className="mx-auto mt-3 max-w-md text-center text-xs text-muted-foreground">
            Add-on séparé de l'abonnement classique - ne débloque pas les corrigés.
          </p>

          <div className="mx-auto mt-9 max-w-md rounded-xl border border-border bg-card p-6 text-center shadow-sm">
            <h3 className="mb-1 font-display text-lg font-semibold">Prêt à débloquer l'add-on ?</h3>
            <p className="mb-4 text-sm text-muted-foreground">Choisis ton cursus pour continuer.</p>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Select value={selectedCursusRepetiteur} onValueChange={setSelectedCursusRepetiteur}>
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
              <Button onClick={handleSubscribeRepetiteur} disabled={!selectedCursusRepetiteur} size="lg">
                S'abonner
              </Button>
            </div>
            <button
              type="button"
              onClick={() => navigate("/fiches")}
              className="mt-4 text-sm text-muted-foreground underline-offset-4 hover:text-primary hover:underline"
            >
              ou découvrir l'outil Fiches d'abord
            </button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
