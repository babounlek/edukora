import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import {
  ArrowRight,
  ArrowRightLeft,
  Check,
  Crown,
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
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { Button } from "@/components/ui/button"
import { SocialProofSection } from "@/components/SocialProofSection"

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

/** Puce de réassurance du hero - même gabarit que /quiz et /cours. */
function ChipReassurance({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
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
  const reference = plan.price
  const supplementaire = plan.prix_enfant_supplementaire
  const total = (nbEnfants: number) => reference + (nbEnfants - 1) * supplementaire

  return (
    <div className="rounded-xl border border-primary/15 bg-primary/[0.03] p-4">
      <p className="text-xs font-medium text-muted-foreground">
        Plusieurs enfants ? {formatAmount(supplementaire)} FCFA pour chaque enfant supplémentaire de la même famille
        (20 % de réduction)
      </p>
      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
        {[1, 2, 3, 4].map((n) => (
          <div key={n} className="contents">
            <dt className="text-muted-foreground">{n === 1 ? "1 enfant" : `${n} enfants`}</dt>
            <dd className="text-right font-medium tabular-nums">{formatAmount(total(n))} FCFA</dd>
          </div>
        ))}
      </dl>
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
      <Crown className="mt-0.5 size-4 shrink-0 text-gold-text" />
      <div>
        <p className="flex items-center gap-1 font-display text-xs font-semibold uppercase tracking-wide text-gold-text">
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
    title: "Prix",
    description: `Abonnement ${SITE_NAME} par Mobile Money, jusqu'à ton examen, pour accéder à tous les corrigés et cours de ton cursus.`,
  })

  const navigate = useNavigate()
  const { country } = useCountry()
  const { user } = useAuth()
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
  const [selectedCursus, setSelectedCursus] = useState("")
  // Passe à true quand on tente de continuer sans avoir choisi de cursus : le
  // sélecteur se signale au lieu de laisser un bouton inerte sans explication.
  const [cursusManquant, setCursusManquant] = useState(false)

  // Un élève qui a déjà déclaré ce qu'il prépare (voir User.cursus_prepare) n'a pas à
  // le redire ici : sans cette préselection, il ne voit pas le nombre de jours avant son
  // examen. Le prix, lui, est le même pour tous les cursus.
  // Il reste libre d'en choisir un autre - le sélecteur n'est pas verrouillé, et son choix
  // manuel gagne (la condition `!selectedCursus` ci-dessous ne le réécrit jamais).
  useEffect(() => {
    if (!user?.cursus_prepare || selectedCursus) return
    setSelectedCursus(String(user.cursus_prepare.id))
  }, [user, selectedCursus])
  const cursusRef = useRef<HTMLDivElement>(null)

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

  // Plan servant à afficher le tarif de référence : celui du cursus choisi, sinon n'importe
  // quel plan Jusqu'à l'Examen - depuis le tarif unique du 2026-10-02 (migration
  // subscriptions/0018), le prix est le même pour tous les cursus.
  const planTarif = useMemo(
    () =>
      jusquaExamen ??
      allPlans.find((p) => p.product_type === "ABONNEMENT" && p.duration_mode === "JUSQUA_EXAMEN"),
    [jusquaExamen, allPlans],
  )

  const cursusEleve = useMemo(() => cursusVendables(allPlans, "ABONNEMENT"), [allPlans])

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
    navigate(`/abonnement?cursus=${selectedCursus}&duree=examen${profilParam ? `&profil=${profilParam}` : ""}`)
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
          <p className="mb-1 font-display text-sm italic text-primary">Prix</p>
          {/* Tutoiement de bout en bout (décision du 2026-09-05) : un brouillon non
              commité vouvoyait cette page ("acheteur adulte" payeur), rompant avec le
              reste du site (accueil, quiz, corrigés) qui tutoie l'élève partout - jamais
              mergé, donc sans effet sur la version publiée, mais présent dans l'arbre de
              travail. Écarté au profit de la cohérence de ton déjà en place ailleurs. */}
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">
            Un seul prix, <span className="text-primary">jusqu'à ton examen</span>.
          </h1>
          <p className="mt-2 text-muted-foreground">
            15 000 FCFA par enfant, puis 12 000 FCFA pour chaque enfant supplémentaire de la même famille.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <ChipReassurance icon={<Smartphone className="size-3.5 text-primary" />}>
              Mobile Money (MTN, Orange)
            </ChipReassurance>
            <ChipReassurance icon={<ShieldCheck className="size-3.5 text-success" />}>
              Aucun prélèvement automatique
            </ChipReassurance>
            <ChipReassurance icon={<Zap className="size-3.5 text-gold-text" />}>
              Accès activé dès le paiement
            </ChipReassurance>
          </div>
        </div>
      </div>

      {/* Deux offres commerciales cohabitaient ici via des onglets (abonnement élève
          classique, add-on Fiches pour répétiteurs/enseignants) - l'add-on Fiches et le
          public répétiteur/enseignant sont mis en veilleuse (2026-09-15), l'onglet est
          donc retiré et seule l'offre élève reste affichée. */}
      <div className="mt-8">
        {/* Cursus et prix fusionnés dans un seul panneau large (retouche du 2026-08-30) :
            deux colonnes séparées par une bordure à partir de sm, plutôt que deux
            boîtes à max-w-md empilées avec plein de vide de chaque côté sur desktop -
            défaut resté depuis la grille à deux formules (Mensuel + Jusqu'à l'Examen),
            qui n'a plus lieu d'être avec une offre unique. Choisir un cursus met à jour
            le prix juste à côté, sans scroll ni "étape 2" à débloquer : plus besoin de
            l'effet qui défilait vers un second bloc pour le révéler (formuleRef/
            formuleMiseEnAvant, retirés) - les deux tiennent déjà dans le même regard. */}
        {/* Pleine largeur du conteneur, comme le hero juste au-dessus : le `max-w-3xl`
            précédent laissait la carte visiblement plus étroite que le bandeau qu'elle
            suit, ce qui se lisait comme un décalage plutôt que comme une hiérarchie -
            et sa colonne de droite, la plus dense (prix, encart exclusif, histogramme
            du tarif famille), s'en trouvait comprimée. */}
        <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
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
                    {/* Tarif unique (2026-10-02) : le même prix quel que soit le cursus et
                        le moment de l'année, donc affiché d'emblée, avant même le choix du
                        cursus - `jusquaExamen` sert surtout à la durée et à la date
                        d'examen. Le prix passe AVANT le callout "Exclusif Edukora" : sur
                        une page Tarifs, c'est la première chose qu'on scanne. */}
                    <div className="mt-4 flex flex-col gap-4">
                      <div>
                        <p className="font-display text-3xl font-semibold text-primary">
                          {formatAmount(planTarif?.price ?? 0)}
                          <span className="ml-1 text-base font-normal text-muted-foreground">FCFA</span>
                        </p>
                        <p className="mt-0.5 text-xs text-muted-foreground">
                          par enfant, jusqu'à l'examen
                          {jusquaExamen && (
                            <>
                              {" - "}
                              {jusquaExamen.effective_duration_days} jours avant ton{" "}
                              {jusquaExamen.cursus.examen_display}, qui commence le{" "}
                              {formatDateDansNJours(jusquaExamen.effective_duration_days)}
                            </>
                          )}
                        </p>
                      </div>
                      <CalloutExclusifsJusquaExamen />
                      {planTarif && <TarifFamille plan={planTarif} />}
                      {jusquaExamen ? (
                        <>
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
      </div>

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
        <h2 className="font-display text-xl font-semibold">Avant de payer</h2>
        <ul role="list" className="mt-5 grid gap-5 sm:grid-cols-2">
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Smartphone className="size-4" />
            </span>
            <div>
              <p className="font-medium">Comment je paie ?</p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                Par Mobile Money, MTN ou Orange. Avec Campay, la demande de paiement arrive directement sur ton
                téléphone pour une activation instantanée ; tu peux aussi transférer toi-même et déclarer ta
                transaction.
              </p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-success/10 text-success">
              <ShieldCheck className="size-4" />
            </span>
            <div>
              <p className="font-medium">Est-ce que je serai prélevé une deuxième fois ?</p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                Non. Chaque paiement est unique et volontaire - aucune carte enregistrée, aucun renouvellement
                automatique. Rien ne se redéclenche sans que tu repasses toi-même par Mobile Money.
              </p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-gold/10 text-gold-text">
              <Lock className="size-4" />
            </span>
            <div>
              <p className="font-medium">Le prix change-t-il selon la date d'achat ?</p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                Non. Le prix est de 15 000 FCFA par enfant, quel que soit le moment où tu t'abonnes, et couvre
                l'accès jusqu'à ton examen. Pour chaque enfant supplémentaire de la même famille, c'est 12 000 FCFA.
              </p>
            </div>
          </li>
          <li className="flex items-start gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <ArrowRightLeft className="size-4" />
            </span>
            <div>
              <p className="font-medium">Et si le paiement Mobile Money échoue ?</p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                Tu peux basculer sur le paiement manuel (Orange Money ou MTN MoMo) sans rien perdre de ta sélection -
                un transfert direct, vérifié avant activation.
              </p>
            </div>
          </li>
        </ul>

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
