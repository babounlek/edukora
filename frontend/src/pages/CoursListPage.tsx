import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { useInfiniteQuery, useQuery } from "@tanstack/react-query"
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  GraduationCap,
  LayoutGrid,
  Layers,
  List,
  Loader2,
  Search,
  X,
} from "lucide-react"

import { getMyProgression, listCours, listCursus, listSubjects } from "@/api/endpoints"
import { examLevelsFor } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { useDebouncedValue } from "@/lib/useDebouncedValue"
import { subjectIcon } from "@/lib/subjectIcon"
import { subjectShortLabel } from "@/lib/subjectLabel"
import { coursReaderPath } from "@/lib/countryPath"
import { capitaliserTheme, cn, formatAmount } from "@/lib/utils"
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
import { ReviserTabs } from "@/components/ReviserTabs"

type ViewMode = "cards" | "list"

const VIEW_MODE_STORAGE_KEY = "edukamer_cours_catalogue_view"

/**
 * Nombre de matières montrées avant dépliage, par palier de largeur. Objectif : deux
 * rangées de pastilles au maximum dans TOUS les formats - au-delà, le bloc de filtres
 * repousse les résultats sous la ligne de flottaison, ce qu'aucun catalogue ne doit
 * faire.
 *
 * Ces quatre valeurs sont mesurées, pas estimées : rendu des pastilles réelles à
 * 375 / 660 / 768 / 1024 px, dans le pire cas (les libellés les plus longs du
 * référentiel camerounais, "Physique-Chimie-Tech." en tête). Un palier unique ne
 * marche pas : `sm` couvre de 640 à 1024 px, où la largeur utile double presque, et
 * une valeur sûre à 660 px gaspille la moitié de la ligne à 1024 px.
 *
 * À revoir si la taille des pastilles change (police, padding, compteur).
 */
const PALIERS_MATIERES = [
  { limite: 4, revele: "" },
  { limite: 5, revele: "sm:flex" },
  { limite: 7, revele: "md:flex" },
  { limite: 10, revele: "lg:flex" },
] as const

const MATIERES_VISIBLES_MIN = PALIERS_MATIERES[0].limite
const MATIERES_VISIBLES_MAX = PALIERS_MATIERES[PALIERS_MATIERES.length - 1].limite

/**
 * Classes de repli d'une pastille selon son rang : masquée jusqu'au palier de largeur
 * qui la fait rentrer dans les deux rangées, puis révélée. `undefined` pour les
 * premières, visibles partout.
 */
function classeRepliMatiere(index: number): string | undefined {
  if (index < MATIERES_VISIBLES_MIN) return undefined
  const palier = PALIERS_MATIERES.find((p) => index < p.limite)
  return palier ? `hidden ${palier.revele}` : "hidden"
}

function CoursCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <CardContent className="flex flex-col gap-2.5 p-4">
        <Skeleton className="size-9 rounded-lg" />
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
 * /epreuves : les deux catalogues doivent se piloter de la même façon. */
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

/** Statistique du hero - même gabarit que les puces de /quiz et /fiches. */
function StatChip({ icon, valeur, libelle }: { icon: ReactNode; valeur: string; libelle: string }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
      {icon}
      <span className="font-medium tabular-nums">{valeur}</span>
      <span className="text-muted-foreground">{libelle}</span>
    </span>
  )
}

