import { useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Crown, TrendingUp } from "lucide-react"

import { getThemesFrequents, listCursus, listSubjects } from "@/api/endpoints"
import { useSeo } from "@/lib/seo"
import { useCountry } from "@/context/CountryContext"
import { capitaliserTheme, cn } from "@/lib/utils"
import { ThemesFrequents } from "@/components/ThemesFrequents"
import { EtapesPresentation, Eyebrow, StatChip } from "@/components/Configurateur"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface ThemeIllustratif {
  id: number
  tag: string
  frequence_pct: number
}

// Aperçu illustratif tant qu'aucune sélection n'a renvoyé de vraies données - même
// procédé que la carte "Fiche - Dérivées" figée sur /fiches : un mockup plausible,
// remplacé dès que la sélection courante renvoie un classement réel (voir son usage
// plus bas, qui préfère toujours `themesData.themes` quand il est disponible).
const CLASSEMENT_ILLUSTRATIF: ThemeIllustratif[] = [
  { id: -1, tag: "Suites numériques", frequence_pct: 68 },
  { id: -2, tag: "Probabilités", frequence_pct: 55 },
  { id: -3, tag: "Trigonométrie", frequence_pct: 47 },
]

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
              "flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-bold tabular-nums",
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

/**
 * Page autonome du classement des thèmes fréquents - contrepartie de l'aperçu tronqué
 * embarqué sur /epreuves (voir ThemesFrequents.tsx, variant="preview" -> lien "Voir le
 * classement complet"). Utilisable seule : ses propres filtres matière/cursus vivent
 * en query params, pas hérités d'une autre page.
 */
