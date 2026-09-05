import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { useNavigate } from "react-router-dom"
import {
  ArrowRight,
  ArrowRightLeft,
  Check,
  Crown,
  FileText,
  Lock,
  ShieldCheck,
  Smartphone,
  Sparkles,
  Users,
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
import { SocialProofSection } from "@/components/SocialProofSection"

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
// Grille "Septembre 20 000 F ... Juin 4 000 F" (plancher et plafond relevés deux fois
// le 2026-09-05, voir subscriptions.models.py) : si elle change côté backend, ces
// trois constantes doivent suivre.
const PLANCHER_AFFICHE = 4000
const PALIER_AFFICHE = 2000
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
          Tu sauras ce que tu dois réviser en priorité : « les thèmes qui reviennent le plus », le classement des notions les plus posées à ton examen, calculé sur les vraies annales.
        </p>
      </div>
    </div>
  )
}

export function PricingPage() {
  useSeo({
    title: "Tarifs",
    description: `Abonnement ${SITE_NAME} par Mobile Money, jusqu'à ton examen, pour accéder à tous les corrigés et cours de ton cursus.`,
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
  const cursusRef = useRef<HTMLDivElement>(null)
  const cursusRepetiteurRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    listPlans()
      .then(setAllPlans)
      .finally(() => setChargement(false))
  }, [])

  // Offre unique depuis le 2026-08-30 (voir migration subscriptions/0013_retire_
  // mensuel) : Mensuel est désactivé, Jusqu'à l'Examen est la seule formule vendue aux
  // élèves. Son prix et sa durée dépendent du cursus choisi, calculés depuis la
  // session d'examen réelle - voir Plan.effective_price/effective_duration_days.
  // Aucun filtre de fenêtre d'urgence ici - l'API ne renvoie plus ce plan hors fenêtre
  // (voir Plan.est_achetable côté backend), qui est le seul endroit où cette règle vit.
  const jusquaExamen = allPlans.find(
    (p) =>
      p.product_type === "ABONNEMENT" &&
      p.duration_mode === "JUSQUA_EXAMEN" &&
      String(p.cursus.id) === selectedCursus,
  )

  // Plafond réel de la grille Jusqu'à l'Examen, lu sur les plans chargés plutôt que
  // recopié en dur (comme PLANCHER_AFFICHE) : contrairement au plancher, qui est une
  // constante Python partagée par tous les cursus (voir PLANCHER_JUSQUA_EXAMEN côté
  // backend), le plafond est le champ `price` de chaque Plan, seedé à 12 000 FCFA par
  // la migration 0009, relevé à 15 000 par la 0014 puis 20 000 par la 0015, mais modifiable cursus par cursus depuis
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

  // Un seul paramètre `duree=examen` possible depuis le retrait de Mensuel (voir
  // 0013_retire_mensuel) - plus besoin de le paramétrer par appelant.
  function choisirFormule() {
    if (!selectedCursus) {
      setCursusManquant(true)
      cursusRef.current?.scrollIntoView({ behavior: "smooth", block: "center" })
      return
    }
    navigate(`/abonnement?cursus=${selectedCursus}&duree=examen`)
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
          {/* Tutoiement de bout en bout, y compris l'onglet Répétiteur plus bas
              (décision du 2026-09-05) : un brouillon non commité vouvoyait cette page
              ("acheteur adulte" payeur), rompant avec le reste du site (accueil, quiz,
              corrigés) qui tutoie l'élève partout - jamais mergé, donc sans effet sur
              la version publiée, mais présent dans l'arbre de travail. Écarté au
              profit de la cohérence de ton déjà en place ailleurs. */}
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">
            Plus tôt tu t'abonnes, <span className="text-primary">plus tu économises</span>.
          </h1>
          <p className="mt-2 text-muted-foreground">
            Un abonnement valable jusqu'à ton examen, dont le prix baisse chaque mois qui passe.
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
          {/* Cursus et prix fusionnés dans un seul panneau large (retouche du 2026-08-30) :
              deux colonnes séparées par une bordure à partir de sm, plutôt que deux
              boîtes à max-w-md empilées avec plein de vide de chaque côté sur desktop -
              défaut resté depuis la grille à deux formules (Mensuel + Jusqu'à l'Examen),
              qui n'a plus lieu d'être avec une offre unique. Choisir un cursus met à jour
              le prix juste à côté, sans scroll ni "étape 2" à débloquer : plus besoin de
              l'effet qui défilait vers un second bloc pour le révéler (formuleRef/
              formuleMiseEnAvant, retirés) - les deux tiennent déjà dans le même regard. */}
          <div className="relative mx-auto max-w-3xl overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            <div className="h-1 bg-gradient-to-r from-gold via-primary to-gold" aria-hidden />
            <div className="grid grid-cols-1 sm:grid-cols-2">
              <div
                ref={cursusRef}
                className={cn(
                  "scroll-mt-24 p-6 transition-colors",
                  cursusManquant && "ring-2 ring-inset ring-primary/40",
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
                    ? "Choisis d'abord ton cursus, puis reprends ton abonnement."
                    : "Rien n'est engagé avant le paiement - change de cursus ici autant que tu veux."}
                </p>

                {/* Rapatrié depuis sa propre boîte sous le panneau (retouche du
                    2026-08-30) : la colonne de droite grandit beaucoup plus que
                    celle-ci une fois l'échéancier affiché (mesuré : jusqu'à 536 px de
                    vide sous les puces sur desktop) - autant combler cet espace avec du
                    vrai contenu déjà présent sur la page plutôt qu'un centrage
                    artificiel ou une boîte séparée en plus. Liste verticale, pas la
                    grille sm:grid-cols-3 de l'ancienne boîte pleine largeur : cette
                    colonne fait environ la moitié de cette largeur. */}
                <div className="mt-6 border-t border-border pt-5">
                  <p className="font-display text-sm font-semibold">Tout ce dont tu as besoin pour préparer ton examen</p>
                  <ul className="mt-3 flex flex-col gap-2.5 text-sm">
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
                    <li className="flex items-start gap-2">
                      <Check className="mt-0.5 size-4 shrink-0 text-success" />
                      <span>
                        Épreuves inédites Edukora
                        <span className="block text-xs text-muted-foreground">
                          Des sujets originaux, jamais vus ailleurs, au format de ton examen.
                        </span>
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="mt-0.5 size-4 shrink-0 text-success" />
                      <span>
                        Les thèmes qui reviennent le plus
                        <span className="block text-xs text-muted-foreground">
                          Le classement des notions les plus posées, calculé sur les vraies annales.
                        </span>
                      </span>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="border-t border-border p-6 sm:border-l sm:border-t-0">
                {chargement && allPlans.length === 0 ? (
                  <div className="flex flex-col gap-4" aria-hidden>
                    <div className="h-4 w-28 animate-pulse rounded bg-muted" />
                    <div className="h-16 w-full animate-pulse rounded-lg bg-muted" />
                    <div className="h-9 w-32 animate-pulse rounded bg-muted" />
                    <div className="h-28 w-full animate-pulse rounded bg-muted" />
                  </div>
                ) : (
                  <>
                    <p className="font-display font-semibold">Jusqu'à l'Examen</p>
                    <p className="text-sm text-muted-foreground">Toute l'année scolaire, jusqu'au jour de l'examen</p>
                    {/* Le prix reste visible cursus ou non (voir jusquaExamen) - avant, la
                        colonne cachait tout chiffre tant que le cursus n'était pas choisi
                        ("Choisis ton cursus pour voir le prix exact"), alors que c'est
                        justement ce qu'on vient chercher sur une page Tarifs. Une fourchette
                        complète (plancher-plafond, voir plafondJusquaExamen) plutôt qu'un
                        "Dès 2 000 FCFA" isolé, essayé puis abandonné : un plancher nu se lit
                        comme LE prix, et le révéler beaucoup plus haut une fois le cursus
                        choisi ressemble à un prix d'appel - la fourchette annonce l'écart
                        avant même le clic. Seuls l'échéancier et le prix exact dépendent du
                        cursus.
                        Le prix passe AVANT le callout "Exclusif Edukora" (inversé le
                        2026-08-30) : sur une page Tarifs, c'est la première chose qu'on
                        scanne - le callout vient ensuite justifier ce chiffre plutôt que
                        retarder sa lecture. */}
                    <div className="mt-4 flex flex-col gap-4">
                      {jusquaExamen ? (
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
                      ) : (
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
                      )}
                      <CalloutExclusifsJusquaExamen />
                      {jusquaExamen ? (
                        <>
                          <Echeancier plan={jusquaExamen} />
                          <Button onClick={choisirFormule} size="lg" className="w-full">
                            S'abonner
                          </Button>
                        </>
                      ) : (
                        // "Choisir ton cursus", pas "S'abonner" : dans cet état,
                        // selectedCursus est par définition vide (voir jusquaExamen plus
                        // haut), le clic ne fait jamais que signaler la colonne de gauche -
                        // le libellé doit décrire CETTE action, pas l'achat qui suivra.
                        // Cliquable, jamais disabled - un bouton mort ne donne aucun
                        // feedback au clic et peut passer pour une page cassée.
                        <Button onClick={choisirFormule} variant="outline" size="lg" className="w-full">
                          Choisir ton cursus
                        </Button>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* L'encart "Prêt à t'abonner ?" vivait ici, sans bouton (la carte porte déjà
              le sien) : une invite à agir qui ne menait nulle part elle-même, retirée
              plutôt que complétée. La mention Mobile Money vivait ici aussi, en 12 px
              sous la grille. Elle est remontée dans les puces du hero et détaillée dans
              les questions en bas de page : la répéter une troisième fois ne rassurait
              personne. */}
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

      {/* Preuve sociale réelle (voir l'audit UX, reco 8.3) juste après les prix, avant
          la FAQ qui traite les dernières objections - de vrais témoignages publiés
          depuis l'admin (jamais générés), déjà utilisés sur /epreuves. Disparaît
          silencieusement tant qu'aucun n'est publié (voir SocialProofSection), donc
          jamais un bloc vide sur cette page.
          -mx-4 sm:-mx-6 annule le padding horizontal du conteneur racine de cette
          page : SocialProofSection porte déjà son propre mx-auto max-w-5xl px-4, pensé
          pour un parent sans contrainte de largeur (voir son usage sur CataloguePage) -
          sans ça le padding se cumule et le bloc paraît plus étroit que le reste de la
          page. */}
      <div className="-mx-4 sm:-mx-6">
        <SocialProofSection />
      </div>

      {/* Hors des onglets : ces quatre points valent pour les deux offres. Une page de
          tarifs sans réponse aux objections laisse l'acheteur seul avec ses doutes au
          moment précis où il doit sortir son téléphone - c'était le trou le plus large
          de cette page. Revue le 2026-08-30 pour l'offre unique Jusqu'à l'Examen : les
          deux anciennes entrées ("prélevé chaque mois", "je reprends avant la fin")
          présupposaient encore un rythme mensuel hérité du palier Mensuel retiré (voir
          0013_retire_mensuel) - remplacées par des objections qui tiennent pour un
          paiement unique valable jusqu'à l'examen.
          Chaque affirmation est vérifiable dans le code, aucune n'est du copywriting :
          les deux modes de paiement (Campay automatique vs paiement manuel + déclaration
          admin, voir payments/models.py Transaction/ManualPayment et campay_client.py),
          l'absence de tout prélèvement récurrent (aucun cron/webhook de reconduction),
          et le prix figé au jour de l'achat (Plan.effective_price/effective_duration_days
          n'est lu qu'une fois, à l'activation - voir subscriptions/models.py). */}
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
                Par Mobile Money, MTN ou Orange. Avec Campay, la demande de paiement arrive directement sur ton
                téléphone pour une activation instantanée ; tu peux aussi transférer toi-même et déclarer ta
                transaction.
              </dd>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-success/10 text-success">
              <ShieldCheck className="size-4" />
            </span>
            <div>
              <dt className="font-medium">Est-ce que je serai prélevé une deuxième fois ?</dt>
              <dd className="mt-0.5 text-sm text-muted-foreground">
                Non. Chaque paiement est unique et volontaire - aucune carte enregistrée, aucun renouvellement
                automatique. Rien ne se redéclenche sans que tu repasses toi-même par Mobile Money.
              </dd>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-gold/10 text-gold">
              <Lock className="size-4" />
            </span>
            <div>
              <dt className="font-medium">Le prix payé aujourd'hui reste-t-il garanti jusqu'à mon examen ?</dt>
              <dd className="mt-0.5 text-sm text-muted-foreground">
                Oui. Le tarif est figé le jour de l'achat et couvre l'accès jusqu'à ton examen, même si le prix
                affiché baisse ensuite pour ceux qui achètent plus tard.
              </dd>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <ArrowRightLeft className="size-4" />
            </span>
            <div>
              <dt className="font-medium">Et si le paiement Mobile Money échoue ?</dt>
              <dd className="mt-0.5 text-sm text-muted-foreground">
                Tu peux basculer sur le paiement manuel (Orange Money ou MTN MoMo) sans rien perdre de ta sélection -
                un transfert direct, vérifié avant activation.
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
          Découvrir un cours avant de t'abonner
          <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
        </button>
      </section>
    </div>
  )
}
