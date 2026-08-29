import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { useNavigate } from "react-router-dom"
import {
  ArrowRight,
  CalendarPlus,
  Check,
  Crown,
  FileText,
  ShieldCheck,
  Smartphone,
  Sparkles,
  Users,
  WifiOff,
  Zap,
} from "lucide-react"

import { listPlans } from "@/api/endpoints"
import type { Cursus, Plan } from "@/api/types"
import { cn, formatAmount } from "@/lib/utils"
import { coursListPath } from "@/lib/countryPath"
import { useCountry } from "@/context/CountryContext"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

// Palier de référence pour l'économie affichée sur les autres formules ("-16 %") : le
// mois est le point d'entrée de la grille, c'est à lui que l'élève compare
// spontanément. En dur plutôt que "le palier le moins cher" pour que l'affichage ne se
// déplace pas silencieusement si un palier plus court réapparaît.
const DUREE_REFERENCE_JOURS = 30

// Sous ce seuil, l'économie n'est pas assez marquée pour mériter un badge - mieux
// vaut ne rien afficher qu'un "-3 %" qui donne l'impression que monter en gamme ne
// sert à rien.
const ECONOMIE_MIN_AFFICHEE = 5

function tierDuration(days: number): string {
  if (days <= 31) return "1 mois"
  if (days <= 90) return "3 mois"
  return "1 an"
}

function formatDateDansNJours(jours: number): string {
  const cible = new Date(Date.now() + jours * 24 * 60 * 60 * 1000)
  return cible.toLocaleDateString("fr-FR", { day: "numeric", month: "long" })
}

function cursusLabel(cursus: Cursus): string {
  return `${cursus.examen_display}${cursus.series ? ` - Série ${cursus.series.code}` : ""}`
}

// Ordre de lecture attendu par un élève (du plus jeune au plus avancé), et non
// l'ordre de création en base (qui entrelace Probatoire et BAC série par série).
const ORDRE_EXAMENS = ["BEPC", "PROBATOIRE", "BAC", "AUTRE"]

function trierCursus(a: Cursus, b: Cursus): number {
  const rang = ORDRE_EXAMENS.indexOf(a.examen) - ORDRE_EXAMENS.indexOf(b.examen)
  if (rang !== 0) return rang
  return (a.series?.code ?? "").localeCompare(b.series?.code ?? "")
}

type GroupeCursus = { examen: string; examenLabel: string; cursus: Cursus[] }

/** Un groupe par examen (BEPC/Probatoire/BAC), dans le même ordre que trierCursus -
 * regrouper permet à la puce elle-même de ne porter que la série ("C", "TI") plutôt
 * que de répéter "BAC -" sur chacune des cinq séries d'un même examen. */
function grouperParExamen(liste: Cursus[]): GroupeCursus[] {
  const groupes = new Map<string, GroupeCursus>()
  liste.forEach((c) => {
    if (!groupes.has(c.examen)) groupes.set(c.examen, { examen: c.examen, examenLabel: c.examen_display, cursus: [] })
    groupes.get(c.examen)!.cursus.push(c)
  })
  return Array.from(groupes.values()).sort(
    (a, b) => ORDRE_EXAMENS.indexOf(a.examen) - ORDRE_EXAMENS.indexOf(b.examen),
  )
}

function ChipCursus({ texte, selected, onClick }: { texte: string; selected: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      className={cn(
        "rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
        selected
          ? "border-primary bg-primary text-primary-foreground shadow-sm"
          : "border-border bg-background text-foreground hover:border-primary/40 hover:bg-primary/5",
      )}
    >
      {texte}
    </button>
  )
}

/**
 * Sélecteur de cursus en puces cliquables plutôt qu'en menu déroulant : les options
 * sont peu nombreuses (jusqu'à 11 pour le Cameroun, souvent 1 à 3 ailleurs - voir
 * cursusVendables) et tiennent sur une ou deux lignes - les voir toutes d'un coup et
 * choisir en un clic vaut mieux que les cacher derrière un menu à ouvrir puis
 * refermer, pour un choix qui conditionne tout le reste de la page (prix et durée de
 * Jusqu'à l'Examen, destination du bouton de chaque carte).
 */
function CursusChips({
  liste,
  selected,
  onSelect,
  label,
  centre = false,
  describedBy,
}: {
  liste: Cursus[]
  selected: string
  onSelect: (id: string) => void
  label: string
  centre?: boolean
  describedBy?: string
}) {
  const groupes = useMemo(() => grouperParExamen(liste), [liste])
  return (
    <div
      role="group"
      aria-label={label}
      aria-describedby={describedBy}
      className={cn("flex flex-col gap-2.5", centre && "items-center")}
    >
      {groupes.map((groupe) => {
        // Un seul cursus dans le groupe et pas de série (ex. BEPC) : la puce porte
        // directement le nom de l'examen, un en-tête de groupe ne ferait que le répéter.
        if (groupe.cursus.length === 1 && !groupe.cursus[0].series) {
          const c = groupe.cursus[0]
          return (
            <ChipCursus
              key={c.id}
              texte={cursusLabel(c)}
              selected={selected === String(c.id)}
              onClick={() => onSelect(String(c.id))}
            />
          )
        }
        return (
          <div key={groupe.examen} className={cn("flex flex-wrap items-center gap-2", centre && "justify-center")}>
            <span className="w-[4.5rem] shrink-0 text-xs font-medium text-muted-foreground">{groupe.examenLabel}</span>
            {groupe.cursus.map((c) => (
              <ChipCursus
                key={c.id}
                texte={c.series?.code ?? cursusLabel(c)}
                selected={selected === String(c.id)}
                onClick={() => onSelect(String(c.id))}
              />
            ))}
          </div>
        )
      })}
    </div>
  )
}

