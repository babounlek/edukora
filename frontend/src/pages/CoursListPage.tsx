import { useEffect, useMemo, useRef, useState, type ReactNode } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { keepPreviousData, useInfiniteQuery, useQuery } from "@tanstack/react-query"
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  GraduationCap,
  LayoutGrid,
  Layers,
  List,
  Loader2,
  Search,
  SearchX,
  Star,
  X,
} from "lucide-react"

import { getMyProgression, listCours, listSubjects } from "@/api/endpoints"
import { examLevelsFor } from "@/lib/cursus"
import { nomPays } from "@/lib/pays"
import { useSeo } from "@/lib/seo"
import { useDebouncedValue } from "@/lib/useDebouncedValue"
import { couleurMatiere } from "@/lib/matiereCouleur"
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
import { FiltreLigne, PastilleFiltre } from "@/components/FiltresCatalogue"
import { ReviserTabs } from "@/components/ReviserTabs"
import { BandeauFiltreCursus, desactiverFiltreCursus, useFiltreCursusParDefaut } from "@/lib/filtreCursus"
import { BandeauMatieres } from "@/components/ChoixMatieres"
import { ErreurChargement } from "@/components/ErreurChargement"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"
import { langueDeListe, PARAM_TOUTES_LANGUES } from "@/lib/discipline"
import { useAbandonCursusHorsLangue, useCursusListe } from "@/lib/cursusLangue"
import { useTotalCours } from "@/lib/totauxCatalogue"

type ViewMode = "cards" | "list"

const VIEW_MODE_STORAGE_KEY = "edukamer_cours_catalogue_view"

