import { useEffect, useMemo, useRef, useState } from "react"
import { useParams, useSearchParams } from "react-router-dom"
import { AideContextuelle } from "@/components/guides/AideContextuelle"
import { keepPreviousData, useInfiniteQuery, useQuery } from "@tanstack/react-query"
import {
  Crown,
  Timer,
  Gift,
  LayoutGrid,
  List,
  Loader2,
  RefreshCw,
  Search,
  SearchX,
  X,
} from "lucide-react"

import { listEpreuves, listSubjects } from "@/api/endpoints"
import type { NatureEpreuve, Origine } from "@/api/types"
import { nomPays } from "@/lib/pays"
import { localeCourante, t, tn, useI18n, type CleI18n } from "@/lib/i18n"
import { langueDeListe, PARAM_TOUTES_LANGUES } from "@/lib/discipline"
import { FILTERS_SESSION_KEY } from "@/lib/filtresListe"
import { useAbandonCursusHorsLangue, useCursusListe } from "@/lib/cursusLangue"
import { useDeclarerSiRienDeclare } from "@/lib/declarerCursus"
import { useSeo } from "@/lib/seo"
import { nouveauGermeAleatoire, triDepuisUrl, triPourApi, valeurUrlDuTri } from "@/lib/triEpreuves"
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
import { BandeauVue } from "@/components/BandeauVue"
import { useAbonneActif, useCursusAbonne } from "@/lib/abonneActif"
import { EpreuveCard } from "@/components/EpreuveCard"
import { EpreuveListRow } from "@/components/EpreuveListRow"
import { BoutonFiltres, MenuFiltre } from "@/components/FiltresCatalogue"
import { ThemesFrequents } from "@/components/ThemesFrequents"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ReviserTabs } from "@/components/ReviserTabs"
import { desactiverFiltreCursus, useFiltreCursusParDefaut } from "@/lib/filtreCursus"
import { useInedites } from "@/lib/cursusAccueil"
import { ErreurChargement } from "@/components/ErreurChargement"
import { SITE_NAME } from "@/lib/site"

type ViewMode = "cards" | "list"

const VIEW_MODE_STORAGE_KEY = "edukamer_epreuves_catalogue_view"
// Mémorise la dernière recherche filtrée (voir plus bas) - un lien nu vers /epreuves
// (nav, logo, retour) doit rouvrir là où l'utilisateur en était, pas repartir d'une
// liste vierge à chaque clic. Session, pas localStorage : une recherche n'a pas
// vocation à survivre à la fermeture de l'onglet, contrairement à une préférence
// d'affichage. La clé est dans lib/filtresListe : un changement de langue l'oublie.

// "tout" inclus : le choix d'élargir au-delà de son cursus (voir filtreCursus) doit
// se restaurer comme les autres filtres, sinon le pré-filtrage revient à la
// navigation suivante et le bouton "Voir tout le catalogue" semble sans effet.
const FILTER_KEYS = ["subject", "cursus", "origine", "nature", "gratuit", "mini", "search", "ordering", "tout"]

const ORIGINE_LABELS: Record<Origine, CleI18n> = {
  OFFICIEL: "ep.origine_OFFICIEL",
  BLANC: "ep.origine_BLANC",
  ETABLISSEMENT: "ep.origine_ETABLISSEMENT",
  AUTRE: "ep.origine_AUTRE",
  INEDITE: "ep.origine_INEDITE",
}

const NATURE_LABELS: Record<NatureEpreuve, CleI18n> = {
  THEORIQUE: "ep.nature_THEORIQUE",
  PRATIQUE: "ep.nature_PRATIQUE",
}