/** Les cursus réellement vendables pour ce type de produit, déduits des offres
 * elles-mêmes. La base compte 179 cursus (14 pays) mais 15 seulement ont un
 * abonnement, et un seul a l'add-on Fiches : peupler la liste depuis /catalog/cursus
 * remplissait le menu de choix qui menaient tous à "Aucune offre disponible pour ce
 * cursus". Une option affichée ici mène toujours à une offre réelle. */
function cursusVendables(plans: Plan[], productType: Plan["product_type"]): Cursus[] {
  const parId = new Map<number, Cursus>()
  plans
    .filter((plan) => plan.product_type === productType)
    .forEach((plan) => parId.set(plan.cursus.id, plan.cursus))
  return Array.from(parId.values()).sort(trierCursus)
}

/** Un exemplaire par durée : le prix des paliers fixes est identique pour tous les
 * cursus, la grille n'a pas à répéter les offres telles quelles. */
function paliersUniquesParDuree(plans: Plan[]): Plan[] {
  const parDuree = new Map<number, Plan>()
  plans.forEach((plan) => {
    if (!parDuree.has(plan.duration_days)) parDuree.set(plan.duration_days, plan)
  })
  return Array.from(parDuree.values()).sort((a, b) => a.duration_days - b.duration_days)
}

/**
 * Coût ramené à une unité lisible. Le mois est l'unité de comparaison de la grille
 * (voir DUREE_REFERENCE_JOURS) : "1 233 FCFA/mois" se compare d'un coup d'œil aux
 * 2 000 FCFA du palier d'entrée, là où "41 FCFA/jour" impose une multiplication
 * mentale avant de valoir quelque chose. Le palier d'entrée EST un mois - y répéter
 * son propre prix n'apprendrait rien, il affiche donc son coût journalier, le chiffre
 * qui le rend concret. "Mois" vaut ici 30 jours, la même convention que celle qui
 * fait appeler "1 mois" le palier de 30 jours : l'économie annoncée est donc
 * légèrement sous-estimée plutôt que flattée.
 */
function prixUnitaire(prix: number, dureeJours: number): string {
  if (dureeJours <= DUREE_REFERENCE_JOURS) {
    return `≈ ${formatAmount(Math.round(prix / dureeJours))} FCFA/jour`
  }
  return `≈ ${formatAmount(Math.round(prix / (dureeJours / 30)))} FCFA/mois`
}

/** Prix au jour du palier de référence d'une grille, base des économies affichées.
 * `null` si cette grille n'a pas de palier de référence : aucune économie n'est alors
 * annonçable, plutôt qu'un pourcentage calculé sur un palier arbitraire. */
function refParJourDe(tiers: Plan[]): number | null {
  const ref = tiers.find((t) => t.duration_days === DUREE_REFERENCE_JOURS)
  return ref ? ref.price / ref.duration_days : null
}

function economie(tier: Plan, refParJour: number | null): number | null {
  if (!refParJour || tier.duration_days === DUREE_REFERENCE_JOURS) return null
  const pourcent = Math.round((1 - tier.price / tier.duration_days / refParJour) * 100)
  return pourcent >= ECONOMIE_MIN_AFFICHEE ? pourcent : null
}

/** Badge d'économie par rapport au palier mensuel de la même grille. */
function BadgeEconomie({ pourcent }: { pourcent: number }) {
  return (
    <span className="rounded-full bg-success/10 px-2 py-0.5 text-[11px] font-semibold text-success">
      -{pourcent} % vs 1 mois
    </span>
  )
}

/** Puce de réassurance du hero - même gabarit que /quiz, /fiches et /cours. */
function ChipReassurance({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
      {icon}
      <span className="text-muted-foreground">{children}</span>
    </span>
  )
}

// Miroir volontaire de subscriptions.models.{PLANCHER_JUSQUA_EXAMEN,
// INCREMENT_PAR_TRANCHE, JOURS_PAR_TRANCHE} - recalculés ici pour dessiner
// l'échéancier visuel ci-dessous, jamais pour fixer un prix (toujours
// jusquaExamen.effective_price/.price, qui viennent du serveur - voir Echeancier).
// Grille "Septembre 12 000 F ... Juin 3 000 F", décision utilisateur du 2026-08-19 :
// si elle change côté backend, ces trois constantes doivent suivre.
const PLANCHER_AFFICHE = 3000
const PALIER_AFFICHE = 1000
const JOURS_PAR_TRANCHE_AFFICHE = 30

type EtapeEcheancier = { tranche: number; prix: number }

/** Une marche par tranche de prix, de la plus loin de l'examen (plafond, tranche la
 * plus haute) à la plus proche (plancher, tranche 0) - voir Echeancier. */
