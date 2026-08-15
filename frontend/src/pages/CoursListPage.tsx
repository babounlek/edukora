import { useEffect, useRef, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { ArrowRight, GraduationCap, LayoutGrid, List, Loader2, Search, X } from "lucide-react"

import { getMyProgression, listCours, listCursus, listSubjects } from "@/api/endpoints"
import type { Cours, Cursus, Progression, Subject } from "@/api/types"
import { useSeo } from "@/lib/seo"
import { coursReaderPath } from "@/lib/countryPath"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { CoursCard } from "@/components/CoursCard"
import { CoursListRow } from "@/components/CoursListRow"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type ViewMode = "cards" | "list"

const VIEW_MODE_STORAGE_KEY = "edukamer_cours_catalogue_view"

function CoursCardSkeleton() {
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

export function CoursListPage() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label
  const { isAuthenticated } = useAuth()
  const [progression, setProgression] = useState<Progression | null>(null)

  // "Reprendre ma lecture" - même logique que CataloguePage : silencieusement absent
  // (pas d'erreur affichée) pour un visiteur anonyme ou sans historique, ce n'est
  // qu'un raccourci, jamais un contenu qu'on impose de voir.
  useEffect(() => {
    if (!isAuthenticated) {
      setProgression(null)
      return
    }
    getMyProgression().then(setProgression).catch(() => {})
  }, [isAuthenticated])

  // La query string est la source de vérité des filtres (pas un useState en plus) :
  // une recherche filtrée doit rester bookmarkable/partageable et survivre à un
  // rechargement, et le bouton précédent/suivant du navigateur doit la restaurer.
  const [searchParams, setSearchParams] = useSearchParams()
  const subjectFilter = searchParams.get("subject") ?? ""
  const cursusFilter = searchParams.get("cursus") ?? ""
  const search = searchParams.get("search") ?? ""

  useSeo({
    title: "Cours de révision",
    description: countryLabel
      ? `${countryLabel} : cours structurés (méthode, exemple résolu, erreurs classiques, exercices) pour le BEPC, le Probatoire et le BAC.`
      : undefined,
  })

  const [coursList, setCoursList] = useState<Cours[]>([])
  const [count, setCount] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [page, setPage] = useState(1)
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [cursusList, setCursusList] = useState<Cursus[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingMore, setIsLoadingMore] = useState(false)

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
  // les filtres d'une URL partagée (ex. /cm?subject=MATH) dès le chargement.
  const previousCountryRef = useRef(country)

  function updateFilter(key: string, value: string) {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        if (value) next.set(key, value)
        else next.delete(key)
        return next
      },
      { replace: true },
    )
  }

  useEffect(() => {
    listSubjects(country).then(setSubjects).catch(() => {})
    listCursus(country).then(setCursusList).catch(() => {})

    if (previousCountryRef.current === country) return
    previousCountryRef.current = country

    // Une matière/un cursus sélectionné dans un autre pays n'existe plus dans les
    // nouvelles listes.
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

  useEffect(() => {
    setIsLoading(true)
    const timeout = setTimeout(() => {
      listCours({
        subject: subjectFilter || undefined,
        cursus: cursusFilter ? Number(cursusFilter) : undefined,
        country,
        search: search || undefined,
        page: 1,
      })
        .then((data) => {
          setCoursList(data.results)
          setCount(data.count)
          setHasMore(data.next !== null)
          setPage(1)
        })
        .finally(() => setIsLoading(false))
    }, 300)
    return () => clearTimeout(timeout)
  }, [subjectFilter, cursusFilter, search, country])

  function handleLoadMore() {
    const nextPage = page + 1
    setIsLoadingMore(true)
    listCours({
      subject: subjectFilter || undefined,
      cursus: cursusFilter ? Number(cursusFilter) : undefined,
      country,
      search: search || undefined,
      page: nextPage,
    })
      .then((data) => {
        setCoursList((prev) => [...prev, ...data.results])
        setHasMore(data.next !== null)
        setPage(nextPage)
      })
      .finally(() => setIsLoadingMore(false))
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
        <div className="relative mx-auto max-w-5xl px-4 py-14 sm:px-6">
          <p className="mb-2 font-display text-sm italic text-primary">
            Cours{countryLabel ? ` - ${countryLabel}` : ""}
          </p>
          <h1 className="max-w-xl font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
            Maîtrise la <span className="text-primary">méthode</span>, pas juste l'exercice du jour.
          </h1>
          <p className="mt-4 max-w-lg text-muted-foreground">
            Des cours complets sur chaque notion clé, avec exemple résolu, erreurs
            classiques et exercices gradués.
          </p>
        </div>
      </section>

      {progression && progression.cours.length > 0 && (
        <div className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
          <Link
            to={coursReaderPath(progression.cours[0].slug)}
            className="flex animate-fade-up items-center justify-between gap-3 rounded-lg border border-border bg-accent/40 px-4 py-3 text-sm transition-colors hover:border-primary/50 hover:bg-accent"
          >
            <span className="min-w-0">
              <span className="text-muted-foreground">Reprendre : </span>
              <span className="font-medium">{progression.cours[0].titre}</span>
            </span>
            <ArrowRight className="size-4 shrink-0 text-primary" />
          </Link>
        </div>
      )}

      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <div className="mb-8 flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Rechercher un cours..."
              value={search}
              onChange={(e) => updateFilter("search", e.target.value)}
              className="pl-9 pr-9"
            />
            {search && (
              <button
                type="button"
                onClick={() => updateFilter("search", "")}
                aria-label="Effacer la recherche"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="size-4" />
              </button>
            )}
          </div>
          <Select value={subjectFilter || "all"} onValueChange={(v) => updateFilter("subject", v === "all" ? "" : v)}>
            <SelectTrigger className="sm:w-56">
              <SelectValue placeholder="Toutes les matières" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Toutes les matières</SelectItem>
              {subjects.map((s) => (
                <SelectItem key={s.id} value={s.code}>
                  {s.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={cursusFilter || "all"} onValueChange={(v) => updateFilter("cursus", v === "all" ? "" : v)}>
            <SelectTrigger className="sm:w-56">
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
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <CoursCardSkeleton key={i} />
            ))}
          </div>
        ) : coursList.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-20 text-center text-muted-foreground">
            <GraduationCap className="size-8" />
            <p>Aucun cours ne correspond à ces critères.</p>
          </div>
        ) : (
          <>
            <div className="mb-4 flex items-center justify-between gap-3">
              <p className="text-sm text-muted-foreground">
                {count} cours trouvé{count > 1 ? "s" : ""}
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
                {coursList.map((cours, index) => (
                  <CoursCard
                    key={cours.id}
                    cours={cours}
                    className="animate-fade-up"
                    style={{ animationDelay: `${Math.min(index, 8) * 60}ms` }}
                  />
                ))}
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                {coursList.map((cours, index) => (
                  <CoursListRow
                    key={cours.id}
                    cours={cours}
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
    </div>
  )
}
