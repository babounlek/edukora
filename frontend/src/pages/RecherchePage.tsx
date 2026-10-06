import { useEffect, useMemo, useRef, useState, type KeyboardEvent } from "react"
import { Link, useLocation, useParams, useSearchParams } from "react-router-dom"
import { keepPreviousData, useInfiniteQuery, useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, Clock, Loader2, Search, SearchX, X } from "lucide-react"

import { completerRecherche, getMyProgression, listCursus, rechercher } from "@/api/endpoints"
import type { GroupeRecherche, ReponseRecherche, ResultatRecherche, TypeResultatRecherche } from "@/api/types"
import { formatCursus } from "@/components/CompteAReboursBadge"
import { ReviserTabs } from "@/components/ReviserTabs"
import { IconeType, ResultatCarte } from "@/components/recherche/ResultatRecherche"
import { ResultatVedette } from "@/components/recherche/ResultatVedette"
import { Surbrillance } from "@/components/recherche/Surbrillance"
import { FiltreLigne, PastilleFiltre } from "@/components/FiltresCatalogue"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { useCursusAccueil } from "@/lib/cursusAccueil"
import { epreuveReaderPath } from "@/lib/countryPath"
import {
  actionsTheme,
  cibleResultat,
  jetonsDeSurbrillance,
  familleDe,
  FAMILLES_RECHERCHE,
  type FamilleRecherche,
  LONGUEUR_MIN_RECHERCHE,
  LIBELLES_MOT_TYPE,
  lireRecentes,
  memoriserRecente,
  oublierRecentes,
  TYPES_RECHERCHE,
  tracerRechercheLancee,
  tracerResultatClique,
  veutFocusRecherche,
} from "@/lib/recherche"
import { useSeo } from "@/lib/seo"
import { useDebouncedValue } from "@/lib/useDebouncedValue"
import { cn } from "@/lib/utils"

// Par groupe dans la vue d'ensemble ; une fois un type choisi, on pagine par PAGE_TYPE.
const PAR_GROUPE = 6
const PAGE_TYPE = 20