export function ThemesFrequentsPage() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label

  const [searchParams, setSearchParams] = useSearchParams()
  const subjectFilter = searchParams.get("subject") ?? ""
  const cursusFilter = searchParams.get("cursus") ?? ""

  useSeo({
    title: "Les thèmes qui reviennent le plus",
    description: countryLabel
      ? `${countryLabel} : le classement des thèmes les plus fréquents aux épreuves officielles, matière par matière et cursus par cursus.`
      : undefined,
  })

  const { data: subjects = [] } = useQuery({
    queryKey: ["subjects", country],
    queryFn: ({ signal }) => listSubjects(country, signal),
  })
  const subjectsTries = [...subjects].sort((a, b) => a.label.localeCompare(b.label, "fr"))

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })

  const cursusId = cursusFilter ? Number(cursusFilter) : undefined

  // Même clé de cache que la requête interne à <ThemesFrequents> : un seul appel
  // réseau, cette requête ne sert qu'à distinguer "corpus trop mince" (disponible:
  // false) d'un simple chargement, pour ne pas laisser la page vide sans explication -
  // <ThemesFrequents> se contente de disparaître silencieusement, ce qui convient à un
  // aperçu embarqué mais pas à une page qui n'affiche que ça.
  const { data: themesData } = useQuery({
    queryKey: ["themes-frequents", cursusId, subjectFilter],
    queryFn: ({ signal }) => getThemesFrequents(cursusId!, subjectFilter, signal),
    enabled: Boolean(cursusId && subjectFilter),
  })

  function updateFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    setSearchParams(next, { replace: true })
  }

  const filtresComplets = Boolean(country && subjectFilter && cursusId)
  const topTheme = themesData?.disponible ? themesData.themes[0] : undefined

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      <div className="relative mb-8 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6 sm:p-8 lg:p-12">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center lg:gap-16">
          <div>
            <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <TrendingUp className="size-5" />
            </div>
            <Eyebrow>Statistiques{countryLabel ? ` - ${countryLabel}` : ""}</Eyebrow>
            <h1 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">
              Les thèmes qui <span className="text-primary">reviennent le plus</span>
            </h1>
            <p className="mt-3 max-w-md text-lg font-medium leading-snug text-foreground/90">
              Sache exactement quoi réviser en priorité.
            </p>
            <p className="mt-2 max-w-md text-muted-foreground">
              Choisis une matière et un cursus : on analyse toutes les épreuves officielles déjà en base pour
              repérer les thèmes qui tombent le plus souvent.
            </p>

            <div className="mt-5 flex flex-wrap gap-2">
              {themesData?.disponible ? (
                <>
                  <StatChip icon={<TrendingUp className="size-3.5 text-primary" />}>
                    <span className="font-medium tabular-nums">{themesData.nb_sessions_disponibles}</span>
                    <span className="text-muted-foreground">sessions officielles analysées</span>
                  </StatChip>
                  {topTheme && (
                    <StatChip icon={<Crown className="size-3.5 text-gold" />}>
                      <span className="text-muted-foreground">Thème n°1 :</span>
                      <span className="max-w-[9rem] truncate font-medium">{capitaliserTheme(topTheme.tag)}</span>
                    </StatChip>
                  )}
                </>
              ) : (
                <StatChip icon={<TrendingUp className="size-3.5 text-primary" />}>
                  <span className="text-muted-foreground">Jusqu'à</span>
                  <span className="font-medium">20 thèmes</span>
                  <span className="text-muted-foreground">classés par matière</span>
                </StatChip>
              )}
            </div>
          </div>

          {/* Accessoire décoratif adossé aux vraies données dès qu'une sélection en
              renvoie (voir MiniClassement) - même procédé que l'anneau de maîtrise de
              /quiz, en mockup plausible tant qu'aucune sélection n'est faite. */}
          <div aria-hidden className="relative mx-auto w-full max-w-[18rem] select-none lg:mx-0 lg:justify-self-end">
            <span className="absolute -top-3 right-6 z-10 -rotate-2 rounded-md bg-gold px-3 py-1 text-[0.65rem] font-bold uppercase tracking-wider text-gold-foreground shadow-md">
              Classement en direct
            </span>
            <div className="rotate-2 rounded-lg border border-border bg-card p-6 shadow-xl transition-transform duration-300 hover:rotate-0">
              <MiniClassement themes={themesData?.disponible ? themesData.themes : []} />
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-3xl">
        <Card className="mb-6">
          <CardHeader className="pb-4">
            <CardTitle className="font-display text-lg">Choisir la sélection</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="flex flex-col gap-1.5">
                <label
                  htmlFor="themes-matiere"
                  className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                >
                  Matière
                </label>
                <Select
                  value={subjectFilter || "none"}
                  onValueChange={(v) => updateFilter("subject", v === "none" ? "" : v)}
                >
                  <SelectTrigger id="themes-matiere">
                    <SelectValue placeholder="Choisir une matière" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Choisir une matière</SelectItem>
                    {subjectsTries.map((subject) => (
                      <SelectItem key={subject.id} value={subject.code}>
                        {subject.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label
                  htmlFor="themes-cursus"
                  className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
                >
                  Cursus
                </label>
                <Select
                  value={cursusFilter || "none"}
                  onValueChange={(v) => updateFilter("cursus", v === "none" ? "" : v)}
                >
                  <SelectTrigger id="themes-cursus">
                    <SelectValue placeholder="Choisir un cursus" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Choisir un cursus</SelectItem>
                    {cursusList.map((c) => (
                      <SelectItem key={c.id} value={String(c.id)}>
                        {c.examen_display}
                        {c.series ? ` - Série ${c.series.code}` : ""}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {!filtresComplets ? (
          <Card className="overflow-hidden border-primary/25 bg-gradient-to-br from-primary/5 via-transparent to-transparent">
            <CardContent className="flex flex-col items-start gap-4 pt-6">
              <span className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
                <TrendingUp className="size-5" />
              </span>
              <div>
                <p className="font-display text-base font-semibold">Comment marche le classement</p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Choisis ta matière et ton cursus ci-dessus pour découvrir quels thèmes tombent le plus souvent.
                </p>
              </div>
              <EtapesPresentation
                etapes={[
                  "Tu choisis ta matière et ton cursus.",
                  "On analyse toutes les épreuves officielles déjà en base.",
                  "Tu vois exactement quels thèmes réviser en priorité.",
                ]}
              />
            </CardContent>
          </Card>
        ) : themesData && !themesData.disponible ? (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center gap-3 py-16 text-center">
              <span className="flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
                <TrendingUp className="size-5" />
              </span>
              <p className="text-muted-foreground">
                Pas encore assez d'épreuves officielles en base pour cette matière et ce cursus (
                {themesData.nb_sessions_disponibles}/{themesData.seuil_minimum} sessions requises).
              </p>
            </CardContent>
          </Card>
        ) : (
          country && (
            <ThemesFrequents
              country={country}
              cursusId={cursusId!}
              subjectCode={subjectFilter}
              variant="full"
            />
          )
        )}
      </div>
    </div>
  )
}
