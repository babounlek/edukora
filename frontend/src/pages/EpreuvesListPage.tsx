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
  List,
  Loader2,
  Search,
  X,
} from "lucide-react"

import { listCursus, listEpreuves, listSubjects } from "@/api/endpoints"
import type { NatureEpreuve, Origine } from "@/api/types"
import { examLevelsFor } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { useDebouncedValue } from "@/lib/useDebouncedValue"
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
import { ThemesFrequents } from "@/components/ThemesFrequents"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type ViewMode = "cards" | "list"

const VIEW_MODE_STORAGE_KEY = "edukamer_epreuves_catalogue_view"
// Mémorise la dernière recherche filtrée (voir plus bas) - un lien nu vers /epreuves
// (nav, logo, retour) doit rouvrir là où l'utilisateur en était, pas repartir d'une
// liste vierge à chaque clic. Session, pas localStorage : une recherche n'a pas
// vocation à survivre à la fermeture de l'onglet, contrairement à une préférence
// d'affichage.
const FILTERS_SESSION_KEY = "edukamer_epreuves_derniers_filtres"

const FILTER_KEYS = ["subject", "cursus", "origine", "nature", "gratuit", "search", "ordering"]

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

// Même paliers de repli que /cours (voir CoursListPage) - les deux catalogues
// partagent le même gabarit de pastilles de matière, donc la même mesure.
const PALIERS_MATIERES = [
  { limite: 4, revele: "" },
  { limite: 5, revele: "sm:flex" },
  { limite: 7, revele: "md:flex" },
  { limite: 10, revele: "lg:flex" },
] as const

const MATIERES_VISIBLES_MIN = PALIERS_MATIERES[0].limite
const MATIERES_VISIBLES_MAX = PALIERS_MATIERES[PALIERS_MATIERES.length - 1].limite

function classeRepliMatiere(index: number): string | undefined {
  if (index < MATIERES_VISIBLES_MIN) return undefined
  const palier = PALIERS_MATIERES.find((p) => index < p.limite)
  return palier ? `hidden ${palier.revele}` : "hidden"
}

function EpreuveCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <CardContent className="flex flex-col gap-2.5 p-4">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
        <div className="flex gap-1.5">
          <Skeleton className="h-5 w-16 rounded-md" />
          <Skeleton className="h-5 w-14 rounded-md" />
        </div>
        <Skeleton className="mt-1 h-3 w-2/3" />
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

  // Déplié par défaut : toutes les matières visibles d'un coup plutôt que tronquées
  // derrière "Toutes les matières (N)" - décision utilisateur du 2026-08-19, le
  // repliement restait un frein à la découverte pour un catalogue qui n'a de toute
  // façon jamais plus d'une dizaine de matières par pays.
  const [matieresDepliees, setMatieresDepliees] = useState(true)

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })

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
  const totalEpreuves = filtresActifs ? totalData?.count : epreuvesQuery.data ? count : undefined

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      {/* Même gabarit de hero que /quiz, /fiches et /cours. */}
      <div className="relative mb-6 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6 sm:p-8">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative max-w-2xl">
          <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <BookOpen className="size-5" />
          </div>
          <p className="mb-1 font-display text-sm italic text-primary">
            Épreuves et corrigés{countryLabel ? ` - ${countryLabel}` : ""}
          </p>
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">
            Toutes les <span className="text-primary">annales corrigées</span>, cursus par cursus.
          </h1>
          <p className="mt-2 text-muted-foreground">
            Sujets officiels, examens blancs et épreuves inédites - filtre par matière, série et type pour trouver
            exactement ce qu'il te faut réviser.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            {totalEpreuves !== undefined && (
              <StatChip
                icon={<BookOpen className="size-3.5 text-primary" />}
                valeur={formatAmount(totalEpreuves)}
                libelle={totalEpreuves > 1 ? "épreuves publiées" : "épreuve publiée"}
              />
            )}
            {examLevels.length > 0 && (
              <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
                <GraduationCap className="size-3.5 text-success" />
                <span className="text-muted-foreground">{examLevels.join(" · ")}</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Panneau de recherche : la carte surélevée fait de la recherche le point focal
          de la page, comme sur /cours. */}
      <div className="mb-6 rounded-2xl border border-border bg-card p-5 shadow-lg shadow-primary/5 sm:p-6">
        <div className="group relative">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            placeholder="Rechercher une épreuve (matière, année, mot-clé)..."
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

        {/* Raccourcis vers les deux facettes les plus demandées - un clic, là où passer
            par le sélecteur "Origine" en coûte deux (ouvrir le menu, choisir "Épreuve
            inédite"). Les deux restent aussi accessibles depuis leurs sélecteurs
            respectifs, ce ne sont que des raccourcis, pas un mécanisme séparé. */}
        <div className="mt-4 flex flex-wrap gap-2">
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
            <Gift className="size-3.5" />
            Gratuites
          </button>
          <button
            type="button"
            onClick={() => updateFilter("origine", origineFilter === "INEDITE" ? "" : "INEDITE")}
            aria-pressed={origineFilter === "INEDITE"}
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
              origineFilter === "INEDITE"
                ? "border-gold/50 bg-gold/15 text-gold"
                : "border-border text-muted-foreground hover:border-gold/40 hover:text-gold",
            )}
          >
            <Crown className="size-3.5" />
            Inédites
          </button>
        </div>

        {subjectsTries.length > 0 && (
          <div className="mt-4">
            <div role="group" aria-label="Filtrer par matière" className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => updateFilter("subject", "")}
                aria-pressed={!subjectFilter}
                className={cn(
                  "rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
                  subjectFilter
                    ? "border-border text-muted-foreground hover:border-primary/40 hover:text-primary"
                    : "border-primary bg-primary/10 text-primary",
                )}
              >
                Toutes
              </button>
              {subjectsTries.map((subject, index) => {
                const SubjectIcon = subjectIcon(subject.code)
                const actif = subjectFilter === subject.code
                return (
                  <button
                    key={subject.id}
                    type="button"
                    onClick={() => updateFilter("subject", actif ? "" : subject.code)}
                    aria-pressed={actif}
                    className={cn(
                      "flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
                      actif
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border text-muted-foreground hover:border-primary/40 hover:text-primary",
                      !matieresDepliees && classeRepliMatiere(index),
                    )}
                  >
                    <SubjectIcon className="size-3.5" aria-hidden="true" />
                    {subjectShortLabel(subject.code, subject.label)}
                  </button>
                )
              })}
            </div>

            {subjectsTries.length > MATIERES_VISIBLES_MIN && (
              <button
                type="button"
                onClick={() => setMatieresDepliees((v) => !v)}
                aria-expanded={matieresDepliees}
                className={cn(
                  "mt-2 inline-flex items-center gap-1 text-xs font-medium text-muted-foreground transition-colors hover:text-primary",
                  subjectsTries.length <= MATIERES_VISIBLES_MAX && !matieresDepliees && "lg:hidden",
                )}
              >
                <ChevronDown className={cn("size-3.5 transition-transform", matieresDepliees && "rotate-180")} />
                {matieresDepliees ? "Réduire" : `Toutes les matières (${subjectsTries.length})`}
              </button>
            )}
          </div>
        )}

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Select value={cursusFilter || "all"} onValueChange={(v) => updateFilter("cursus", v === "all" ? "" : v)}>
            <SelectTrigger className="w-full sm:w-56">
              <SelectValue placeholder="Tous les cursus" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les cursus</SelectItem>
              {cursusList.map((c) => (
                <SelectItem key={c.id} value={String(c.id)}>
                  {c.examen_display}
                  {c.series ? ` - Série ${c.series.code}` : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={origineFilter || "all"}
            onValueChange={(v) => updateFilter("origine", v === "all" ? "" : v)}
          >
            <SelectTrigger className="w-full sm:w-48">
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
            <SelectTrigger className="w-full sm:w-40">
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

          <Select value={ordering || "default"} onValueChange={(v) => updateFilter("ordering", v === "default" ? "" : v)}>
            <SelectTrigger className="w-full sm:w-48">
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
        </div>

        {activeFilterChips.length > 0 && (
          <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-border pt-3.5">
            {activeFilterChips.map((chip) => (
              <FilterChip key={chip.key} label={chip.label} onRemove={chip.clear} />
            ))}
            {activeFilterChips.length > 1 && (
              <button
                type="button"
                onClick={resetFilters}
                className="text-xs font-medium text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
              >
                Tout effacer
              </button>
            )}
          </div>
        )}
      </div>

      {country && subjectFilter && cursusFilter && (
        <ThemesFrequents country={country} cursusId={Number(cursusFilter)} subjectCode={subjectFilter} />
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <EpreuveCardSkeleton key={i} />
          ))}
        </div>
      ) : epreuvesList.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-20 text-center text-muted-foreground">
          <BookOpen className="size-8" />
          <p>Aucune épreuve ne correspond à ces critères.</p>
          {(activeFilterChips.length > 0 || search) && (
            <Button variant="outline" size="sm" onClick={resetFilters}>
              Réinitialiser la recherche
            </Button>
          )}
        </div>
      ) : (
        <>
          {/* Barre de résultats collante : même hauteur (top-[72px]) et même motif que
              /cours - voir CoursListPage pour l'explication de cette valeur exacte. */}
          <div className="sticky top-[72px] z-10 -mx-4 mb-4 flex items-center justify-between gap-3 border-b border-border bg-background/85 px-4 py-2.5 backdrop-blur sm:-mx-6 sm:px-6">
            <p className="text-sm text-muted-foreground">
              <span className="font-medium tabular-nums text-foreground">{formatAmount(count)}</span> épreuve
              {count > 1 ? "s" : ""} trouvée{count > 1 ? "s" : ""}
            </p>
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
