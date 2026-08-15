import { useEffect, useRef, useState } from "react"
import { Link, useLocation, useParams, useSearchParams } from "react-router-dom"
import { useInfiniteQuery, useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, ChevronDown, Clock, Crown, LayoutGrid, List, Loader2, Search, Sparkles, SlidersHorizontal, X } from "lucide-react"

import heroStudent from "@/assets/hero-student.jpg"
import { getMyProgression, listCursus, listEpreuves, listSubjects } from "@/api/endpoints"
import { trackEvent } from "@/lib/analytics"
import { examLevelsFor, joinExamLevelsFr } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { useDebouncedValue } from "@/lib/useDebouncedValue"
import { epreuveReaderPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"
import { EpreuveRail } from "@/components/EpreuveRail"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveCard } from "@/components/EpreuveCard"
import { EpreuveListRow } from "@/components/EpreuveListRow"
import { SocialProofSection } from "@/components/SocialProofSection"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type ViewMode = "cards" | "list"

// Libellés partagés entre le Select et la puce de filtre actif correspondante -
// une seule source de vérité pour ne jamais les laisser diverger.
const ORIGINE_LABELS: Record<string, string> = {
  OFFICIEL: "Sujet officiel",
  BLANC: "Examen blanc",
  ETABLISSEMENT: "Épreuve d'établissement",
  AUTRE: "Autre",
  INEDITE: "Épreuve inédite",
}
const NATURE_LABELS: Record<string, string> = {
  theorique: "Théorique",
  pratique: "Pratique",
}

interface FilterSelectProps {
  label: string
  value: string
  placeholder: string
  onValueChange: (value: string) => void
  options: { value: string; label: string }[]
}

/** Select de filtre avec son étiquette au-dessus - un utilisateur qui arrive sur la
 * page doit comprendre ce que chaque contrôle filtre sans avoir à cliquer dessus. */
function FilterSelect({ label, value, placeholder, onValueChange, options }: FilterSelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      <Select value={value || "all"} onValueChange={(v) => onValueChange(v === "all" ? "" : v)}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">{placeholder}</SelectItem>
          {options.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

interface FilterChipProps {
  label: string
  onRemove: () => void
}

/** Puce de filtre actif, retirable individuellement - donne un aperçu immédiat de
 * ce qui restreint les résultats, sans avoir à rouvrir chaque menu pour vérifier. */
function FilterChip({ label, onRemove }: FilterChipProps) {
  return (
    <button
      type="button"
      onClick={onRemove}
      className="inline-flex items-center gap-1 rounded-full border border-primary/30 bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/15"
    >
      {label}
      <X className="size-3" />
    </button>
  )
}

const VIEW_MODE_STORAGE_KEY = "edukamer_catalogue_view"

// Portée session (sessionStorage), jamais localStorage : les critères de recherche
// doivent survivre à un aller-retour vers une fiche épreuve (voir "Retour au
// catalogue", qui pointe vers une URL nue plutôt que de dépiler l'historique), mais
// pas à travers plusieurs visites - un lien partagé ou un nouvel onglet doit repartir
// sur un catalogue vierge plutôt que d'afficher silencieusement une recherche
// oubliée d'il y a plusieurs jours. Une clé par pays : les critères d'un pays n'ont
// aucun sens pour un autre.
const CATALOGUE_FILTERS_STORAGE_KEY_PREFIX = "edukamer_catalogue_filters_"

function EpreuveCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <CardContent className="flex flex-col gap-2 p-4">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
        <div className="flex gap-1.5">
          <Skeleton className="h-5 w-16 rounded-md" />
          <Skeleton className="h-5 w-14 rounded-md" />
        </div>
      </CardContent>
    </Card>
  )
}

