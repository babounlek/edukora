import { Link, useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowLeft, ArrowRight, Check, FileText, Lock, TrendingUp } from "lucide-react"

import { getThemeExercices } from "@/api/endpoints"
import type { ThemeExercice } from "@/api/types"
import { useSeo } from "@/lib/seo"
import { epreuveDetailPath, epreuveReaderPath, themesFrequentsPath } from "@/lib/countryPath"
import { exerciceAnchorId } from "@/components/EpreuveSommaire"
import { Eyebrow, StatChip } from "@/components/Configurateur"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { capitaliserTheme, cn } from "@/lib/utils"

/**
 * Contrepartie du bouton "Exercices" sur ThemesFrequents/ThemesFrequentsPage : liste
 * précisément les exercices qui traitent ce thème (pas toute l'épreuve qui les
 * contient) - chacun renvoie directement au bon passage du corrigé (ancre partagée
 * avec EpreuveReaderPage/EpreuveDetailPage, voir exerciceAnchorId) plutôt que de
 * laisser l'élève rechercher lui-même dans un corrigé entier.
 */
export function ThemeExercicesPage() {
  const { country, tagId } = useParams<{ country: string; tagId: string }>()
  const [searchParams] = useSearchParams()
  const subjectCode = searchParams.get("subject") ?? ""
  const cursusId = searchParams.get("cursus") ?? ""
  // Contexte optionnel transmis par le lien "Exercices" de <ThemesFrequents> - jamais
  // requis : un lien direct/partagé sans ces paramètres retombe simplement sur un
  // en-tête sans cette puce, jamais sur une page cassée.
  const pct = searchParams.get("pct")
  const nb = searchParams.get("nb")
  const total = searchParams.get("total")

  const cleListe = ["theme-exercices", cursusId, tagId, subjectCode]
  const { data, isLoading } = useQuery({
    queryKey: cleListe,
    queryFn: ({ signal }) => getThemeExercices(Number(cursusId), Number(tagId), subjectCode, signal),
    enabled: Boolean(cursusId && tagId && subjectCode),
  })


  useSeo({
    title: data ? `Exercices sur « ${capitaliserTheme(data.tag)} »` : "Exercices par thème",
    description: data ? `Tous les exercices corrigés qui traitent "${capitaliserTheme(data.tag)}".` : undefined,
  })

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      <Link
        to={`${themesFrequentsPath(country ?? "")}?subject=${subjectCode}&cursus=${cursusId}`}
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-3.5" />
        Retour au classement
      </Link>

      <div className="relative mb-6 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6 sm:p-8">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative">
          <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <FileText className="size-5" />
          </div>
          <Eyebrow>Exercices par thème</Eyebrow>
          <h1 className="font-display text-2xl font-semibold leading-[1.15] sm:text-3xl">
            {data ? (
              <>
                Exercices sur <span className="text-primary">« {capitaliserTheme(data.tag)} »</span>
              </>
            ) : (
              "Exercices par thème"
            )}
          </h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">
            Tous les exercices de notre base qui traitent ce thème, tous corrigés confondus.
          </p>

          {(pct || (data && data.exercices.length > 0)) && (
            <div className="mt-4 flex flex-wrap gap-2">
              {data && data.exercices.length > 0 && (
                <StatChip icon={<FileText className="size-3.5 text-primary" />}>
                  <span className="font-medium tabular-nums">{data.exercices.length}</span>
                  <span className="text-muted-foreground">
                    exercice{data.exercices.length > 1 ? "s" : ""} trouvé{data.exercices.length > 1 ? "s" : ""}
                  </span>
                </StatChip>
              )}
              {pct && (
                <StatChip icon={<TrendingUp className="size-3.5 text-gold" />}>
                  <span className="font-medium tabular-nums">{pct}%</span>
                  <span className="text-muted-foreground">des sessions officielles{nb && total ? ` (${nb}/${total})` : ""}</span>
                </StatChip>
              )}
            </div>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="grid gap-2.5 sm:grid-cols-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-xl" />
          ))}
        </div>
      ) : !data || data.exercices.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center gap-3 py-14 text-center">
            <span className="flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
              <FileText className="size-5" />
            </span>
            <p className="text-muted-foreground">Aucun exercice trouvé pour ce thème.</p>
          </CardContent>
        </Card>
      ) : (
        <>
          <AvancementFile
            exercices={data.exercices}
            faits={data.faits}
            total={data.total}
            country={country ?? ""}
          />
        <div className="grid gap-2.5 sm:grid-cols-2">
          {data.exercices.map((exercice) => (
            <div
              key={exercice.exercise_id}
              className={cn(
                "flex items-center gap-3 rounded-xl border px-4 py-3 transition-colors",
                // Un exercice fait s'efface sans disparaître : il reste consultable,
                // mais ne dispute plus l'attention à ceux qui restent.
                exercice.fait
                  ? "border-border/60 bg-muted/30"
                  : "border-border hover:border-primary/40 hover:bg-accent/40",
              )}
            >
              <EtatFait exercice={exercice} />
              {!exercice.has_access && (
                <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <FileText className="size-4" />
                </span>
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{exercice.lesson_title}</p>
                <p className="text-xs text-muted-foreground">
                  Exercice {exercice.numero_exercice}
                  {exercice.lesson_year ? ` - ${exercice.lesson_year}` : ""}
                </p>
              </div>
              <Button asChild size="sm" variant={exercice.has_access ? "default" : "outline"} className="shrink-0">
                <Link
                  to={`${
                    exercice.has_access
                      ? epreuveReaderPath(country ?? "", exercice.lesson_slug)
                      : epreuveDetailPath(country ?? "", exercice.lesson_slug)
                  }#${exerciceAnchorId(exercice.numero_exercice)}`}
                >
                  {exercice.has_access ? (
                    exercice.fait ? "Revoir" : "Lire"
                  ) : (
                    <>
                      <Lock className="size-3.5" />
                      Voir
                    </>
                  )}
                </Link>
              </Button>
            </div>
          ))}
        </div>
        </>
      )}
    </div>
  )
}