function construireEcheancier(plafond: number): EtapeEcheancier[] {
  const nbTranches = Math.round((plafond - PLANCHER_AFFICHE) / PALIER_AFFICHE)
  return Array.from({ length: nbTranches + 1 }, (_, i) => {
    const tranche = nbTranches - i
    return { tranche, prix: Math.min(plafond, PLANCHER_AFFICHE + tranche * PALIER_AFFICHE) }
  })
}

/**
 * Échéancier visuel de Jusqu'à l'Examen : une marche par mois entamé, du plafond
 * (loin de l'examen, à gauche) au plancher (dernier mois, à droite) - rend concret
 * "plus tu t'abonnes tôt, moins tu payes" au lieu de le laisser en simple phrase.
 * La marche de l'utilisateur (déduite de son cursus, donc de la vraie date
 * d'examen - jamais un mois calendaire supposé) est repérée par un badge doré
 * plutôt que noyée dans la liste.
 */
function Echeancier({ plan }: { plan: Plan }) {
  const etapes = useMemo(() => construireEcheancier(plan.price), [plan.price])
  const trancheActuelle = Math.min(
    etapes[0]?.tranche ?? 0,
    Math.floor(plan.effective_duration_days / JOURS_PAR_TRANCHE_AFFICHE),
  )

  return (
    <div className="rounded-xl border border-primary/15 bg-primary/[0.03] p-4">
      <p className="text-xs font-medium text-muted-foreground">
        Le tarif baisse à chaque mois qui passe, jusqu'à ton examen
      </p>
      <div className="mt-6 flex items-end gap-1 sm:gap-1.5" role="img" aria-label={`Grille de prix par mois, de ${formatAmount(etapes[0]?.prix ?? 0)} à ${formatAmount(PLANCHER_AFFICHE)} FCFA`}>
        {etapes.map((etape) => {
          const actif = etape.tranche === trancheActuelle
          const extremite = etape.tranche === etapes[0].tranche || etape.tranche === 0
          const hauteurPx = Math.round(18 + (etape.prix / plan.price) * 74)
          return (
            <div key={etape.tranche} className="relative flex flex-1 flex-col items-center">
              {actif && (
                <span className="absolute -top-6 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full bg-gold px-2 py-0.5 font-display text-[10px] font-semibold tracking-wide text-gold-foreground shadow-sm">
                  Toi
                </span>
              )}
              <div
                className={cn("w-full rounded-t-[3px] transition-colors", actif ? "bg-gold" : "bg-primary/20")}
                style={{ height: `${hauteurPx}px` }}
              />
              <span className={cn("mt-1.5 text-[10px] tabular-nums text-muted-foreground", !extremite && "opacity-0")}>
                {formatAmount(etape.prix)}
              </span>
            </div>
          )
        })}
      </div>
      <div className="mt-0.5 flex justify-between text-[10px] text-muted-foreground">
        <span>Rentrée</span>
        <span>Jour de l'examen</span>
      </div>
      <p className="mt-2 text-center text-[11px] text-muted-foreground">
        <span className="font-medium text-gold">Dernière ligne droite</span> : {formatAmount(PLANCHER_AFFICHE)} FCFA
        garantis, même à la veille de l'examen.
      </p>
    </div>
  )
}

/** Callout unique, seul argument mis en avant sur la carte (voir son usage plus bas) :
 * les annales seules sont gratuites ailleurs, ce qui justifie le prix d'Edukora ce
 * sont les à-côtés introuvables ailleurs - un entraînement au format et au programme
 * réels de l'examen (inédites), et la connaissance de ce qui tombe vraiment
 * (classement des thèmes fréquents, voir ThemesFrequents.tsx côté catalogue). */
function CalloutExclusifsJusquaExamen() {
  return (
    <div className="flex items-start gap-2.5 rounded-lg border border-gold/30 bg-gold/[0.06] px-3 py-2.5">
      <Crown className="mt-0.5 size-4 shrink-0 text-gold" />
      <div>
        <p className="flex items-center gap-1 font-display text-[11px] font-semibold uppercase tracking-wide text-gold">
          <Sparkles className="size-3" />
          Exclusif Edukora
        </p>
        <p className="mt-0.5 text-sm text-foreground">
          Épreuves inédites incluses - des sujets originaux conçus pour ton programme et le format de ton examen.
        </p>
        <p className="mt-1 text-sm text-foreground">
          « Les thèmes qui reviennent le plus » - le classement des notions les plus posées à ton examen, calculé sur les vraies annales.
        </p>
      </div>
    </div>
  )
}

function CarteSquelette() {
  return (
    <Card className="flex flex-col" aria-hidden>
      <CardHeader className="gap-2">
        <div className="h-5 w-24 animate-pulse rounded bg-muted" />
        <div className="h-4 w-16 animate-pulse rounded bg-muted" />
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4">
        <div className="h-9 w-32 animate-pulse rounded bg-muted" />
        <div className="flex flex-col gap-2">
          <div className="h-4 w-full animate-pulse rounded bg-muted" />
          <div className="h-4 w-4/5 animate-pulse rounded bg-muted" />
          <div className="h-4 w-3/5 animate-pulse rounded bg-muted" />
        </div>
      </CardContent>
    </Card>
  )
}

