import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { useParams, useSearchParams } from "react-router-dom"
import { useInfiniteQuery, useQuery } from "@tanstack/react-query"
import {
  BookOpen,
  ChevronDown,
  Crown,
  Gift,
  GraduationCap,
  LayoutGrid,
  Layers,
  List,
  Loader2,
  RefreshCw,
  Search,
  SearchX,
  SlidersHorizontal,
  X,
} from "lucide-react"

import { listCursus, listEpreuves, listSubjects } from "@/api/endpoints"
import type { NatureEpreuve, Origine } from "@/api/types"
import { examLevelsFor } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { useDebouncedValue } from "@/lib/useDebouncedValue"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { subjectShortLabel } from "@/lib/subjectLabel"
import { cn, formatAmount } from "@/lib/utils"
import { useCountry } from "@/context/CountryContext"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { EpreuveCard } from "@/components/EpreuveCard"
import { EpreuveListRow } from "@/components/EpreuveListRow"
import { FiltreLigne, PastilleFiltre } from "@/components/FiltresCatalogue"
import { ThemesFrequents } from "@/components/ThemesFrequents"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ReviserTabs } from "@/components/ReviserTabs"
import { BandeauFiltreCursus, useFiltreCursusParDefaut } from "@/lib/filtreCursus"

type ViewMode = "cards" | "list"

const VIEW_MODE_STORAGE_KEY = "edukamer_epreuves_catalogue_view"
// Mémorise la dernière recherche filtrée (voir plus bas) - un lien nu vers /epreuves
// (nav, logo, retour) doit rouvrir là où l'utilisateur en était, pas repartir d'une
// liste vierge à chaque clic. Session, pas localStorage : une recherche n'a pas
// vocation à survivre à la fermeture de l'onglet, contrairement à une préférence
// d'affichage.
const FILTERS_SESSION_KEY = "edukamer_epreuves_derniers_filtres"

// "tout" inclus : le choix d'élargir au-delà de son cursus (voir filtreCursus) doit
// se restaurer comme les autres filtres, sinon le pré-filtrage revient à la
// navigation suivante et le bouton "Voir tout le catalogue" semble sans effet.
const FILTER_KEYS = ["subject", "cursus", "origine", "nature", "gratuit", "search", "ordering", "tout"]

const ORIGINE_LABELS: Record<Origine, string> = {
  OFFICIEL: "Épreuve officielle",
  BLANC: "Examen blanc",
  ETABLISSEMENT: "Sujet d'établissement",
  AUTRE: "Autre",
  INEDITE: "Épreuve inédite",
}

const NATURE_LABELS: Record<NatureEpreuve, string> = {
  THEORIQUE: "Théorique",
  PRATIQUE: "Pratique",
}

const ORDERING_LABELS = {
  year: "Année (plus récente)",
  recent: "Ajoutées récemment",
  popular: "Les plus consultées",
} as const

function EpreuveCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <Skeleton className="h-1 w-full rounded-none" />
      <CardContent className="flex flex-col gap-3 p-4">
        <div className="flex items-start gap-3">
          <Skeleton className="size-10 shrink-0 rounded-xl" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3 w-1/3" />
            <Skeleton className="h-4 w-4/5" />
          </div>
        </div>
        <div className="flex gap-1.5">
          <Skeleton className="h-5 w-24 rounded-md" />
          <Skeleton className="h-5 w-16 rounded-md" />
        </div>
        <Skeleton className="h-3 w-2/3" />
        <Skeleton className="mt-1 h-8 w-full" />
      </CardContent>
    </Card>
  )
}

/** Puce de filtre actif, retirable individuellement - même composant visuel que sur
 * /cours : les deux catalogues doivent se piloter de la même façon. */
function FilterChip({ label, onRemove }: { label: string; onRemove: () => void }) {
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

/** Statistique du hero - même gabarit que les puces de /quiz, /fiches et /cours. */
function StatChip({ icon, valeur, libelle }: { icon: ReactNode; valeur: string; libelle: string }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
      {icon}
      <span className="font-medium tabular-nums">{valeur}</span>
      <span className="text-muted-foreground">{libelle}</span>
    </span>
  )
}

