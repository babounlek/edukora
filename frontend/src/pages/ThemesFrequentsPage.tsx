import { useEffect, useState } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import {
  ArrowRight,
  BadgeCheck,
  Crown,
  FileText,
  Layers,
  ListChecks,
  Lock,
  RefreshCw,
  Repeat,
  TrendingUp,
} from "lucide-react"

import { getThemesFrequents, getThemesFrequentsMatieres, listCursus } from "@/api/endpoints"
import type { Cursus, ThemeFrequent, ThemesFrequentsMatiere } from "@/api/types"
import { useSeo } from "@/lib/seo"
import { useCountry } from "@/context/CountryContext"
import { capitaliserTheme, cn } from "@/lib/utils"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { subjectShortLabel } from "@/lib/subjectLabel"
import { lienExercicesTheme } from "@/components/ThemesFrequents"
import { AnneauFrequence } from "@/components/AnneauFrequence"
import { EtapesPresentation, StatChip } from "@/components/Configurateur"
import { FiltreLigne, PastilleFiltre } from "@/components/FiltresCatalogue"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ReviserTabs } from "@/components/ReviserTabs"
import { useFiltreCursusParDefaut } from "@/lib/filtreCursus"

interface ThemeIllustratif {
  id: number
  tag: string
  frequence_pct: number
}

// Aperçu illustratif tant qu'aucune sélection n'a renvoyé de vraies données - même
// procédé que la carte "Fiche - Dérivées" figée sur /fiches : un mockup plausible,
// remplacé dès que la sélection courante renvoie un classement réel.
const CLASSEMENT_ILLUSTRATIF: ThemeIllustratif[] = [
  { id: -1, tag: "Suites numériques", frequence_pct: 68 },
  { id: -2, tag: "Probabilités", frequence_pct: 55 },
  { id: -3, tag: "Trigonométrie", frequence_pct: 47 },
]

// Lignes fantômes affichées sous le teaser d'un non-abonné : de quoi montrer la
// profondeur du classement sans jamais en révéler le contenu (le serveur ne l'envoie pas).
const MAX_LIGNES_FANTOMES = 5

// Le classement affiche 20 thèmes par défaut ("Top 20", voir le hero) puis révèle 10
// thèmes de plus par clic sur "Charger 10 thèmes de plus" - le serveur en renvoie déjà
// jusqu'à 50 (voir MAX_THEMES_FREQUENTS côté catalog.views), donc chaque clic ne fait
// que révéler des données déjà en main, aucune requête supplémentaire.
const THEMES_AFFICHES_PAR_DEFAUT = 20
const THEMES_CHARGES_PAR_CLIC = 10
// En dessous, le thème suivant n'est plus assez fréquent pour qu'aller le chercher
// vaille le clic (mesuré sur le corpus réel : le signal reste net jusque-là, voir la
// proposition qui a motivé ce chantier) - le bouton disparaît plutôt que de promettre
// un classement qui se dilue en bruit statistique.
const SEUIL_CHARGER_PLUS_PCT = 15

function libelleCursus(c: Pick<Cursus, "examen_display" | "series">) {
  return `${c.examen_display}${c.series ? ` ${c.series.code}` : ""}`
}

/** Mini-podium décoratif du hero, même procédé que l'anneau de maîtrise de /quiz ou la
 * fiche annotée de /fiches - un accessoire concret plutôt qu'une simple icône, adossé
 * aux vraies données dès qu'elles existent. */