export function PricingPage() {
  useSeo({
    title: "Tarifs",
    description: `Abonnement ${SITE_NAME} par Mobile Money : au mois, ou jusqu'à ton examen, pour accéder à tous les corrigés et cours de ton cursus.`,
  })

  const navigate = useNavigate()
  const { country } = useCountry()
  const [allPlans, setAllPlans] = useState<Plan[]>([])
  const [chargement, setChargement] = useState(true)
  const [selectedCursus, setSelectedCursus] = useState("")
  const [selectedCursusRepetiteur, setSelectedCursusRepetiteur] = useState("")
  // Passe à true quand on tente de continuer sans avoir choisi de cursus : le
  // sélecteur se signale au lieu de laisser un bouton inerte sans explication.
  const [cursusManquant, setCursusManquant] = useState(false)
  // Passe brièvement à true au tout premier choix de cursus, pour un léger encadré
  // sur "Ta formule" pendant le scroll - jamais retriggée sur un changement de cursus
  // suivant (voir l'effet plus bas), pour ne pas ressauter sous les yeux de qui compare
  // déjà les formules après un premier choix.
  const [formuleMiseEnAvant, setFormuleMiseEnAvant] = useState(false)
  const aDejaScrolleVersFormule = useRef(false)
  const cursusRef = useRef<HTMLDivElement>(null)
  const formuleRef = useRef<HTMLDivElement>(null)
  const cursusRepetiteurRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    listPlans()
      .then(setAllPlans)
      .finally(() => setChargement(false))
  }, [])

  const abonnements = useMemo(
    () => allPlans.filter((p) => p.product_type === "ABONNEMENT"),
    [allPlans],
  )
  // Grille à 2 paliers du 2026-08-19 (voir migration subscriptions/0009_grille_deux_
  // paliers) : Mensuel (durée fixe, prix uniforme par cursus) et Jusqu'à l'Examen
  // (dépend du cursus choisi, prix/durée calculés depuis la session d'examen réelle -
  // voir Plan.effective_price/effective_duration_days). `tiers` ne porte donc plus
  // que Mensuel en pratique (les autres paliers fixes historiques sont désactivés),
  // mais reste générique par durée plutôt que single-valeur : un futur palier fixe
  // réapparaîtrait dans la grille sans changement de code ici.
  const tiers = useMemo(
    () => paliersUniquesParDuree(abonnements.filter((p) => p.duration_mode === "FIXE")),
    [abonnements],
  )
  const refParJour = useMemo(() => refParJourDe(tiers), [tiers])

  // Le Pack "Jusqu'à l'Examen" dépend du cursus (son prix et sa durée courent jusqu'à
  // la session) : il n'entre pas dans `tiers` et n'apparaît qu'une fois le cursus
  // choisi. Aucun filtre de fenêtre d'urgence ici - l'API ne renvoie plus ce plan hors
  // fenêtre (voir Plan.est_achetable côté backend), qui est le seul endroit où cette
  // règle vit.
  const jusquaExamen = allPlans.find(
    (p) =>
      p.product_type === "ABONNEMENT" &&
      p.duration_mode === "JUSQUA_EXAMEN" &&
      String(p.cursus.id) === selectedCursus,
  )

  // Plafond réel de la grille Jusqu'à l'Examen, lu sur les plans chargés plutôt que
  // recopié en dur (comme PLANCHER_AFFICHE) : contrairement au plancher, qui est une
  // constante Python partagée par tous les cursus (voir PLANCHER_JUSQUA_EXAMEN côté
  // backend), le plafond est le champ `price` de chaque Plan, seedé à 12 000 FCFA pour
  // tous les cursus par la migration 0009 mais modifiable cursus par cursus depuis
  // l'admin - un futur écart entre cursus resterait donc correct ici. Sert à afficher
  // une fourchette avant le choix du cursus plutôt qu'un plancher nu (voir son usage
  // plus bas) : montrer "dès 3 000 FCFA" seul, puis révéler 11 000 FCFA après le choix
  // du cursus, ressemble à un prix d'appel - la fourchette annonce l'écart d'emblée.
  const plafondJusquaExamen = useMemo(() => {
    const prix = allPlans
      .filter((p) => p.product_type === "ABONNEMENT" && p.duration_mode === "JUSQUA_EXAMEN")
      .map((p) => p.price)
    return prix.length > 0 ? Math.max(...prix) : null
  }, [allPlans])

  const cursusEleve = useMemo(() => cursusVendables(allPlans, "ABONNEMENT"), [allPlans])
  const cursusRepetiteur = useMemo(() => cursusVendables(allPlans, "ADDON_REPETITEUR"), [allPlans])

  const repetiteurTiers = useMemo(
    () =>
      paliersUniquesParDuree(
        allPlans.filter((p) => p.product_type === "ADDON_REPETITEUR" && p.duration_mode === "FIXE"),
      ),
    [allPlans],
  )
  // Une référence par offre, jamais une seule pour les deux : l'add-on Fiches a sa
  // propre grille (3 000 F le mois là où l'abonnement est à 2 000), comparer son
  // annuel au mois de l'abonnement élève afficherait une économie qui n'existe pas.
  const refParJourRepetiteur = useMemo(() => refParJourDe(repetiteurTiers), [repetiteurTiers])

  // Un seul cursus vendable (cas actuel de l'add-on Fiches) : le faire choisir n'a
  // aucun sens, on le présélectionne.
  useEffect(() => {
    if (cursusRepetiteur.length === 1) setSelectedCursusRepetiteur(String(cursusRepetiteur[0].id))
  }, [cursusRepetiteur])

  useEffect(() => {
    if (selectedCursus) setCursusManquant(false)
  }, [selectedCursus])

  // Premier choix de cursus : la grille de formules (déjà visible, mais parfois hors
  // écran sur mobile juste sous le sélecteur) se signale et défile jusqu'à l'écran -
  // sans ça, rien n'indique que choisir un cursus vient de débloquer l'étape suivante.
  useEffect(() => {
    if (!selectedCursus || aDejaScrolleVersFormule.current) return
    aDejaScrolleVersFormule.current = true
    formuleRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
    setFormuleMiseEnAvant(true)
    const timer = setTimeout(() => setFormuleMiseEnAvant(false), 1600)
    return () => clearTimeout(timer)
  }, [selectedCursus])

  function choisirFormule(dureeParam: string) {
    if (!selectedCursus) {
      setCursusManquant(true)
      cursusRef.current?.scrollIntoView({ behavior: "smooth", block: "center" })
      return
    }
    navigate(`/abonnement?cursus=${selectedCursus}&duree=${dureeParam}`)
  }

  function handleSubscribeRepetiteur() {
    if (!selectedCursusRepetiteur) {
      cursusRepetiteurRef.current?.scrollIntoView({ behavior: "smooth", block: "center" })
      return
    }
    navigate(`/abonnement?cursus=${selectedCursusRepetiteur}&require=repetiteur`)
  }

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      {/* Même gabarit de hero que /quiz, /fiches et /cours. Un seul titre, là où la
          page en empilait deux ("Choisis ton profil." puis "Un seul prix...") avant
          d'avoir rien dit du prix ni de la façon de payer. Les trois puces répondent
          d'entrée aux objections qui bloquent un achat Mobile Money : combien, avec
          quoi, et est-ce que ça va me prélever tous les mois. */}
      <div className="relative mb-8 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.08] via-transparent to-transparent p-6 sm:p-10">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        {/* Halo doré, décentré - profondeur discrète derrière le titre plutôt qu'un
            fond plat, sans concurrencer la grille de prix qui doit rester l'élément
            le plus lu de la page. */}
        <div
          className="pointer-events-none absolute -right-24 -top-24 size-72 rounded-full bg-gold/10 blur-3xl"
          aria-hidden
        />
        <div className="relative max-w-2xl">
          <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Sparkles className="size-5" />
          </div>
          <p className="mb-1 font-display text-sm italic text-primary">Tarifs</p>
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">
            Plus tôt tu t'abonnes, <span className="text-primary">moins tu payes</span>.
          </h1>
          <p className="mt-2 text-muted-foreground">
            Un mois simple pour tester, ou un forfait qui suit ton année scolaire et devient moins cher chaque mois
            qui passe - jusqu'à ton examen.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <ChipReassurance icon={<Smartphone className="size-3.5 text-primary" />}>
              Mobile Money (MTN, Orange)
            </ChipReassurance>
            <ChipReassurance icon={<ShieldCheck className="size-3.5 text-success" />}>
              Aucun prélèvement automatique
            </ChipReassurance>
            <ChipReassurance icon={<Zap className="size-3.5 text-gold" />}>
              Accès activé dès le paiement
            </ChipReassurance>
          </div>
        </div>
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
          {/* Le cursus est demandé AVANT les formules, pas après : c'est lui qui
              conditionne le prix de Jusqu'à l'Examen affiché plus bas et la
              destination du bouton de chaque carte. Le parcours devient "je choisis
              mon cursus, je clique ma formule, je paie" au lieu de "je lis les
              formules, je redescends choisir un cursus, je clique Continuer sans
              savoir quelle formule je viens de prendre".
              Pas de badge "1"/"2" numéroté ici (essayé puis retiré) : les deux cartes de
              formule affichent déjà un prix réel sans cursus choisi (voir jusquaExamen et
              plafondJusquaExamen plus bas) - un numéro de pastille suggérait une page à
              débloquer étape par étape, comme un formulaire de commande, alors qu'on peut
              déjà tout lire sans rien choisir. Même style de titre que "Compris dans les
              deux formules" plus bas, pour que ce soit un intitulé de section, pas une
              étape de wizard. */}
          <div
            ref={cursusRef}
            className={cn(
              "mx-auto mt-2 max-w-md scroll-mt-24 rounded-xl border bg-card p-5 shadow-sm transition-colors",
              cursusManquant ? "border-primary ring-2 ring-primary/30" : "border-border",
            )}
          >
            <p className="mb-2.5 font-display font-semibold">Ton cursus</p>
            <CursusChips
              liste={cursusEleve}
              selected={selectedCursus}
              onSelect={setSelectedCursus}
              label="Ton cursus"
              describedBy="cursus-eleve-aide"
            />
            <p
              id="cursus-eleve-aide"
              role={cursusManquant ? "alert" : undefined}
              className={cn("mt-2 text-xs", cursusManquant ? "text-primary" : "text-muted-foreground")}
            >
              {cursusManquant
                ? "Choisis d'abord ton cursus, puis reprends la formule que tu veux."
                : "Tu pourras en changer plus tard depuis ton compte."}
            </p>
          </div>

          {/* ref + surbrillance temporaire : voir l'effet qui défile ici au premier
              choix de cursus. rounded-2xl + ring-offset donnent un encadré visible même
              sans fond propre (la Card ci-dessous garde le sien) - transition-shadow
              plutôt que "hidden ring" pour que l'apparition/disparition soit un
              fondu, pas un saut. */}
          <div
            ref={formuleRef}
            className={cn(
              "scroll-mt-24 rounded-2xl transition-shadow duration-500",
              formuleMiseEnAvant && "ring-2 ring-primary/40 ring-offset-4 ring-offset-background",
            )}
          >
            <p className="mx-auto mb-4 max-w-md pt-9 font-display font-semibold">Ta formule</p>

            {/* items-start (pas le stretch par défaut de la grille) : Jusqu'à l'Examen
                (callout + échéancier une fois le cursus choisi) et Mensuel n'ont pas la
                même hauteur de contenu. Étirer les deux cartes à la même hauteur créait un
                vide interne dans la plus courte plutôt que deux cartes de hauteurs
                naturelles différentes - un vide est pire qu'une asymétrie. */}
            <div className="grid grid-cols-1 items-start gap-5 sm:grid-cols-2">
            {chargement && tiers.length === 0 ? (
              <>
                <CarteSquelette />
                <CarteSquelette />
              </>
            ) : (
              <>
                {tiers.map((tier) => {
                  const pourcent = economie(tier, refParJour)
                  return (
                    <Card key={tier.duration_days} className="relative flex flex-col">
                      <CardHeader>
                        <CardTitle className="font-display text-lg">Mensuel</CardTitle>
                        <CardDescription>{tierDuration(tier.duration_days)} - pour tester ou réviser une notion précise</CardDescription>
                      </CardHeader>
                      <CardContent className="flex flex-1 flex-col gap-4">
                        <div>
                          <p className="font-display text-3xl font-semibold text-primary">
                            {formatAmount(tier.price)}
                            <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
                          </p>
                          <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
                            <p className="text-xs text-muted-foreground">{prixUnitaire(tier.price, tier.duration_days)}</p>
                            {pourcent !== null && <BadgeEconomie pourcent={pourcent} />}
                          </div>
                        </div>
                        <Button
                          onClick={() => choisirFormule(String(tier.duration_days))}
                          variant="outline"
                          size="lg"
                          className="mt-auto w-full"
                        >
                          Choisir Mensuel
                        </Button>
                      </CardContent>
                    </Card>
                  )
                })}

                {/* Offre principale de la grille (voir la refonte du 2026-08-19) : mise
                    en avant au même titre que Mensuel plutôt que reléguée en simple
                    encart sous la grille, pour qu'un élève dont l'examen approche la
                    voie tout de suite comme une vraie option, pas comme une note de bas
                    de page. */}
                <Card
                  className={cn(
                    "relative flex flex-col",
                    jusquaExamen && "border-primary shadow-lg shadow-primary/10 sm:-my-2 sm:scale-[1.03]",
                  )}
                >
                  {jusquaExamen && (
                    <>
                      {/* Liseré doré en tête de carte - seul détail "premium" propre à
                          l'offre phare, pour que la mise en avant tienne à la finition
                          plutôt qu'au seul badge flottant. rounded-t-lg (pas
                          overflow-hidden sur la Card) pour ne pas rogner le badge
                          "Offre principale" juste en dessous, qui déborde volontairement
                          au-dessus du cadre. */}
                      <div className="absolute inset-x-0 top-0 h-1 rounded-t-lg bg-gradient-to-r from-gold via-primary to-gold" aria-hidden />
                      <span className="absolute -top-3 left-1/2 flex -translate-x-1/2 items-center gap-1 whitespace-nowrap rounded-full bg-primary px-3 py-1 font-display text-xs font-semibold tracking-wide text-primary-foreground shadow-sm">
                        <Sparkles className="size-3" />
                        Offre principale
                      </span>
                    </>
                  )}
                  <CardHeader>
                    <CardTitle className="font-display text-lg">Jusqu'à l'Examen</CardTitle>
                    <CardDescription>Toute l'année scolaire, jusqu'au jour de l'examen</CardDescription>
                  </CardHeader>
                  {/* Le prix reste visible cursus ou non (voir jusquaExamen) - avant, la
                      carte cachait tout chiffre tant que le cursus n'était pas choisi
                      ("Choisis ton cursus pour voir le prix exact"), alors que c'est
                      justement ce qu'on vient chercher sur une page Tarifs. Une fourchette
                      complète (plancher-plafond, voir plafondJusquaExamen) plutôt qu'un
                      "Dès 3 000 FCFA" isolé, essayé puis abandonné : un plancher nu se lit
                      comme LE prix, et le révéler à 11 000 FCFA une fois le cursus choisi
                      ressemble à un prix d'appel - la fourchette annonce l'écart avant
                      même le clic. Seuls l'échéancier et le prix exact dépendent du
                      cursus. Un seul argument texte (le callout) plutôt que callout + puces
                      + note de délai empilés : la répétition des trois bénéfices déjà
                      listés dans "Compris dans les deux formules" plus bas n'apprenait
                      rien de plus ici. */}
                  <CardContent className="flex flex-1 flex-col gap-4">
                    <CalloutExclusifsJusquaExamen />
                    {jusquaExamen ? (
                      <>
                        <div>
                          <p className="font-display text-3xl font-semibold text-primary">
                            {formatAmount(jusquaExamen.effective_price)}
                            <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
                          </p>
                          <p className="mt-0.5 text-xs text-muted-foreground">
                            ≈ {formatAmount(Math.round(jusquaExamen.effective_price / jusquaExamen.effective_duration_days))} FCFA/jour
                            {" - "}
                            ton {jusquaExamen.cursus.examen_display} commence le{" "}
                            {formatDateDansNJours(jusquaExamen.effective_duration_days)}
                          </p>
                        </div>
                        <Echeancier plan={jusquaExamen} />
                        <Button onClick={() => choisirFormule("examen")} size="lg" className="mt-auto w-full">
                          Prendre le Pack Examen
                        </Button>
                      </>
                    ) : (
                      <>
                        <div>
                          <p className="font-display text-3xl font-semibold text-primary">
                            {formatAmount(PLANCHER_AFFICHE)}
                            <span className="mx-1.5 text-lg font-normal text-muted-foreground">-</span>
                            {formatAmount(plafondJusquaExamen ?? PLANCHER_AFFICHE)}
                            <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
                          </p>
                          <p className="mt-0.5 text-xs text-muted-foreground">
                            Selon le temps qu'il te reste avant ton examen - {formatAmount(PLANCHER_AFFICHE)} FCFA le
                            dernier mois.
                          </p>
                        </div>
                        {/* Cliquable, jamais disabled - un bouton mort ne donne aucun
                            feedback au clic et peut passer pour une page cassée.
                            choisirFormule gère déjà l'absence de cursus (voir sa
                            définition) en signalant le sélecteur et en y défilant, exactement
                            le même comportement que "Choisir Mensuel" juste à côté : les
                            deux cartes réagissent maintenant pareil à un clic prématuré. */}
                        <Button
                          onClick={() => choisirFormule("examen")}
                          variant="outline"
                          size="lg"
                          className="mt-auto w-full"
                        >
                          Choisir Jusqu'à l'Examen
                        </Button>
                      </>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
            </div>
          </div>

          {/* Le socle commun aux deux formules, énoncé une fois et en grand plutôt que
              recopié en petit sur chaque carte : ce qu'on achète ne dépend pas de la
              durée choisie, seul le temps d'accès change. */}
          <div className="mt-6 rounded-xl border border-border bg-card p-5 sm:p-6">
            <p className="font-display font-semibold">Compris dans les deux formules</p>
            <ul className="mt-3 grid gap-2.5 text-sm sm:grid-cols-3">
              <li className="flex items-start gap-2">
                <Check className="mt-0.5 size-4 shrink-0 text-success" />
                <span>
                  Corrigés complets en illimité
                  <span className="block text-xs text-muted-foreground">
                    Annales et sujets, rédigés pas à pas.
                  </span>
                </span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="mt-0.5 size-4 shrink-0 text-success" />
                <span>
                  Cours et exercices d'application
                  <span className="block text-xs text-muted-foreground">
                    Méthode, exemple résolu, erreurs classiques.
                  </span>
                </span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="mt-0.5 size-4 shrink-0 text-success" />
                <span>
                  Le quiz qui cible tes révisions
                  <span className="block text-xs text-muted-foreground">
                    Il repère tes lacunes et te les repropose au bon moment.
                  </span>
                </span>
              </li>
            </ul>
          </div>

          {/* L'encart "Prêt à t'abonner ?" vivait ici, sans bouton (chaque carte porte
              déjà le sien - "Choisir Mensuel"/"Prendre le Pack Examen") : une invite à
              agir qui ne menait nulle part elle-même, retirée plutôt que complétée.
              La mention Mobile Money vivait ici aussi, en 12 px sous la grille. Elle est
              remontée dans les puces du hero et détaillée dans les questions en bas de
              page : la répéter une troisième fois ne rassurait personne. */}
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

          {/* Les paliers de l'add-on tenaient dans deux boîtes grises de la largeur
              d'un pouce, sans prix unitaire, sans liste, sans mise en avant - un
              produit à part entière traité comme une note de bas de page à côté de la
              grille élève. Même gabarit de carte que celle-ci, à deux colonnes. */}
          {repetiteurTiers.length > 0 && (
            <div className="mx-auto mt-8 grid max-w-2xl grid-cols-1 gap-5 sm:grid-cols-2">
              {repetiteurTiers.map((tier) => {
                const pourcent = economie(tier, refParJourRepetiteur)
                return (
                <Card key={tier.duration_days} className="flex flex-col">
                  <CardHeader>
                    <CardTitle className="font-display text-lg">Add-on Fiches</CardTitle>
                    <CardDescription>{tierDuration(tier.duration_days)}</CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-1 flex-col gap-4">
                    <div>
                      <p className="font-display text-3xl font-semibold text-primary">
                        {formatAmount(tier.price)}
                        <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
                      </p>
                      {/* L'intérêt de l'annuel était invisible : ni prix ramené au mois,
                          ni économie affichée, alors que la grille élève avait les deux. */}
                      <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
                        <p className="text-xs text-muted-foreground">{prixUnitaire(tier.price, tier.duration_days)}</p>
                        {pourcent !== null && <BadgeEconomie pourcent={pourcent} />}
                      </div>
                    </div>
                    <ul className="mt-auto flex flex-col gap-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <FileText className="mt-0.5 size-4 shrink-0 text-success" />
                        Fiches illimitées, énoncé + corrigé
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="mt-0.5 size-4 shrink-0 text-success" />
                        Deux PDF à ton nom, prêts à imprimer
                      </li>
                    </ul>
                  </CardContent>
                </Card>
                )
              })}
            </div>
          )}
          {/* Add-on distinct de l'abonnement classique (voir SubscribePage.tsx) - ne
              débloque jamais, à lui seul, les corrigés/cours de l'onglet Élève.
              Précisé ici plutôt que supposé implicite : même risque de confusion déjà
              identifié pour l'add-on Épreuves Inédites. */}
          <p className="mx-auto mt-3 max-w-md text-center text-xs text-muted-foreground">
            Add-on séparé de l'abonnement classique - ne débloque pas les corrigés.
          </p>

          <div
            ref={cursusRepetiteurRef}
            className="mx-auto mt-9 max-w-md scroll-mt-24 rounded-xl border border-border bg-card p-6 text-center shadow-sm"
          >
            <h3 className="mb-1 font-display text-lg font-semibold">Prêt à débloquer l'add-on ?</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              {cursusRepetiteur.length > 1
                ? "Choisis ton cursus pour continuer."
                : "L'outil Fiches est disponible sur le cursus ci-dessous."}
            </p>
            {/* Un seul cursus vendable : aucune puce à afficher, le message ci-dessus
                suffit à dire lequel (voir la présélection automatique plus haut). */}
            {cursusRepetiteur.length > 1 && (
              <div className="mb-4">
                <CursusChips
                  liste={cursusRepetiteur}
                  selected={selectedCursusRepetiteur}
                  onSelect={setSelectedCursusRepetiteur}
                  label="Ton cursus"
                  centre
                />
              </div>
            )}
            <Button
              onClick={handleSubscribeRepetiteur}
              disabled={!selectedCursusRepetiteur}
              size="lg"
              className="w-full sm:w-auto"
            >
              S'abonner
            </Button>
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

      {/* Hors des onglets : ces quatre points valent pour les deux offres. Une page de
          tarifs sans réponse aux objections laisse l'acheteur seul avec ses doutes au
          moment précis où il doit sortir son téléphone - c'était le trou le plus large
          de cette page.
          Chaque affirmation est vérifiable dans le code, aucune n'est du copywriting :
          absence de prélèvement (aucun mécanisme de reconduction côté subscriptions),
          cumul des jours (Subscription.extend repart de expires_at quand l'abonnement
          court encore), lecture hors connexion (Workbox met /access/read/ et
          /access/cours/read/ en StaleWhileRevalidate, voir vite.config.ts). */}
      <section className="mt-12 border-t border-border pt-10">
        <h2 className="font-display text-xl font-semibold">Avant de payer</h2>
        <dl className="mt-5 grid gap-5 sm:grid-cols-2">
          <div className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Smartphone className="size-4" />
            </span>
            <div>
              <dt className="font-medium">Comment je paie ?</dt>
              <dd className="mt-0.5 text-sm text-muted-foreground">
                Par Mobile Money, MTN ou Orange. Aucune carte bancaire n'est nécessaire, et ton accès s'ouvre dès la
                confirmation du paiement.
              </dd>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-success/10 text-success">
              <ShieldCheck className="size-4" />
            </span>
            <div>
              <dt className="font-medium">Est-ce que je serai prélevé chaque mois ?</dt>
              <dd className="mt-0.5 text-sm text-muted-foreground">
                Non. Tu paies une fois, pour la durée choisie. À la fin, l'accès s'arrête simplement - rien n'est
                reconduit sans que tu le demandes.
              </dd>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <CalendarPlus className="size-4" />
            </span>
            <div>
              <dt className="font-medium">Et si je reprends avant la fin ?</dt>
              <dd className="mt-0.5 text-sm text-muted-foreground">
                Les jours s'ajoutent à ceux qu'il te reste, ils ne repartent pas de zéro. Tu ne perds jamais du temps
                déjà payé.
              </dd>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-gold/10 text-gold">
              <WifiOff className="size-4" />
            </span>
            <div>
              <dt className="font-medium">Il me faut de la connexion en permanence ?</dt>
              <dd className="mt-0.5 text-sm text-muted-foreground">
                Non. Un corrigé ou un cours déjà ouvert une fois reste consultable sans réseau - de quoi réviser dans
                le taxi ou en zone mal couverte.
              </dd>
            </div>
          </div>
        </dl>

        {/* Jamais "/cm/cours" en dur : /tarifs n'est pas une route préfixée par pays,
            le pays courant vient donc du contexte (URL précédente, sinon dernier choix
            mémorisé) - voir CountryContext et coursListPath. */}
        <button
          type="button"
          onClick={() => navigate(coursListPath(country))}
          className="group mt-8 inline-flex items-center gap-1.5 text-sm font-medium text-primary underline-offset-4 hover:underline"
        >
          Voir ce qu'il y a à lire avant de te décider
          <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
        </button>
      </section>
    </div>
  )
}