export function RecherchePage() {
  const { country = "" } = useParams<{ country: string }>()
  const { user } = useAuth()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label
  const [searchParams, setSearchParams] = useSearchParams()

  // Arrivé par la loupe, le bouton des onglets ou un raccourci clavier (voir ETAT_FOCUS_RECHERCHE) : le
  // champ passe en saisie, texte déjà tapé sélectionné pour être remplacé d'une frappe. `location.key`
  // dans les dépendances : recliquer sur la loupe depuis cette même page refait la mise au point.
  const location = useLocation()
  const champRef = useRef<HTMLInputElement>(null)
  useEffect(() => {
    if (!veutFocusRecherche(location.state)) return
    champRef.current?.focus()
    champRef.current?.select()
  }, [location.key, location.state])

  const q = searchParams.get("q") ?? ""
  const matiere = searchParams.get("matiere") ?? ""
  const typeBrut = searchParams.get("type") ?? ""
  // `type` de l URL : un type de résultat, ramené à son onglet (voir FAMILLES_RECHERCHE).
  const famille = (TYPES_RECHERCHE as string[]).includes(typeBrut) ? familleDe(typeBrut as TypeResultatRecherche) : undefined
  const elargir = searchParams.get("elargir") === "1"
  const exact = searchParams.get("exact") === "1"
  // Parties de l'intention que l'élève a retirées (pastilles « Compris » : cursus, matiere, annee, type).
  const sansBrut = searchParams.get("sans") ?? ""
  const sans = useMemo(() => sansBrut.split(",").filter(Boolean), [sansBrut])

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
        // Une nouvelle saisie repart d'une recherche corrigée et interprétée normalement.
        suivant.delete("exact")
        suivant.delete("sans")
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

  /** Retire une pastille « Compris » : ce mot redevient un mot comme un autre (paramètre `sans`). */
  function retirer(partie: "cursus" | "matiere" | "annee" | "type") {
    majParams({ sans: [...new Set([...sans, partie])].join(",") })
  }

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
  const cursusLabel = useMemo(() => {
    const trouve = cursusList.find((c) => c.id === cursusDeclare)
    return trouve ? formatCursus(trouve) : ""
  }, [cursusList, cursusDeclare])

  const termes = q.trim()
  const interroger = termes.length >= LONGUEUR_MIN_RECHERCHE && cursusDeclare !== undefined
  const identite = user?.id ?? 0

  // Vue d'ensemble : tous les groupes, quelques résultats chacun - et les compteurs des onglets.
  const ensemble = useQuery({
    queryKey: ["recherche", "page", country, identite, termes, matiere, cursusDeclare ?? null, elargir, exact, sansBrut],
    queryFn: ({ signal }) =>
      rechercher(
        { q: termes, pays: country, cursus: cursusDeclare, matiere: matiere || undefined, elargir, exact, sans, limite: PAR_GROUPE },
        signal,
      ),
    enabled: interroger,
    placeholderData: keepPreviousData,
  })

  const data = ensemble.data
  const jetons = useMemo(() => jetonsDeSurbrillance(data?.corrige ?? termes), [data?.corrige, termes])
  const groupes: GroupeRecherche[] = data?.groupes ?? []
  const attente = interroger && ensemble.isLoading
  // Les filtres (matière, type) n'existent qu'une fois des résultats connus : ils s'en déduisent.
  const filtrable = data !== undefined && data.indexe && data.total > 0

  // Le meilleur thème de la vue d'ensemble : mis en avant avec de quoi agir (cours, exercices, quiz).
  // Seulement s'il a de quoi proposer, et jamais dans une vue filtrée par type - la carte est une porte
  // d'entrée, pas un résultat de plus.
  const themes = groupes.find((g) => g.type === "THEME")?.resultats ?? []
  // Une requête qui réclame des épreuves ou des cours (« bac c 2019 corrigé ») n'a que faire d'un thème en
  // vedette : ce qu'elle demande passe devant, pas une porte d'entrée vers un thème.
  const typesVoulus = data?.intention?.types ?? []
  const veutAutreChoseQueDesThemes = typesVoulus.length > 0 && !typesVoulus.includes("THEME")
  const vedette =
    famille === undefined && !veutAutreChoseQueDesThemes
      ? themes.find((t) => actionsTheme(country, t).length > 0)
      : undefined
  // Les autres thèmes, en pastilles : de quoi rebondir sans retaper (un thème par intitulé distinct).
  const associees = themes
    .filter((t) => t.id !== vedette?.id && t.titre.toLowerCase() !== vedette?.titre.toLowerCase())
    .filter((t, i, tous) => tous.findIndex((u) => u.titre.toLowerCase() === t.titre.toLowerCase()) === i)
    .slice(0, 5)
  // Ce que le moteur a compris de la requête, sous forme de pastilles retirables.
  const intention = data?.intention
  const compris: { cle: "cursus" | "matiere" | "annee" | "type"; libelle: string }[] = []
  if (intention && !intention.ignoree) {
    if (intention.cursus) compris.push({ cle: "cursus", libelle: intention.cursus.libelle })
    if (intention.matiere) compris.push({ cle: "matiere", libelle: intention.matiere.libelle })
    if (intention.annees.length > 0) compris.push({ cle: "annee", libelle: intention.annees.join(", ") })
    if (intention.mots_type.length > 0) {
      compris.push({ cle: "type", libelle: intention.mots_type.map((m) => LIBELLES_MOT_TYPE[m] ?? m).join(", ") })
    }
  }

  // Complétion pendant la frappe : des intitulés de thèmes, demandés après une courte pause. Fermée tant que
  // l'élève n'a rien tapé (arriver sur la page avec une recherche ne déroule rien).
  const [completionOuverte, setCompletionOuverte] = useState(false)
  const [completionActive, setCompletionActive] = useState(-1)
  const saisieCompletion = useDebouncedValue(saisie.trim(), 150)
  const completions = useQuery({
    queryKey: ["recherche", "completer", country, cursusDeclare ?? null, saisieCompletion],
    queryFn: ({ signal }) => completerRecherche({ q: saisieCompletion, pays: country, cursus: cursusDeclare }, signal),
    enabled: completionOuverte && saisieCompletion.length >= LONGUEUR_MIN_RECHERCHE && cursusDeclare !== undefined,
    staleTime: 5 * 60_000,
    placeholderData: keepPreviousData,
  })
  // Une proposition identique à ce qui est déjà tapé n'apprend rien.
  const propositions = (completionOuverte ? (completions.data?.completions ?? []) : []).filter(
    (c) => c.texte.trim().toLowerCase() !== saisie.trim().toLowerCase(),
  )
  const jetonsCompletion = useMemo(() => jetonsDeSurbrillance(saisie), [saisie])

  function choisirCompletion(proposition: string) {
    setCompletionOuverte(false)
    setCompletionActive(-1)
    setSaisie(proposition)
    majParams({ q: proposition, exact: null, sans: null })
    memoriserRecente(proposition)
    tracerRechercheLancee("page", "completion")
  }

  function surTouche(e: KeyboardEvent<HTMLInputElement>) {
    // Sans liste ouverte, Entrée valide le formulaire comme d'habitude.
    if (!completionOuverte || propositions.length === 0) return
    if (e.key === "ArrowDown") {
      e.preventDefault()
      setCompletionActive((i) => (i + 1) % propositions.length)
    } else if (e.key === "ArrowUp") {
      e.preventDefault()
      setCompletionActive((i) => (i <= 0 ? propositions.length - 1 : i - 1))
    } else if (e.key === "Enter" && completionActive >= 0) {
      e.preventDefault()
      choisirCompletion(propositions[completionActive].texte)
    } else if (e.key === "Escape") {
      setCompletionOuverte(false)
      setCompletionActive(-1)
    }
  }

  const retenir = () => memoriserRecente(termes)
  // Ouvrir un résultat : on retient la recherche et on note son type et son rang (1 = premier de son groupe).
  const ouvrir = (resultat: ResultatRecherche, rang: number) => () => {
    retenir()
    tracerResultatClique("page", resultat, rang + 1)
  }

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      {/* La recherche appartient à « Réviser » : mêmes onglets que les autres surfaces de révision
          (voir ReviserTabs), aucun d'eux n'est actif - la recherche les traverse tous. */}
      <ReviserTabs />
      {/* Même hero que /epreuves, /cours et /themes-frequents : filigrane, pastille d'intitulé en italique,
          titre en Fraunces avec la fin en couleur, puis la carte de recherche surélevée qui porte les filtres. */}
      <div className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <Search aria-hidden className="pointer-events-none absolute -bottom-6 -right-4 hidden size-44 rotate-[-12deg] text-primary/[0.07] sm:block" />
        <div className="relative max-w-2xl">
          <p className="mb-2 font-display text-sm italic text-primary">
            Recherche{countryLabel ? ` - ${countryLabel}` : ""}
          </p>
          <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight text-balance sm:text-4xl">
            Un mot, et on te dit <span className="text-primary">par où commencer</span>.
          </h1>
          <p className="mt-2 hidden max-w-xl text-muted-foreground sm:block">
            Thèmes, cours, épreuves, exercices et quiz : tape une notion, une épreuve ou une année, on trouve ce
            qu'il te faut pour ton examen.
          </p>
        </div>
      </div>

      {/* Panneau de recherche : la carte surélevée fait de la recherche le point focal de la page, comme
          sur /epreuves et /cours - et les filtres (examen, matière, type) s'y composent des mêmes pièces. */}
      <div className="mb-6 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:p-6">
        <form
          role="search"
          onSubmit={(e) => {
            e.preventDefault()
            setCompletionOuverte(false)
            majParams({ q: saisie.trim() || null, exact: null, sans: null })
            memoriserRecente(saisie)
            if (saisie.trim().length >= LONGUEUR_MIN_RECHERCHE) tracerRechercheLancee("page")
          }}
        >
          <div className="group relative">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 size-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" aria-hidden="true" />
            <Input
              type="search"
              role="combobox"
              inputMode="search"
              ref={champRef}
              value={saisie}
              onChange={(e) => {
                setSaisie(e.target.value)
                setCompletionOuverte(true)
                setCompletionActive(-1)
              }}
              onKeyDown={surTouche}
              onBlur={() => setCompletionOuverte(false)}
              placeholder="Un thème, une notion, une épreuve, une année…"
              aria-label="Rechercher"
              aria-expanded={propositions.length > 0}
              aria-controls="completions-recherche"
              aria-autocomplete="list"
              aria-activedescendant={completionActive >= 0 ? `completion-${completionActive}` : undefined}
              autoFocus={!q}
              autoComplete="off"
              enterKeyHint="search"
              className="h-12 border-input pl-10 pr-10 text-base shadow-none focus-visible:border-primary/60 focus-visible:ring-primary/25 [&::-webkit-search-cancel-button]:hidden"
            />
            {saisie && (
              <button
                type="button"
                onClick={() => {
                  setSaisie("")
                  setCompletionOuverte(false)
                  majParams({ q: null, exact: null, sans: null })
                }}
                aria-label="Effacer la recherche"
                className="absolute right-2 top-1/2 flex size-8 -translate-y-1/2 items-center justify-center rounded-full text-muted-foreground hover:bg-muted hover:text-foreground"
              >
                <X className="size-4" />
              </button>
            )}
            {/* Ce que l'élève est peut-être en train d'écrire : des intitulés de thèmes. Choisir une
                proposition lance la recherche tout de suite ; le champ garde le focus (onMouseDown) pour que le
                clic ne le ferme pas avant d'être pris en compte. */}
            {propositions.length > 0 && (
              <ul
                id="completions-recherche"
                role="listbox"
                aria-label="Suggestions"
                className="absolute left-0 right-0 top-full z-30 mt-1 overflow-hidden rounded-xl border border-border bg-card py-1 shadow-lg"
              >
                {propositions.map((c, i) => (
                  <li
                    key={c.texte}
                    id={`completion-${i}`}
                    role="option"
                    aria-selected={i === completionActive}
                    onMouseDown={(e) => {
                      e.preventDefault()
                      choisirCompletion(c.texte)
                    }}
                    className={cn(
                      "flex cursor-pointer items-center gap-3 px-3.5 py-2 text-sm",
                      i === completionActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/60",
                    )}
                  >
                    <Search className="size-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
                    <span className="min-w-0 flex-1 truncate">
                      <Surbrillance texte={c.texte} jetons={jetonsCompletion} />
                    </span>
                    <span className="shrink-0 text-xs text-muted-foreground">{c.matiere}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </form>

        {/* Ce que le moteur a compris (« bac c maths 2019 corrigé » : un examen, une matière, une année, un type) -
            jamais en silence : chaque pastille se retire d'un clic, et le mot redevient un mot comme un autre. */}
        {(compris.length > 0 || intention?.ignoree) && (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-sm" aria-live="polite">
            {compris.length > 0 && (
              <span className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">Compris</span>
            )}
            {compris.map((pastille) => (
              <span
                key={pastille.cle}
                className="inline-flex items-center gap-1 rounded-full bg-primary/10 py-1 pl-3 pr-1 text-sm font-medium text-primary"
              >
                {pastille.libelle}
                <button
                  type="button"
                  onClick={() => retirer(pastille.cle)}
                  aria-label={`Retirer ${pastille.libelle}`}
                  className="flex size-5 items-center justify-center rounded-full hover:bg-primary/20"
                >
                  <X className="size-3" aria-hidden="true" />
                </button>
              </span>
            ))}
            {intention?.ignoree && (
              <span className="text-muted-foreground">
                Rien avec les filtres que j'avais compris : je cherche tes mots tels quels.
              </span>
            )}
          </div>
        )}

        {/* Périmètre : l'examen de l'élève par défaut, jamais caché - c'est ce qui explique pourquoi un
            résultat attendu manque, et un clic suffit pour l'élargir. */}
        {cursusLabel && (
          <FiltreLigne titre="Examen">
            <PastilleFiltre actif={!elargir} onClick={() => majParams({ elargir: null })}>
              Mon examen · {cursusLabel}
            </PastilleFiltre>
            <PastilleFiltre actif={elargir} onClick={() => majParams({ elargir: "1" })}>
              Tous les examens
            </PastilleFiltre>
          </FiltreLigne>
        )}

        {/* Plusieurs matières : « tangente » existe en maths, en physique et en chimie. Les pastilles disent
            combien de résultats chacune apporte et filtrent d'un clic - la liste reste complète quand l'une
            est choisie, pour en changer sans repartir de zéro. */}
        {filtrable && data.matieres.length > 1 && (
          <FiltreLigne titre="Matière">
            <PastilleFiltre actif={!matiere} onClick={() => majParams({ matiere: null })}>
              Toutes les matières <span className="opacity-75">{data.matieres.reduce((somme, m) => somme + m.total, 0)}</span>
            </PastilleFiltre>
            {data.matieres.map((m) => (
              <PastilleFiltre key={m.code} actif={matiere === m.code} onClick={() => majParams({ matiere: m.code })}>
                <span className={cn("size-2 rounded-full", couleurMatiere(m.code).barre)} aria-hidden="true" />
                {m.label} <span className="opacity-75">{m.total}</span>
              </PastilleFiltre>
            ))}
          </FiltreLigne>
        )}

        {filtrable && <Onglets groupes={groupes} total={data.total} famille={famille} onChoisir={(f) => majParams({ type: f?.cle ?? null })} />}
      </div>

      {termes.length < LONGUEUR_MIN_RECHERCHE ? (
        <PageVide
          country={country}
          identite={identite}
          cursusDeclare={cursusDeclare}
          cursusLabel={cursusLabel}
          onChercher={(requete) => {
            setSaisie(requete)
            majParams({ q: requete, exact: null })
            memoriserRecente(requete)
            tracerRechercheLancee("page")
          }}
        />
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
          {data.total > 0 && (
            <p className="mt-5 text-sm text-muted-foreground" aria-live="polite">
              <strong className="font-display text-base font-semibold text-foreground">{data.total}</strong>{" "}
              résultat{data.total > 1 ? "s" : ""} pour « {termes} »
            </p>
          )}
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

              {famille === undefined ? (
                <div>
                  {vedette && <ResultatVedette resultat={vedette} jetons={jetons} country={country} onChoisir={ouvrir(vedette, 0)} />}

                  {associees.length > 0 && (
                    <div className="mt-5 flex flex-wrap items-center gap-2 text-sm">
                      <span className="text-muted-foreground">À explorer aussi :</span>
                      {associees.map((theme) => (
                        <button
                          key={theme.id}
                          type="button"
                          onClick={() => {
                            setSaisie(theme.titre)
                            majParams({ q: theme.titre, exact: null })
                          }}
                          className="rounded-full border border-border bg-background px-3 py-1 transition-colors hover:border-primary hover:text-primary"
                        >
                          {theme.titre}
                        </button>
                      ))}
                    </div>
                  )}

                  <div className="mt-8 space-y-9">
                    {groupes.map((groupe, index) => {
                      const resultats = groupe.type === "THEME" && vedette ? groupe.resultats.filter((r) => r.id !== vedette.id) : groupe.resultats
                      if (resultats.length === 0) return null
                      return (
                        <section
                          key={groupe.type}
                          aria-labelledby={`groupe-${groupe.type}`}
                          className="animate-fade-up"
                          style={{ animationDelay: `${Math.min(index, 5) * 70}ms` }}
                        >
                          <div className="mb-3 flex items-center justify-between gap-3">
                            <h2 id={`groupe-${groupe.type}`} className="flex items-center gap-2 font-display text-lg font-semibold">
                              <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
                                <IconeType type={groupe.type} className="size-4" />
                              </span>
                              {groupe.libelle} <span className="text-sm font-normal text-muted-foreground">({groupe.total})</span>
                            </h2>
                            {groupe.total > groupe.resultats.length && (
                              <button
                                type="button"
                                onClick={() => majParams({ type: familleDe(groupe.type).cle })}
                                className="inline-flex items-center gap-1 rounded-full border border-border px-3 py-1 text-sm font-medium text-primary transition-colors hover:border-primary"
                              >
                                Voir les {groupe.total}
                                <ArrowRight className="size-3.5" aria-hidden="true" />
                              </button>
                            )}
                          </div>
                          <div className="grid gap-3 md:grid-cols-2">
                            {resultats.map((resultat, rang) => (
                              <ResultatCarte key={`${resultat.type}-${resultat.id}`} resultat={resultat} jetons={jetons} country={country} onChoisir={ouvrir(resultat, rang)} />
                            ))}
                          </div>
                        </section>
                      )
                    })}
                  </div>
                </div>
              ) : (
                <div className="mt-6 space-y-9">
                  {/* Un onglet = un ou plusieurs types (Épreuves : épreuves, inédites, exercices). Chaque
                      type garde sa propre liste paginée, sous son titre quand il y en a plusieurs. */}
                  {famille.types
                    .map((t) => groupes.find((g) => g.type === t))
                    .filter((g): g is GroupeRecherche => g !== undefined)
                    .map((groupe) => (
                      <SectionPaginee
                        key={groupe.type}
                        groupe={groupe}
                        avecTitre={famille.types.length > 1}
                        cle={["recherche", "type", country, identite, termes, matiere, cursusDeclare ?? null, elargir, exact, sansBrut, groupe.type]}
                        chercher={(decalage, signal) =>
                          rechercher(
                            {
                              q: termes, pays: country, cursus: cursusDeclare, matiere: matiere || undefined, elargir, exact, sans,
                              type: groupe.type, limite: PAGE_TYPE, decalage,
                            },
                            signal,
                          )
                        }
                        jetons={jetons}
                        country={country}
                        ouvrir={ouvrir}
                      />
                    ))}
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
  groupes, total, famille, onChoisir,
}: {
  groupes: GroupeRecherche[]
  total: number
  famille: FamilleRecherche | undefined
  onChoisir: (famille: FamilleRecherche | undefined) => void
}) {
  // Mêmes mots et même ordre que les onglets « Réviser » (voir FAMILLES_RECHERCHE), et la même rangée de
  // pastilles que les filtres de /epreuves et /cours. Les compteurs viennent de la vue d'ensemble :
  // toujours à jour, que l'onglet choisi pagine ou non. Un type sans résultat n'est pas proposé (sauf
  // s'il est celui où l'on est).
  const onglets = FAMILLES_RECHERCHE.map((f) => ({
    ...f,
    total: groupes.filter((g) => f.types.includes(g.type)).reduce((somme, g) => somme + g.total, 0),
  })).filter((f) => f.total > 0 || f.cle === famille?.cle)
  return (
    <FiltreLigne titre="Type">
      <PastilleFiltre actif={famille === undefined} onClick={() => onChoisir(undefined)}>
        Tout <span className="opacity-75">{total}</span>
      </PastilleFiltre>
      {onglets.map((f) => (
        <PastilleFiltre key={f.cle} actif={famille?.cle === f.cle} onClick={() => onChoisir(f)}>
          {f.libelle} <span className="opacity-75">{f.total}</span>
        </PastilleFiltre>
      ))}
    </FiltreLigne>
  )
}

/** La liste paginée d'UN type de résultat (« Afficher plus » charge la suite). Chaque section porte sa
 * propre requête : un onglet qui regroupe plusieurs types en affiche plusieurs, indépendantes. */
function SectionPaginee({
  groupe, avecTitre, cle, chercher, jetons, country, ouvrir,
}: {
  groupe: GroupeRecherche
  avecTitre: boolean
  cle: unknown[]
  chercher: (decalage: number, signal: AbortSignal) => Promise<ReponseRecherche>
  jetons: string[]
  country: string
  ouvrir: (resultat: ResultatRecherche, rang: number) => () => void
}) {
  const liste = useInfiniteQuery({
    queryKey: cle,
    queryFn: ({ pageParam, signal }) => chercher(pageParam, signal),
    initialPageParam: 0,
    getNextPageParam: (derniere, pages) => {
      const total = derniere.groupes[0]?.total ?? 0
      const charges = pages.reduce((somme, page) => somme + (page.groupes[0]?.resultats.length ?? 0), 0)
      return charges < total ? charges : undefined
    },
  })
  const resultats = liste.data?.pages.flatMap((p) => p.groupes[0]?.resultats ?? []) ?? []
  return (
    <section aria-labelledby={avecTitre ? `groupe-${groupe.type}` : undefined} aria-label={avecTitre ? undefined : groupe.libelle}>
      {avecTitre && (
        <h2 id={`groupe-${groupe.type}`} className="mb-3 flex items-center gap-2 font-display text-lg font-semibold">
          <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <IconeType type={groupe.type} className="size-4" />
          </span>
          {groupe.libelle} <span className="text-sm font-normal text-muted-foreground">({groupe.total})</span>
        </h2>
      )}
      {liste.isLoading ? (
        <Chargement />
      ) : (
        <>
          <div className="grid gap-3 md:grid-cols-2">
            {resultats.map((resultat, rang) => (
              <ResultatCarte key={`${resultat.type}-${resultat.id}`} resultat={resultat} jetons={jetons} country={country} onChoisir={ouvrir(resultat, rang)} />
            ))}
          </div>
          {liste.hasNextPage && (
            <div className="mt-5 flex justify-center">
              <Button variant="outline" onClick={() => liste.fetchNextPage()} disabled={liste.isFetchingNextPage}>
                {liste.isFetchingNextPage && <Loader2 className="animate-spin" />}
                Afficher plus de résultats
              </Button>
            </div>
          )}
        </>
      )}
    </section>
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

/**
 * La page de recherche avant toute requête - celle où arrivent la loupe de l'en-tête, le bouton des onglets
 * Réviser et les raccourcis clavier. Un champ vide ne dit rien ; elle propose donc de quoi commencer sans
 * rien taper : reprendre sa lecture, relancer une recherche récente, ou partir d'un thème de son examen.
 */
function PageVide({
  country, identite, cursusDeclare, cursusLabel, onChercher,
}: {
  country: string
  identite: number
  cursusDeclare: number | null | undefined
  cursusLabel: string
  onChercher: (requete: string) => void
}) {
  const { isAuthenticated } = useAuth()
  const [recentes, setRecentes] = useState(lireRecentes)

  const accueil = useQuery({
    queryKey: ["recherche", "accueil", country, identite, cursusDeclare ?? null],
    queryFn: ({ signal }) => rechercher({ q: "", pays: country, cursus: cursusDeclare, rapide: true }, signal),
    enabled: cursusDeclare !== undefined,
  })
  const progression = useQuery({
    queryKey: ["progression"],
    queryFn: ({ signal }) => getMyProgression(signal),
    enabled: isAuthenticated,
  })
  // `enabled: false` laisse le cache d'une session précédente intact : sans ce garde, une déconnexion sans
  // rechargement complet afficherait encore la lecture de l'élève précédent.
  const reprise = isAuthenticated ? progression.data?.lessons[0] : undefined
  const themes = accueil.data?.suggestions ?? []

  const pastille =
    "inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-3 py-1.5 text-sm transition-colors hover:border-primary hover:text-primary"

  return (
    <div className="mt-8 space-y-8">
      {reprise && (
        <Link
          to={epreuveReaderPath(reprise.subject.country.code.toLowerCase(), reprise.slug as string)}
          className="group flex items-center gap-3 rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent px-5 py-4 transition-colors hover:border-primary/50"
        >
          <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <BookOpen className="size-5" aria-hidden="true" />
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">Reprendre ma lecture</span>
            <span className="block truncate font-display font-medium">{reprise.title}</span>
          </span>
          <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
        </Link>
      )}

      {recentes.length > 0 && (
        <section aria-labelledby="recherches-recentes">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 id="recherches-recentes" className="font-display text-lg font-semibold">
              Tes dernières recherches
            </h2>
            <button
              type="button"
              onClick={() => {
                oublierRecentes()
                setRecentes([])
              }}
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              Effacer
            </button>
          </div>
          <ul className="flex flex-wrap gap-2">
            {recentes.map((requete) => (
              <li key={requete}>
                <button type="button" onClick={() => onChercher(requete)} className={pastille}>
                  <Clock className="size-3.5 text-muted-foreground" aria-hidden="true" />
                  {requete}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section aria-labelledby="themes-pour-commencer">
        <h2 id="themes-pour-commencer" className="mb-3 font-display text-lg font-semibold">
          {cursusLabel ? (
            <>
              Des thèmes pour ton examen <span className="text-sm font-normal text-muted-foreground">· {cursusLabel}</span>
            </>
          ) : (
            "Des thèmes pour commencer"
          )}
        </h2>
        {accueil.isLoading ? (
          <div className="flex flex-wrap gap-2" role="status" aria-label="Chargement des thèmes">
            {[0, 1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-9 w-32 rounded-full" />
            ))}
          </div>
        ) : themes.length > 0 ? (
          <ul className="flex flex-wrap gap-2">
            {themes.map((theme) => (
              <li key={theme.id}>
                <button type="button" onClick={() => onChercher(theme.titre)} className={pastille}>
                  {theme.titre}
                  <span className="text-xs text-muted-foreground">{theme.matiere.label}</span>
                </button>
              </li>
            ))}
          </ul>
        ) : null}
        <p className="mt-4 text-sm text-muted-foreground">
          Tu peux aussi chercher une notion (« discriminant »), une épreuve ou une année (« BAC C maths 2019 »).
        </p>
      </section>
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