function MiniClassement({ themes }: { themes: ThemeIllustratif[] }) {
  const items = themes.length > 0 ? themes.slice(0, 3) : CLASSEMENT_ILLUSTRATIF
  return (
    <div className="flex flex-col gap-3">
      {items.map((theme, index) => (
        <div key={theme.id} className="flex items-center gap-2.5">
          <span
            className={cn(
              "flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-bold tabular-nums",
              index === 0 ? "bg-gold text-gold-foreground" : "bg-muted text-muted-foreground",
            )}
          >
            {index + 1}
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-2 text-xs">
              <span className="min-w-0 truncate font-medium">{capitaliserTheme(theme.tag)}</span>
              <span className="shrink-0 tabular-nums text-muted-foreground">{theme.frequence_pct}%</span>
            </div>
            <div className="relative mt-1 h-1.5 w-full rounded-full bg-muted">
              <div
                className={cn("absolute inset-y-0 left-0 rounded-full", index === 0 ? "bg-gold" : "bg-primary/60")}
                style={{ width: `${theme.frequence_pct}%` }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

interface ActionsThemeProps {
  country: string
  theme: ThemeFrequent
  subjectCode: string
  cursusId: number
  total: number
  mis_en_avant?: boolean
}

/** "Exercices" et "Quiz" côte à côte, jamais fusionnés : lire le corrigé en contexte ou
 * s'entraîner sur des items autonomes, le bon choix dépend de l'élève (voir
 * ThemesFrequents.tsx). */
function ActionsTheme({ country, theme, subjectCode, cursusId, total, mis_en_avant }: ActionsThemeProps) {
  return (
    <div className="flex shrink-0 gap-1.5">
      <Button asChild size="sm" variant={mis_en_avant ? "default" : "outline"} className="h-8 px-3 text-xs">
        <Link to={lienExercicesTheme(country, theme, subjectCode, cursusId, total)}>
          <FileText className="size-3.5" />
          Exercices
        </Link>
      </Button>
      {theme.quiz_disponible ? (
        <Button asChild size="sm" variant="outline" className="h-8 px-3 text-xs">
          <Link to={`/quiz?cursus=${cursusId}&theme=${theme.id}`}>
            <ListChecks className="size-3.5" />
            Quiz
          </Link>
        </Button>
      ) : (
        <Button
          size="sm"
          variant="outline"
          disabled
          title="Pas encore de question de quiz sur ce thème précis"
          className="h-8 px-3 text-xs"
        >
          <ListChecks className="size-3.5" />
          Quiz
        </Button>
      )}
    </div>
  )
}

/** Une marche du podium (rangs 1 à 3). Le n°1 est doré et, dès `sm`, placé au centre et
 * surélevé, comme un vrai podium. */
function CartePodium(props: Omit<ActionsThemeProps, "mis_en_avant"> & { rang: number }) {
  const { rang, theme, total } = props
  const premier = rang === 1
  return (
    <div
      className={cn(
        "relative flex flex-col gap-4 overflow-hidden rounded-2xl border p-5 transition-shadow hover:shadow-lg",
        premier
          ? "border-gold/50 bg-gradient-to-br from-gold/[0.14] via-card to-card shadow-md shadow-gold/10 sm:order-2 sm:-translate-y-3"
          : "border-border bg-card shadow-sm",
        rang === 2 && "sm:order-1",
        rang === 3 && "sm:order-3",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <span
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-bold uppercase tracking-wider",
            premier ? "bg-gold text-gold-foreground" : "bg-primary/10 text-primary",
          )}
        >
          {premier && <Crown className="size-3.5" />}
          N°{rang}
        </span>
        <AnneauFrequence pct={theme.frequence_pct} dore={premier} />
      </div>
      <div className="min-w-0 flex-1">
        <h3 className="font-display text-lg font-semibold leading-snug text-balance">{capitaliserTheme(theme.tag)}</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Présent dans <span className="font-medium tabular-nums text-foreground">{theme.nb_epreuves}</span> sessions
          sur <span className="tabular-nums">{total}</span>
        </p>
      </div>
      <ActionsTheme {...props} mis_en_avant={premier} />
    </div>
  )
}

/** Troisième marche verrouillée pour un non-abonné : le podium reste complet à l'œil,
 * le contenu n'est jamais envoyé par le serveur. */
function CartePodiumVerrouillee({ cursusId }: { cursusId: number }) {
  return (
    <Link
      to={`/abonnement?cursus=${cursusId}`}
      className="group relative flex flex-col items-center justify-center gap-3 overflow-hidden rounded-2xl border border-dashed border-gold/50 bg-gold/[0.04] p-5 text-center transition-colors hover:bg-gold/[0.08] sm:order-3"
    >
      <span className="flex size-12 items-center justify-center rounded-full bg-gold/15 text-gold-text ring-4 ring-gold/10">
        <Lock className="size-5" />
      </span>
      <div>
        <p className="font-display text-lg font-semibold">N°3 et suivants</p>
        <p className="mt-1 text-sm text-muted-foreground">Réservés à l'abonnement Jusqu'à l'Examen</p>
      </div>
      <span className="inline-flex items-center gap-1 text-sm font-medium text-gold-text group-hover:underline">
        Débloquer
        <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
      </span>
    </Link>
  )
}

function LigneClassement(props: Omit<ActionsThemeProps, "mis_en_avant"> & { rang: number }) {
  const { rang, theme, total } = props
  return (
    <li className="flex flex-col gap-3 px-4 py-3.5 transition-colors hover:bg-accent/40 sm:flex-row sm:items-center sm:gap-4 sm:px-5">
      <div className="flex min-w-0 flex-1 items-center gap-3.5">
        <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted font-display text-sm font-semibold tabular-nums text-muted-foreground">
          {rang}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-3">
            <span className="min-w-0 flex-1 truncate font-medium">{capitaliserTheme(theme.tag)}</span>
            <span className="shrink-0 text-sm font-semibold tabular-nums text-primary">{theme.frequence_pct}%</span>
          </div>
          <div className="mt-2 flex items-center gap-3">
            <span className="block h-1.5 flex-1 overflow-hidden rounded-full bg-primary/10">
              <span
                className="block h-full rounded-full bg-primary/70 transition-[width] duration-500"
                style={{ width: `${theme.frequence_pct}%` }}
              />
            </span>
            <span className="w-12 shrink-0 text-right text-xs tabular-nums text-muted-foreground">
              {theme.nb_epreuves}/{total}
            </span>
          </div>
        </div>
      </div>
      <div className="pl-[2.875rem] sm:pl-0">
        <ActionsTheme {...props} />
      </div>
    </li>
  )
}

/** Suite du classement pour un non-abonné : des lignes floutées (jamais de vrai contenu)
 * sous un appel à débloquer - la profondeur se voit, le détail reste payant. */
function SuiteVerrouillee({
  nbVerrouilles, premierRang, dernierPct, cursusId, matiereLabel,
}: { nbVerrouilles: number; premierRang: number; dernierPct: number; cursusId: number; matiereLabel?: string }) {
  const nbLignes = Math.min(nbVerrouilles, MAX_LIGNES_FANTOMES)
  return (
    <div className="relative overflow-hidden rounded-2xl border border-border bg-card">
      <ul aria-hidden className="select-none divide-y divide-border blur-[3px]">
        {Array.from({ length: nbLignes }, (_, i) => {
          const pct = Math.max(8, Math.round(dernierPct * (0.85 - i * 0.12)))
          return (
            <li key={i} className="flex items-center gap-3.5 px-5 py-4">
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted text-sm font-semibold text-muted-foreground">
                {premierRang + i}
              </span>
              <div className="flex-1">
                <span className="block h-3 rounded bg-foreground/15" style={{ width: `${45 - i * 4}%` }} />
                <span className="mt-2.5 block h-1.5 w-full rounded-full bg-primary/10">
                  <span className="block h-full rounded-full bg-primary/50" style={{ width: `${pct}%` }} />
                </span>
              </div>
            </li>
          )
        })}
      </ul>
      <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-b from-card/40 via-card/85 to-card p-4">
        <div className="flex max-w-md flex-col items-center gap-3 text-center">
          <span className="flex size-11 items-center justify-center rounded-full bg-gold text-gold-foreground shadow-md">
            <Crown className="size-5" />
          </span>
          <p className="font-display text-xl font-semibold">
            Encore {nbVerrouilles} thème{nbVerrouilles > 1 ? "s" : ""} classé{nbVerrouilles > 1 ? "s" : ""}
            {matiereLabel ? ` en ${matiereLabel}` : ""}
          </p>
          <p className="text-sm text-muted-foreground">
            Le classement complet, avec les exercices corrigés et les quiz de chaque thème, est inclus dans
            l'abonnement Jusqu'à l'Examen.
          </p>
          <Button asChild className="mt-1">
            <Link to={`/abonnement?cursus=${cursusId}`}>
              Débloquer le classement complet
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      </div>
    </div>
  )
}

function ClassementSquelette() {
  return (
    <div className="flex flex-col gap-5">
      <div className="grid gap-4 sm:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-52 rounded-2xl" />
        ))}
      </div>
      <Skeleton className="h-64 rounded-2xl" />
    </div>
  )
}

/** Les trois garanties de méthode, dites une fois sous le classement : c'est ce qui en
 * fait une statistique et pas une intuition de professeur. */
function Methode() {
  const points = [
    {
      icon: BadgeCheck,
      titre: "Épreuves officielles uniquement",
      texte: "Les examens blancs et les sujets d'établissement ne comptent pas.",
    },
    {
      icon: Repeat,
      titre: "Une fois par session",
      texte: "Un thème traité dans trois exercices d'un même sujet ne compte qu'une fois.",
    },
    {
      icon: RefreshCw,
      titre: "Toujours à jour",
      texte: "Le classement est recalculé à chaque nouvelle épreuve ajoutée.",
    },
  ]
  return (
    <section aria-labelledby="methode-titre" className="mt-10 rounded-2xl border border-border bg-muted/30 p-5 sm:p-6">
      <h2 id="methode-titre" className="font-display text-base font-semibold">
        Comment on établit ce classement
      </h2>
      <ul className="mt-4 grid gap-4 sm:grid-cols-3">
        {points.map(({ icon: Icon, titre, texte }) => (
          <li key={titre} className="flex gap-3">
            <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Icon className="size-4" />
            </span>
            <div>
              <p className="text-sm font-medium">{titre}</p>
              <p className="mt-0.5 text-sm text-muted-foreground">{texte}</p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}

/**
 * Page autonome du classement des thèmes fréquents - contrepartie de l'aperçu tronqué
 * embarqué sur /epreuves (voir ThemesFrequents.tsx, lien "Voir le classement complet").
 * Utilisable seule : ses propres filtres cursus/matière vivent en query params, pas
 * hérités d'une autre page.
 */
export function ThemesFrequentsPage() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label

  const [searchParams, setSearchParams] = useSearchParams()
  // Pré-sélection de l'examen déclaré : une étape de moins avant le classement. Pas de
  // bandeau "Voir tout le catalogue" ici (voir BandeauFiltreCursus) : sans cursus, cette
  // page n'a rien à montrer.
  useFiltreCursusParDefaut()
  const subjectFilter = searchParams.get("subject") ?? ""
  const cursusFilter = searchParams.get("cursus") ?? ""
  const cursusId = cursusFilter ? Number(cursusFilter) : undefined

  useSeo({
    title: "Les thèmes qui reviennent le plus",
    description: countryLabel
      ? `${countryLabel} : le classement des thèmes les plus fréquents aux épreuves officielles, matière par matière et cursus par cursus.`
      : undefined,
  })

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })
  // Même tri que /epreuves : les séries d'un même examen se suivent.
  const cursusTries = [...cursusList].sort(
    (x, y) =>
      x.examen_display.localeCompare(y.examen_display, "fr") ||
      (x.series?.code ?? "").localeCompare(y.series?.code ?? "", "fr"),
  )
  const cursusCourant = cursusList.find((c) => c.id === cursusId)

  // Seulement les matières qui ont des épreuves officielles sur ce cursus : le
  // référentiel complet proposait l'EPS ou l'Allemand en BAC C, pour un écran vide.
  const { data: matieres, isLoading: matieresEnChargement } = useQuery({
    queryKey: ["themes-frequents-matieres", cursusId],
    queryFn: ({ signal }) => getThemesFrequentsMatieres(cursusId!, signal),
    enabled: Boolean(cursusId),
  })
  const matiereCourante: ThemesFrequentsMatiere | undefined = matieres?.find((m) => m.code === subjectFilter)

  const { data: themesData, isLoading: themesEnChargement } = useQuery({
    queryKey: ["themes-frequents", cursusId, subjectFilter],
    queryFn: ({ signal }) => getThemesFrequents(cursusId!, subjectFilter, signal),
    enabled: Boolean(cursusId && subjectFilter),
  })

  // Combien de thèmes révéler - remis à la valeur par défaut à chaque changement
  // d'examen/matière, sinon "Charger 10 de plus" cliqué en Maths resterait ouvert en
  // arrivant sur Anglais.
  const [nbAffiches, setNbAffiches] = useState(THEMES_AFFICHES_PAR_DEFAUT)
  useEffect(() => {
    setNbAffiches(THEMES_AFFICHES_PAR_DEFAUT)
  }, [cursusId, subjectFilter])

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    setSearchParams(next, { replace: true })
  }

  // Une matière absente du cursus choisi (ou pas encore choisie) bascule sur la plus
  // fournie : on arrive directement sur un classement, jamais sur un écran à compléter.
  // La matière en cours est gardée d'un cursus à l'autre quand elle y existe (Maths en
  // BAC C puis en BAC D).
  useEffect(() => {
    if (!matieres || matieres.some((m) => m.code === subjectFilter)) return
    const premiere = matieres.find((m) => m.disponible)
    if (!premiere) return
    const next = new URLSearchParams(searchParams)
    next.set("subject", premiere.code)
    setSearchParams(next, { replace: true })
  }, [matieres, subjectFilter, searchParams, setSearchParams])

  const disponible = themesData?.disponible === true
  const themes = disponible ? themesData.themes : []
  const total = themesData?.nb_sessions_disponibles ?? 0
  const themesAffiches = themes.slice(0, nbAffiches)
  const podium = themesAffiches.slice(0, 3)
  const suite = themesAffiches.slice(3)
  const verrouille = disponible && !themesData.has_access && themesData.nb_themes_verrouilles > 0
  // Le thème juste sous la coupure actuelle : tant qu'il reste assez fréquent pour
  // valoir le clic, "Charger 10 de plus" révèle la suite déjà reçue du serveur.
  const prochainTheme = themes[nbAffiches]
  const chargerPlusVisible = Boolean(prochainTheme && prochainTheme.frequence_pct >= SEUIL_CHARGER_PLUS_PCT)
  const topTheme = themes[0]
  const matiereLabel = matiereCourante?.label
  const MatiereIcon = subjectIcon(subjectFilter)

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <ReviserTabs />

      {/* Hero : même gabarit que /epreuves et /cours (arrondi, dégradé vert-or, filigrane),
          avec le mini-classement en accessoire, adossé aux vraies données dès qu'il y en a. */}
      <div className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative grid gap-8 lg:grid-cols-[1.3fr_0.7fr] lg:items-center lg:gap-12">
          <div>
            <p className="mb-2 font-display text-sm italic text-primary">
              Statistiques{countryLabel ? ` - ${countryLabel}` : ""}
            </p>
            <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight text-balance sm:text-4xl">
              Les thèmes qui <span className="text-primary">reviennent le plus</span> à l'examen.
            </h1>
            <p className="mt-2 max-w-xl text-muted-foreground">
              On a passé au crible toutes les épreuves officielles en base pour repérer ce qui tombe vraiment. Révise
              d'abord ce qui compte.
            </p>

            <div className="mt-4 flex flex-wrap gap-2 sm:mt-5">
              {disponible ? (
                <>
                  <StatChip icon={<TrendingUp className="size-3.5 text-primary" />}>
                    <span className="font-medium tabular-nums">{total}</span>
                    <span className="text-muted-foreground">sessions officielles analysées</span>
                  </StatChip>
                  {topTheme && (
                    <StatChip icon={<Crown className="size-3.5 text-gold-text" />}>
                      <span className="text-muted-foreground">N°1 :</span>
                      <span className="max-w-[12rem] truncate font-medium">{capitaliserTheme(topTheme.tag)}</span>
                    </StatChip>
                  )}
                </>
              ) : (
                <>
                  <StatChip icon={<TrendingUp className="size-3.5 text-primary" />}>
                    <span className="font-medium">Top 20</span>
                    <span className="text-muted-foreground">des thèmes par matière</span>
                  </StatChip>
                  {cursusList.length > 0 && (
                    <StatChip icon={<Layers className="size-3.5 text-primary" />}>
                      <span className="font-medium tabular-nums">{cursusList.length}</span>
                      <span className="text-muted-foreground">examens couverts</span>
                    </StatChip>
                  )}
                </>
              )}
            </div>
          </div>

          <div aria-hidden className="relative mx-auto hidden w-full max-w-[17rem] select-none sm:block lg:mx-0 lg:justify-self-end">
            <span className="absolute -top-3 right-6 z-10 -rotate-2 rounded-md bg-gold px-3 py-1 text-[0.65rem] font-bold uppercase tracking-wider text-gold-foreground shadow-md">
              Classement en direct
            </span>
            <div className="rotate-2 rounded-xl border border-border bg-card p-5 shadow-xl transition-transform duration-300 hover:rotate-0">
              <MiniClassement themes={themes} />
            </div>
          </div>
        </div>
      </div>

      {/* Sélection : la même carte surélevée et les mêmes pastilles que /epreuves, pour
          que les trois onglets de "Réviser" se pilotent de la même façon. */}
      <div className="mb-8 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:p-6">
        <p className="font-display text-lg font-semibold">Ton examen, ta matière</p>
        <p className="text-sm text-muted-foreground">Le classement se met à jour dès que tu changes de sélection.</p>

        {cursusTries.length > 0 ? (
          <FiltreLigne titre="Examen">
            {cursusTries.map((c) => (
              <PastilleFiltre
                key={c.id}
                actif={cursusId === c.id}
                onClick={() => updateFilter("cursus", String(c.id))}
              >
                {libelleCursus(c)}
              </PastilleFiltre>
            ))}
          </FiltreLigne>
        ) : (
          <Skeleton className="mt-4 h-16 rounded-xl" />
        )}

        <FiltreLigne titre="Matière">
          {!cursusId ? (
            <p className="py-1.5 text-sm text-muted-foreground">Choisis d'abord ton examen.</p>
          ) : matieresEnChargement ? (
            [0, 1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-9 w-24 shrink-0 rounded-full" />)
          ) : matieres && matieres.length > 0 ? (
            matieres.map((m) => {
              const Icon = subjectIcon(m.code)
              const actif = subjectFilter === m.code
              return (
                <PastilleFiltre
                  key={m.code}
                  actif={actif}
                  disabled={!m.disponible}
                  title={
                    m.disponible
                      ? `${m.nb_sessions} sessions officielles analysées`
                      : `Seulement ${m.nb_sessions} session${m.nb_sessions > 1 ? "s" : ""} en base pour l'instant : pas assez pour un classement fiable`
                  }
                  onClick={() => updateFilter("subject", m.code)}
                >
                  <span className={cn("flex size-5 items-center justify-center rounded-full", couleurMatiere(m.code).puce)}>
                    <Icon className="size-3" aria-hidden="true" />
                  </span>
                  {subjectShortLabel(m.code, m.label)}
                  <span
                    className={cn(
                      "rounded-full px-1.5 text-[0.7rem] font-semibold tabular-nums",
                      actif ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground",
                    )}
                  >
                    {m.nb_sessions}
                  </span>
                </PastilleFiltre>
              )
            })
          ) : (
            <p className="py-1.5 text-sm text-muted-foreground">
              Pas encore d'épreuve officielle en base pour cet examen.
            </p>
          )}
        </FiltreLigne>
      </div>

      {!cursusId ? (
        <div className="rounded-2xl border border-primary/25 bg-gradient-to-br from-primary/5 via-transparent to-transparent p-6">
          <div className="flex flex-col items-start gap-4">
            <span className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
              <TrendingUp className="size-5" />
            </span>
            <div>
              <p className="font-display text-lg font-semibold">Choisis ton examen pour voir ton classement</p>
              <p className="mt-1 text-sm text-muted-foreground">
                En un clic, tu sais quels thèmes réviser en priorité.
              </p>
            </div>
            <EtapesPresentation
              etapes={[
                "Tu choisis ton examen et ta matière.",
                "On analyse toutes les épreuves officielles déjà en base.",
                "Tu vois exactement quels thèmes réviser en priorité.",
              ]}
            />
          </div>
        </div>
      ) : !subjectFilter || themesEnChargement || matieresEnChargement ? (
        matieres && matieres.length > 0 && !matieres.some((m) => m.disponible) ? (
          <div className="rounded-2xl border border-dashed border-border px-6 py-14 text-center text-muted-foreground">
            Pas encore assez d'épreuves officielles en base pour classer les thèmes de cet examen.
          </div>
        ) : (
          <ClassementSquelette />
        )
      ) : themesData && !themesData.disponible ? (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border px-6 py-14 text-center">
          <span className="flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
            <TrendingUp className="size-5" />
          </span>
          <p className="max-w-md text-muted-foreground">
            Pas encore assez d'épreuves officielles en base pour cette matière et cet examen (
            {themesData.nb_sessions_disponibles}/{themesData.seuil_minimum} sessions requises).
          </p>
        </div>
      ) : (
        country &&
        cursusId &&
        themes.length > 0 && (
          <section aria-labelledby="classement-titre">
            <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "flex size-11 shrink-0 items-center justify-center rounded-xl",
                    couleurMatiere(subjectFilter).puce,
                  )}
                >
                  <MatiereIcon className="size-5" aria-hidden="true" />
                </span>
                <div>
                  <h2 id="classement-titre" className="font-display text-xl font-semibold sm:text-2xl">
                    {matiereLabel ?? "Classement"}
                    {cursusCourant && (
                      <span className="text-muted-foreground"> · {libelleCursus(cursusCourant)}</span>
                    )}
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    Établi sur <span className="font-medium tabular-nums text-foreground">{total}</span> sessions
                    officielles.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid gap-4 pt-2 sm:grid-cols-3 sm:items-end">
              {podium.map((theme, index) => (
                <CartePodium
                  key={theme.id}
                  rang={index + 1}
                  country={country}
                  theme={theme}
                  subjectCode={subjectFilter}
                  cursusId={cursusId}
                  total={total}
                />
              ))}
              {verrouille && podium.length < 3 && <CartePodiumVerrouillee cursusId={cursusId} />}
            </div>

            {suite.length > 0 && (
              <ol className="mt-6 divide-y divide-border overflow-hidden rounded-2xl border border-border bg-card">
                {suite.map((theme, index) => (
                  <LigneClassement
                    key={theme.id}
                    rang={index + 4}
                    country={country}
                    theme={theme}
                    subjectCode={subjectFilter}
                    cursusId={cursusId}
                    total={total}
                  />
                ))}
              </ol>
            )}

            {chargerPlusVisible && (
              <div className="mt-6 flex justify-center">
                <Button variant="outline" onClick={() => setNbAffiches((n) => n + THEMES_CHARGES_PAR_CLIC)}>
                  Charger {THEMES_CHARGES_PAR_CLIC} thèmes de plus
                </Button>
              </div>
            )}

            {verrouille && (
              <div className="mt-6">
                <SuiteVerrouillee
                  nbVerrouilles={themesData.nb_themes_verrouilles}
                  premierRang={podium.length < 3 ? 4 : themes.length + 1}
                  dernierPct={themes[themes.length - 1].frequence_pct}
                  cursusId={cursusId}
                  matiereLabel={matiereLabel}
                />
              </div>
            )}

            <Methode />
          </section>
        )
      )}
    </div>
  )
}