export function CataloguePage() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label
  const { isAuthenticated } = useAuth()
  const location = useLocation()
  const searchInputRef = useRef<HTMLInputElement>(null)

  // Replié par défaut : la recherche doit dominer visuellement la carte plutôt que de
  // partager la vedette avec 4 Select au même niveau (voir la refonte de cette carte -
  // décision utilisateur). Initialisé à `true` si un filtre est déjà actif (lien
  // partagé, ou session restaurée par l'effet plus bas) - jamais masquer un filtre déjà
  // appliqué derrière un panneau fermé que l'utilisateur ne pense pas à rouvrir.
  const [filtersExpanded, setFiltersExpanded] = useState(() => {
    const params = new URLSearchParams(window.location.search)
    return Boolean(params.get("subject") || params.get("cursus") || params.get("origine") || params.get("nature"))
  })

  // La query string est la source de vérité des filtres (pas un useState en plus) :
  // une recherche filtrée doit rester bookmarkable/partageable et survivre à un
  // rechargement, et le bouton précédent/suivant du navigateur doit la restaurer.
  const [searchParams, setSearchParams] = useSearchParams()
  const subjectFilter = searchParams.get("subject") ?? ""
  const cursusFilter = searchParams.get("cursus") ?? ""
  const origineFilter = searchParams.get("origine") ?? ""
  const natureFilter = searchParams.get("nature") ?? ""
  const orderingFilter = searchParams.get("ordering") ?? ""
  const gratuitFilter = searchParams.get("gratuit") === "true"
  const search = searchParams.get("search") ?? ""

  useEffect(() => {
    // ?ref=pdf_fiche_sujet : posé par le PDF énoncé d'une fiche répétiteur (voir
    // backend fiches.pdf._sujet_deep_link) sur son propre CTA - ce PDF circule auprès
    // des élèves du répétiteur, jamais encore inscrits sur edukora à ce stade, donc son
    // point d'atterrissage est le catalogue public plutôt qu'une page qui exigerait
    // déjà un compte. Seule façon de mesurer combien de visites viennent réellement
    // d'une fiche imprimée/partagée hors plateforme.
    if (searchParams.get("ref") !== "pdf_fiche_sujet") return
    trackEvent("pdf_fiche_sujet_landing", { country })
  }, [searchParams, country])

  // "Reprendre ma lecture" - jusqu'ici uniquement visible sur /compte, où un
  // utilisateur qui revient doit activement penser à aller la chercher. Ici c'est
  // silencieusement absent (pas d'erreur affichée) pour un visiteur anonyme ou sans
  // historique : ce n'est qu'un raccourci, jamais un contenu qu'on impose de voir.
  const { data: progressionData } = useQuery({
    queryKey: ["progression"],
    queryFn: ({ signal }) => getMyProgression(signal),
    enabled: isAuthenticated,
  })
  // `enabled: false` laisse le cache d'une session précédente intact plutôt que de le
  // vider - sans ce garde, une déconnexion sans rechargement complet de page
  // continuerait d'afficher "Reprendre : ..." avec la progression de l'utilisateur
  // précédent.
  const progression = isAuthenticated ? progressionData : undefined

  const { data: subjects = [] } = useQuery({
    queryKey: ["subjects", country],
    queryFn: ({ signal }) => listSubjects(country, signal),
  })

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })

  // Alimente le rail "Corrigés gratuits" : épreuves en accès libre pour ce pays,
  // choisies par un admin (Lesson.est_vitrine). `enabled: !!country` évite un appel
  // prématuré au tout premier rendu, avant que le paramètre d'URL ne soit résolu.
  const { data: vitrineEpreuves } = useQuery({
    queryKey: ["vitrine-epreuve", country],
    queryFn: ({ signal }) => listEpreuves({ country, est_vitrine: true }, signal),
    enabled: Boolean(country),
  })

  // Rail "Derniers ajouts" : les N épreuves les plus récemment créées sur la
  // plateforme (created_at), pas les plus récentes par année d'examen (voir
  // ordering=recent côté API) - un vieux sujet tout juste corrigé doit y apparaître.
  // Nombre fixe plutôt qu'un seuil de fraîcheur (badge "Nouveau" à J+N) : reste
  // pertinent même quand le catalogue a été ingéré en un seul lot, contrairement à un
  // seuil temporel qui marquerait alors soit tout, soit rien.
  const { data: recentEpreuvesData } = useQuery({
    queryKey: ["epreuves-recent", country],
    queryFn: ({ signal }) => listEpreuves({ country, ordering: "recent" }, signal),
    enabled: Boolean(country),
  })
  const recentEpreuves = (recentEpreuvesData?.results ?? []).slice(0, 10)

  // Débounce la clé de query, pas le champ affiché : le champ reste réactif à chaque
  // frappe (voir l'Input plus bas, contrôlé par `search` directement), seule la
  // requête réseau attend que l'utilisateur "s'installe" sur une valeur. Un simple
  // changement de clé de query annule automatiquement toute requête encore en vol
  // pour l'ancienne clé (voir api/client.ts, AbortSignal transmis à fetch) - plus
  // besoin du setTimeout/clearTimeout manuel d'avant pour éviter qu'une réponse
  // tardive et périmée n'écrase un résultat plus récent.
  const debouncedSearch = useDebouncedValue(search, 300)

  const epreuvesQuery = useInfiniteQuery({
    queryKey: ["epreuves", country, subjectFilter, cursusFilter, origineFilter, natureFilter, orderingFilter, gratuitFilter, debouncedSearch],
    queryFn: ({ pageParam, signal }) =>
      listEpreuves(
        {
          subject: subjectFilter || undefined,
          cursus: cursusFilter ? Number(cursusFilter) : undefined,
          country,
          origine: origineFilter || undefined,
          nature: natureFilter || undefined,
          search: debouncedSearch || undefined,
          ordering: orderingFilter === "year" ? "year" : undefined,
          est_vitrine: gratuitFilter || undefined,
          page: pageParam,
        },
        signal,
      ),
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => (lastPage.next ? allPages.length + 1 : undefined),
  })

  const epreuves = epreuvesQuery.data?.pages.flatMap((p) => p.results) ?? []
  const count = epreuvesQuery.data?.pages[0]?.count ?? 0
  const hasMore = epreuvesQuery.hasNextPage ?? false
  const isLoading = epreuvesQuery.isLoading
  const isLoadingMore = epreuvesQuery.isFetchingNextPage

  // Un vrai terme de recherche qui ne remonte rien - jamais un simple filtre matière/
  // cursus/origine sans texte, signal distinct visé par la reco 5.3 de l'audit UX.
  // Dépend de epreuves.length (pas du tableau lui-même, une référence neuve à chaque
  // rendu) : se déclenche une fois par recherche stabilisée, pas à chaque rendu tant
  // que le même résultat vide persiste (ex. bascule cartes/liste).
  useEffect(() => {
    if (isLoading || !debouncedSearch) return
    if (epreuves.length === 0) trackEvent("search_no_results", { country })
  }, [isLoading, debouncedSearch, epreuves.length, country])

  // Cible du bouton recherche du Header (#catalogue) : un Link classique change
  // location.hash sans que le navigateur ne scrolle vers l'ancre côté SPA (ce
  // comportement natif ne s'applique qu'aux navigations plein-document) - on le
  // reproduit ici à la main, plus focus du champ pour pouvoir taper immédiatement,
  // qu'on arrive d'une autre page ou qu'on soit déjà sur celle-ci (ex. lien "Envie
  // d'aller plus loin" d'EpreuveDetailPage.tsx, même ancre).
  useEffect(() => {
    if (location.hash !== "#catalogue") return
    document.getElementById("catalogue")?.scrollIntoView({ behavior: "smooth", block: "start" })
    searchInputRef.current?.focus()
  }, [location.hash])

  // Préférence d'affichage personnelle (pas un filtre de recherche) : persistée en
  // localStorage plutôt que dans l'URL, comme le thème - pas besoin d'être partagée
  // via un lien, mais doit survivre à la navigation et aux prochaines visites.
  const [viewMode, setViewModeState] = useState<ViewMode>(() => {
    try {
      return (localStorage.getItem(VIEW_MODE_STORAGE_KEY) as ViewMode) || "cards"
    } catch {
      return "cards"
    }
  })

  function setViewMode(mode: ViewMode) {
    try {
      localStorage.setItem(VIEW_MODE_STORAGE_KEY, mode)
    } catch {
      // stockage indisponible (navigation privée) - la préférence ne persistera pas
    }
    setViewModeState(mode)
  }

  // Détecte un vrai changement de pays (valeur précédente vs actuelle) plutôt que
  // "est-ce le premier appel" : StrictMode invoque cet effet deux fois au montage
  // avec la même valeur, un simple ref booléen s'y ferait piéger et purgerait à tort
  // les filtres d'une URL partagée (ex. /cm?subject=MATH) dès le chargement. Initialisé
  // à `undefined` (pas à `country`) : le tout premier rendu doit lui aussi compter
  // comme "un pays vient d'apparaître", pour restaurer ses filtres sauvegardés au
  // premier chargement de la page, pas seulement à un changement ultérieur.
  const previousCountryRef = useRef<string | undefined>(undefined)

  // Niveaux d'examen réellement présents pour ce pays (voir examLevelsFor) - jamais un
  // texte fixe : la plupart des pays n'ont pas de Probatoire. Repli générique tant que
  // cursusList n'a pas encore chargé, pour éviter un flash vide au premier rendu.
  const examLevels = examLevelsFor(cursusList)
  const examLevelsHero = examLevels.length > 0 ? examLevels.join(" · ") : "BEPC · Probatoire · BAC"
  const examLevelsProse = examLevels.length > 0 ? joinExamLevelsFr(examLevels) : "le BEPC, le Probatoire et le BAC"

  // Une puce par filtre actif (hors recherche texte, déjà visible dans son propre
  // champ, et hors tri, qui ne restreint aucun résultat) - vue d'ensemble immédiate
  // de ce qui limite la liste, sans avoir à rouvrir chaque menu pour vérifier.
  const activeFilterChips = [
    subjectFilter && {
      key: "subject",
      label: subjects.find((s) => s.code === subjectFilter)?.label ?? subjectFilter,
      clear: () => updateFilter("subject", ""),
    },
    cursusFilter && {
      key: "cursus",
      label: (() => {
        const c = cursusList.find((c) => String(c.id) === cursusFilter)
        return c ? `${c.examen_display}${c.series ? ` - Série ${c.series.code}` : ""}` : cursusFilter
      })(),
      clear: () => updateFilter("cursus", ""),
    },
    origineFilter && {
      key: "origine",
      label: ORIGINE_LABELS[origineFilter] ?? origineFilter,
      clear: () => updateFilter("origine", ""),
    },
    natureFilter && {
      key: "nature",
      label: NATURE_LABELS[natureFilter] ?? natureFilter,
      clear: () => updateFilter("nature", ""),
    },
    gratuitFilter && {
      key: "gratuit",
      label: "Corrigés gratuits",
      clear: () => updateFilter("gratuit", ""),
    },
  ].filter((chip): chip is { key: string; label: string; clear: () => void } => Boolean(chip))

  function clearAllFilters() {
    // Ne réutilise pas updateFilter() en boucle : `searchParams` ne change qu'au
    // prochain rendu, donc 5 appels successifs dans le même tick partiraient chacun
    // de l'état initial et ne retireraient effectivement qu'une seule clé (la
    // dernière traitée) - un seul next/un seul setSearchParams pour les 5 à la fois.
    const next = new URLSearchParams(searchParams)
    for (const key of ["subject", "cursus", "origine", "nature", "gratuit"]) next.delete(key)
    try {
      sessionStorage.setItem(CATALOGUE_FILTERS_STORAGE_KEY_PREFIX + country, next.toString())
    } catch {
      // navigation privée ou quota plein - la préférence ne survivra simplement pas
    }
    setSearchParams(next, { replace: true })
  }

  useSeo({
    title: "Cours, corrigés et quiz - BEPC, Probatoire, BAC",
    // "{pays} : ..." plutôt que "... au {pays}" - évite l'accord de genre de la
    // préposition ("au Cameroun" vs "en Côte d'Ivoire") qui varie par pays.
    description: countryLabel
      ? `${countryLabel} : cours structurés, corrigés d'annales et quiz d'entraînement pour ${examLevelsProse}, classés par matière et par série.`
      : undefined,
  })

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    try {
      sessionStorage.setItem(CATALOGUE_FILTERS_STORAGE_KEY_PREFIX + country, next.toString())
    } catch {
      // navigation privée ou quota plein - la préférence ne survivra simplement pas
    }
    setSearchParams(next, { replace: true })
  }

  // Un changement de pays (au premier chargement comme à un aller-retour ultérieur via
  // le sélecteur du header - voir CountrySwitcher, qui navigue vers une URL nue) doit
  // retrouver les critères sauvegardés par updateFilter pour CE pays plus tôt dans la
  // session, plutôt que de systématiquement retomber sur un catalogue vierge : une
  // matière/un cursus choisi dans un autre pays n'a de toute façon aucun sens ici (les
  // queries subjects/cursusList ci-dessus se rechargent déjà seules sur `country`).
  // Seulement si l'URL d'arrivée est entièrement vierge - jamais si elle porte déjà des
  // paramètres explicites, ex. un lien partagé, qui doivent rester prioritaires.
  useEffect(() => {
    if (!country || previousCountryRef.current === country) return
    previousCountryRef.current = country
    if (searchParams.toString() !== "") return
    try {
      const saved = sessionStorage.getItem(CATALOGUE_FILTERS_STORAGE_KEY_PREFIX + country)
      if (saved) setSearchParams(new URLSearchParams(saved), { replace: true })
    } catch {
      // navigation privée - repli silencieux sur un catalogue vierge
    }
  }, [country, searchParams, setSearchParams])

  function handleLoadMore() {
    epreuvesQuery.fetchNextPage()
  }

  return (
    <div>
      <section className="relative overflow-hidden border-b border-border">
        <div
          className="absolute inset-0 opacity-[0.05]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "28px 28px",
          }}
        />
        <div className="relative mx-auto grid max-w-5xl gap-8 px-4 py-14 sm:px-6 md:grid-cols-[1.15fr_1fr] md:items-center md:gap-10">
          <div>
            <p className="mb-2 font-display text-sm italic text-primary">
              {examLevelsHero}{countryLabel ? ` - ${countryLabel}` : ""}
            </p>
            <h1 className="max-w-xl font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
              La méthode qui t'apprend{" "}
              <span className="text-primary">à réussir</span>, pas juste la réponse.
            </h1>
            <p className="mt-4 max-w-lg text-muted-foreground">
              Cours structurés et corrigés d'annales, classés par matière et par série - avec
              un quiz qui repère tes lacunes et te fait réviser exactement ce qu'il faut, au
              bon moment.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <Button
                size="lg"
                onClick={() => {
                  updateFilter("origine", "INEDITE")
                  document.getElementById("catalogue")?.scrollIntoView({ behavior: "smooth", block: "start" })
                }}
              >
                Voir les épreuves inédites
                <ArrowRight />
              </Button>
            </div>
          </div>
          <img
            src={heroStudent}
            alt="Élève souriante prenant des notes, ordinateur portable ouvert sur son bureau"
            className="w-full rounded-2xl border border-border"
          />
        </div>
      </section>

      {/* Juste sous le hero, avant la preuve sociale et les rails : un visiteur qui
          sait déjà ce qu'il cherche (voir l'audit UX) ne doit pas avoir à scroller
          plusieurs écrans de contenu de découverte avant de trouver la recherche -
          c'est aussi la cible du bouton recherche du Header, voir son commentaire. */}
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <div id="catalogue" className="mb-6 scroll-mt-20 rounded-2xl border border-border bg-card p-5 shadow-lg shadow-primary/5 sm:p-6">
          <div className="group relative">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
            <Input
              ref={searchInputRef}
              placeholder="Rechercher une épreuve (titre, notion, mot-clé)..."
              value={search}
              onChange={(e) => updateFilter("search", e.target.value)}
              className="h-12 border-input pl-10 pr-10 text-base shadow-none focus-visible:border-primary/60 focus-visible:ring-primary/25"
            />
            {search && (
              <button
                type="button"
                onClick={() => updateFilter("search", "")}
                aria-label="Effacer la recherche"
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="size-4" />
              </button>
            )}
          </div>

          <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
            <button
              type="button"
              onClick={() => updateFilter("gratuit", gratuitFilter ? "" : "true")}
              aria-pressed={gratuitFilter}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
                gratuitFilter
                  ? "border-success/40 bg-success/15 text-success"
                  : "border-border text-muted-foreground hover:border-success/40 hover:text-success",
              )}
            >
              <Sparkles className="size-3.5" />
              Corrigés gratuits uniquement
            </button>

            {/* Filtres avancés repliés par défaut (voir filtersExpanded) : la recherche
                doit rester le point focal de la carte, les 4 Select ne s'affichent que
                si on demande explicitement à les voir. */}
            <button
              type="button"
              onClick={() => setFiltersExpanded((v) => !v)}
              aria-expanded={filtersExpanded}
              className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-primary"
            >
              <SlidersHorizontal className="size-3.5" />
              Filtres avancés
              {activeFilterChips.length > 0 && (
                <span className="flex size-4 items-center justify-center rounded-full bg-primary/15 text-[10px] font-semibold text-primary">
                  {activeFilterChips.length}
                </span>
              )}
              <ChevronDown className={cn("size-3.5 transition-transform", filtersExpanded && "rotate-180")} />
            </button>
          </div>

          {filtersExpanded && (
            <div className="mt-4 grid grid-cols-2 gap-3 border-t border-border pt-4 sm:grid-cols-4">
              <FilterSelect
                label="Matière"
                placeholder="Toutes les matières"
                value={subjectFilter}
                onValueChange={(v) => updateFilter("subject", v)}
                options={subjects.map((s) => ({ value: s.code, label: s.label }))}
              />
              <FilterSelect
                label="Cursus"
                placeholder="Tous les cursus"
                value={cursusFilter}
                onValueChange={(v) => updateFilter("cursus", v)}
                options={cursusList.map((c) => ({
                  value: String(c.id),
                  label: `${c.examen_display}${c.series ? ` - Série ${c.series.code}` : ""}`,
                }))}
              />
              <FilterSelect
                label="Nature"
                placeholder="Théorique et pratique"
                value={natureFilter}
                onValueChange={(v) => updateFilter("nature", v)}
                options={[
                  { value: "theorique", label: NATURE_LABELS.theorique },
                  { value: "pratique", label: NATURE_LABELS.pratique },
                ]}
              />
              <FilterSelect
                label="Origine"
                placeholder="Toutes origines"
                value={origineFilter}
                onValueChange={(v) => updateFilter("origine", v)}
                options={Object.entries(ORIGINE_LABELS).map(([value, label]) => ({ value, label }))}
              />
            </div>
          )}

          {activeFilterChips.length > 0 && (
            <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-border pt-3.5">
              {activeFilterChips.map((chip) => (
                <FilterChip key={chip.key} label={chip.label} onRemove={chip.clear} />
              ))}
              {activeFilterChips.length > 1 && (
                <button
                  type="button"
                  onClick={clearAllFilters}
                  className="text-xs font-medium text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
                >
                  Tout effacer
                </button>
              )}
            </div>
          )}
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <EpreuveCardSkeleton key={i} />
            ))}
          </div>
        ) : epreuves.length === 0 ? (
          <div className="flex flex-col items-center gap-3 py-20 text-center text-muted-foreground">
            <BookOpen className="size-8" />
            <p>Aucune épreuve ne correspond à ces critères.</p>
            {(activeFilterChips.length > 0 || search) && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  clearAllFilters()
                  updateFilter("search", "")
                }}
              >
                Réinitialiser la recherche
              </Button>
            )}
          </div>
        ) : (
          <>
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-muted-foreground">
                {count} épreuve{count > 1 ? "s" : ""} trouvée{count > 1 ? "s" : ""}
              </p>
              <div className="flex shrink-0 items-center gap-2">
                <Select value={orderingFilter || "recent"} onValueChange={(v) => updateFilter("ordering", v === "recent" ? "" : v)}>
                  <SelectTrigger className="h-8 w-[188px] text-xs">
                    <SelectValue placeholder="Trier par année" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="recent">Plus récentes d'abord</SelectItem>
                    <SelectItem value="year">Plus anciennes d'abord</SelectItem>
                  </SelectContent>
                </Select>
                <div className="flex shrink-0 gap-1 rounded-md border border-border p-0.5">
                  <Button
                    variant={viewMode === "cards" ? "secondary" : "ghost"}
                    size="icon"
                    className="size-7 tap-target-44"
                    aria-label="Affichage en cartes"
                    aria-pressed={viewMode === "cards"}
                    onClick={() => setViewMode("cards")}
                  >
                    <LayoutGrid className="size-4" />
                  </Button>
                  <Button
                    variant={viewMode === "list" ? "secondary" : "ghost"}
                    size="icon"
                    className="size-7 tap-target-44"
                    aria-label="Affichage en liste"
                    aria-pressed={viewMode === "list"}
                    onClick={() => setViewMode("list")}
                  >
                    <List className="size-4" />
                  </Button>
                </div>
              </div>
            </div>

            {viewMode === "cards" ? (
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {epreuves.map((epreuve, index) => (
                  <EpreuveCard
                    key={`${epreuve.kind}-${epreuve.id}`}
                    epreuve={epreuve}
                    className="animate-fade-up"
                    style={{ animationDelay: `${Math.min(index, 8) * 60}ms` }}
                  />
                ))}
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {epreuves.map((epreuve, index) => (
                  <EpreuveListRow
                    key={`${epreuve.kind}-${epreuve.id}`}
                    epreuve={epreuve}
                    className="animate-fade-up"
                    style={{ animationDelay: `${Math.min(index, 8) * 60}ms` }}
                  />
                ))}
              </div>
            )}

            {hasMore && (
              <div className="mt-8 flex justify-center">
                <Button variant="outline" onClick={handleLoadMore} disabled={isLoadingMore}>
                  {isLoadingMore && <Loader2 className="size-4 animate-spin" />}
                  Charger plus
                </Button>
              </div>
            )}
          </>
        )}
      </div>

      {/* La preuve sociale suit immédiatement la recherche/résultats : construit la
          confiance pour le visiteur qui vient de voir ce qu'il y a à trouver, avant
          qu'il ne descende plus loin vers les rails de découverte. */}
      <SocialProofSection />

      <section className="mx-auto max-w-5xl px-4 py-6 sm:px-6">
        {/* Réassurance sur la formule Max, jamais la même action que le CTA du hero
            (qui filtre déjà le catalogue sur origine=INEDITE) - pointer les deux vers
            la même action aurait été une redite pure. Ici : convaincre puis renvoyer
            vers les tarifs, pas reproposer la liste déjà accessible depuis le hero. */}
        <Link
          to="/tarifs"
          className="group flex w-full animate-fade-up flex-col items-start justify-between gap-4 overflow-hidden rounded-2xl border border-gold/30 bg-gradient-to-br from-gold/10 via-transparent to-transparent p-6 text-left transition-colors hover:border-gold/50 sm:flex-row sm:items-center"
        >
          <div className="flex items-start gap-3">
            <Crown className="mt-0.5 size-6 shrink-0 text-gold" />
            <div>
              <p className="font-display text-lg font-semibold">Épreuves Inédites</p>
              <p className="mt-1 max-w-md text-sm text-muted-foreground">
                Une épreuve d'examen jamais vue, jamais publiée ailleurs - le seul moyen de te tester en
                conditions réelles. Incluses avec la formule Max.
              </p>
            </div>
          </div>
          <span className="flex shrink-0 items-center gap-1.5 whitespace-nowrap text-sm font-medium text-primary group-hover:underline">
            Voir les tarifs
            <ArrowRight className="size-3.5" />
          </span>
        </Link>
      </section>

      <EpreuveRail
        title="Corrigés gratuits"
        icon={<Sparkles className="size-5 text-success" />}
        epreuves={vitrineEpreuves?.results ?? []}
        threePerView
      />

      {progression && progression.lessons.length > 0 && (
        <div className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
          <Link
            // getMyProgression() (endpoint access, non modifié par la fusion) ne
            // renvoie jamais que des Lesson classiques - slug toujours renseigné.
            to={epreuveReaderPath(
              progression.lessons[0].subject.country.code.toLowerCase(),
              progression.lessons[0].slug as string,
            )}
            className="flex animate-fade-up items-center justify-between gap-3 rounded-lg border border-border bg-accent/40 px-4 py-3 text-sm transition-colors hover:border-primary/50 hover:bg-accent"
          >
            <span className="min-w-0">
              <span className="text-muted-foreground">Reprendre : </span>
              <span className="font-medium">{progression.lessons[0].title}</span>
            </span>
            <ArrowRight className="size-4 shrink-0 text-primary" />
          </Link>
        </div>
      )}

      <EpreuveRail
        title="Derniers ajouts"
        icon={<Clock className="size-5 text-primary" />}
        epreuves={recentEpreuves}
        threePerView
      />
    </div>
  )
}
