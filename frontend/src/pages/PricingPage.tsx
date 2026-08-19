import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { Check, Crown, Sparkles, Users } from "lucide-react"

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

function formatDateDansNJours(jours: number): string {
  const cible = new Date(Date.now() + jours * 24 * 60 * 60 * 1000)
  return cible.toLocaleDateString("fr-FR", { day: "numeric", month: "long" })
}

function tierDuration(days: number): string {
  if (days <= 31) return "1 mois"
  return "1 an"
}

export function PricingPage() {
  useSeo({
    title: "Tarifs",
    description: `Abonnement ${SITE_NAME} par Mobile Money : au mois, ou jusqu'à ton examen, pour accéder à tous les corrigés et cours de ton cursus.`,
  })

  const navigate = useNavigate()
  const [allPlans, setAllPlans] = useState<Plan[]>([])
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  const [selectedCursus, setSelectedCursus] = useState("")
  const [selectedCursusRepetiteur, setSelectedCursusRepetiteur] = useState("")

  useEffect(() => {
    listPlans().then(setAllPlans)
    listCursus().then(setCursusList)
  }, [])

  // Mensuel : prix uniforme par cursus (voir migration 0009_grille_deux_paliers) -
  // n'importe quel exemplaire suffit à l'afficher, même avant qu'un cursus soit
  // choisi. Jusqu'à l'Examen, à l'inverse, dépend du cursus choisi (prix et durée
  // calculés depuis la session d'examen réelle - voir
  // subscriptions.models.Plan.effective_price/effective_duration_days) : rien de
  // concret à afficher tant qu'aucun cursus n'est sélectionné.
  const mensuel = allPlans.find((p) => p.product_type === "ABONNEMENT" && p.duration_mode === "FIXE")
  const jusquaExamen = allPlans.find(
    (p) =>
      p.product_type === "ABONNEMENT" &&
      p.duration_mode === "JUSQUA_EXAMEN" &&
      String(p.cursus.id) === selectedCursus,
  )

  // Même dédoublonnage par durée que par le passé - le prix de l'add-on Fiches est
  // pensé comme uniforme par durée, indépendant du cursus. Tant qu'un seul cursus
  // pilote a des Plan ADDON_REPETITEUR (voir le chantier "Outil Fiches"), cette
  // liste ne reflète que son tarif - correct dès qu'un autre cursus recevra les
  // siens, au même prix par convention.
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
              Deux façons de t'abonner.
            </h2>
            <p className="mt-3 text-muted-foreground">
              Corrigés d'annales, sujets et cours complets - pour la matière et la série de ton choix.
            </p>
          </div>

          <div className="mx-auto mt-8 max-w-xs">
            <Select value={selectedCursus} onValueChange={setSelectedCursus}>
              <SelectTrigger>
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
          </div>

          <div className="mx-auto mt-8 grid max-w-2xl grid-cols-1 gap-5 sm:grid-cols-2">
            {mensuel && (
              <Card className="relative flex flex-col">
                <CardHeader>
                  <CardTitle className="font-display text-lg">Mensuel</CardTitle>
                  <CardDescription>{tierDuration(mensuel.duration_days)} - pour tester ou réviser une notion précise</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-1 flex-col gap-4">
                  <div>
                    <p className="font-display text-3xl font-semibold text-primary">
                      {formatAmount(mensuel.effective_price)}
                      <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
                    </p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      ≈ {formatAmount(Math.round(mensuel.effective_price / mensuel.duration_days))} FCFA/jour
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
                  </ul>
                </CardContent>
              </Card>
            )}

            <Card
              className={cn(
                "relative flex flex-col",
                jusquaExamen && "border-primary shadow-lg shadow-primary/10 sm:-my-2 sm:scale-[1.03]",
              )}
            >
              {jusquaExamen && (
                <span className="absolute -top-3 left-1/2 flex -translate-x-1/2 items-center gap-1 rounded-full bg-primary px-3 py-1 font-display text-xs font-semibold tracking-wide text-primary-foreground shadow-sm">
                  <Sparkles className="size-3" />
                  Offre principale
                </span>
              )}
              <CardHeader>
                <CardTitle className="font-display text-lg">Jusqu'à l'Examen</CardTitle>
                <CardDescription>
                  {jusquaExamen
                    ? "Toute l'année scolaire, jusqu'au jour de l'examen"
                    : "Choisis ton cursus pour voir le prix exact"}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-1 flex-col gap-4">
                {jusquaExamen ? (
                  <>
                    <div>
                      <p className="font-display text-3xl font-semibold text-primary">
                        {formatAmount(jusquaExamen.effective_price)}
                        <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
                      </p>
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        ≈ {formatAmount(Math.round(jusquaExamen.effective_price / jusquaExamen.effective_duration_days))} FCFA/jour
                        {" - "}jamais plus cher au jour qu'un abonnement Mensuel
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
                      <li className="flex items-center gap-2 font-medium text-foreground">
                        <Check className="size-4 shrink-0 text-success" />
                        <Crown className="size-3.5 shrink-0 text-gold" />
                        Accès aux épreuves inédites inclus
                      </li>
                      <li className="text-xs text-muted-foreground">
                        Accès jusqu'au {formatDateDansNJours(jusquaExamen.effective_duration_days)} (
                        {jusquaExamen.effective_duration_days} jour{jusquaExamen.effective_duration_days > 1 ? "s" : ""})
                      </li>
                    </ul>
                  </>
                ) : (
                  <p className="flex flex-1 items-center text-sm text-muted-foreground">
                    Le prix s'ajuste à ton examen : plus tu t'abonnes tôt dans l'année, plus le tarif au jour est bas.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="mx-auto mt-12 max-w-md rounded-xl border border-border bg-card p-6 shadow-sm">
            <h3 className="mb-1 font-display text-lg font-semibold">Prêt à t'abonner ?</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              {selectedCursus ? "Continue vers le paiement." : "Choisis ton cursus ci-dessus pour continuer."}
            </p>
            <Button onClick={handleSubscribe} disabled={!selectedCursus} size="lg" className="w-full">
              Continuer
            </Button>
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
                    {formatAmount(tier.effective_price)}
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