export function EpreuvesListPage() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label

  const [searchParams, setSearchParams] = useSearchParams()

  // Une recherche filtrée déjà en session reprend la main sur une arrivée nue (lien
  // nav/logo), jamais sur un lien qui porte déjà ses propres filtres (partagé,
  // "Retour au catalogue" depuis une fiche épreuve avec ?cursus=X) : ce dernier doit
  // rester prioritaire. Effectué une seule fois, avant le premier rendu utile des
  // filtres, pour ne jamais écraser un changement que l'utilisateur vient de faire.
  const restauredRef = useRef(false)
  useEffect(() => {
    if (restauredRef.current) return
    restauredRef.current = true
    const hasFilters = FILTER_KEYS.some((key) => searchParams.has(key))
    if (hasFilters) return
    try {
      const saved = sessionStorage.getItem(FILTERS_SESSION_KEY)
      if (saved) setSearchParams(new URLSearchParams(saved), { replace: true })
    } catch {
      // stockage indisponible (navigation privée) - on repart d'une liste vierge
    }
  }, [searchParams, setSearchParams])

  // Pré-filtrage sur l'examen déclaré, déclaré APRÈS la restauration de session
  // ci-dessus : l'ordre des deux effets compte, sans quoi une recherche sauvegardée
  // serait ignorée (voir useFiltreCursusParDefaut).
  useFiltreCursusParDefaut()

  const subjectFilter = searchParams.get("subject") ?? ""
  const cursusFilter = searchParams.get("cursus") ?? ""
  const origineFilter = (searchParams.get("origine") ?? "") as Origine | ""
  const natureFilter = (searchParams.get("nature") ?? "") as NatureEpreuve | ""
  const gratuitFilter = searchParams.get("gratuit") === "true"
  const search = searchParams.get("search") ?? ""
  const ordering = (searchParams.get("ordering") ?? "") as keyof typeof ORDERING_LABELS | ""

  useSeo({
    title: "Épreuves et corrigés",
    description: countryLabel
      ? `${countryLabel} : sujets et corrigés d'annales, examens blancs et épreuves inédites, classés par matière, cursus et série.`
      : undefined,
  })

  const { data: subjects = [] } = useQuery({
    queryKey: ["subjects", country],
    queryFn: ({ signal }) => listSubjects(country, signal),
  })

  const subjectsTries = useMemo(
    () => [...subjects].sort((a, b) => a.label.localeCompare(b.label, "fr")),
    [subjects],
  )

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })

  // Origine et nature sont des filtres de second rang : repliés tant qu'ils ne servent pas, mais
  // jamais cachés quand l'un d'eux est actif (on doit voir ce qui restreint la liste).
  const [plusOuvert, setPlusOuvert] = useState(false)

  const filtresActifs = Boolean(
    subjectFilter || cursusFilter || origineFilter || natureFilter || gratuitFilter || search,
  )

  // Volumétrie totale du pays, affichée dans le hero - même clé de cache que sur
  // CataloguePage, donc un aller-retour entre les deux pages ne repaie pas la requête.
  const { data: totalData } = useQuery({
    queryKey: ["epreuves-total", country],
    queryFn: ({ signal }) => listEpreuves({ country }, signal),
    enabled: Boolean(country) && filtresActifs,
  })

  const debouncedSearch = useDebouncedValue(search, 300)

  const epreuvesQuery = useInfiniteQuery({
    queryKey: [
      "epreuves",
      country,
      subjectFilter,
      cursusFilter,
      origineFilter,
      natureFilter,
      gratuitFilter,
      debouncedSearch,
      ordering,
    ],
    queryFn: ({ pageParam, signal }) =>
      listEpreuves(
        {
          subject: subjectFilter || undefined,
          cursus: cursusFilter ? Number(cursusFilter) : undefined,
          country,
          origine: origineFilter || undefined,
          nature: natureFilter || undefined,
          // Jamais `false` : le backend ne teste que la valeur "true", envoyer
          // est_vitrine=false polluerait l'URL de l'API pour rien.
          est_vitrine: gratuitFilter || undefined,
          search: debouncedSearch || undefined,
          ordering: ordering || undefined,
          page: pageParam,
        },
        signal,
      ),
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => (lastPage.next ? allPages.length + 1 : undefined),
  })

  const epreuvesList = epreuvesQuery.data?.pages.flatMap((p) => p.results) ?? []
  const count = epreuvesQuery.data?.pages[0]?.count ?? 0
  const hasMore = epreuvesQuery.hasNextPage ?? false
  const isLoading = epreuvesQuery.isLoading
  const isLoadingMore = epreuvesQuery.isFetchingNextPage

  // Chargement automatique au défilement plutôt qu'un bouton "Charger plus" : sur un
  // catalogue de plusieurs centaines d'épreuves, laisser la lecture continuer sans
  // interruption réduit la friction du parcours de recherche. La sentinelle vit après
  // la grille ; elle entre dans le viewport un peu avant que l'utilisateur n'atteigne
  // réellement le bas, pour que la page suivante soit déjà là le temps qu'il y arrive.
  const sentinelRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const el = sentinelRef.current
    if (!el || !hasMore) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isLoadingMore) epreuvesQuery.fetchNextPage()
      },
      { rootMargin: "400px" },
    )
    observer.observe(el)
    return () => observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasMore, isLoadingMore])

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

  const previousCountryRef = useRef(country)
  useEffect(() => {
    if (previousCountryRef.current === country) return
    previousCountryRef.current = country
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        next.delete("subject")
        next.delete("cursus")
        return next
      },
      { replace: true },
    )
  }, [country, setSearchParams])

  function updateFilter(key: string, value: string) {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        if (value) next.set(key, value)
        else next.delete(key)
        try {
          sessionStorage.setItem(FILTERS_SESSION_KEY, next.toString())
        } catch {
          // stockage indisponible (navigation privée) - rien à mémoriser
        }
        return next
      },
      { replace: true },
    )
  }

  function resetFilters() {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        for (const key of FILTER_KEYS) next.delete(key)
        try {
          sessionStorage.removeItem(FILTERS_SESSION_KEY)
        } catch {
          // stockage indisponible - rien à effacer
        }
        return next
      },
      { replace: true },
    )
  }

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
      label: ORIGINE_LABELS[origineFilter],
      clear: () => updateFilter("origine", ""),
    },
    natureFilter && {
      key: "nature",
      label: NATURE_LABELS[natureFilter],
      clear: () => updateFilter("nature", ""),
    },
    gratuitFilter && {
      key: "gratuit",
      label: "Gratuites uniquement",
      clear: () => updateFilter("gratuit", ""),
    },
  ].filter((chip): chip is { key: string; label: string; clear: () => void } => Boolean(chip))

  const examLevels = examLevelsFor(cursusList)
  const plusVisible = plusOuvert || Boolean(origineFilter || natureFilter)
  const nbFiltresSecondaires = (origineFilter ? 1 : 0) + (natureFilter ? 1 : 0)
  // Le cursus est LE filtre d'un élève ("mon BAC D") : en pastilles d'un clic plutôt que caché
  // dans une liste déroulante, triées pour que les séries d'un même examen se suivent.
  const cursusTries = [...cursusList].sort(
    (x, y) =>
      x.examen_display.localeCompare(y.examen_display, "fr") ||
      (x.series?.code ?? "").localeCompare(y.series?.code ?? "", "fr"),
  )
  const totalEpreuves = filtresActifs ? totalData?.count : epreuvesQuery.data ? count : undefined

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <ReviserTabs />
      <BandeauFiltreCursus />
      {/* Hero : plus court qu'avant (les résultats doivent apparaître sans défiler sur un
          ordinateur), avec un filigrane et le volume du catalogue - la preuve qu'il y a de quoi
          chercher avant même d'avoir cherché. */}
      <div className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <BookOpen aria-hidden className="pointer-events-none absolute -bottom-6 -right-4 hidden size-44 rotate-[-12deg] text-primary/[0.07] sm:block" />
        <div className="relative max-w-2xl">
          <p className="mb-2 font-display text-sm italic text-primary">
            Épreuves et corrigés{countryLabel ? ` - ${countryLabel}` : ""}
          </p>
          <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight text-balance sm:text-4xl">
            Toutes les <span className="text-primary">annales corrigées</span>, cursus par cursus.
          </h1>
          <p className="mt-2 hidden max-w-xl text-muted-foreground sm:block">
            Sujets officiels, examens blancs et épreuves inédites : choisis ton examen, ta matière, et lis le corrigé
            détaillé.
          </p>

          <div className="mt-4 flex flex-wrap gap-2 sm:mt-5">
            {totalEpreuves !== undefined && (
              <StatChip
                icon={<BookOpen className="size-3.5 text-primary" />}
                valeur={formatAmount(totalEpreuves)}
                libelle={totalEpreuves > 1 ? "épreuves publiées" : "épreuve publiée"}
              />
            )}
            {subjectsTries.length > 0 && (
              <StatChip
                icon={<Layers className="size-3.5 text-primary" />}
                valeur={String(subjectsTries.length)}
                libelle={subjectsTries.length > 1 ? "matières" : "matière"}
              />
            )}
            {examLevels.length > 0 && (
              <span className="hidden items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm sm:flex">
                <GraduationCap className="size-3.5 text-success" />
                <span className="text-muted-foreground">{examLevels.join(" · ")}</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Panneau de recherche : la carte surélevée fait de la recherche le point focal
          de la page, comme sur /cours. */}
      <div className="mb-6 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:p-6">
        <div className="group relative">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            type="search"
            inputMode="search"
            enterKeyHint="search"
            aria-label="Rechercher une épreuve"
            placeholder="Rechercher une épreuve…"
            value={search}
            onChange={(e) => updateFilter("search", e.target.value)}
            className="h-12 border-input pl-10 pr-10 text-base shadow-none focus-visible:border-primary/60 focus-visible:ring-primary/25 [&::-webkit-search-cancel-button]:hidden"
          />
          {search && (
            <button
              type="button"
              onClick={() => updateFilter("search", "")}
              aria-label="Effacer la recherche"
              className="absolute right-2 top-1/2 flex size-8 -translate-y-1/2 items-center justify-center rounded-full text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              <X className="size-4" />
            </button>
          )}
        </div>

        {cursusTries.length > 0 && (
          <FiltreLigne titre="Examen">
            <PastilleFiltre actif={!cursusFilter} onClick={() => updateFilter("cursus", "")}>
              Tous
            </PastilleFiltre>
            {cursusTries.map((c) => (
              <PastilleFiltre
                key={c.id}
                actif={cursusFilter === String(c.id)}
                onClick={() => updateFilter("cursus", cursusFilter === String(c.id) ? "" : String(c.id))}
              >
                {c.examen_display}
                {c.series ? ` ${c.series.code}` : ""}
              </PastilleFiltre>
            ))}
          </FiltreLigne>
        )}

        {subjectsTries.length > 0 && (
          <FiltreLigne titre="Matière">
            <PastilleFiltre actif={!subjectFilter} onClick={() => updateFilter("subject", "")}>
              Toutes
            </PastilleFiltre>
            {subjectsTries.map((subject) => {
              const SubjectIcon = subjectIcon(subject.code)
              const actif = subjectFilter === subject.code
              return (
                <PastilleFiltre
                  key={subject.id}
                  actif={actif}
                  onClick={() => updateFilter("subject", actif ? "" : subject.code)}
                >
                  <span className={cn("flex size-5 items-center justify-center rounded-full", couleurMatiere(subject.code).puce)}>
                    <SubjectIcon className="size-3" aria-hidden="true" />
                  </span>
                  {subjectShortLabel(subject.code, subject.label)}
                </PastilleFiltre>
              )
            })}
          </FiltreLigne>
        )}

        {/* Raccourcis vers les facettes les plus demandées - un clic, là où passer par le
            sélecteur "Origine" en coûte deux. Restent aussi accessibles depuis leurs
            sélecteurs, ce ne sont que des raccourcis. */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => updateFilter("gratuit", gratuitFilter ? "" : "true")}
            aria-pressed={gratuitFilter}
            className={cn(
              "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
              gratuitFilter
                ? "border-success/40 bg-success/15 text-success"
                : "border-border text-muted-foreground hover:border-success/40 hover:text-success",
            )}
          >
            <Gift className="size-4" />
            Gratuites
          </button>
          <button
            type="button"
            onClick={() => updateFilter("origine", origineFilter === "INEDITE" ? "" : "INEDITE")}
            aria-pressed={origineFilter === "INEDITE"}
            className={cn(
              "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
              origineFilter === "INEDITE"
                ? "border-gold bg-gold text-gold-foreground"
                : "border-border text-muted-foreground hover:border-gold/40 hover:text-gold",
            )}
          >
            <Crown className="size-4" />
            Inédites
          </button>
          <button
            type="button"
            onClick={() => setPlusOuvert((v) => !v)}
            aria-expanded={plusVisible}
            className="ml-auto inline-flex min-h-9 items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
          >
            <SlidersHorizontal className="size-4" />
            <span className="sm:hidden">Filtres</span>
            <span className="hidden sm:inline">Plus de filtres</span>
            {nbFiltresSecondaires > 0 && (
              <span className="flex size-5 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                {nbFiltresSecondaires}
              </span>
            )}
            <ChevronDown className={cn("size-4 transition-transform", plusVisible && "rotate-180")} />
          </button>
        </div>

        {plusVisible && (
          <div className="mt-3 flex flex-wrap items-center gap-2 rounded-xl bg-muted/50 p-3">
            <Select
              value={origineFilter || "all"}
              onValueChange={(v) => updateFilter("origine", v === "all" ? "" : v)}
            >
              <SelectTrigger className="w-full bg-background sm:w-52" aria-label="Origine">
                <SelectValue placeholder="Toute origine" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toute origine</SelectItem>
                {(Object.keys(ORIGINE_LABELS) as Origine[]).map((code) => (
                  <SelectItem key={code} value={code}>
                    {ORIGINE_LABELS[code]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={natureFilter || "all"} onValueChange={(v) => updateFilter("nature", v === "all" ? "" : v)}>
              <SelectTrigger className="w-full bg-background sm:w-48" aria-label="Théorique ou pratique">
                <SelectValue placeholder="Théorique/Pratique" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Théorique/Pratique</SelectItem>
                {(Object.keys(NATURE_LABELS) as NatureEpreuve[]).map((code) => (
                  <SelectItem key={code} value={code}>
                    {NATURE_LABELS[code]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {activeFilterChips.length > 0 && (
          <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-border pt-3.5">
            <span className="text-sm text-muted-foreground">Filtres :</span>
            {activeFilterChips.map((chip) => (
              <FilterChip key={chip.key} label={chip.label} onRemove={chip.clear} />
            ))}
            {activeFilterChips.length > 1 && (
              <button
                type="button"
                onClick={resetFilters}
                className="text-sm font-medium text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
              >
                Tout effacer
              </button>
            )}
          </div>
        )}
      </div>

      {country && subjectFilter && cursusFilter && (
        <ThemesFrequents
          country={country}
          cursusId={Number(cursusFilter)}
          subjectCode={subjectFilter}
          variant="preview"
        />
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true" aria-label="Chargement des épreuves">
          {Array.from({ length: 6 }).map((_, i) => (
            <EpreuveCardSkeleton key={i} />
          ))}
        </div>
      ) : epreuvesQuery.isError && epreuvesList.length === 0 ? (
        // Une panne n'est pas "aucun résultat" : sans ce cas, une coupure réseau se lisait
        // comme un catalogue vide et l'élève cherchait l'erreur dans ses filtres.
        <div role="alert" className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-card/60 px-6 py-14 text-center">
          <span className="flex size-12 items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
            <RefreshCw className="size-6" />
          </span>
          <p className="font-display text-lg font-semibold">Impossible de charger les épreuves</p>
          <p className="max-w-sm text-sm text-muted-foreground">
            Vérifie ta connexion : tes filtres sont conservés, il suffit de réessayer.
          </p>
          <Button onClick={() => epreuvesQuery.refetch()} className="rounded-full">
            <RefreshCw />
            Réessayer
          </Button>
        </div>
      ) : epreuvesList.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-card/60 px-6 py-14 text-center">
          <span className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <SearchX className="size-6" />
          </span>
          <p className="font-display text-lg font-semibold">Aucune épreuve ne correspond</p>
          <p className="max-w-sm text-sm text-muted-foreground">
            {search
              ? `Rien pour « ${search} » avec ces filtres. Essaie un mot plus court, ou élargis la recherche.`
              : "Élargis un filtre pour voir plus d'épreuves."}
          </p>
          <div className="mt-1 flex flex-wrap justify-center gap-2">
            {(activeFilterChips.length > 0 || search) && (
              <Button variant="outline" onClick={resetFilters} className="rounded-full">
                Tout réinitialiser
              </Button>
            )}
            {!gratuitFilter && (
              <Button variant="ghost" onClick={() => updateFilter("gratuit", "true")} className="rounded-full">
                <Gift />
                Voir les épreuves gratuites
              </Button>
            )}
          </div>
        </div>
      ) : (
        <>
          {/* Barre de résultats collante : même hauteur (top-[72px]) et même motif que
              /cours - voir CoursListPage pour l'explication de cette valeur exacte. */}
          <div className="sticky top-[72px] z-10 -mx-4 mb-4 flex items-center justify-between gap-3 border-b border-border bg-background/85 px-4 py-2.5 backdrop-blur sm:-mx-6 sm:px-6">
            <p className="text-sm text-muted-foreground" aria-live="polite">
              <span className="font-medium tabular-nums text-foreground">{formatAmount(count)}</span> épreuve
              {count > 1 ? "s" : ""} trouvée{count > 1 ? "s" : ""}
            </p>
            <div className="flex shrink-0 items-center gap-2">
            <Select value={ordering || "default"} onValueChange={(v) => updateFilter("ordering", v === "default" ? "" : v)}>
              <SelectTrigger className="h-8 w-36 text-sm sm:w-48" aria-label="Trier les épreuves">
                <SelectValue placeholder="Tri par défaut" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="default">Tri par défaut</SelectItem>
                {(Object.keys(ORDERING_LABELS) as (keyof typeof ORDERING_LABELS)[]).map((key) => (
                  <SelectItem key={key} value={key}>
                    {ORDERING_LABELS[key]}
                  </SelectItem>
                ))}
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
              {epreuvesList.map((epreuve, index) => (
                <EpreuveCard
                  key={epreuve.id}
                  epreuve={epreuve}
                  className="animate-fade-up"
                  style={{ animationDelay: `${Math.min(index, 8) * 60}ms` }}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {epreuvesList.map((epreuve, index) => (
                <EpreuveListRow
                  key={epreuve.id}
                  epreuve={epreuve}
                  className="animate-fade-up"
                  style={{ animationDelay: `${Math.min(index, 8) * 60}ms` }}
                />
              ))}
            </div>
          )}

          {hasMore && (
            <div ref={sentinelRef} className="mt-8 flex flex-col items-center gap-2 py-4">
              {isLoadingMore && <Loader2 className="size-5 animate-spin text-muted-foreground" />}
              <p className="text-xs tabular-nums text-muted-foreground">
                {formatAmount(epreuvesList.length)} sur {formatAmount(count)}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