function CoursCardSkeleton() {
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
          <Skeleton className="h-5 w-20 rounded-md" />
          <Skeleton className="h-5 w-14 rounded-md" />
        </div>
        <Skeleton className="h-3 w-2/3" />
        <Skeleton className="mt-1 h-8 w-full" />
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
  useI18n()
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = nomPays(countries, country)
  const { isAuthenticated } = useAuth()

  // La query string est la source de vérité des filtres (pas un useState en plus) :
  // une recherche filtrée doit rester bookmarkable/partageable et survivre à un
  // rechargement, et le bouton précédent/suivant du navigateur doit la restaurer.
  const [searchParams, setSearchParams] = useSearchParams()
  // Pré-filtrage sur l'examen déclaré - voir useFiltreCursusParDefaut : un défaut
  // annoncé et réversible, jamais un masquage.
  const { cursusPrepare } = useFiltreCursusParDefaut()
  useAbandonCursusHorsLangue(country)
  const subjectFilter = searchParams.get("subject") ?? ""
  const cursusFilter = searchParams.get("cursus") ?? ""
  // Sans examen choisi, la liste suit la langue de l'interface ; « Toutes les langues » lève ce filtre.
  const toutesLangues = searchParams.get(PARAM_TOUTES_LANGUES) === "toutes"
  const langueFiltre = langueDeListe(cursusFilter, toutesLangues)
  const nonLusFilter = searchParams.get("nonlus") === "true"
  const frequentFilter = searchParams.get("frequent") === "true"
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
    title: t("co.seo_liste"),
    description: countryLabel ? t("co.seo_description_pays", { pays: countryLabel }) : undefined,
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

  // Un examen choisi → seules les matières de cet examen, jamais des pastilles qui mènent à une
  // liste vide. Sans examen, toutes les matières du pays.
  const { data: subjects = [], isSuccess: subjectsChargees, isPlaceholderData: subjectsPlaceholder } = useQuery({
    queryKey: ["subjects", country, cursusFilter, langueFiltre],
    queryFn: ({ signal }) => listSubjects(country, signal, cursusFilter ? Number(cursusFilter) : undefined, langueFiltre),
    placeholderData: keepPreviousData,
  })

  // Une matière déjà choisie qui n'existe pas dans le nouvel examen : on l'abandonne plutôt que
  // de laisser une liste vide sans pastille active pour s'en défaire.
  useEffect(() => {
    if (!cursusFilter || !subjectFilter || !subjectsChargees || subjectsPlaceholder) return
    if (!subjects.some((s) => s.code === subjectFilter)) updateFilter("subject", "")
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cursusFilter, subjectFilter, subjects, subjectsChargees, subjectsPlaceholder])

  // Par volume de cours décroissant, jamais l'ordre alphabétique de l'API : celui-ci
  // ouvrait la rangée sur Anglais, Chimie, Espagnol et reléguait Mathématiques en 8e
  // position, hors des premières pastilles alors que c'est la matière la plus
  // demandée. Départage par libellé pour un ordre stable entre deux matières à
  // volume égal. Copie explicite : sort() modifie le tableau en place, et celui-ci
  // appartient au cache de TanStack Query.
  const subjectsTries = useMemo(
    () =>
      [...subjects].sort(
        (a, b) => (b.cours_count ?? 0) - (a.cours_count ?? 0) || a.label.localeCompare(b.label, localeCourante()),
      ),
    [subjects],
  )

  // Les examens proposés suivent la langue de l'interface (« Toutes les langues » les montre tous) ; l'examen
  // déjà choisi et l'examen déclaré restent proposés quelle que soit leur langue (voir lib/cursusLangue).
  const { data: cursusList, tous: tousLesCursus } = useCursusListe(country, {
    langue: langueDeListe("", toutesLangues),
    garder: [cursusFilter, cursusPrepare?.id],
  })

  const filtresActifs = Boolean(subjectFilter || cursusFilter || nonLusFilter || frequentFilter || search || savoirFilter || themeFilter)

  // Volumétrie totale du pays, affichée dans le hero : jamais `count` de la liste
  // ci-dessous, qui est le nombre de résultats APRÈS filtrage et tomberait à 3 dès
  // qu'on tape un mot-clé. Sans filtre les deux coïncident, d'où le `enabled` : le
  // cas courant (arrivée sur la page nue) ne paie aucune requête supplémentaire, et
  // seule une arrivée déjà filtrée - un lien partagé - en déclenche une, pour que le
  // hero annonce quand même le catalogue complet.
  // Dans la langue de l'interface (sauf « Toutes les langues ») : le total d'un filtre actif ne doit pas
  // compter les cours de l'autre langue, que la liste n'affiche pas.
  // Un examen choisi fixe la langue du total, comme celle de la liste : sans cela, un lien vers un examen d'une
  // autre langue que l'interface annonçait le total de la langue de l'interface à côté d'une liste de l'examen.
  const cursusChoisi = tousLesCursus.find((c) => String(c.id) === cursusFilter)
  const { data: totalData } = useTotalCours(country, cursusChoisi?.langue ?? langueDeListe("", toutesLangues), filtresActifs)

  // Débounce la clé de query, pas le champ affiché : le champ reste réactif à chaque
  // frappe (il est contrôlé par `search` directement), seule la requête réseau attend
  // que l'utilisateur s'installe sur une valeur. Un changement de clé annule au
  // passage toute requête encore en vol pour l'ancienne (AbortSignal transmis à
  // fetch), donc plus besoin du setTimeout/clearTimeout manuel d'avant pour éviter
  // qu'une réponse tardive et périmée n'écrase un résultat plus récent.
  const debouncedSearch = useDebouncedValue(search, 300)

  const coursQuery = useInfiniteQuery({
    queryKey: ["cours", country, subjectFilter, cursusFilter, langueFiltre, nonLusFilter, frequentFilter, debouncedSearch, savoirFilter, themeFilter],
    queryFn: ({ pageParam, signal }) =>
      listCours(
        {
          subject: subjectFilter || undefined,
          cursus: cursusFilter ? Number(cursusFilter) : undefined,
          langue: langueFiltre,
          country,
          search: debouncedSearch || undefined,
          // Jamais `false` : le backend ne teste que la valeur "true", mais envoyer
          // exclude_read=false polluerait l'URL de l'API pour rien.
          exclude_read: nonLusFilter || undefined,
          // Les plus fréquents d'abord : filtrer sur « tombe souvent » sans les classer ne servirait à rien.
          tombe_souvent: frequentFilter || undefined,
          ordering: frequentFilter ? "frequent" : undefined,
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
  // Page suivante en échec : voir l'observateur ci-dessous, qui sinon la relançait en boucle.
  const erreurPageSuivante = coursQuery.isFetchNextPageError

  // Chargement automatique au défilement, comme /epreuves : la lecture d'un catalogue de plusieurs
  // milliers de cours ne doit pas s'interrompre sur un bouton. Le bouton "Charger plus" reste
  // dessous - accessible au clavier, et repli si l'observateur ne se déclenche pas.
  const sentinelRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const el = sentinelRef.current
    if (!el || !hasMore || erreurPageSuivante) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isLoadingMore) coursQuery.fetchNextPage()
      },
      { rootMargin: "400px" },
    )
    observer.observe(el)
    return () => observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasMore, isLoadingMore, erreurPageSuivante])

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
        // Retirer le cursus (puce, « Tous », re-clic sur la pastille) est un choix explicite :
        // sans `tout=1`, le pré-filtrage le remettait aussitôt dans l'URL.
        else if (key === "cursus" && cursusPrepare) desactiverFiltreCursus(next)
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
        for (const key of ["subject", "cursus", "nonlus", "frequent", "search", "savoir", "theme", "savoir_label"]) next.delete(key)
        // « Tout effacer » veut dire tout le catalogue : `tout=1` empêche le cursus par défaut de revenir.
        if (cursusPrepare) desactiverFiltreCursus(next)
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
        return c ? `${c.examen_display}${c.series ? ` - ${t("prix.serie", { code: c.series.code })}` : ""}` : cursusFilter
      })(),
      clear: () => updateFilter("cursus", ""),
    },
    nonLusFilter && {
      key: "nonlus",
      label: t("co.non_lus"),
      clear: () => updateFilter("nonlus", ""),
    },
    frequentFilter && {
      key: "frequent",
      label: t("co.tombe_souvent"),
      clear: () => updateFilter("frequent", ""),
    },
    savoirFilter && {
      key: "savoir",
      label: savoirLabel ? t("co.savoir", { x: capitaliserTheme(savoirLabel) }) : t("co.savoir_filtre"),
      clear: clearSavoirFilter,
    },
    themeFilter && {
      key: "theme",
      label: savoirLabel ? t("co.theme_filtre_x", { x: capitaliserTheme(savoirLabel) }) : t("co.theme_filtre"),
      clear: clearSavoirFilter,
    },
  ].filter((chip): chip is { key: string; label: string; clear: () => void } => Boolean(chip))

  // Niveaux d'examen réellement présents pour ce pays - jamais un texte fixe : la
  // plupart des pays n'ont pas de Probatoire (voir examLevelsFor).
  const examLevels = examLevelsFor(cursusList)
  // Le cursus est LE filtre d'un élève ("mon BAC D") : en pastilles d'un clic plutôt que caché
  // dans une liste déroulante, triées pour que les séries d'un même examen se suivent.
  const cursusTries = [...cursusList].sort(
    (x, y) =>
      x.examen_display.localeCompare(y.examen_display, localeCourante()) ||
      (x.series?.code ?? "").localeCompare(y.series?.code ?? "", localeCourante()),
  )
  const coursEnCours = progression?.cours?.[0]
  // `undefined` tant que rien n'est chargé - la puce du hero ne s'affiche pas plutôt
  // que d'annoncer un "0 cours publiés" démenti une seconde plus tard.
  const totalCours = filtresActifs ? totalData?.count : coursQuery.data ? count : undefined

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <ReviserTabs />
      <BandeauFiltreCursus />
      <BandeauMatieres suitFiltreCursus />
      {/* Même hero compact que /epreuves : les résultats doivent apparaître sans défiler, et le
          volume du catalogue est la preuve qu'il y a de quoi chercher. */}
      <div className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <GraduationCap aria-hidden className="pointer-events-none absolute -bottom-6 -right-4 hidden size-44 rotate-[-12deg] text-primary/[0.07] sm:block" />
        <div className="relative max-w-2xl">
          <p className="mb-2 font-display text-sm italic text-primary">
            {t("co.eyebrow")}{countryLabel ? ` - ${countryLabel}` : ""}
          </p>
          <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight text-balance sm:text-4xl">
            {t("co.titre_debut")} <span className="text-primary">{t("co.titre_accent")}</span>{t("co.titre_fin")}
          </h1>
          <p className="mt-2 hidden max-w-xl text-muted-foreground sm:block">
            {t("co.hero_texte")}
          </p>

          <div className="mt-4 flex flex-wrap gap-2 sm:mt-5">
            {totalCours !== undefined && (
              <StatChip
                icon={<BookOpen className="size-3.5 text-primary" />}
                valeur={formatAmount(totalCours)}
                libelle={tn("co.stat_publies", totalCours > 1 ? 2 : 1)}
              />
            )}
            {subjects.length > 0 && (
              <StatChip
                icon={<Layers className="size-3.5 text-primary" />}
                valeur={String(subjects.length)}
                libelle={tn("accueil.stat_matieres", subjects.length > 1 ? 2 : 1)}
              />
            )}
            {examLevels.length > 0 && (
              <span className="hidden items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm sm:flex">
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
              {t("accueil.reprendre_lecture")}
            </span>
            <span className="block truncate font-display font-medium">{coursEnCours.titre}</span>
          </span>
          <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
        </Link>
      )}

      {/* Panneau de recherche : la carte surélevée fait de la recherche le point focal de la page,
          comme sur /epreuves. Examen et matière sont des pastilles d'un clic - choisir sa matière est
          le premier geste sur un catalogue de plusieurs milliers de cours, il ne doit pas coûter deux
          clics et la lecture d'une liste. */}
      <div className="mb-6 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:p-6">
        <div className="group relative">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            type="search"
            inputMode="search"
            enterKeyHint="search"
            aria-label={t("co.rechercher")}
            placeholder={t("co.rechercher_placeholder")}
            value={search}
            onChange={(e) => updateFilter("search", e.target.value)}
            className="h-12 border-input pl-10 pr-10 text-base shadow-none focus-visible:border-primary/60 focus-visible:ring-primary/25 [&::-webkit-search-cancel-button]:hidden"
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

        {cursusTries.length > 0 && (
          <FiltreLigne titre={t("quiz.examen")}>
            <PastilleFiltre actif={!cursusFilter} onClick={() => updateFilter("cursus", "")}>
              {t("ep.tous")}
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
          <FiltreLigne titre={t("quiz.matiere")}>
            <PastilleFiltre actif={!subjectFilter} onClick={() => updateFilter("subject", "")}>
              {t("ep.toutes")}
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
                  {/* Le compteur est un repère de tri (les matières sont classées par nombre de
                      cours), pas une information dont dépend le choix : il cède la place sur
                      téléphone, où une pastille plus étroite laisse voir la suivante. */}
                  {subject.cours_count !== undefined && (
                    <span className="hidden tabular-nums opacity-60 sm:inline">{subject.cours_count}</span>
                  )}
                </PastilleFiltre>
              )
            })}
          </FiltreLigne>
        )}

        <div className="mt-4 flex flex-wrap items-center gap-2">
          {/* Ouvert à tous, visiteurs compris : c'est un repère de contenu, pas un historique. Seuls les cours
              du quart supérieur de leur matière y figurent (voir catalog.FrequenceCours) : le filtre montre ce
              qu'on sait, jamais le reste n'est déclaré sans importance. */}
          <button
            type="button"
            onClick={() => updateFilter("frequent", frequentFilter ? "" : "true")}
            aria-pressed={frequentFilter}
            className={cn(
              "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
              frequentFilter
                ? "border-gold/50 bg-gold/15 text-gold-text"
                : "border-border text-muted-foreground hover:border-gold/50 hover:text-gold-text",
            )}
          >
            <Star className="size-4" fill={frequentFilter ? "currentColor" : "none"} />
            {t("co.tombe_souvent")}
          </button>
          {/* Réservé aux connectés : le backend n'a aucun historique de lecture à exclure pour un
              visiteur anonyme (voir CoursListView.exclude_read), le bouton n'y filtrerait rien. */}
          {isAuthenticated && (
            <button
              type="button"
              onClick={() => updateFilter("nonlus", nonLusFilter ? "" : "true")}
              aria-pressed={nonLusFilter}
              className={cn(
                "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
                nonLusFilter
                  ? "border-success/40 bg-success/15 text-success"
                  : "border-border text-muted-foreground hover:border-success/40 hover:text-success",
              )}
            >
              <CheckCircle2 className="size-4" />
              {t("co.masquer_lus")}
            </button>
          )}
        </div>

        {activeFilterChips.length > 0 && (
          <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-border pt-3.5">
            <span className="text-sm text-muted-foreground">{t("ep.filtres_actifs")}</span>
            {activeFilterChips.map((chip) => (
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

      {isLoading ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true" aria-label={t("co.chargement")}>
          {Array.from({ length: 6 }).map((_, i) => (
            <CoursCardSkeleton key={i} />
          ))}
        </div>
      ) : coursQuery.isError && coursList.length === 0 ? (
        // Une panne n'est pas "aucun résultat" : sans ce cas, une coupure réseau se lisait comme
        // un catalogue vide et l'élève cherchait l'erreur dans ses filtres.
        <ErreurChargement
          objet={t("co.objet")}
          message={t("ep.erreur_message")}
          onRetry={() => coursQuery.refetch()}
        />
      ) : coursList.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-card/60 px-6 py-14 text-center">
          <span className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <SearchX className="size-6" />
          </span>
          <p className="font-display text-lg font-semibold">{t("co.aucun")}</p>
          <p className="max-w-sm text-sm text-muted-foreground">
            {search
              ? t("ep.aucune_recherche", { search })
              : t("co.aucun_filtre")}
          </p>
          {(activeFilterChips.length > 0 || search) && (
            <Button variant="outline" onClick={resetFilters} className="mt-1 rounded-full">
              {t("ep.reinitialiser")}
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
            <p className="text-sm text-muted-foreground" aria-live="polite">
              <span className="font-medium tabular-nums text-foreground">{formatAmount(count)}</span> {tn("co.trouves", count)}
            </p>
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

          {viewMode === "cards" ? (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {coursList.map((cours, index) => (
                <CoursCard
                  key={cours.id}
                  niveauTitre={2}
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
            <div ref={sentinelRef} className="mt-8 flex flex-col items-center gap-2">
              <Button variant="outline" onClick={() => coursQuery.fetchNextPage()} disabled={isLoadingMore}>
                {isLoadingMore && <Loader2 className="size-4 animate-spin" />}
                {t("ep.charger_plus")}
              </Button>
              {erreurPageSuivante && !isLoadingMore && (
                <p role="alert" className="text-sm text-destructive">
                  {t("co.suite_erreur")}
                </p>
              )}
              {/* Repère de progression dans la liste : sans lui, "Charger plus" sur
                  3 700 résultats ne dit jamais où on en est ni combien il reste. */}
              <p className="text-xs tabular-nums text-muted-foreground">
                {t("ep.sur", { a: formatAmount(coursList.length), b: formatAmount(count) })}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
