import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { createPortal } from "react-dom"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import {
  ArrowRight,
  ArrowRightLeft,
  CalendarCheck,
  CalendarClock,
  Check,
  ChevronDown,
  Lock,
  ShieldCheck,
  Smartphone,
  Sparkles,
  Zap,
} from "lucide-react"

import { listPlans } from "@/api/endpoints"
import { trackEvent } from "@/lib/analytics"
import type { Cursus, Plan } from "@/api/types"
import { cn, formatAmount } from "@/lib/utils"
import { coursListPath } from "@/lib/countryPath"
import { codeSerieAffiche } from "@/lib/cursus"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { useCursusDeclare } from "@/lib/cursusAccueil"
import { BandeauCampagne } from "@/components/BandeauCampagne"
import { BandeauEnfantVise } from "@/components/BandeauEnfantVise"
import { dateLimiteCampagne, useCampagne } from "@/lib/campagne"
import { usePaymentConfig } from "@/lib/paymentConfig"
import { useSeo } from "@/lib/seo"
import { CONTACT_WHATSAPP_AFFICHAGE, CONTACT_WHATSAPP_URL, EDITEUR_NOM, SITE_NAME } from "@/lib/site"
import { Button } from "@/components/ui/button"
import { ComparatifFascicule } from "@/components/ComparatifFascicule"
import { ErreurChargement } from "@/components/ErreurChargement"
import { SocialProofSection } from "@/components/SocialProofSection"
import { LienAide } from "@/components/aide/LienAide"
import { delaiVerificationPaiementAffiche } from "@/lib/delaiVerificationPaiement"
import { langueCourante, t, tn, useI18n } from "@/lib/i18n"
import {
  MOIS_PAR_DEFAUT, PRIX_MOIS_FCFA, estAuMois, moisValides, prixTotal,
  prixTotalReference,
} from "@/lib/tarifs"
import { ChoixDuree, RecapDuree } from "@/components/SelecteurDuree"

function cursusLabel(cursus: Cursus): string {
  if (cursus.series?.code.startsWith("GCE_")) return `${cursus.examen_display} - ${codeSerieAffiche(cursus.series)}`
  return `${cursus.examen_display}${cursus.series ? ` - ${t("prix.serie", { code: cursus.series.code })}` : ""}`
}

// Ordre de lecture attendu par un élève (du plus jeune au plus avancé), et non
// l'ordre de création en base (qui entrelace Probatoire et BAC série par série).
const ORDRE_EXAMENS_FR = ["BEPC", "PROBATOIRE", "BAC", "GCE_OL", "GCE_AL", "AUTRE"]
// Interface anglaise : le GCE d'abord. Un élève anglophone cherchait « GCE O Level » tout au bout d'une liste de
// cursus francophones (audit du 2026-11-12, UX-13).
const ORDRE_EXAMENS_EN = ["GCE_OL", "GCE_AL", "BEPC", "PROBATOIRE", "BAC", "AUTRE"]

function ordreExamens(): string[] {
  return langueCourante() === "en" ? ORDRE_EXAMENS_EN : ORDRE_EXAMENS_FR
}

function trierCursus(a: Cursus, b: Cursus): number {
  const ordre = ordreExamens()
  const rang = ordre.indexOf(a.examen) - ordre.indexOf(b.examen)
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
  const ordre = ordreExamens()
  return Array.from(groupes.values()).sort((a, b) => ordre.indexOf(a.examen) - ordre.indexOf(b.examen))
}

