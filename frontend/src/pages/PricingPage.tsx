import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { createPortal } from "react-dom"
import { Link, useNavigate, useSearchParams } from "react-router-dom"
import {
  ArrowRight,
  ArrowRightLeft,
  CalendarCheck,
  CalendarClock,
  Check,
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
import { dateLimiteCampagne, nomCampagne, useCampagne } from "@/lib/campagne"
import { usePaymentConfig } from "@/lib/paymentConfig"
import { useSeo } from "@/lib/seo"
import { CONTACT_WHATSAPP_AFFICHAGE, CONTACT_WHATSAPP_URL, EDITEUR_NOM, SITE_NAME } from "@/lib/site"
import { Button } from "@/components/ui/button"
import { ComparatifFascicule } from "@/components/ComparatifFascicule"
import { ErreurChargement } from "@/components/ErreurChargement"
import { SocialProofSection } from "@/components/SocialProofSection"
import { LienAide } from "@/components/aide/LienAide"
import { delaiVerificationPaiementAffiche } from "@/lib/delaiVerificationPaiement"
import { t, tn, useI18n } from "@/lib/i18n"
import {
  MOIS_PAR_DEFAUT, PRIX_MOIS_ENFANT_SUPPLEMENTAIRE_FCFA, PRIX_MOIS_FCFA, estAuMois, moisValides, prixTotal,
  prixTotalReference,
} from "@/lib/tarifs"
import { SelecteurDuree } from "@/components/SelecteurDuree"

function cursusLabel(cursus: Cursus): string {
  if (cursus.series?.code.startsWith("GCE_")) return `${cursus.examen_display} - ${codeSerieAffiche(cursus.series)}`
  return `${cursus.examen_display}${cursus.series ? ` - ${t("prix.serie", { code: cursus.series.code })}` : ""}`
}

// Ordre de lecture attendu par un élève (du plus jeune au plus avancé), et non
// l'ordre de création en base (qui entrelace Probatoire et BAC série par série).
const ORDRE_EXAMENS = ["BEPC", "PROBATOIRE", "BAC", "GCE_OL", "GCE_AL", "AUTRE"]

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

/**
 * Tarif famille, rendu concret par un petit tableau plutôt qu'une phrase. Le tarif de
 * référence vient du serveur (`plan.price`) ; l'enfant supplémentaire en est déduit
 * par la même remise fixe de 20 % que subscriptions.models.REMISE_ENFANT_SUPPLEMENTAIRE_PCT
 * (voir Plan.prix_enfant_supplementaire) - jamais cumulative : le 2e, le 3e, le 4e
 * enfant paient tous le même prix.
 */
function TarifFamille({ plan }: { plan: Plan }) {
  // Pendant une campagne, le premier enfant paie `effective_price` (calculé pour un visiteur sans famille) et
  // les suivants `prix_enfant_supplementaire`, que le serveur donne campagne comprise : la campagne se cumule
  // avec la remise famille (voir Plan.tarif).
  const reference = plan.effective_price
  const supplementaire = plan.prix_enfant_supplementaire
  const total = (nbEnfants: number) => reference + (nbEnfants - 1) * supplementaire

  return (
    <div className="rounded-xl border border-primary/15 bg-primary/[0.03] p-4">
      <p className="text-xs font-medium text-muted-foreground">
        {plan.campagne
          ? t("prix.famille_intro_campagne", { prix: formatAmount(supplementaire), nom: nomCampagne(plan.campagne) })
          : t("prix.famille_intro", { prix: formatAmount(supplementaire) })}
      </p>
      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
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
      {plan.campagne && (
        <p className="mt-3 text-xs text-muted-foreground">
          {t("prix.famille_note_campagne", { nom: nomCampagne(plan.campagne) })}
        </p>
      )}
    </div>
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
    title: t("nav.prix"),
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
    navigate(`/abonnement?cursus=${selectedCursus}&mois=${mois}${profilParam ? `&profil=${profilParam}` : ""}`)
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
  const prixSupHero = planTarif?.prix_enfant_supplementaire ?? PRIX_MOIS_ENFANT_SUPPLEMENTAIRE_FCFA
  const afficherBarreMobile = !!planTarif && !ctaVisible

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
      {/* Même gabarit de hero que /quiz, /fiches et /cours. Un seul titre, là où la
          page en empilait deux ("Choisis ton profil." puis "Un seul prix...") avant
          d'avoir rien dit du prix ni de la façon de payer. Les trois puces répondent
          d'entrée aux objections qui bloquent un achat Mobile Money : combien, avec
          quoi, et est-ce que ça va me prélever tous les mois. */}
      <div className="relative mb-5 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.08] via-transparent to-transparent p-5 sm:mb-8 sm:p-10">
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
          <p className="mb-1 font-display text-sm italic text-primary">{t("nav.prix")}</p>
          {/* Tutoiement de bout en bout (décision du 2026-09-05) : un brouillon non
              commité vouvoyait cette page ("acheteur adulte" payeur), rompant avec le
              reste du site (accueil, quiz, corrigés) qui tutoie l'élève partout - jamais
              mergé, donc sans effet sur la version publiée, mais présent dans l'arbre de
              travail. Écarté au profit de la cohérence de ton déjà en place ailleurs. */}
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">
            {t("prix.titre_debut")}{" "}
            <span className={cn("whitespace-nowrap text-primary transition-opacity", !offresPretes && "opacity-0")}>
              {t("prix.titre_accent", { prix: formatAmount(prixHero) })}
            </span>
            .
          </h1>
          <p className={cn("mt-2 text-muted-foreground transition-opacity", !offresPretes && "opacity-0")}>
            {t("prix.sous_titre", {
              prix: formatAmount(prixHero),
              prix_sup: formatAmount(prixSupHero),
            })}
          </p>

          <div className="mt-4 flex flex-wrap gap-2 sm:mt-5">
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

      {/* Deux offres commerciales cohabitaient ici via des onglets (abonnement élève
          classique, add-on Fiches pour répétiteurs/enseignants) - l'add-on Fiches et le
          public répétiteur/enseignant sont mis en veilleuse (2026-09-15), l'onglet est
          donc retiré et seule l'offre élève reste affichée. */}
      <div className="mt-5 sm:mt-8">
        {/* Une seule carte, deux colonnes à partir de sm (cursus + avantages à gauche, prix + bouton +
            famille à droite). Sur mobile, les deux colonnes passent en `contents` et leurs blocs
            s'ordonnent d'eux-mêmes (max-sm:order-N) : prix → cursus → bouton → avantages → famille →
            étapes. Avant, la colonne du cursus et ses cinq avantages précédaient le prix, qui
            n'apparaissait qu'après deux écrans de défilement, et le bouton arrivait en dernier. */}
        <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
          <div className="h-1 bg-gradient-to-r from-gold via-primary to-gold" aria-hidden />
          <div className="flex flex-col gap-6 p-5 sm:grid sm:grid-cols-2 sm:gap-0 sm:p-0">
            <div className="max-sm:contents sm:flex sm:flex-col sm:gap-6 sm:p-6">
              <div
                ref={cursusRef}
                className={cn(
                  "scroll-mt-24 rounded-lg max-sm:order-2",
                  cursusManquant && "outline outline-2 outline-offset-8 outline-primary/40",
                )}
              >
                <p className="mb-2.5 font-display font-semibold">{t("prix.ton_cursus")}</p>
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

              <div className="border-t border-border pt-5 max-sm:order-5">
                <p className="font-display text-sm font-semibold">{t("prix.tout_besoin")}</p>
                <ul role="list" className="mt-3 flex flex-col gap-2.5 text-sm">
                  {AVANTAGES.map((avantage) => (
                    <li key={avantage.titre} className="flex items-start gap-2">
                      <Check className="mt-0.5 size-4 shrink-0 text-success" aria-hidden />
                      <span>
                        {t(avantage.titre, { site: SITE_NAME })}
                        {avantage.exclusif && <PastilleExclusif />}
                        <span className="block text-xs text-muted-foreground">{t(avantage.texte)}</span>
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="max-sm:contents sm:flex sm:flex-col sm:gap-5 sm:border-l sm:border-border sm:p-6">
              {chargement && allPlans.length === 0 ? (
                <div className="flex flex-col gap-4 max-sm:order-1" aria-hidden>
                  <div className="h-4 w-28 animate-pulse rounded bg-muted" />
                  <div className="h-16 w-full animate-pulse rounded-lg bg-muted" />
                  <div className="h-9 w-32 animate-pulse rounded bg-muted" />
                  <div className="h-28 w-full animate-pulse rounded bg-muted" />
                </div>
              ) : erreurPlans && allPlans.length === 0 ? (
                <ErreurChargement
                  compact
                  objet={t("prix.objet_tarifs")}
                  onRetry={reessayerPlans}
                  className="h-full justify-center max-sm:order-1"
                />
              ) : (
                <>
                  {/* Prix du mois : le même pour tous les cursus, donc affiché d'emblée, avant même le choix
                      du cursus - `planCursus` sert à la durée maximale et au total. */}
                  <div className="max-sm:order-1">
                    <p className="font-display font-semibold">{t("prix.formule")}</p>
                    <p className="hidden text-sm text-muted-foreground sm:block">{t("prix.formule_texte")}</p>
                    <div className="mt-2 sm:mt-4">
                      {/* Jamais de repli sur 0 : sans plan chargé, on n'affiche pas de prix du tout. */}
                      {planTarif && (
                        <p className="flex flex-wrap items-baseline gap-x-2 font-display text-3xl font-semibold text-primary">
                          <span>
                            {formatAmount(planTarif.effective_price)}
                            <span className="ml-1 text-base font-normal text-muted-foreground">
                              FCFA {t("prix.par_mois_court")}
                            </span>
                          </span>
                          {planTarif.campagne && (
                            <>
                              <s className="text-lg font-normal text-muted-foreground">
                                {formatAmount(planTarif.prix_reference)}
                              </s>
                              <span className="rounded-full bg-gold/15 px-2 py-0.5 text-xs font-semibold text-gold-text">
                                {t("camp.etiquette", { pct: planTarif.campagne.pourcentage })}
                              </span>
                            </>
                          )}
                        </p>
                      )}
                      {planTarif?.campagne && (
                        <p className="mt-0.5 text-xs font-semibold text-gold-text">
                          {t("camp.prix_promo_jusqu_au", { date: dateLimiteCampagne(planTarif.campagne.fin) })}
                        </p>
                      )}
                      <p className="mt-0.5 text-xs text-muted-foreground">{t("prix.par_enfant")}</p>
                    </div>
                  </div>

                  {/* La durée : seulement une fois le cursus connu, puisque le nombre de mois achetables en dépend
                      (il s'arrête à la fin de l'examen). Avant, une phrase dit pourquoi elle n'est pas encore là. */}
                  <div className="max-sm:order-3">
                    {planCursus ? (
                      <SelecteurDuree plan={planCursus} mois={mois} onChoisir={choisirDuree} />
                    ) : (
                      <p className="rounded-xl border border-dashed border-input px-4 py-3 text-sm text-muted-foreground">
                        {t("prix.duree_apres_cursus")}
                      </p>
                    )}
                  </div>

                  <div className="flex flex-col gap-3 max-sm:order-4">
                    {/* Toujours le bouton principal, plein : « Choisir ton cursus » en contour discret
                        ressemblait à un lien secondaire alors que c'est l'action de la page. Cliquable,
                        jamais disabled - un bouton mort ne donne aucun feedback au clic et peut passer
                        pour une page cassée ; sans cursus, il remonte au sélecteur et le signale. */}
                    {/* La barre mobile se retire quand CE bouton est à l'écran (et non tout le bloc : le
                        texte sous le bouton gardait la barre cachée alors que le bouton était déjà sorti). */}
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
                    {/* L'essai gratuit se lit ici, à côté du bouton, et non plus tout en bas après la FAQ. */}
                    <p className="text-center text-sm text-muted-foreground">
                      {t("prix.essayer_avant")}{" "}
                      {/* Jamais "/cm/cours" en dur : /tarifs n'est pas une route préfixée par pays, le pays
                          courant vient du contexte (voir CountryContext et coursListPath). */}
                      <Link
                        to={coursListPath(country)}
                        className="group inline-flex min-h-11 items-center gap-1 font-medium text-primary underline-offset-4 hover:underline"
                      >
                        {t("prix.decouvrir_cours")}
                        <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
                      </Link>
                    </p>
                  </div>

                  {planTarif && (
                    <div className="max-sm:order-6">
                      <TarifFamille plan={planTarif} />
                    </div>
                  )}

                  {/* Un parent décide avant de se connecter : le déroulé du paiement et un contact doivent se
                      lire ici, pas derrière la connexion (test élève 2026-11-07, « Q6 : peut-être »). */}
                  {!isAuthenticated && (
                    <div className="rounded-xl border border-border/70 bg-muted/40 px-4 py-3 text-left text-sm max-sm:order-7">
                      <p className="font-medium">{t("prix.etapes_titre")}</p>
                      <ol className="mt-1.5 list-decimal space-y-0.5 pl-5 text-muted-foreground">
                        <li>{t("prix.etape1")}</li>
                        <li>{t("prix.etape2")}</li>
                        <li>
                          {campayActif
                            ? t("prix.etape3_immediat")
                            : t("prix.etape3_verifie", { delai: delaiVerificationPaiementAffiche() })}
                        </li>
                      </ol>
                      <p className="mt-2 text-xs text-muted-foreground">
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
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <ComparatifFascicule />

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

      {/* Une page de
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
        <h2 className="font-display text-xl font-semibold">{t("prix.avant_payer")}</h2>
        <ul role="list" className="mt-5 grid gap-5 sm:grid-cols-2">
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Smartphone className="size-4" />
            </span>
            <div>
              <p className="font-medium">{t("prix.faq1_q")}</p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                {campayActif
                  ? t("prix.faq1_r_campay")
                  : t("prix.faq1_r_manuel")}
              </p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-success/10 text-success">
              <ShieldCheck className="size-4" />
            </span>
            <div>
              <p className="font-medium">{t("prix.faq2_q")}</p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                {t("prix.faq2_r")}
              </p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-gold/10 text-gold-text">
              <Lock className="size-4" />
            </span>
            <div>
              <p className="font-medium">{t("prix.faq3_q")}</p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                {t("prix.faq3_r", {
                  prix: formatAmount(PRIX_MOIS_FCFA),
                  prix3: formatAmount(PRIX_MOIS_FCFA * 3),
                  prix_sup: formatAmount(PRIX_MOIS_ENFANT_SUPPLEMENTAIRE_FCFA),
                })}
              </p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <CalendarClock className="size-4" />
            </span>
            <div>
              <p className="font-medium">{t("prix.faq5_q")}</p>
              <p className="mt-0.5 text-sm text-muted-foreground">{t("prix.faq5_r")}</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-gold/10 text-gold-text">
              <CalendarCheck className="size-4" />
            </span>
            <div>
              <p className="font-medium">{t("prix.faq6_q")}</p>
              <p className="mt-0.5 text-sm text-muted-foreground">{t("prix.faq6_r")}</p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <ArrowRightLeft className="size-4" />
            </span>
            <div>
              <p className="font-medium">
                {campayActif ? t("prix.faq4_q_campay") : t("prix.faq4_q_manuel")}
              </p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                {campayActif
                  ? t("prix.faq4_r_campay")
                  : t("prix.faq4_r_manuel", { delai: delaiVerificationPaiementAffiche() })}
              </p>
            </div>
          </li>
        </ul>
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