export function CoursListPage() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label
  const { isAuthenticated } = useAuth()

  // La query string est la source de vérité des filtres (pas un useState en plus) :
  // une recherche filtrée doit rester bookmarkable/partageable et survivre à un
  // rechargement, et le bouton précédent/suivant du navigateur doit la restaurer.
  const [searchParams, setSearchParams] = useSearchParams()
  const subjectFilter = searchParams.get("subject") ?? ""
  const cursusFilter = searchParams.get("cursus") ?? ""
  const nonLusFilter = searchParams.get("nonlus") === "true"
  const search = searchParams.get("search") ?? ""
  // Arrivée depuis /parcours ("voir tous les cours" d'un savoir/thème) - `savoir` et
  // `theme` pilotent le filtre API (voir CoursListView), mutuellement exclusifs selon
  // que la matière est en mode Parcours par fréquence ou Module→Savoir classique (voir
  // ParcoursSubjectPage.lienCoursDuSavoir). `savoir_label` n'est qu'un libellé
  // d'affichage pour la puce de filtre ci-dessous (l'API ne le lit jamais).
  const savoirFilter = searchParams.get("savoir") ?? ""
  const themeFilter = searchParams.get("theme") ?? ""
  const savoirLabel = searchParams.get("savoir_label") ?? ""

  useSeo({
    title: "Cours de révision",
    description: countryLabel
      ? `${countryLabel} : cours structurés (méthode, exemple résolu, erreurs classiques, exercices) pour le BEPC, le Probatoire et le BAC.`
      : undefined,
  })

  // "Reprendre ma lecture" - même logique que CataloguePage : silencieusement absent
  // (pas d'erreur affichée) pour un visiteur anonyme ou sans historique, ce n'est
  // qu'un raccourci, jamais un contenu qu'on impose de voir. `enabled: false` laisse
  // le cache d'une session précédente intact plutôt que de le vider, d'où le second
  // garde sur isAuthenticated à la lecture (voir CataloguePage, même motif).
  const { data: progressionData } = useQuery({
    queryKey: ["progression"],
    queryFn: ({ signal }) => getMyProgression(signal),
    enabled: isAuthenticated,
  })
  const progression = isAuthenticated ? progressionData : undefined

  const { data: subjects = [] } = useQuery({
    queryKey: ["subjects", country],
    queryFn: ({ signal }) => listSubjects(country, signal),
  })

  // Par volume de cours décroissant, jamais l'ordre alphabétique de l'API : celui-ci
  // ouvrait la rangée sur Anglais, Chimie, Espagnol et reléguait Mathématiques en 8e
  // position, hors des premières pastilles alors que c'est la matière la plus
  // demandée. Départage par libellé pour un ordre stable entre deux matières à
  // volume égal. Copie explicite : sort() modifie le tableau en place, et celui-ci
  // appartient au cache de TanStack Query.
  const subjectsTries = useMemo(
    () =>
      [...subjects].sort(
        (a, b) => (b.cours_count ?? 0) - (a.cours_count ?? 0) || a.label.localeCompare(b.label, "fr"),
      ),
    [subjects],
  )

  // Déplié d'entrée quand une matière est déjà filtrée (lien partagé, retour
  // arrière) : la pastille active doit être visible, sinon le filtre s'applique sans
  // que rien à l'écran ne le montre. Initialiseur paresseux : il ne lit `subjectFilter`
  // qu'au premier rendu, le dépliage reste ensuite entre les mains de l'utilisateur et
  // ne se réinitialise pas à chaque changement de filtre. Depuis le routeur et non
  // window.location (comme le fait EpreuvesListPage) : les deux divergent dès qu'on
  // n'est pas sous un BrowserRouter, ce qu'un test a immédiatement montré.
  const [matieresDepliees, setMatieresDepliees] = useState(() => Boolean(subjectFilter))

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })

  const filtresActifs = Boolean(subjectFilter || cursusFilter || nonLusFilter || search || savoirFilter || themeFilter)

  // Volumétrie totale du pays, affichée dans le hero : jamais `count` de la liste
  // ci-dessous, qui est le nombre de résultats APRÈS filtrage et tomberait à 3 dès
  // qu'on tape un mot-clé. Sans filtre les deux coïncident, d'où le `enabled` : le
  // cas courant (arrivée sur la page nue) ne paie aucune requête supplémentaire, et
  // seule une arrivée déjà filtrée - un lien partagé - en déclenche une, pour que le
  // hero annonce quand même le catalogue complet.
  const { data: totalData } = useQuery({
    queryKey: ["cours-total", country],
    queryFn: ({ signal }) => listCours({ country }, signal),
    enabled: Boolean(country) && filtresActifs,
  })

  // Débounce la clé de query, pas le champ affiché : le champ reste réactif à chaque
  // frappe (il est contrôlé par `search` directement), seule la requête réseau attend
  // que l'utilisateur s'installe sur une valeur. Un changement de clé annule au
  // passage toute requête encore en vol pour l'ancienne (AbortSignal transmis à
  // fetch), donc plus besoin du setTimeout/clearTimeout manuel d'avant pour éviter
  // qu'une réponse tardive et périmée n'écrase un résultat plus récent.
  const debouncedSearch = useDebouncedValue(search, 300)

  const coursQuery = useInfiniteQuery({
    queryKey: ["cours", country, subjectFilter, cursusFilter, nonLusFilter, debouncedSearch, savoirFilter, themeFilter],
    queryFn: ({ pageParam, signal }) =>
      listCours(
        {
          subject: subjectFilter || undefined,
          cursus: cursusFilter ? Number(cursusFilter) : undefined,
          country,
          search: debouncedSearch || undefined,
          // Jamais `false` : le backend ne teste que la valeur "true", mais envoyer
          // exclude_read=false polluerait l'URL de l'API pour rien.
          exclude_read: nonLusFilter || undefined,
          savoir: savoirFilter ? Number(savoirFilter) : undefined,
          theme: themeFilter ? Number(themeFilter) : undefined,
          page: pageParam,
        },
        signal,
      ),
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => (lastPage.next ? allPages.length + 1 : undefined),
  })

  const coursList = coursQuery.data?.pages.flatMap((p) => p.results) ?? []
  const count = coursQuery.data?.pages[0]?.count ?? 0
  const hasMore = coursQuery.hasNextPage ?? false
  const isLoading = coursQuery.isLoading
  const isLoadingMore = coursQuery.isFetchingNextPage

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
  // les filtres d'une URL partagée (ex. /cm/cours?subject=MATHS) dès le chargement.
  const previousCountryRef = useRef(country)

  useEffect(() => {
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

  function resetFilters() {
    // Un seul setSearchParams pour toutes les clés : `searchParams` ne change qu'au
    // prochain rendu, donc plusieurs updateFilter() dans le même tick partiraient
    // chacun de l'état initial et n'en retireraient effectivement qu'un seul.
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        for (const key of ["subject", "cursus", "nonlus", "search", "savoir", "theme", "savoir_label"]) next.delete(key)
        return next
      },
      { replace: true },
    )
  }

  function clearSavoirFilter() {
    // `savoir`/`theme` et `savoir_label` vont toujours ensemble (voir
    // ParcoursSubjectPage.lienCoursDuSavoir) - même raison multi-clés que
    // resetFilters ci-dessus. Les deux clés sont mutuellement exclusives, donc
    // supprimer les deux à chaque fois est sans risque.
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        next.delete("savoir")
        next.delete("theme")
        next.delete("savoir_label")
        return next
      },
      { replace: true },
    )
  }

  // Une puce par filtre actif (hors recherche texte, déjà visible dans son propre
  // champ) - vue d'ensemble immédiate de ce qui restreint la liste, sans rouvrir
  // chaque menu pour vérifier.
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
    nonLusFilter && {
      key: "nonlus",
      label: "Non lus uniquement",
      clear: () => updateFilter("nonlus", ""),
    },
    savoirFilter && {
      key: "savoir",
      label: savoirLabel ? `Savoir : ${capitaliserTheme(savoirLabel)}` : "Savoir filtré",
      clear: clearSavoirFilter,
    },
    themeFilter && {
      key: "theme",
      label: savoirLabel ? `Thème : ${capitaliserTheme(savoirLabel)}` : "Thème filtré",
      clear: clearSavoirFilter,
    },
  ].filter((chip): chip is { key: string; label: string; clear: () => void } => Boolean(chip))

  // Niveaux d'examen réellement présents pour ce pays - jamais un texte fixe : la
  // plupart des pays n'ont pas de Probatoire (voir examLevelsFor).
  const examLevels = examLevelsFor(cursusList)
  const coursEnCours = progression?.cours?.[0]
  // `undefined` tant que rien n'est chargé - la puce du hero ne s'affiche pas plutôt
  // que d'annoncer un "0 cours publiés" démenti une seconde plus tard.
  const totalCours = filtresActifs ? totalData?.count : coursQuery.data ? count : undefined

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      <ReviserTabs />
      {/* Même gabarit de hero que /quiz et /fiches : carte arrondie contenue plutôt
          qu'une bande pleine largeur, pastille d'icône, accroche puis puces de
          volumétrie - les trois outils de la plateforme doivent se reconnaître. */}
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
            <GraduationCap className="size-5" />
          </div>
          <p className="mb-1 font-display text-sm italic text-primary">
            Cours structurés{countryLabel ? ` - ${countryLabel}` : ""}
          </p>
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">
            Maîtrise la <span className="text-primary">méthode</span>, pas juste l'exercice du jour.
          </h1>
          <p className="mt-2 text-muted-foreground">
            Chaque notion clé du programme en un cours complet : la règle, un exemple résolu pas à pas, les erreurs
            classiques à éviter et des exercices gradués.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            {totalCours !== undefined && (
              <StatChip
                icon={<BookOpen className="size-3.5 text-primary" />}
                valeur={formatAmount(totalCours)}
                libelle={totalCours > 1 ? "cours publiés" : "cours publié"}
              />
            )}
            {subjects.length > 0 && (
              <StatChip
                icon={<Layers className="size-3.5 text-gold" />}
                valeur={String(subjects.length)}
                libelle={subjects.length > 1 ? "matières couvertes" : "matière couverte"}
              />
            )}
            {examLevels.length > 0 && (
              <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
                <CheckCircle2 className="size-3.5 text-success" />
                <span className="text-muted-foreground">{examLevels.join(" · ")}</span>
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Reprise de lecture juste sous le hero, avant les filtres : pour qui revient,
          c'est l'action la plus probable de la page - la faire chercher au milieu
          d'une grille de plusieurs milliers de cartes n'aurait aucun sens. */}
      {coursEnCours && (
        <Link
          to={coursReaderPath(coursEnCours.slug)}
          className="group mb-6 flex items-center gap-3 rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent px-5 py-4 transition-colors hover:border-primary/50"
        >
          <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <BookOpen className="size-5" />
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Reprendre ma lecture
            </span>
            <span className="block truncate font-display font-medium">{coursEnCours.titre}</span>
          </span>
          <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
        </Link>
      )}

      {/* Panneau de recherche : la carte surélevée fait de la recherche le point focal
          de la page, comme sur /epreuves. Les matières sont des pastilles cliquables
          plutôt qu'un menu déroulant - sur un catalogue de plusieurs milliers de
          cours, choisir sa matière est le premier geste, il ne doit pas coûter deux
          clics et une lecture de liste. */}
      <div className="mb-6 rounded-2xl border border-border bg-card p-5 shadow-lg shadow-primary/5 sm:p-6">
        <div className="group relative">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            placeholder="Rechercher un cours (notion, chapitre, mot-clé)..."
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

        {/* Bloc de facettes qui s'enveloppe, jamais une rangée à défilement horizontal :
            une pastille coupée au bord d'un carrousel se rattrape (le parcours y est
            facultatif), une matière coupée dans un FILTRE cache une décision que le
            visiteur doit prendre - et la molette ne défile de toute façon pas
            horizontalement à la souris. Le repli passe par des classes conditionnelles
            plutôt que par un `overflow-hidden` sur une hauteur mesurée : `display:none`
            sort réellement les pastilles masquées du parcours clavier et de l'arbre
            d'accessibilité, là où un simple rognage les y laisserait, focalisables et
            invisibles. */}
        {subjectsTries.length > 0 && (
          <div className="mt-4">
            {/* role="group" nommé : sans lui, quinze boutons se suivent sans dire à un
                lecteur d'écran ce qu'ils ont en commun ni ce qu'ils pilotent. */}
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
                    {/* Compteur masqué sur téléphone : mesuré, il fait passer les
                        quatre premières pastilles de deux à trois rangées à 375 px.
                        C'est un repère de tri, pas une information dont dépend le
                        choix - il cède la place plutôt que la ligne. */}
                    {subject.cours_count !== undefined && (
                      <span className="hidden tabular-nums opacity-60 sm:inline">{subject.cours_count}</span>
                    )}
                  </button>
                )
              })}
            </div>

            {/* Libellé sans compteur : le nombre de matières masquées dépend de la
                largeur de l'écran (voir les deux seuils ci-dessus), un "+7" affiché
                mentirait sur l'un des deux formats. */}
            {subjectsTries.length > MATIERES_VISIBLES_MIN && (
              <button
                type="button"
                onClick={() => setMatieresDepliees((v) => !v)}
                aria-expanded={matieresDepliees}
                className={cn(
                  "mt-2 inline-flex items-center gap-1 text-xs font-medium text-muted-foreground transition-colors hover:text-primary",
                  // Sur grand écran tout tient déjà quand il y a peu de matières :
                  // proposer de "tout afficher" alors que tout est affiché n'aurait
                  // aucun sens.
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
            <SelectTrigger className="w-full sm:w-64">
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

          {/* Réservé aux connectés : le backend n'a aucun historique de lecture à
              exclure pour un visiteur anonyme (voir CoursListView.exclude_read), le
              bouton n'y filtrerait donc rien du tout. */}
          {isAuthenticated && (
            <button
              type="button"
              onClick={() => updateFilter("nonlus", nonLusFilter ? "" : "true")}
              aria-pressed={nonLusFilter}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
                nonLusFilter
                  ? "border-success/40 bg-success/15 text-success"
                  : "border-border text-muted-foreground hover:border-success/40 hover:text-success",
              )}
            >
              <CheckCircle2 className="size-3.5" />
              Masquer les cours déjà lus
            </button>
          )}
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

      {isLoading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CoursCardSkeleton key={i} />
          ))}
        </div>
      ) : coursList.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-20 text-center text-muted-foreground">
          <GraduationCap className="size-8" />
          <p>Aucun cours ne correspond à ces critères.</p>
          {(activeFilterChips.length > 0 || search) && (
            <Button variant="outline" size="sm" onClick={resetFilters}>
              Réinitialiser la recherche
            </Button>
          )}
        </div>
      ) : (
        <>
          {/* Barre de résultats collante : sur un catalogue de plusieurs milliers de
              cartes, le compteur et la bascule cartes/liste doivent rester atteignables
              sans remonter en haut de page. */}
          {/* top-[72px] = la hauteur exacte du Header collant (voir Header.tsx, même
              hauteur en mobile et en desktop) : une valeur ronde comme top-20
              laisserait une bande de 8px où le contenu défilerait à découvert entre
              les deux barres, top-16 ferait passer celle-ci sous le header. */}
          <div className="sticky top-[72px] z-10 -mx-4 mb-4 flex items-center justify-between gap-3 border-b border-border bg-background/85 px-4 py-2.5 backdrop-blur sm:-mx-6 sm:px-6">
            <p className="text-sm text-muted-foreground">
              <span className="font-medium tabular-nums text-foreground">{formatAmount(count)}</span> cours
              trouvé{count > 1 ? "s" : ""}
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
            <div className="mt-8 flex flex-col items-center gap-2">
              <Button variant="outline" onClick={() => coursQuery.fetchNextPage()} disabled={isLoadingMore}>
                {isLoadingMore && <Loader2 className="size-4 animate-spin" />}
                Charger plus
              </Button>
              {/* Repère de progression dans la liste : sans lui, "Charger plus" sur
                  3 700 résultats ne dit jamais où on en est ni combien il reste. */}
              <p className="text-xs tabular-nums text-muted-foreground">
                {formatAmount(coursList.length)} sur {formatAmount(count)}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