// Trois tris : « Plus récentes (année) » (le défaut : des plus récentes aux plus anciennes), « Ajoutées
// récemment » puis « Aléatoire ». Les règles sont dans lib/triEpreuves.ts.
const ORDERING_LABELS = {
  annee: "ep.tri_annee",
  recent: "ep.tri_recent",
  aleatoire: "ep.tri_aleatoire",
} as const satisfies Record<string, CleI18n>

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
      // Le libellé seul (« BAC D ») ne dit pas que le bouton retire le filtre : sans cela, un
      // lecteur d'écran annonce juste le nom de la puce. min-h-9 : cible tactile utilisable.
      aria-label={t("ep.retirer_filtre", { label })}
      className="inline-flex min-h-9 items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/15"
    >
      {label}
      <X className="size-3" aria-hidden="true" />
    </button>
  )
}

export function EpreuvesListPage() {
  const abonne = useAbonneActif()
  const cursusAbonne = useCursusAbonne()
  useI18n()
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = nomPays(countries, country)

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
  const { cursusPrepare } = useFiltreCursusParDefaut()
  const declarerSiRienDeclare = useDeclarerSiRienDeclare()
  useAbandonCursusHorsLangue(country)

  const subjectFilter = searchParams.get("subject") ?? ""
  const cursusFilter = searchParams.get("cursus") ?? ""
  // Sans examen choisi, la liste suit la langue de l'interface (le GCE a ses propres matières) ; « Toutes les langues » lève ce filtre.
  const toutesLangues = searchParams.get(PARAM_TOUTES_LANGUES) === "toutes"
  const langueFiltre = langueDeListe(cursusFilter, toutesLangues)
  const origineFilter = (searchParams.get("origine") ?? "") as Origine | ""
  const natureFilter = (searchParams.get("nature") ?? "") as NatureEpreuve | ""
  const gratuitFilter = searchParams.get("gratuit") === "true"
  const miniFilter = searchParams.get("mini") === "true"
  const search = searchParams.get("search") ?? ""
  const ordering = triDepuisUrl(searchParams.get("ordering"))
  // Germe du tri aléatoire : fixé pour la visite (le défilement infini redemande la liste page par page, il
  // lui faut le même ordre), renouvelé quand on re-choisit « Aléatoire » pour une autre sélection.
  const [germeAleatoire, setGermeAleatoire] = useState(nouveauGermeAleatoire)

  // Arrivé par « Inédites » (menu, accueil, fiche) : la page parle d'inédites, pas d'annales. Le
  // titre « Toutes les annales corrigées » au-dessus d'une liste d'épreuves jamais tirées des
  // annales disait l'inverse de ce que le visiteur venait chercher.
  const pageInedites = origineFilter === "INEDITE"

  useSeo({
    // Avec le pays, comme le titre servi aux moteurs (backend/catalog/pages_statiques) : le même texte des deux côtés.
    title: pageInedites ? t("ep.seo_inedites") : countryLabel ? t("ep.seo_liste_pays", { pays: countryLabel }) : t("ep.seo_liste"),
    description: pageInedites
      ? countryLabel
        ? t("ep.seo_desc_inedites_pays", { pays: countryLabel, site: SITE_NAME })
        : t("ep.seo_desc_inedites", { site: SITE_NAME })
      : countryLabel
        ? t("ep.seo_desc_liste_pays", { pays: countryLabel })
        : undefined,
  })

  // Un examen choisi → seules les matières de cet examen (« Allemand » sous BEPC menait à une
  // liste vide). Sans examen, toutes les matières du pays.
  const { data: subjects = [], isSuccess: subjectsChargees, isPlaceholderData: subjectsPlaceholder } = useQuery({
    queryKey: ["subjects", country, cursusFilter, langueFiltre, "epreuves"],
    queryFn: ({ signal }) =>
      listSubjects(country, signal, cursusFilter ? Number(cursusFilter) : undefined, langueFiltre, "epreuves"),
    placeholderData: keepPreviousData,
  })

  // Une matière déjà choisie qui n'existe pas dans le nouvel examen ferait une liste vide
  // sans pastille active pour s'en défaire : on l'abandonne.
  useEffect(() => {
    if (!cursusFilter || !subjectFilter || !subjectsChargees || subjectsPlaceholder) return
    if (!subjects.some((s) => s.code === subjectFilter)) updateFilter("subject", "")
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cursusFilter, subjectFilter, subjects, subjectsChargees, subjectsPlaceholder])

  // Sur la page des inédites, ne proposer que les matières et examens qui EN ONT : vingt-deux
  // pastilles de matières dont la plupart menaient à une liste vide poussaient les résultats à
  // plus d'un écran de hauteur. Même requête (et même cache) que le point du menu.
  const { data: ineditesDuPays } = useInedites(country ?? "", null, pageInedites)
  const couvertureInedites = useMemo(() => {
    // Liste tronquée par la pagination : on ne sait pas tout ce qu'elle couvre, on ne filtre pas.
    if (!pageInedites || !ineditesDuPays || ineditesDuPays.results.length < ineditesDuPays.count) return null
    return {
      matieres: new Set(ineditesDuPays.results.map((e) => e.subject.code)),
      cursus: new Set(ineditesDuPays.results.flatMap((e) => e.cursus.map((c) => c.id))),
    }
  }, [pageInedites, ineditesDuPays])

  // « Gratuites » n'a de sens sur la page des inédites que s'il y en a une d'offerte (voir
  // EpreuveInedite.est_gratuite) - sinon la pastille mènerait à une liste vide.
  const uneInediteOfferte = Boolean(ineditesDuPays?.results.some((e) => e.est_vitrine))

  const subjectsTries = useMemo(
    () =>
      [...subjects]
        .filter((s) => !couvertureInedites || couvertureInedites.matieres.has(s.code) || s.code === subjectFilter)
        .sort((a, b) => a.label.localeCompare(b.label, localeCourante())),
    [subjects, couvertureInedites, subjectFilter],
  )

  // Les examens proposés suivent la langue de l'interface (« Toutes les langues » les montre tous) ; seul l'examen
  // déjà choisi reste proposé quelle que soit sa langue. L'examen déclaré, lui, n'est pas gardé : en anglais, un
  // « Probatoire C » parmi les pastilles du GCE n'avait rien à y faire (voir lib/cursusLangue).
  const { data: cursusList } = useCursusListe(country, {
    langue: langueDeListe("", toutesLangues),
    garder: [cursusFilter],
    fixeLaLangue: true,
  })

  // Les filtres de second rang (gratuites, inédites, origine, nature) sont repliés derrière « Filtres » ; ceux qui sont
  // actifs restent visibles en puces, panneau fermé (on doit voir ce qui restreint la liste).
  const [plusOuvert, setPlusOuvert] = useState(false)

  const debouncedSearch = useDebouncedValue(search, 300)

  const epreuvesQuery = useInfiniteQuery({
    queryKey: [
      "epreuves",
      country,
      subjectFilter,
      cursusFilter,
      langueFiltre,
      origineFilter,
      natureFilter,
      gratuitFilter,
      miniFilter,
      debouncedSearch,
      ordering,
      ordering === "aleatoire" ? germeAleatoire : null,
    ],
    queryFn: ({ pageParam, signal }) =>
      listEpreuves(
        {
          subject: subjectFilter || undefined,
          cursus: cursusFilter ? Number(cursusFilter) : undefined,
          langue: langueFiltre,
          country,
          origine: origineFilter || undefined,
          nature: natureFilter || undefined,
          // Jamais `false` : le backend ne teste que la valeur "true", envoyer
          // est_vitrine=false polluerait l'URL de l'API pour rien.
          est_vitrine: gratuitFilter || undefined,
          mini: miniFilter || undefined,
          search: debouncedSearch || undefined,
          ordering: triPourApi(ordering),
          seed: ordering === "aleatoire" ? germeAleatoire : undefined,
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
  // Page N+1 en échec alors que les pages précédentes sont là : on garde la liste et on offre un
  // repli (voir plus bas). Sans ce drapeau, l'observateur ci-dessous relançait la requête en boucle.
  const erreurPageSuivante = epreuvesQuery.isFetchNextPageError

  // Chargement automatique au défilement plutôt qu'un bouton "Charger plus" : sur un
  // catalogue de plusieurs centaines d'épreuves, laisser la lecture continuer sans
  // interruption réduit la friction du parcours de recherche. La sentinelle vit après
  // la grille ; elle entre dans le viewport un peu avant que l'utilisateur n'atteigne
  // réellement le bas, pour que la page suivante soit déjà là le temps qu'il y arrive.
  const sentinelRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const el = sentinelRef.current
    // Pas d'observateur après un échec : la sentinelle est encore dans le viewport, il
    // relancerait la requête à chaque rendu. Le bouton « Charger plus » prend le relais.
    if (!el || !hasMore || erreurPageSuivante) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isLoadingMore) epreuvesQuery.fetchNextPage()
      },
      { rootMargin: "400px" },
    )
    observer.observe(el)
    return () => observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasMore, isLoadingMore, erreurPageSuivante])

  const [viewMode, setViewModeState] = useState<ViewMode>(() => {
    try {
      const stocke = localStorage.getItem(VIEW_MODE_STORAGE_KEY)
      if (stocke === "cards" || stocke === "list") return stocke
    } catch {
      // stockage indisponible : on retombe sur le défaut ci-dessous
    }
    // Sans préférence enregistrée : la liste sur un téléphone, les cartes ailleurs. Une carte d'épreuve ou de cours fait
    // ~260 px de haut, la liste en tient trois fois plus par écran (revue des pages de liste, 2026-11-23).
    return window.matchMedia?.("(max-width: 639px)").matches ? "list" : "cards"
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
        // Retirer le cursus (puce, « Tous », re-clic sur la pastille) est un choix explicite :
        // sans `tout=1`, le pré-filtrage le remettait aussitôt dans l'URL.
        else if (key === "cursus" && cursusPrepare) desactiverFiltreCursus(next)
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
        // « Tout effacer » veut dire tout le catalogue : on garde `tout=1` (et on le mémorise en
        // session) pour que le cursus par défaut ne revienne pas au prochain rendu.
        // Un abonné garde son examen ; sinon « tout effacer » veut dire tout le catalogue.
        if (cursusAbonne) next.set("cursus", String(cursusAbonne))
        else if (cursusPrepare) desactiverFiltreCursus(next)
        try {
          if (cursusPrepare) sessionStorage.setItem(FILTERS_SESSION_KEY, next.toString())
          else sessionStorage.removeItem(FILTERS_SESSION_KEY)
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
    // Un abonné n'a que son examen : sa puce (et sa croix) n'apporte rien, et le retirer ouvrirait tout le catalogue.
    cursusFilter && cursusFilter !== String(cursusAbonne) && {
      key: "cursus",
      label: (() => {
        const c = cursusList.find((c) => String(c.id) === cursusFilter)
        return c ? `${c.examen_display}${c.series ? ` - ${t("prix.serie", { code: c.series.code })}` : ""}` : cursusFilter
      })(),
      clear: () => updateFilter("cursus", ""),
    },
    miniFilter && {
      key: "mini",
      label: t("ep.mini_filtre"),
      clear: () => updateFilter("mini", ""),
    },
    origineFilter && {
      key: "origine",
      label: t(ORIGINE_LABELS[origineFilter]),
      clear: () => updateFilter("origine", ""),
    },
    natureFilter && {
      key: "nature",
      label: t(NATURE_LABELS[natureFilter]),
      clear: () => updateFilter("nature", ""),
    },
    gratuitFilter && {
      key: "gratuit",
      label: t("ep.gratuites_seules"),
      clear: () => updateFilter("gratuit", ""),
    },
  ].filter((chip): chip is { key: string; label: string; clear: () => void } => Boolean(chip))

  // Sur la page des inédites l'origine est déjà la page elle-même : pas de « 1 » sur le bouton « Filtres ».
  const nbFiltresSecondaires = [
    gratuitFilter,
    miniFilter,
    Boolean(origineFilter) && !pageInedites,
    Boolean(natureFilter),
  ].filter(Boolean).length
  // Le cursus est LE filtre d'un élève ("mon BAC D") : en pastilles d'un clic plutôt que caché
  // dans une liste déroulante, triées pour que les séries d'un même examen se suivent.
  const cursusTries = cursusList
    .filter((c) => !couvertureInedites || couvertureInedites.cursus.has(c.id) || String(c.id) === cursusFilter)
    .sort(
    (x, y) =>
      x.examen_display.localeCompare(y.examen_display, localeCourante()) ||
      (x.series?.code ?? "").localeCompare(y.series?.code ?? "", localeCourante()),
  )
  const pucesSecondaires = activeFilterChips.filter((chip) => chip.key !== "subject" && chip.key !== "cursus")

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <ReviserTabs sansLoupeMobile />
      <BandeauVue />
      {/* Un titre d'une ligne : la grande carte de présentation repoussait le premier résultat sous le premier écran
          d'un téléphone (revue du 2026-11-25). Pour un abonné, la liste générale n'en montre aucun : l'onglet
          « Épreuves » la nomme déjà. */}
      <h1
        className={
          abonne && !pageInedites
            ? "sr-only"
            : "mb-3 font-display text-xl font-semibold tracking-tight sm:text-2xl"
        }
      >
        {pageInedites ? t("ep.seo_inedites") : t("ep.titre_court")}
      </h1>

      {/* Recherche, examen, matière : les trois gestes de base. Tout le reste est derrière « Filtres ». Sur un téléphone,
          la recherche et « Filtres » sur une ligne, les deux menus dessous ; dès `sm`, tout sur une ligne. */}
      <div className="mb-4">
        <div className="flex flex-wrap items-center gap-2">
          <div className={cn("flex w-full gap-2 sm:w-auto sm:flex-1", pageInedites && "hidden")}>
            <div className={cn("group relative min-w-0 flex-1", pageInedites && "hidden")}>
              <Search className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
              <Input
                type="search"
                inputMode="search"
                enterKeyHint="search"
                aria-label={t("ep.rechercher")}
                placeholder={t("ep.rechercher_court")}
                value={search}
                onChange={(e) => updateFilter("search", e.target.value)}
                className="h-11 border-input pl-10 pr-10 text-base shadow-none focus-visible:border-primary/60 focus-visible:ring-primary/25 [&::-webkit-search-cancel-button]:hidden"
              />
              {search && (
                <button
                  type="button"
                  onClick={() => updateFilter("search", "")}
                  aria-label={t("ep.effacer")}
                  className="absolute right-2 top-1/2 flex size-8 -translate-y-1/2 items-center justify-center rounded-full text-muted-foreground hover:bg-muted hover:text-foreground"
                >
                  <X className="size-4" />
                </button>
              )}
            </div>
            <BoutonFiltres
              ouvert={plusOuvert}
              nombre={nbFiltresSecondaires}
              onClick={() => setPlusOuvert((v) => !v)}
              className="sm:hidden"
            />
          </div>
          {!abonne && cursusTries.length > 0 && (
            <MenuFiltre
              titre={t("quiz.examen")}
              valeur={cursusFilter}
              libelleTout={t("ep.tous_examens_menu")}
              options={cursusTries.map((c) => ({
                valeur: String(c.id),
                libelle: `${c.examen_display}${c.series ? ` ${c.series.code}` : ""}`,
              }))}
              onChange={(v) => {
                updateFilter("cursus", v)
                declarerSiRienDeclare(cursusTries.find((c) => String(c.id) === v))
              }}
            />
          )}
          {subjectsTries.length > 0 && (
            <MenuFiltre
              titre={t("quiz.matiere")}
              valeur={subjectFilter}
              libelleTout={t("ep.toutes_matieres_menu")}
              options={subjectsTries.map((subject) => {
                const SubjectIcon = subjectIcon(subject.code)
                const libelle = subjectShortLabel(subject.code, subject.label)
                return {
                  valeur: subject.code,
                  libelle,
                  contenu: (
                    <span className="flex items-center gap-2">
                      <span className={cn("flex size-5 items-center justify-center rounded-full", couleurMatiere(subject.code).puce)}>
                        <SubjectIcon className="size-3" aria-hidden="true" />
                      </span>
                      {libelle}
                    </span>
                  ),
                }
              })}
              onChange={(v) => updateFilter("subject", v)}
            />
          )}
          <BoutonFiltres
            ouvert={plusOuvert}
            nombre={nbFiltresSecondaires}
            onClick={() => setPlusOuvert((v) => !v)}
            className={cn("h-9 rounded-full", !pageInedites && "max-sm:hidden")}
          />
        </div>

        {plusOuvert && (
          <div className="mt-2 flex flex-wrap items-center gap-2 rounded-xl bg-muted/50 p-3">
          <button
            type="button"
            hidden={pageInedites && !uneInediteOfferte}
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
            {t("ep.gratuites")}
          </button>
          <button
            type="button"
            onClick={() => updateFilter("origine", origineFilter === "INEDITE" ? "" : "INEDITE")}
            aria-pressed={origineFilter === "INEDITE"}
            className={cn(
              "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
              origineFilter === "INEDITE"
                ? "border-gold bg-gold text-gold-foreground"
                : "border-border text-muted-foreground hover:border-gold/40 hover:text-gold-text",
            )}
          >
            <Crown className="size-4" />
            {t("cpt.inedites")}
          </button>
          <button
            type="button"
            onClick={() => updateFilter("mini", miniFilter ? "" : "true")}
            aria-pressed={miniFilter}
            className={cn(
              "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
              miniFilter
                ? "border-gold bg-gold text-gold-foreground"
                : "border-gold/40 text-gold-text hover:border-gold hover:bg-gold/10",
            )}
          >
            <Timer className="size-4" />
            {t("ep.mini_filtre")}
          </button>
            <Select
              value={origineFilter || "all"}
              onValueChange={(v) => updateFilter("origine", v === "all" ? "" : v)}
            >
              <SelectTrigger className="w-full bg-background sm:w-52" aria-label={t("ep.origine")}>
                <SelectValue placeholder={t("ep.toute_origine")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t("ep.toute_origine")}</SelectItem>
                {(Object.keys(ORIGINE_LABELS) as Origine[]).map((code) => (
                  <SelectItem key={code} value={code}>
                    {t(ORIGINE_LABELS[code])}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={natureFilter || "all"} onValueChange={(v) => updateFilter("nature", v === "all" ? "" : v)}>
              <SelectTrigger className="w-full bg-background sm:w-48" aria-label={t("ep.theorique_pratique_aria")}>
                <SelectValue placeholder={t("ep.theorique_pratique")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t("ep.theorique_pratique")}</SelectItem>
                {(Object.keys(NATURE_LABELS) as NatureEpreuve[]).map((code) => (
                  <SelectItem key={code} value={code}>
                    {t(NATURE_LABELS[code])}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {(pucesSecondaires.length > 0 || activeFilterChips.length > 1) && (
          <div className="mt-2 flex flex-wrap items-center gap-2">
            {pucesSecondaires.map((chip) => (
              <FilterChip key={chip.key} label={chip.label} onRemove={chip.clear} />
            ))}
            {activeFilterChips.length > 1 && (
              <button
                type="button"
                onClick={resetFilters}
                className="text-sm font-medium text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
              >
                {t("ep.tout_effacer")}
              </button>
            )}
          </div>
        )}
      </div>

      {/* La première visite montre l'aide de la page, sous les filtres qu'elle explique ; ensuite elle se relance par
          le « ? » de l'en-tête. */}
      <AideContextuelle guide="annales" className="mt-0 mb-4" />

      {country && subjectFilter && cursusFilter && (
        <ThemesFrequents
          country={country}
          cursusId={Number(cursusFilter)}
          subjectCode={subjectFilter}
        />
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true" aria-label={t("ep.chargement")}>
          {Array.from({ length: 6 }).map((_, i) => (
            <EpreuveCardSkeleton key={i} />
          ))}
        </div>
      ) : epreuvesQuery.isError && epreuvesList.length === 0 ? (
        // Une panne n'est pas "aucun résultat" : sans ce cas, une coupure réseau se lisait
        // comme un catalogue vide et l'élève cherchait l'erreur dans ses filtres.
        <ErreurChargement
          objet={t("ep.objet")}
          message={t("ep.erreur_message")}
          onRetry={() => epreuvesQuery.refetch()}
        />
      ) : epreuvesList.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-card/60 px-6 py-14 text-center">
          <span className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <SearchX className="size-6" />
          </span>
          <p className="font-display text-lg font-semibold">{t("ep.aucune")}</p>
          <p className="max-w-sm text-sm text-muted-foreground">
            {search
              ? t("ep.aucune_recherche", { search })
              : t("ep.aucune_filtre")}
          </p>
          <div className="mt-1 flex flex-wrap justify-center gap-2">
            {(activeFilterChips.length > 0 || search) && (
              <Button variant="outline" onClick={resetFilters} className="rounded-full">
                {t("ep.reinitialiser")}
              </Button>
            )}
            {!gratuitFilter && (
              <Button variant="ghost" onClick={() => updateFilter("gratuit", "true")} className="rounded-full">
                <Gift />
                {t("ep.voir_gratuites")}
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
              <span className="font-medium tabular-nums text-foreground">{formatAmount(count)}</span> {tn("ep.trouvees", count)}
            </p>
            <div className="flex shrink-0 items-center gap-2">
            <Select
              value={ordering}
              onValueChange={(v) => {
                if (v === "aleatoire") setGermeAleatoire(nouveauGermeAleatoire())
                updateFilter("ordering", valeurUrlDuTri(v))
              }}
            >
              <SelectTrigger className="h-8 w-36 text-xs sm:w-48 sm:text-sm" aria-label={t("ep.trier")}>
                <SelectValue placeholder={t("ep.tri_annee")} />
              </SelectTrigger>
              <SelectContent>
                {(Object.keys(ORDERING_LABELS) as (keyof typeof ORDERING_LABELS)[]).map((key) => (
                  <SelectItem key={key} value={key}>
                    {t(ORDERING_LABELS[key])}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="flex shrink-0 gap-1 rounded-md border border-border p-0.5">
              <Button
                variant={viewMode === "cards" ? "secondary" : "ghost"}
                size="icon"
                className="size-7 tap-target-44"
                aria-label={t("ep.vue_cartes")}
                aria-pressed={viewMode === "cards"}
                onClick={() => setViewMode("cards")}
              >
                <LayoutGrid className="size-4" />
              </Button>
              <Button
                variant={viewMode === "list" ? "secondary" : "ghost"}
                size="icon"
                className="size-7 tap-target-44"
                aria-label={t("ep.vue_liste")}
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
                  niveauTitre={2}
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
              {erreurPageSuivante && !isLoadingMore && (
                <div role="alert" className="flex flex-col items-center gap-2 text-center">
                  <p className="text-sm text-destructive">{t("ep.suite_erreur")}</p>
                  <Button variant="outline" onClick={() => epreuvesQuery.fetchNextPage()} className="min-h-11">
                    <RefreshCw />
                    {t("ep.charger_plus")}
                  </Button>
                </div>
              )}
              <p className="text-xs tabular-nums text-muted-foreground">
                {t("ep.sur", { a: formatAmount(epreuvesList.length), b: formatAmount(count) })}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