function ChipCursus({ texte, selected, onClick }: { texte: string; selected: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      className={cn(
        // min-h-11 : cible tactile de 44 px, sinon la puce ne fait qu'une trentaine de pixels de haut.
        "inline-flex min-h-11 min-w-11 items-center justify-center rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
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
  // Les examens sans série (BEPC, GCE O Level, GCE A Level) n'ont pas d'en-tête de groupe : la puce
  // porte directement leur nom. Plutôt qu'une puce pleine largeur par ligne, les examens sans série
  // qui se suivent dans l'ordre de lecture partagent une même rangée.
  const rangees = useMemo(() => {
    const resultat: Array<{ cle: string; groupe?: GroupeCursus; simples?: Cursus[] }> = []
    groupes.forEach((groupe) => {
      if (groupe.cursus.length === 1 && !groupe.cursus[0].series) {
        const derniere = resultat[resultat.length - 1]
        if (derniere?.simples) derniere.simples.push(groupe.cursus[0])
        else resultat.push({ cle: `simples-${groupe.examen}`, simples: [groupe.cursus[0]] })
      } else {
        resultat.push({ cle: groupe.examen, groupe })
      }
    })
    return resultat
  }, [groupes])
  return (
    <div
      role="group"
      aria-label={label}
      aria-describedby={describedBy}
      className={cn("flex flex-col gap-3", centre ? "items-center" : "items-start")}
    >
      {rangees.map((rangee) =>
        rangee.simples ? (
          <div key={rangee.cle} className={cn("flex flex-wrap gap-2", centre && "justify-center")}>
            {rangee.simples.map((c) => (
              <ChipCursus
                key={c.id}
                texte={cursusLabel(c)}
                selected={selected === String(c.id)}
                onClick={() => onSelect(String(c.id))}
              />
            ))}
          </div>
        ) : (
          // Mobile : l'intitulé passe au-dessus des puces, sinon « TI » tombait seule sur une 2e ligne
          // (4,5 rem d'intitulé + cinq puces de 44 px ne tiennent pas en 303 px).
          <div
            key={rangee.cle}
            className={cn("flex flex-wrap items-center gap-x-2 gap-y-1.5", centre && "justify-center")}
          >
            <span className="w-full text-xs font-medium text-muted-foreground sm:w-[4.5rem] sm:shrink-0">
              {rangee.groupe!.examenLabel}
            </span>
            {rangee.groupe!.cursus.map((c) => (
              <ChipCursus
                key={c.id}
                texte={c.series ? codeSerieAffiche(c.series) : cursusLabel(c)}
                selected={selected === String(c.id)}
                onClick={() => onSelect(String(c.id))}
              />
            ))}
          </div>
        ),
      )}
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

/** Ce que contient l'abonnement, dans l'ordre d'affichage. Les deux derniers sont les seuls
 * introuvables ailleurs : ils portent la pastille « Exclusif ». */
const AVANTAGES: Array<{
  titre: Parameters<typeof t>[0]
  texte: Parameters<typeof t>[0]
  exclusif: boolean
}> = [
  { titre: "prix.inclus1_titre", texte: "prix.inclus1_texte", exclusif: false },
  { titre: "prix.inclus2_titre", texte: "prix.inclus2_texte", exclusif: false },
  { titre: "prix.inclus3_titre", texte: "prix.inclus3_texte", exclusif: false },
  { titre: "prix.inclus4_titre", texte: "prix.inclus4_texte", exclusif: true },
  { titre: "prix.inclus5_titre", texte: "prix.inclus5_texte", exclusif: true },
]

/** Puce de réassurance du hero - même gabarit que /quiz et /cours (plus petite sur mobile, où les
 * trois puces occupaient près de 200 px de haut). */
function ChipReassurance({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-2.5 py-1 text-xs sm:px-3 sm:py-1.5 sm:text-sm">
      {icon}
      <span className="text-muted-foreground">{children}</span>
    </span>
  )
}

/** Titre d'une étape du calculateur : un numéro et son intitulé, pour que l'ordre des choix se lise d'un coup d'œil. */
function EtapeTitre({ n, children }: { n: number; children: ReactNode }) {
  return (
    <p className="mb-2.5 flex items-center gap-2 font-display font-semibold">
      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
        {n}
      </span>
      {children}
    </p>
  )
}

/**
 * Le prix pour une famille, rendu concret par un petit tableau plutôt qu'une phrase. Aucune remise
 * famille (décision du 2026-11-13) : chaque enfant paie le prix du mois (`plan.effective_price`, campagne
 * comprise), le tableau n'est donc qu'une multiplication.
 */
function TarifFamille({ plan }: { plan: Plan }) {
  const total = (nbEnfants: number) => nbEnfants * plan.effective_price

  // Replié : une ligne suffit à la plupart des visiteurs, et le tableau ne doit pas allonger la colonne du bouton.
  return (
    <details className="group rounded-xl border border-primary/15 bg-primary/[0.03] px-4 py-2">
      <summary className="flex min-h-9 cursor-pointer list-none items-center justify-between gap-2 text-sm font-medium [&::-webkit-details-marker]:hidden">
        <span>{t("prix.famille_resume")}</span>
        <ChevronDown
          className="size-4 shrink-0 text-muted-foreground transition-transform group-open:rotate-180"
          aria-hidden
        />
      </summary>
      <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1.5 pb-1 text-sm">
        {[1, 2, 3, 4].map((n) => (
          <div key={n} className="contents">
            <dt className="text-muted-foreground">{tn("prix.enfants", n)}</dt>
            <dd className="text-right font-medium tabular-nums">
              {formatAmount(total(n))} FCFA{" "}
              <span className="text-xs font-normal text-muted-foreground">{t("prix.par_mois_court")}</span>
            </dd>
          </div>
        ))}
      </dl>
    </details>
  )
}

/** Pastille « Exclusif » des deux avantages introuvables ailleurs : les annales seules sont
 * gratuites ailleurs, ce qui justifie le prix d'Edukora ce sont les épreuves inédites et le
 * classement des thèmes fréquents. Elle remplace l'encart doré qui répétait ces deux lignes
 * juste sous la liste des avantages. */
function PastilleExclusif() {
  return (
    <span className="ml-1.5 inline-flex items-center gap-0.5 whitespace-nowrap rounded-full bg-gold/15 px-1.5 py-0.5 align-middle font-display text-[10px] font-semibold uppercase tracking-wide text-gold-text">
      <Sparkles className="size-2.5" aria-hidden />
      {t("prix.exclusif", { site: SITE_NAME })}
    </span>
  )
}

/** Barre d'action collée en bas de l'écran sur mobile : le bouton de la carte se trouve à ~3 écrans du
 * haut, et rien ne le gardait à portée de pouce. Elle se retire quand le bouton de la carte est visible. */
function BarreActionMobile({
  prix,
  prixBarre,
  sousTexte,
  libelle,
  onClick,
}: {
  prix: number
  prixBarre?: number
  /** Ce que le prix couvre : « par mois et par enfant » ou « pour 5 mois ». */
  sousTexte: string
  libelle: string
  onClick: () => void
}) {
  // Portail : le conteneur de la page porte `animate-fade-up` (transform), qui devient le repère des
  // éléments `fixed` - sans portail, la barre se collait au bas de la page entière et non de l'écran.
  return createPortal(
    <div
      // Au-dessus de la barre d'onglets des élèves connectés (--bottom-tab-bar, publiée par BottomTabBar).
      style={{ bottom: "var(--bottom-tab-bar, 0px)" }}
      className="fixed inset-x-0 z-30 border-t border-border bg-background/95 px-4 py-2.5 pb-[calc(0.625rem+env(safe-area-inset-bottom))] shadow-[0_-4px_12px_rgba(0,0,0,0.06)] backdrop-blur sm:hidden"
    >
      <div className="mx-auto flex max-w-5xl items-center gap-3">
        <div className="min-w-0 shrink-0">
          <p className="font-display text-lg font-semibold leading-tight text-primary tabular-nums">
            {formatAmount(prix)} <span className="text-xs font-normal text-muted-foreground">FCFA</span>
            {prixBarre !== undefined && (
              <s className="ml-1.5 text-xs font-normal text-muted-foreground">{formatAmount(prixBarre)}</s>
            )}
          </p>
          <p className="text-[11px] leading-tight text-muted-foreground">{sousTexte}</p>
        </div>
        <Button onClick={onClick} className="min-w-0 flex-1">
          <span className="truncate">{libelle}</span>
        </Button>
      </div>
    </div>,
    document.body,
  )
}

export function PricingPage() {
  // S'abonne au changement de langue : les `t(...)` de la page se relisent à chaque bascule.
  useI18n()
  useSeo({
    // « Prix » seul disait trop peu dans un onglet ou un résultat de recherche (audit du 2026-11-12, SEO-06).
    title: t("prix.seo_titre"),
    description: t("prix.seo_description", { site: SITE_NAME }),
  })

  const navigate = useNavigate()
  const { country } = useCountry()
  // Campay coupé côté serveur : la FAQ ne doit plus promettre une activation instantanée.
  const { campayActif } = usePaymentConfig()
  const { isAuthenticated } = useAuth()
  const campagne = useCampagne()
  const [allPlans, setAllPlans] = useState<Plan[]>([])
  // Présent quand on arrive ici pour acheter l'abonnement d'un enfant qu'on vient de
  // créer ("Ajouter un enfant", AccesPage.tsx) - relayé tel quel vers /abonnement,
  // jamais interprété ici.
  const [searchParams] = useSearchParams()
  const profilParam = searchParams.get("profil")

  useEffect(() => {
    trackEvent("tarifs_vus")
  }, [])
  const [chargement, setChargement] = useState(true)
  // Échec du chargement des offres : sans ce signal, `planTarif` restait indéfini et le bloc
  // prix affichait « 0 FCFA » - un prix faux, pire qu'une absence de prix.
  const [erreurPlans, setErreurPlans] = useState(false)
  // Incrémenté par « Réessayer » pour relancer l'effet de chargement.
  const [tentative, setTentative] = useState(0)
  const [selectedCursus, setSelectedCursus] = useState("")
  // Le nombre de mois choisi par le visiteur (null : pas encore touché, voir `mois` plus bas).
  const [moisChoisi, setMoisChoisi] = useState<number | null>(null)
  // Passe à true quand on tente de continuer sans avoir choisi de cursus : le
  // sélecteur se signale au lieu de laisser un bouton inerte sans explication.
  const [cursusManquant, setCursusManquant] = useState(false)

  // Un élève qui a déjà déclaré ce qu'il prépare (voir User.cursus_prepare) n'a pas à
  // le redire ici : sans cette préselection, il ne voit pas le nombre de jours avant son
  // examen. Le prix, lui, est le même pour tous les cursus.
  // Il reste libre d'en choisir un autre - le sélecteur n'est pas verrouillé, et son choix
  // manuel gagne (la condition `!selectedCursus` ci-dessous ne le réécrit jamais).
  const cursusDeclare = useCursusDeclare()
  useEffect(() => {
    if (cursusDeclare === null || selectedCursus) return
    setSelectedCursus(String(cursusDeclare))
  }, [cursusDeclare, selectedCursus])
  const cursusRef = useRef<HTMLDivElement>(null)
  // Bloc du bouton principal : la barre d'action mobile ne s'affiche que lorsqu'il est hors écran.
  const ctaRef = useRef<HTMLDivElement>(null)
  const [ctaVisible, setCtaVisible] = useState(false)

  useEffect(() => {
    const cible = ctaRef.current
    if (!cible || typeof IntersectionObserver === "undefined") return
    const observateur = new IntersectionObserver(([entree]) => setCtaVisible(entree.isIntersecting))
    observateur.observe(cible)
    return () => observateur.disconnect()
    // Le bloc n'existe qu'une fois les offres chargées.
  }, [chargement, erreurPlans])

  useEffect(() => {
    let annule = false
    listPlans()
      .then((plans) => {
        if (!annule) setAllPlans(plans)
      })
      .catch(() => {
        if (!annule) setErreurPlans(true)
      })
      .finally(() => {
        if (!annule) setChargement(false)
      })
    return () => {
      annule = true
    }
  }, [tentative])

  function reessayerPlans() {
    setErreurPlans(false)
    setChargement(true)
    setTentative((n) => n + 1)
  }

  // Offre unique depuis le 2026-11-11 : l'abonnement au mois (2 000 FCFA par mois), dont l'élève choisit le
  // nombre de mois. Le prix du mois est le même pour tous les cursus ; ce qui change d'un cursus à l'autre, c'est
  // le nombre de mois qu'on peut acheter (`mois_max` : jusqu'à la fin de l'examen, calculé par le serveur).
  const planCursus = allPlans.find(
    (p) => p.product_type === "ABONNEMENT" && estAuMois(p) && String(p.cursus.id) === selectedCursus,
  )

  // Plan servant à afficher le prix du mois : celui du cursus choisi, sinon n'importe quel plan au mois.
  const planTarif = useMemo(
    () => planCursus ?? allPlans.find((p) => p.product_type === "ABONNEMENT" && estAuMois(p)),
    [planCursus, allPlans],
  )

  const cursusEleve = useMemo(() => cursusVendables(allPlans, "ABONNEMENT"), [allPlans])

  useEffect(() => {
    if (selectedCursus) setCursusManquant(false)
  }, [selectedCursus])

  // Le nombre de mois retenu : le choix du visiteur, sinon un trimestre - toujours ramené à ce que le plan autorise.
  const mois = planCursus ? moisValides(planCursus, moisChoisi ?? MOIS_PAR_DEFAUT) : MOIS_PAR_DEFAUT
  const totalChoisi = planCursus ? prixTotal(planCursus, mois) : 0

  // La durée choisie ici arrive présélectionnée dans le tunnel (`?mois=`) : le choix n'est jamais perdu.
  function choisirFormule(source: "bouton" | "barre") {
    trackEvent("tarifs_bouton_clic", {
      source,
      cursus_id: selectedCursus ? Number(selectedCursus) : undefined,
      mois: planCursus ? mois : undefined,
    })
    if (!selectedCursus) {
      setCursusManquant(true)
      cursusRef.current?.scrollIntoView({ behavior: "smooth", block: "center" })
      return
    }
    // `recap` : le choix (cursus, mois, total) accompagne le visiteur jusqu'à la connexion, qui le rappelle -
    // sinon l'écran de connexion ne dit rien de ce qu'il vient de choisir.
    const recap = planCursus
      ? tn("prix.recap_choix", mois, { cursus: cursusLabel(planCursus.cursus), montant: formatAmount(totalChoisi) })
      : undefined
    navigate(`/abonnement?cursus=${selectedCursus}&mois=${mois}${profilParam ? `&profil=${profilParam}` : ""}`, {
      state: { recap },
    })
  }

  function choisirDuree(n: number) {
    if (n === mois) return
    setMoisChoisi(n)
    trackEvent("tarifs_duree_choisie", {
      mois: n,
      mois_max: planCursus?.mois_max,
      cursus_id: selectedCursus ? Number(selectedCursus) : undefined,
    })
  }

  // Prix et sous-titre du hero : ceux de l'offre en cours (campagne comprise), pour que le haut de page ne
  // dise pas « 2 000 FCFA » pendant que la carte et le bandeau affichent 1 800. Masqué le temps du
  // chargement des offres plutôt que de afficher les montants de référence puis de les corriger.
  const offresPretes = !chargement || allPlans.length > 0
  const prixHero = planTarif?.effective_price ?? PRIX_MOIS_FCFA
  const afficherBarreMobile = !!planTarif && !ctaVisible

  // Les questions fréquentes, les plus bloquantes d'abord : le paiement, le prix exact, le prélèvement.
  const faq = [
    {
      cle: "paiement",
      icone: <Smartphone className="size-4" />,
      teinte: "bg-primary/10 text-primary",
      q: t("prix.faq1_q"),
      r: campayActif ? t("prix.faq1_r_campay") : t("prix.faq1_r_manuel"),
    },
    {
      cle: "prix",
      icone: <Lock className="size-4" />,
      teinte: "bg-gold/10 text-gold-text",
      q: t("prix.faq3_q"),
      r: t("prix.faq3_r", {
        prix: formatAmount(PRIX_MOIS_FCFA),
        prix3: formatAmount(PRIX_MOIS_FCFA * 3),
      }),
    },
    {
      cle: "prelevement",
      icone: <ShieldCheck className="size-4" />,
      teinte: "bg-success/10 text-success",
      q: t("prix.faq2_q"),
      r: t("prix.faq2_r"),
    },
    {
      cle: "fin",
      icone: <CalendarClock className="size-4" />,
      teinte: "bg-primary/10 text-primary",
      q: t("prix.faq5_q"),
      r: t("prix.faq5_r"),
    },
    {
      cle: "maximum",
      icone: <CalendarCheck className="size-4" />,
      teinte: "bg-gold/10 text-gold-text",
      q: t("prix.faq6_q"),
      r: t("prix.faq6_r"),
    },
    {
      cle: "echec",
      icone: <ArrowRightLeft className="size-4" />,
      teinte: "bg-primary/10 text-primary",
      q: campayActif ? t("prix.faq4_q_campay") : t("prix.faq4_q_manuel"),
      r: campayActif ? t("prix.faq4_r_campay") : t("prix.faq4_r_manuel", { delai: delaiVerificationPaiementAffiche() }),
    },
  ]

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 pb-28 pt-6 sm:px-6 sm:pb-10 sm:pt-10">
      <BandeauEnfantVise profilId={profilParam} />
      {campagne && (campagne.cursus.length === 0 || !selectedCursus || campagne.cursus.includes(Number(selectedCursus))) && (
        // Compact : le prix et sa date limite sont déjà dans la carte, juste en dessous.
        <BandeauCampagne
          campagne={campagne}
          prix={campagne.prix}
          prixReference={campagne.prix_reference}
          className="mb-4 sm:mb-6"
          compact
        />
      )}
      {/* Hero compact : le prix se lit tout de suite, mais il ne prend plus un écran entier - le calculateur
          (cursus, durée, total) doit tenir dans le premier écran sur ordinateur. Les trois puces répondent aux
          objections qui bloquent un achat Mobile Money : combien, avec quoi, et est-ce que ça va me prélever. */}
      <div className="relative mb-5 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.08] via-transparent to-transparent p-5 sm:mb-6 sm:p-7">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div
          className="pointer-events-none absolute -right-24 -top-24 size-72 rounded-full bg-gold/10 blur-3xl"
          aria-hidden
        />
        <div className="relative max-w-3xl">
          {/* Tutoiement de bout en bout (décision du 2026-09-05), comme le reste du site. */}
          <h1 className="font-display text-2xl font-semibold leading-[1.15] sm:text-3xl">
            {t("prix.titre_debut")}{" "}
            <span className={cn("whitespace-nowrap text-primary transition-opacity", !offresPretes && "opacity-0")}>
              {t("prix.titre_accent", { prix: formatAmount(prixHero) })}
            </span>
            .
          </h1>
          <p className={cn("mt-1.5 text-sm text-muted-foreground transition-opacity sm:text-base", !offresPretes && "opacity-0")}>
            {t("prix.sous_titre", { prix: formatAmount(prixHero) })}
          </p>

          <div className="mt-3.5 flex flex-wrap gap-2">
            <ChipReassurance icon={<Smartphone className="size-3.5 text-primary" />}>
              Mobile Money (MTN, Orange)
            </ChipReassurance>
            <ChipReassurance icon={<ShieldCheck className="size-3.5 text-success" />}>
              {t("prix.puce_aucun_prelevement")}
            </ChipReassurance>
            <ChipReassurance icon={<Zap className="size-3.5 text-gold-text" />}>
              {/* Même condition que la FAQ plus bas : Campay coupé, l'accès n'est activé qu'après la vérification manuelle. */}
              {campayActif
                ? t("prix.puce_acces_immediat")
                : t("prix.puce_acces_verifie", { delai: delaiVerificationPaiementAffiche() })}
            </ChipReassurance>
          </div>
        </div>
      </div>

      {/* Le calculateur : à gauche les deux choix, dans l'ordre où l'on les fait (1 cursus, 2 durée) ; à droite le
          récapitulatif, collé en haut pendant qu'on choisit, avec le total et le bouton. Avant, le cursus et la durée
          étaient dans deux colonnes différentes et le regard faisait des allers-retours. Sur mobile, les deux blocs
          s'empilent : choix, puis récapitulatif et bouton (le prix est déjà dans le titre, et la barre collée en
          bas garde le bouton à portée de pouce). */}
      {chargement && allPlans.length === 0 ? (
        <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_21rem] lg:grid-cols-[minmax(0,1fr)_23rem]" aria-hidden>
          <div className="h-72 animate-pulse rounded-2xl bg-muted" />
          <div className="h-72 animate-pulse rounded-2xl bg-muted" />
        </div>
      ) : erreurPlans && allPlans.length === 0 ? (
        <ErreurChargement objet={t("prix.objet_tarifs")} onRetry={reessayerPlans} />
      ) : (
        <div className="grid gap-5 md:grid-cols-[minmax(0,1fr)_21rem] md:items-start lg:grid-cols-[minmax(0,1fr)_23rem]">
          <div className="flex flex-col gap-6 rounded-2xl border border-border bg-card p-5 shadow-sm sm:p-6">
            <div
              ref={cursusRef}
              className={cn(
                "scroll-mt-24 rounded-lg",
                cursusManquant && "outline outline-2 outline-offset-8 outline-primary/40",
              )}
            >
              <EtapeTitre n={1}>{t("prix.ton_cursus")}</EtapeTitre>
              <CursusChips
                liste={cursusEleve}
                selected={selectedCursus}
                onSelect={setSelectedCursus}
                label={t("prix.ton_cursus")}
                describedBy="cursus-eleve-aide"
              />
              <p
                id="cursus-eleve-aide"
                role={cursusManquant ? "alert" : undefined}
                className={cn("mt-2 text-xs", cursusManquant ? "text-primary" : "text-muted-foreground")}
              >
                {cursusManquant ? t("prix.cursus_manquant") : t("prix.cursus_aide")}
              </p>
            </div>

            <div className="border-t border-border pt-5">
              <EtapeTitre n={2}>{t("sb.duree_titre")}</EtapeTitre>
              {/* La durée : seulement une fois le cursus connu, puisque le nombre de mois achetables en dépend (il
                  s'arrête à la fin de l'examen). Avant, une phrase dit pourquoi elle n'est pas encore là. */}
              {planCursus ? (
                <ChoixDuree plan={planCursus} mois={mois} onChoisir={choisirDuree} afficherTitre={false} />
              ) : (
                <p className="rounded-xl border border-dashed border-input px-4 py-3 text-sm text-muted-foreground">
                  {t("prix.duree_apres_cursus")}
                </p>
              )}
            </div>
          </div>

          <aside
            aria-label={t("prix.recap_titre")}
            className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-sm md:sticky md:top-24"
          >
            <div className="h-1 bg-gradient-to-r from-gold via-primary to-gold" aria-hidden />
            <div className="flex flex-col gap-4 p-5">
              <div>
                <p className="font-display font-semibold">{t("prix.recap_titre")}</p>
                {/* Prix du mois : le même pour tous les cursus, donc affiché d'emblée. Jamais de repli sur 0 : sans
                    plan chargé, on n'affiche pas de prix du tout. */}
                {planTarif && (
                  <>
                    <p className="mt-1.5 flex flex-wrap items-baseline gap-x-2 font-display text-2xl font-semibold text-primary">
                      <span>
                        {formatAmount(planTarif.effective_price)}
                        <span className="ml-1 text-sm font-normal text-muted-foreground">
                          FCFA {t("prix.par_mois_court")}
                        </span>
                      </span>
                      {planTarif.campagne && (
                        <>
                          <s className="text-base font-normal text-muted-foreground">
                            {formatAmount(planTarif.prix_reference)}
                          </s>
                          <span className="rounded-full bg-gold/15 px-2 py-0.5 text-xs font-semibold text-gold-text">
                            {t("camp.etiquette", { pct: planTarif.campagne.pourcentage })}
                          </span>
                        </>
                      )}
                    </p>
                    {planTarif.campagne && (
                      <p className="mt-0.5 text-xs font-semibold text-gold-text">
                        {t("camp.prix_promo_jusqu_au", { date: dateLimiteCampagne(planTarif.campagne.fin) })}
                      </p>
                    )}
                    <p className="mt-0.5 text-xs text-muted-foreground">{t("prix.par_enfant_court")}</p>
                  </>
                )}
              </div>

              {planCursus ? (
                <div className="flex flex-col gap-3 border-t border-border pt-4">
                  <p className="text-sm font-medium">{cursusLabel(planCursus.cursus)}</p>
                  <RecapDuree plan={planCursus} mois={mois} />
                </div>
              ) : (
                <p className="rounded-xl border border-dashed border-input px-4 py-3 text-sm text-muted-foreground">
                  {t("prix.recap_vide")}
                </p>
              )}

              <div className="flex flex-col gap-3">
                {/* Toujours le bouton principal, plein : « Choisir ton cursus » en contour discret ressemblait à un
                    lien secondaire alors que c'est l'action de la page. Cliquable, jamais disabled - un bouton mort
                    ne donne aucun feedback au clic et peut passer pour une page cassée ; sans cursus, il remonte au
                    choix du cursus et le signale. La barre mobile se retire quand CE bouton est à l'écran. */}
                <div ref={ctaRef}>
                  <Button onClick={() => choisirFormule("bouton")} size="lg" className="w-full">
                    {planCursus
                      ? tn("prix.continuer_mois", mois, { montant: formatAmount(totalChoisi) })
                      : t("prix.choisir_cursus")}
                  </Button>
                </div>
                {/* Le bouton mène à la connexion avant tout paiement : le dire avant le clic (test parent 10-24). */}
                {!isAuthenticated && (
                  <p className="text-center text-xs text-muted-foreground">{t("prix.avant_connexion")}</p>
                )}
                {/* L'essai gratuit se lit ici, à côté du bouton. Jamais "/cm/cours" en dur : /tarifs n'est pas une
                    route préfixée par pays, le pays courant vient du contexte (voir CountryContext et coursListPath). */}
                <p className="text-center text-sm text-muted-foreground">
                  {t("prix.essayer_avant")}{" "}
                  <Link
                    to={coursListPath(country)}
                    className="group inline-flex min-h-11 items-center gap-1 font-medium text-primary underline-offset-4 hover:underline"
                  >
                    {t("prix.decouvrir_cours")}
                    <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
                  </Link>
                </p>
              </div>

              {planTarif && <TarifFamille plan={planTarif} />}
            </div>
          </aside>
        </div>
      )}

      {/* Ce que contient l'abonnement, en bandeau : sous le calculateur, pas dans une colonne qui laissait un grand vide
          à côté du récapitulatif. Les deux avantages introuvables ailleurs sont plus larges et dorés. */}
      <section className="mt-10 sm:mt-12">
        <h2 className="font-display text-xl font-semibold">{t("prix.tout_besoin")}</h2>
        <ul role="list" className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
          {AVANTAGES.map((avantage, index) => (
            <li
              key={avantage.titre}
              className={cn(
                "flex items-start gap-3 rounded-xl border p-4",
                avantage.exclusif ? "border-gold/30 bg-gold/[0.05] lg:col-span-3" : "border-border bg-card lg:col-span-2",
                index === 2 && "sm:col-span-2",
              )}
            >
              <Check className="mt-0.5 size-4 shrink-0 text-success" aria-hidden />
              <span className="text-sm">
                <span className="font-medium">{t(avantage.titre, { site: SITE_NAME })}</span>
                {avantage.exclusif && <PastilleExclusif />}
                <span className="mt-0.5 block text-xs text-muted-foreground">{t(avantage.texte)}</span>
              </span>
            </li>
          ))}
        </ul>
      </section>

      {/* Un parent décide avant de se connecter : le déroulé du paiement et un contact doivent se lire ici, pas
          derrière la connexion (test élève 2026-11-07, « Q6 : peut-être »). En trois étapes côte à côte plutôt
          qu'un encart dans la colonne du bouton. */}
      {!isAuthenticated && (
        <section className="mt-10 sm:mt-12">
          <h2 className="font-display text-xl font-semibold">{t("prix.etapes_titre")}</h2>
          <ol role="list" className="mt-4 grid gap-3 sm:grid-cols-3">
            {(
              [
                t("prix.etape1"),
                t("prix.etape2"),
                campayActif
                  ? t("prix.etape3_immediat")
                  : t("prix.etape3_verifie", { delai: delaiVerificationPaiementAffiche() }),
              ] as string[]
            ).map((texte, i) => (
              <li key={i} className="flex items-start gap-3 rounded-xl border border-border bg-card p-4 text-sm">
                <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                  {i + 1}
                </span>
                <span>{texte}</span>
              </li>
            ))}
          </ol>
          <p className="mt-3 text-sm text-muted-foreground">
            {t("prix.contact_paiement")}{" "}
            <a
              href={CONTACT_WHATSAPP_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-primary underline-offset-2 hover:underline"
            >
              {CONTACT_WHATSAPP_AFFICHAGE}
            </a>
            {" · "}
            {EDITEUR_NOM}
          </p>
          <LienAide slug="comment-payer" className="mt-1">{t("aide.lien.comment_payer")}</LienAide>
        </section>
      )}

      <ComparatifFascicule />

      {/* Preuve sociale réelle (voir l'audit UX, reco 8.3) juste après les prix, avant la FAQ qui traite les
          dernières objections - de vrais témoignages publiés depuis l'admin (jamais générés). Disparaît
          silencieusement tant qu'aucun n'est publié (voir SocialProofSection), donc jamais un bloc vide.
          -mx-4 sm:-mx-6 annule le padding horizontal du conteneur racine : SocialProofSection porte déjà son
          propre mx-auto max-w-5xl px-4. */}
      <div className="-mx-4 sm:-mx-6">
        <SocialProofSection />
      </div>

      {/* Les objections, en accordéon : six réponses courtes qui tenaient sur deux écrans, ouvertes à la demande.
          Les questions de paiement d'abord, c'est là que les parents bloquent. Chaque affirmation est vérifiable
          dans le code (deux modes de paiement Campay et manuel, aucun prélèvement récurrent, durée choisie et
          bornée par la fin de l'examen). */}
      <section className="mt-12 border-t border-border pt-10">
        <h2 className="font-display text-xl font-semibold">{t("prix.avant_payer")}</h2>
        <div className="mt-5 flex max-w-3xl flex-col divide-y divide-border rounded-xl border border-border bg-card">
          {faq.map((question) => (
            <details key={question.cle} className="group px-4">
              <summary className="flex min-h-12 cursor-pointer list-none items-center gap-3 py-2 font-medium [&::-webkit-details-marker]:hidden">
                <span className={cn("flex size-8 shrink-0 items-center justify-center rounded-lg", question.teinte)}>
                  {question.icone}
                </span>
                <span className="min-w-0 flex-1">{question.q}</span>
                <ChevronDown
                  className="size-4 shrink-0 text-muted-foreground transition-transform group-open:rotate-180"
                  aria-hidden
                />
              </summary>
              <p className="pb-4 pl-11 text-sm text-muted-foreground">{question.r}</p>
            </details>
          ))}
        </div>
      </section>

      {afficherBarreMobile && planTarif && (
        <BarreActionMobile
          prix={planCursus ? totalChoisi : planTarif.effective_price}
          prixBarre={
            planTarif.campagne
              ? planCursus ? prixTotalReference(planCursus, mois) : planTarif.prix_reference
              : undefined
          }
          sousTexte={planCursus ? tn("prix.sous_barre_mois", mois) : t("prix.par_enfant")}
          libelle={planCursus ? t("prix.continuer") : t("prix.choisir_cursus_court")}
          onClick={() => choisirFormule("barre")}
        />
      )}
    </div>
  )
}