/**
 * Barre d'avancement et action principale de la file d'entraînement.
 *
 * La page listait 33 exercices sans dire où l'élève en était : sur un thème fréquent,
 * il recommençait au hasard et refaisait les mêmes. Deux ajouts suffisent à en faire
 * une file : savoir combien sont faits, et avoir UN bouton qui ouvre le suivant.
 *
 * "Continuer" vise le premier exercice non fait auquel l'élève a accès - jamais un
 * exercice verrouillé, qui transformerait l'action principale en mur de paiement.
 */
function AvancementFile({
  exercices, faits, total, country,
}: {
  exercices: ThemeExercice[]
  faits: number
  total: number
  country: string
}) {
  const suivant = exercices.find((e) => !e.fait && e.has_access)
  const termine = total > 0 && faits >= total

  return (
    <div className="mb-6 rounded-2xl border border-border bg-card p-4 sm:p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="font-display text-lg font-semibold">
            {termine ? "Thème bouclé" : `${faits} exercice${faits > 1 ? "s" : ""} sur ${total}`}
          </p>
          <p className="mt-0.5 text-sm text-muted-foreground">
            {termine
              ? "Tu as traité tous les exercices de ce thème. Il reviendra en révision au bon moment."
              : "Chaque exercice se valide à la fin de son corrigé, une fois que tu l'as lu."}
          </p>
        </div>
        {suivant && (
          <Button asChild size="lg" className="shrink-0">
            <Link
              to={`${epreuveReaderPath(country, suivant.lesson_slug)}#${exerciceAnchorId(suivant.numero_exercice)}`}
            >
              {faits > 0 ? "Continuer" : "Commencer"}
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        )}
      </div>
      {/* Barre pleine largeur plutôt qu'un pourcentage : sur 33 exercices, "12 %" ne
          dit rien, une barre qui avance se lit d'un coup d'œil. */}
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all duration-500"
          style={{ width: `${total > 0 ? Math.round((faits / total) * 100) : 0}%` }}
          role="progressbar"
          aria-valuenow={faits}
          aria-valuemin={0}
          aria-valuemax={total}
          aria-label="Exercices traités"
        />
      </div>
    </div>
  )
}

/**
 * L'état "fait" d'une ligne - un INDICATEUR, jamais un contrôle.
 *
 * C'était une case à cocher : on pouvait donc valider treize exercices sans en avoir
 * ouvert un seul, et le compteur sur lequel l'élève juge son avancement ne mesurait
 * plus rien. La validation a été déplacée à la fin du corrigé, dans le lecteur (voir
 * ValiderResolution) - le seul endroit où il a de quoi répondre à "tu l'as traité ?".
 *
 * Volontairement pas un bouton : rien à cliquer ici, donc rien qui laisse croire
 * qu'on peut cocher depuis la liste. Pour revenir sur une validation, on rouvre
 * l'exercice - là où on voit ce qu'on annule.
 */
function EtatFait({ exercice }: { exercice: ThemeExercice }) {
  if (!exercice.has_access) return null
  return (
    <span
      role="img"
      aria-label={exercice.fait ? "Exercice validé" : "Exercice pas encore traité"}
      title={exercice.fait ? "Validé" : "Pas encore traité"}
      className={cn(
        "flex size-8 shrink-0 items-center justify-center rounded-full border",
        exercice.fait
          ? "border-primary bg-primary text-primary-foreground"
          : "border-dashed border-border text-transparent",
      )}
    >
      <Check className="size-4" />
    </span>
  )
}
