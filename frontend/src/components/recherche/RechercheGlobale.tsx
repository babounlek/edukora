import { useEffect, useMemo, useState, type KeyboardEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { ArrowRight, Clock, Search, SearchX } from "lucide-react"

import { rechercher } from "@/api/endpoints"
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { ResultatCompact } from "@/components/recherche/ResultatRecherche"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { useCursusAccueil } from "@/lib/cursusAccueil"
import {
  cibleResultat,
  jetonsDeSurbrillance,
  LONGUEUR_MIN_RECHERCHE,
  lireRecentes,
  memoriserRecente,
  oublierRecentes,
} from "@/lib/recherche"
import { recherchePath } from "@/lib/countryPath"
import { useDebouncedValue } from "@/lib/useDebouncedValue"

// Résultats montrés par groupe dans la palette : de quoi se repérer, la page complète fait le reste.
const PAR_GROUPE = 3
// Pause de frappe avant d'interroger le serveur : une requête par mot tapé, pas par lettre.
const DELAI_SAISIE_MS = 220

const ID_LISTE = "resultats-recherche-rapide"
const idOption = (index: number) => `recherche-option-${index}`

/**
 * Recherche globale en palette (touche « / », Ctrl/⌘+K, ou la loupe de l'en-tête) : on tape, les
 * meilleurs thèmes, cours, épreuves... s'affichent sous le champ, flèches + Entrée pour ouvrir.
 * Une recherche plus fine (filtres, tous les résultats) vit sur la page /:pays/recherche.
 */
export function RechercheGlobale({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  const { country } = useCountry()
  const { user } = useAuth()
  const navigate = useNavigate()
  const cursus = useCursusAccueil(country)

  const [saisie, setSaisie] = useState("")
  const [actif, setActif] = useState(-1)
  const [recentes, setRecentes] = useState<string[]>([])

  // À chaque ouverture : champ vide, rien de sélectionné, historique relu.
  useEffect(() => {
    if (!open) return
    setSaisie("")
    setActif(-1)
    setRecentes(lireRecentes())
  }, [open])

  const termes = useDebouncedValue(saisie.trim(), DELAI_SAISIE_MS)
  const interroger = open && termes.length >= LONGUEUR_MIN_RECHERCHE && cursus !== undefined

  const { data, isFetching, isError } = useQuery({
    // L'identité fait partie de la clé : un résultat « verrouillé » mis en cache pour un visiteur ne
    // doit pas rester affiché une fois l'élève connecté.
    queryKey: ["recherche", "rapide", country, user?.id ?? 0, cursus ?? null, termes],
    queryFn: ({ signal }) => rechercher({ q: termes, pays: country, cursus, limite: PAR_GROUPE, rapide: true }, signal),
    enabled: interroger,
    placeholderData: keepPreviousData,
  })

  // On surligne la requête CORRIGÉE quand le serveur en a retenté une : surligner « equatoin » ne
  // marquerait rien dans des résultats qui parlent d'« équation ».
  const jetons = useMemo(() => jetonsDeSurbrillance(data?.corrige ?? termes), [data?.corrige, termes])
  const groupes = useMemo(() => data?.groupes ?? [], [data])
  const resultats = useMemo(() => groupes.flatMap((g) => g.resultats), [groupes])
  // La dernière « option » est toujours le lien vers la page complète : Entrée y mène quand rien n'est choisi.
  const total = resultats.length + (termes.length >= LONGUEUR_MIN_RECHERCHE ? 1 : 0)

  // Une nouvelle liste repart sans sélection.
  useEffect(() => setActif(-1), [data])
  useEffect(() => {
    if (actif >= 0) document.getElementById(idOption(actif))?.scrollIntoView({ block: "nearest" })
  }, [actif])

  function fermer() {
    onOpenChange(false)
  }

  function allerAuxResultats() {
    memoriserRecente(saisie)
    fermer()
    navigate(`${recherchePath(country)}?q=${encodeURIComponent(saisie.trim())}`)
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "ArrowDown" && total > 0) {
      event.preventDefault()
      setActif((i) => (i + 1) % total)
    } else if (event.key === "ArrowUp" && total > 0) {
      event.preventDefault()
      setActif((i) => (i <= 0 ? total - 1 : i - 1))
    } else if (event.key === "Enter") {
      event.preventDefault()
      if (saisie.trim().length < LONGUEUR_MIN_RECHERCHE) return
      const choisi = actif >= 0 && actif < resultats.length ? resultats[actif] : null
      if (choisi) {
        memoriserRecente(saisie)
        fermer()
        navigate(cibleResultat(country, choisi))
      } else {
        allerAuxResultats()
      }
    }
  }

  const aucun = Boolean(data) && !isFetching && data!.total === 0 && !data!.trop_court
  let indexOption = -1

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/* Ancrée en HAUT, même sur mobile : le clavier virtuel couvre le bas de l'écran, une feuille
          collée en bas cacherait justement les résultats qu'on cherche à lire. */}
      <DialogContent className="top-0 bottom-auto max-h-[90vh] rounded-b-2xl rounded-t-none p-0 sm:top-[10%] sm:max-w-xl sm:-translate-y-0 sm:rounded-2xl">
        <DialogTitle className="sr-only">Rechercher sur le site</DialogTitle>
        <DialogDescription className="sr-only">
          Tape un thème, une notion, une matière ou une année. Utilise les flèches pour choisir un résultat et Entrée pour l'ouvrir.
        </DialogDescription>

        <div className="flex items-center gap-2 border-b border-border px-4 py-3 pr-12">
          <Search className="size-4.5 shrink-0 text-muted-foreground" aria-hidden="true" />
          <input
            type="search"
            value={saisie}
            onChange={(e) => setSaisie(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Un thème, une notion, une année…"
            aria-label="Rechercher"
            role="combobox"
            aria-expanded={total > 0}
            aria-controls={ID_LISTE}
            aria-autocomplete="list"
            aria-activedescendant={actif >= 0 ? idOption(actif) : undefined}
            autoComplete="off"
            autoCorrect="off"
            spellCheck={false}
            enterKeyHint="search"
            className="h-9 min-w-0 flex-1 bg-transparent text-base outline-none placeholder:text-muted-foreground [&::-webkit-search-cancel-button]:hidden"
          />
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-2" aria-busy={isFetching}>
          {termes.length < LONGUEUR_MIN_RECHERCHE && saisie.trim().length < LONGUEUR_MIN_RECHERCHE ? (
            <Accueil recentes={recentes} onChoisir={setSaisie} onEffacer={() => { oublierRecentes(); setRecentes([]) }} />
          ) : isError ? (
            <p className="px-3 py-6 text-center text-sm text-muted-foreground">
              La recherche est momentanément indisponible. Réessaie dans un instant.
            </p>
          ) : !data ? (
            <div className="space-y-2 p-2" role="status" aria-label="Recherche en cours">
              {[0, 1, 2].map((i) => (
                <Skeleton key={i} className="h-12 w-full rounded-lg" />
              ))}
            </div>
          ) : !data.indexe ? (
            <p className="px-3 py-6 text-center text-sm text-muted-foreground">
              La recherche est en cours de préparation. Réessaie dans quelques minutes.
            </p>
          ) : aucun ? (
            <AucunResultat termes={termes} country={country} onChoisir={fermer} />
          ) : (
            <div id={ID_LISTE} role="listbox" aria-label="Résultats de la recherche">
              {data.corrige && (
                <p className="px-3 pb-1 pt-2 text-xs text-muted-foreground">
                  Résultats pour « {data.corrige} »
                </p>
              )}
              {groupes.map((groupe) => (
                <div key={groupe.type} role="group" aria-label={groupe.libelle} className="mb-1">
                  <div className="px-3 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                    {groupe.libelle}
                  </div>
                  {groupe.resultats.map((resultat) => {
                    indexOption += 1
                    return (
                      <ResultatCompact
                        key={`${resultat.type}-${resultat.id}`}
                        id={idOption(indexOption)}
                        actif={indexOption === actif}
                        resultat={resultat}
                        jetons={jetons}
                        country={country}
                        onChoisir={() => {
                          memoriserRecente(saisie)
                          fermer()
                        }}
                      />
                    )
                  })}
                </div>
              ))}
              <Link
                id={idOption(resultats.length)}
                role="option"
                aria-selected={actif === resultats.length}
                to={`${recherchePath(country)}?q=${encodeURIComponent(saisie.trim())}`}
                onClick={() => {
                  memoriserRecente(saisie)
                  fermer()
                }}
                className={`mt-1 flex items-center justify-between gap-2 rounded-lg px-3 py-2.5 text-sm font-medium text-primary outline-none ${
                  actif === resultats.length ? "bg-accent" : "hover:bg-accent/60"
                }`}
              >
                <span className="truncate">
                  Voir tous les résultats{data.total > 0 ? ` (${data.total})` : ""}
                </span>
                <ArrowRight className="size-4 shrink-0" aria-hidden="true" />
              </Link>
            </div>
          )}
        </div>

        <div className="hidden items-center gap-4 border-t border-border px-4 py-2 text-[11px] text-muted-foreground sm:flex" aria-hidden="true">
          <span>↑ ↓ pour choisir</span>
          <span>Entrée pour ouvrir</span>
          <span>Échap pour fermer</span>
        </div>
      </DialogContent>
    </Dialog>
  )
}

function Accueil({
  recentes, onChoisir, onEffacer,
}: {
  recentes: string[]
  onChoisir: (requete: string) => void
  onEffacer: () => void
}) {
  if (recentes.length === 0) {
    return (
      <p className="px-3 py-6 text-center text-sm text-muted-foreground">
        Cherche un thème (« théorème de Thalès »), une notion (« discriminant »), une épreuve (« BAC C maths 2019 »)…
      </p>
    )
  }
  return (
    <div className="p-1">
      <div className="flex items-center justify-between px-2 pb-1 pt-1">
        <span className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Recherches récentes</span>
        <button type="button" onClick={onEffacer} className="text-xs text-muted-foreground hover:text-foreground">
          Effacer
        </button>
      </div>
      <ul>
        {recentes.map((requete) => (
          <li key={requete}>
            <button
              type="button"
              onClick={() => onChoisir(requete)}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm hover:bg-accent/60"
            >
              <Clock className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
              <span className="truncate">{requete}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

function AucunResultat({ termes, country, onChoisir }: { termes: string; country: string; onChoisir: () => void }) {
  return (
    <div className="flex flex-col items-center gap-2 px-4 py-8 text-center">
      <SearchX className="size-7 text-muted-foreground" aria-hidden="true" />
      <p className="text-sm font-medium">Aucun résultat pour « {termes} »</p>
      <p className="text-xs text-muted-foreground">Essaie un mot plus court, ou un autre mot pour la même notion.</p>
      <Link
        to={`${recherchePath(country)}?q=${encodeURIComponent(termes)}`}
        onClick={onChoisir}
        className="mt-1 text-xs font-medium text-primary hover:underline"
      >
        Voir des suggestions
      </Link>
    </div>
  )
}
