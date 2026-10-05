import { useEffect, useMemo, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { keepPreviousData, useInfiniteQuery, useQuery } from "@tanstack/react-query"
import { Loader2, Search, SearchX, X } from "lucide-react"

import { listCursus, listSubjects, rechercher } from "@/api/endpoints"
import type { GroupeRecherche, ReponseRecherche, TypeResultatRecherche } from "@/api/types"
import { formatCursus } from "@/components/CompteAReboursBadge"
import { ResultatCarte } from "@/components/recherche/ResultatRecherche"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCursusAccueil } from "@/lib/cursusAccueil"
import { coursListPath, epreuvesListPath, themesFrequentsPath } from "@/lib/countryPath"
import {
  cibleResultat,
  jetonsDeSurbrillance,
  LIBELLES_TYPE,
  LONGUEUR_MIN_RECHERCHE,
  memoriserRecente,
  TYPES_RECHERCHE,
} from "@/lib/recherche"
import { useSeo } from "@/lib/seo"
import { useDebouncedValue } from "@/lib/useDebouncedValue"
import { cn } from "@/lib/utils"

// Par groupe dans la vue d'ensemble ; une fois un type choisi, on pagine par PAGE_TYPE.
const PAR_GROUPE = 6
const PAGE_TYPE = 20
const TOUTES_MATIERES = "tous"

export function RecherchePage() {
  const { country = "" } = useParams<{ country: string }>()
  const { user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()

  const q = searchParams.get("q") ?? ""
  const matiere = searchParams.get("matiere") ?? ""
  const typeBrut = searchParams.get("type") ?? ""
  const type = (TYPES_RECHERCHE as string[]).includes(typeBrut) ? (typeBrut as TypeResultatRecherche) : undefined
  const elargir = searchParams.get("elargir") === "1"
  const exact = searchParams.get("exact") === "1"

  useSeo({
    title: q ? `Recherche : ${q}` : "Recherche",
    description: "Cherche un thème, un cours, une épreuve ou un exercice.",
    // Une page de résultats n'a rien à faire dans un moteur de recherche : l'infinité de requêtes
    // possibles y ferait des milliers de pages quasi vides.
    noindex: true,
  })

  // Le champ est local (réactif à la frappe), l'URL suit après une pause : on peut partager le lien
  // d'une recherche, et « retour » revient à la précédente.
  const [saisie, setSaisie] = useState(q)
  const saisieStable = useDebouncedValue(saisie, 350)
  useEffect(() => {
    if (saisieStable.trim() === q.trim()) return
    setSearchParams(
      (prev) => {
        const suivant = new URLSearchParams(prev)
        if (saisieStable.trim()) suivant.set("q", saisieStable.trim())
        else suivant.delete("q")
        // Une nouvelle saisie repart d'une recherche corrigée normalement.
        suivant.delete("exact")
        return suivant
      },
      { replace: true },
    )
    // `q` volontairement hors dépendances : seule une pause de frappe doit écrire dans l'URL.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [saisieStable])
  // L'URL change de l'extérieur (palette, lien, retour) : le champ suit.
  useEffect(() => {
    if (q !== saisieStable.trim()) setSaisie(q)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q])

  function majParams(modifs: Record<string, string | null>) {
    setSearchParams(
      (prev) => {
        const suivant = new URLSearchParams(prev)
        for (const [cle, valeur] of Object.entries(modifs)) {
          if (valeur) suivant.set(cle, valeur)
          else suivant.delete(cle)
        }
        return suivant
      },
      { replace: true },
    )
  }

  const cursusDeclare = useCursusAccueil(country)
  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
    enabled: Boolean(country),
  })
  const { data: subjects = [] } = useQuery({
    queryKey: ["subjects", country],
    queryFn: ({ signal }) => listSubjects(country, signal),
    enabled: Boolean(country),
  })
  const cursusLabel = useMemo(() => {
    const trouve = cursusList.find((c) => c.id === cursusDeclare)
    return trouve ? formatCursus(trouve) : ""
  }, [cursusList, cursusDeclare])

  const termes = q.trim()
  const interroger = termes.length >= LONGUEUR_MIN_RECHERCHE && cursusDeclare !== undefined
  const identite = user?.id ?? 0

  // Vue d'ensemble : tous les groupes, quelques résultats chacun - et les compteurs des onglets.
  const ensemble = useQuery({
    queryKey: ["recherche", "page", country, identite, termes, matiere, cursusDeclare ?? null, elargir, exact],
    queryFn: ({ signal }) =>
      rechercher(
        { q: termes, pays: country, cursus: cursusDeclare, matiere: matiere || undefined, elargir, exact, limite: PAR_GROUPE },
        signal,
      ),
    enabled: interroger,
    placeholderData: keepPreviousData,
  })

  // Un type choisi : ce seul groupe, paginé.
  const detail = useInfiniteQuery({
    queryKey: ["recherche", "type", country, identite, termes, matiere, cursusDeclare ?? null, elargir, exact, type],
    queryFn: ({ pageParam, signal }) =>
      rechercher(
        {
          q: termes, pays: country, cursus: cursusDeclare, matiere: matiere || undefined, elargir, exact,
          type, limite: PAGE_TYPE, decalage: pageParam,
        },
        signal,
      ),
    initialPageParam: 0,
    getNextPageParam: (derniere, pages) => {
      const total = derniere.groupes[0]?.total ?? 0
      const charges = pages.reduce((somme, page) => somme + (page.groupes[0]?.resultats.length ?? 0), 0)
      return charges < total ? charges : undefined
    },
    enabled: interroger && type !== undefined,
  })

  const data = ensemble.data
  const jetons = useMemo(() => jetonsDeSurbrillance(data?.corrige ?? termes), [data?.corrige, termes])
  const groupes: GroupeRecherche[] = data?.groupes ?? []
  const resultatsDuType = detail.data?.pages.flatMap((p) => p.groupes[0]?.resultats ?? []) ?? []
  const attente = interroger && ensemble.isLoading
  const retenir = () => memoriserRecente(termes)

  return (
    <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6 sm:py-8">
      <h1 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Recherche</h1>

      <form
        role="search"
        className="mt-4"
        onSubmit={(e) => {
          e.preventDefault()
          majParams({ q: saisie.trim() || null, exact: null })
          memoriserRecente(saisie)
        }}
      >
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
          <Input
            type="search"
            value={saisie}
            onChange={(e) => setSaisie(e.target.value)}
            placeholder="Un thème, une notion, une épreuve, une année…"
            aria-label="Rechercher"
            autoFocus={!q}
            autoComplete="off"
            enterKeyHint="search"
            className="h-12 pl-10 pr-10 text-base [&::-webkit-search-cancel-button]:hidden"
          />
          {saisie && (
            <button
              type="button"
              onClick={() => {
                setSaisie("")
                majParams({ q: null, exact: null })
              }}
              aria-label="Effacer la recherche"
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground"
            >
              <X className="size-4" />
            </button>
          )}
        </div>
      </form>

      {/* Périmètre : l'examen de l'élève par défaut, jamais caché - c'est ce qui explique pourquoi un
          résultat attendu manque, et un clic suffit pour l'élargir. */}
      <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-2">
        <Select value={matiere || TOUTES_MATIERES} onValueChange={(v) => majParams({ matiere: v === TOUTES_MATIERES ? null : v })}>
          <SelectTrigger aria-label="Matière" className="h-9 w-auto min-w-[10rem] text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={TOUTES_MATIERES}>Toutes les matières</SelectItem>
            {[...subjects]
              .sort((a, b) => a.label.localeCompare(b.label, "fr"))
              .map((s) => (
                <SelectItem key={s.id} value={s.code}>
                  {s.label}
                </SelectItem>
              ))}
          </SelectContent>
        </Select>
        {cursusLabel && (
          <p className="text-sm text-muted-foreground">
            {elargir ? "Dans tous les examens" : <>Dans ton examen : <strong className="font-medium text-foreground">{cursusLabel}</strong></>}
            {" · "}
            <button
              type="button"
              onClick={() => majParams({ elargir: elargir ? null : "1" })}
              className="font-medium text-primary hover:underline"
            >
              {elargir ? `Seulement ${cursusLabel}` : "Tous les examens"}
            </button>
          </p>
        )}
      </div>

      {termes.length < LONGUEUR_MIN_RECHERCHE ? (
        <Invitation country={country} />
      ) : attente ? (
        <Chargement />
      ) : ensemble.isError ? (
        <p role="alert" className="mt-8 text-center text-sm text-muted-foreground">
          La recherche est momentanément indisponible.{" "}
          <button type="button" onClick={() => ensemble.refetch()} className="font-medium text-primary hover:underline">
            Réessayer
          </button>
        </p>
      ) : data && !data.indexe ? (
        <p className="mt-8 text-center text-sm text-muted-foreground">
          La recherche est en cours de préparation. Réessaie dans quelques minutes.
        </p>
      ) : data ? (
        <div aria-busy={ensemble.isFetching}>
          {data.corrige && (
            <p className="mt-5 text-sm text-muted-foreground">
              Résultats pour « <strong className="font-medium text-foreground">{data.corrige}</strong> ».{" "}
              <button type="button" onClick={() => majParams({ exact: "1" })} className="font-medium text-primary hover:underline">
                Chercher plutôt « {termes} »
              </button>
            </p>
          )}

          {data.total === 0 ? (
            <AucunResultat
              termes={termes}
              country={country}
              data={data}
              onElargir={cursusLabel && !elargir ? () => majParams({ elargir: "1" }) : undefined}
              onRetenir={retenir}
            />
          ) : (
            <>
              {data.autres_cursus > 0 && !elargir && (
                <p className="mt-5 rounded-lg border border-border bg-muted/40 px-3 py-2 text-sm">
                  {data.autres_cursus} autre{data.autres_cursus > 1 ? "s" : ""} résultat{data.autres_cursus > 1 ? "s" : ""} dans d'autres examens.{" "}
                  <button type="button" onClick={() => majParams({ elargir: "1" })} className="font-medium text-primary hover:underline">
                    Les voir
                  </button>
                </p>
              )}

              <Onglets groupes={groupes} total={data.total} type={type} onChoisir={(t) => majParams({ type: t ?? null })} />

              {type === undefined ? (
                <div className="mt-2 space-y-8">
                  {groupes.map((groupe) => (
                    <section key={groupe.type} aria-labelledby={`groupe-${groupe.type}`}>
                      <div className="mb-3 flex items-baseline justify-between gap-3">
                        <h2 id={`groupe-${groupe.type}`} className="font-display text-lg font-semibold">
                          {groupe.libelle} <span className="text-sm font-normal text-muted-foreground">({groupe.total})</span>
                        </h2>
                        {groupe.total > groupe.resultats.length && (
                          <button
                            type="button"
                            onClick={() => majParams({ type: groupe.type })}
                            className="text-sm font-medium text-primary hover:underline"
                          >
                            Voir les {groupe.total}
                          </button>
                        )}
                      </div>
                      <div className="space-y-3">
                        {groupe.resultats.map((resultat) => (
                          <ResultatCarte key={`${resultat.type}-${resultat.id}`} resultat={resultat} jetons={jetons} country={country} onChoisir={retenir} />
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              ) : (
                <div className="mt-4">
                  {detail.isLoading ? (
                    <Chargement />
                  ) : (
                    <>
                      <div className="space-y-3">
                        {resultatsDuType.map((resultat) => (
                          <ResultatCarte key={`${resultat.type}-${resultat.id}`} resultat={resultat} jetons={jetons} country={country} onChoisir={retenir} />
                        ))}
                      </div>
                      {detail.hasNextPage && (
                        <div className="mt-5 flex justify-center">
                          <Button variant="outline" onClick={() => detail.fetchNextPage()} disabled={detail.isFetchingNextPage}>
                            {detail.isFetchingNextPage && <Loader2 className="animate-spin" />}
                            Afficher plus de résultats
                          </Button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      ) : null}
    </div>
  )
}

function Onglets({
  groupes, total, type, onChoisir,
}: {
  groupes: GroupeRecherche[]
  total: number
  type: TypeResultatRecherche | undefined
  onChoisir: (type: TypeResultatRecherche | undefined) => void
}) {
  // Les compteurs viennent de la vue d'ensemble : toujours à jour, que le type choisi pagine ou non.
  const bouton = (actif: boolean) =>
    cn(
      "whitespace-nowrap rounded-full border px-3 py-1.5 text-sm transition-colors",
      actif ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background hover:border-primary/60",
    )
  return (
    <div className="-mx-4 mt-5 overflow-x-auto px-4 sm:mx-0 sm:px-0" role="group" aria-label="Type de résultat">
      <div className="flex gap-2">
        <button type="button" onClick={() => onChoisir(undefined)} aria-pressed={type === undefined} className={bouton(type === undefined)}>
          Tout ({total})
        </button>
        {groupes.map((groupe) => (
          <button
            key={groupe.type}
            type="button"
            onClick={() => onChoisir(groupe.type)}
            aria-pressed={type === groupe.type}
            className={bouton(type === groupe.type)}
          >
            {LIBELLES_TYPE[groupe.type].pluriel} ({groupe.total})
          </button>
        ))}
      </div>
    </div>
  )
}

function Chargement() {
  return (
    <div className="mt-6 space-y-3" role="status" aria-label="Recherche en cours">
      {[0, 1, 2, 3].map((i) => (
        <Skeleton key={i} className="h-24 w-full rounded-xl" />
      ))}
    </div>
  )
}

function Invitation({ country }: { country: string }) {
  return (
    <div className="mt-10 text-center text-sm text-muted-foreground">
      <p>Cherche un thème (« théorème de Thalès »), une notion (« discriminant »), une épreuve (« BAC C maths 2019 »).</p>
      <p className="mt-4 flex flex-wrap items-center justify-center gap-x-4 gap-y-1">
        <Link to={epreuvesListPath(country)} className="font-medium text-primary hover:underline">Parcourir les épreuves</Link>
        <Link to={coursListPath(country)} className="font-medium text-primary hover:underline">Parcourir les cours</Link>
        <Link to={themesFrequentsPath(country)} className="font-medium text-primary hover:underline">Thèmes les plus fréquents</Link>
      </p>
    </div>
  )
}

function AucunResultat({
  termes, country, data, onElargir, onRetenir,
}: {
  termes: string
  country: string
  data: ReponseRecherche
  onElargir?: () => void
  onRetenir: () => void
}) {
  return (
    <div className="mt-10">
      <div className="flex flex-col items-center gap-2 text-center">
        <SearchX className="size-8 text-muted-foreground" aria-hidden="true" />
        <h2 className="font-display text-lg font-semibold">Aucun résultat pour « {termes} »</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          Essaie un mot plus court, une autre façon de nommer la notion, ou retire un filtre.
        </p>
        {onElargir && (
          <Button variant="outline" size="sm" onClick={onElargir} className="mt-1">
            Chercher dans tous les examens
          </Button>
        )}
      </div>
      {data.suggestions.length > 0 && (
        <section className="mt-8" aria-labelledby="suggestions-themes">
          <h3 id="suggestions-themes" className="mb-3 font-display text-base font-semibold">
            Des thèmes pour commencer
          </h3>
          <ul className="flex flex-wrap gap-2">
            {data.suggestions.map((theme) => (
              <li key={theme.id}>
                <Link
                  to={cibleResultat(country, theme)}
                  onClick={onRetenir}
                  className="inline-flex items-center rounded-full border border-border bg-background px-3 py-1.5 text-sm transition-colors hover:border-primary hover:text-primary"
                >
                  {theme.titre}
                  <span className="ml-1.5 text-xs text-muted-foreground">{theme.matiere.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
