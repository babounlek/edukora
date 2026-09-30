import { useEffect, useState, type ReactNode } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCheck,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Crown,
  Eye,
  EyeOff,
  Lightbulb,
  Lock,
  PartyPopper,
  Target,
} from "lucide-react"

import { getExerciceLecture, getThemeExercices, marquerExerciceFait } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ExerciceLecture, QuestionLecture, ThemeExercice } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useSeo } from "@/lib/seo"
import {
  epreuveDetailPath,
  epreuveReaderPath,
  themeExerciceLecturePath,
  themeExercicesPath,
} from "@/lib/countryPath"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { capitaliserTheme, cn } from "@/lib/utils"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { exerciceAnchorId } from "@/components/EpreuveSommaire"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

const ORIGINES: Record<string, string> = {
  OFFICIEL: "Sujet officiel",
  BLANC: "Examen blanc",
  ETABLISSEMENT: "Établissement",
  SUJET_ZERO: "Sujet zéro",
  INEDITE: "Inédite",
  AUTRE: "Autre",
}

// Préférence "Essaie d'abord" mémorisée d'une visite à l'autre - simple confort
// d'affichage, jamais une donnée à garantir : tout accès au stockage est protégé.
const CLE_ESSAI = "edukora_exercice_essai_dabord"

function lireEssai(): boolean {
  try {
    return window.localStorage.getItem(CLE_ESSAI) !== "0"
  } catch {
    return true
  }
}

function ecrireEssai(valeur: boolean) {
  try {
    window.localStorage.setItem(CLE_ESSAI, valeur ? "1" : "0")
  } catch {
    // stockage indisponible (navigation privée...) : la préférence vaut pour la visite
  }
}

const PROSE = "prose prose-neutral max-w-none text-justify dark:prose-invert prose-headings:font-display"

/**
 * Un exercice lu SEUL, depuis la liste d'un thème (ThemeExercicesPage).
 *
 * "Lire" ouvrait jusque-là l'épreuve entière : l'élève atterrissait au milieu
 * d'exercices sans rapport avec ce qu'il révisait, et "Exercice suivant" le sortait du
 * thème. Ici, tout est centré sur le thème :
 * - les questions qui portent le thème sont surlignées (donnée exacte, par question,
 *   voir ThemeExerciceLectureView) - dans un exercice de cinq questions, souvent deux
 *   seulement concernent ce qu'on révise ;
 * - "Essaie d'abord" replie chaque corrigé derrière un bouton, question par question,
 *   pour chercher avant de lire - désactivable, et mémorisé ;
 * - la navigation suit la file du thème (précédent/suivant), jamais l'épreuve.
 */
export function ThemeExerciceLecturePage() {
  const { country = "", tagId = "", exerciseId = "" } = useParams<{
    country: string
    tagId: string
    exerciseId: string
  }>()
  const [searchParams] = useSearchParams()
  const subjectCode = searchParams.get("subject") ?? ""
  const cursusId = searchParams.get("cursus") ?? ""
  const contexte = cursusId && subjectCode ? `?subject=${subjectCode}&cursus=${cursusId}` : ""

  const { data, isLoading, isError } = useQuery({
    queryKey: ["exercice-lecture", tagId, exerciseId],
    queryFn: ({ signal }) => getExerciceLecture(Number(tagId), Number(exerciseId), signal),
    // Un exercice introuvable ne le sera pas davantage au 3e essai : réponse immédiate.
    retry: (essais, erreur) => !(erreur instanceof ApiError && erreur.status === 404) && essais < 2,
  })

  // La file du thème : même clé de cache que ThemeExercicesPage, donc déjà là en
  // arrivant depuis la liste.
  const { data: file } = useQuery({
    queryKey: ["theme-exercices", cursusId, tagId, subjectCode],
    queryFn: ({ signal }) => getThemeExercices(Number(cursusId), Number(tagId), subjectCode, signal),
    enabled: Boolean(cursusId && tagId && subjectCode),
  })

  useSeo({
    title: data
      ? `${data.exercise.titre || `Exercice ${data.exercise.numero_exercice}`} - ${capitaliserTheme(data.theme.name)}`
      : "Exercice",
  })

  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [exerciseId])

  const exercices = file?.exercices ?? []
  const index = exercices.findIndex((e) => e.exercise_id === Number(exerciseId))
  const precedent = index > 0 ? exercices[index - 1] : undefined
  const suivantDansListe = index >= 0 ? exercices[index + 1] : undefined
  // "Suivant" vise d'abord le prochain exercice à faire et accessible - comme
  // "Continuer" sur la liste - et retombe sur le suivant tout court.
  const suivantAFaire = index >= 0 ? exercices.slice(index + 1).find((e) => !e.fait && e.has_access) : undefined
  const suivant = suivantAFaire ?? suivantDansListe

  const lien = (e: ThemeExercice) => `${themeExerciceLecturePath(country, tagId, e.exercise_id)}${contexte}`
  const retourListe = `${themeExercicesPath(country, Number(tagId))}${contexte}`

  if (isError) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-16 text-center sm:px-6">
        <p className="text-muted-foreground">Cet exercice est introuvable.</p>
        <Link to={retourListe} className="mt-3 inline-block text-sm text-primary hover:underline">
          Retour aux exercices du thème
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 pb-28 pt-6 sm:px-6 sm:pb-12 sm:pt-10">
      {/* Barre de file : retour au thème, position, précédent/suivant. */}
      <div className="mb-5 flex items-center justify-between gap-3">
        <Link
          to={retourListe}
          className="inline-flex min-w-0 items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
        >
          <ArrowLeft className="size-3.5 shrink-0" />
          <span className="truncate">{data ? capitaliserTheme(data.theme.name) : "Exercices du thème"}</span>
        </Link>
        {index >= 0 && (
          <div className="flex shrink-0 items-center gap-1.5">
            <span className="mr-1 text-sm tabular-nums text-muted-foreground">
              <span className="font-medium text-foreground">{index + 1}</span> / {exercices.length}
            </span>
            <BoutonFile to={precedent && lien(precedent)} label="Exercice précédent">
              <ChevronLeft className="size-4" />
            </BoutonFile>
            <BoutonFile to={suivantDansListe && lien(suivantDansListe)} label="Exercice suivant">
              <ChevronRight className="size-4" />
            </BoutonFile>
          </div>
        )}
      </div>

      {isLoading || !data ? (
        <div className="flex flex-col gap-4">
          <Skeleton className="h-40 w-full rounded-3xl" />
          <Skeleton className="h-16 w-full rounded-2xl" />
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-32 w-full rounded-2xl" />
          ))}
        </div>
      ) : (
        <Lecture
          key={exerciseId}
          data={data}
          country={country}
          suivant={suivant}
          lienSuivant={suivant && lien(suivant)}
          retourListe={retourListe}
          cursusId={cursusId}
          dernier={index >= 0 && !suivantDansListe}
        />
      )}

      {/* Sur téléphone, précédent/suivant restent sous le pouce, sans remonter. */}
      {index >= 0 && (
        <div className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-background/95 px-4 py-3 backdrop-blur sm:hidden">
          <div className="flex items-center gap-2">
            {precedent ? (
              <Button asChild variant="outline" size="lg" className="flex-1">
                <Link to={lien(precedent)}>
                  <ChevronLeft className="size-4" />
                  Précédent
                </Link>
              </Button>
            ) : (
              <Button variant="outline" size="lg" disabled className="flex-1">
                <ChevronLeft className="size-4" />
                Précédent
              </Button>
            )}
            <Button asChild size="lg" className="flex-1">
              <Link to={suivant ? lien(suivant) : retourListe}>
                {suivant ? "Suivant" : "Terminer"}
                <ChevronRight className="size-4" />
              </Link>
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

function BoutonFile({ to, label, children }: { to?: string; label: string; children: ReactNode }) {
  const classe =
    "flex size-9 items-center justify-center rounded-full border border-border bg-card text-muted-foreground transition-colors"
  if (!to) {
    return (
      <span aria-hidden className={cn(classe, "opacity-40")}>
        {children}
      </span>
    )
  }
  return (
    <Link to={to} aria-label={label} title={label} className={cn(classe, "hover:border-primary/40 hover:text-primary")}>
      {children}
    </Link>
  )
}

interface LectureProps {
  data: ExerciceLecture
  country: string
  suivant?: ThemeExercice
  lienSuivant?: string
  retourListe: string
  cursusId: string
  dernier: boolean
}

function Lecture({ data, country, suivant, lienSuivant, retourListe, cursusId, dernier }: LectureProps) {
  const { exercise, lesson, theme, has_access: acces } = data
  const questions = data.questions ?? []
  const nbSurTheme = questions.filter((q) => q.sur_le_theme).length
  const [essai, setEssai] = useState(lireEssai)
  // Corrigés dépliés en mode "Essaie d'abord" (par numéro de question ; "*" = bloc
  // unique d'un exercice non découpé).
  const [ouverts, setOuverts] = useState<Set<string>>(new Set())
  const MatiereIcon = subjectIcon(lesson.subject_code)

  function basculerEssai(valeur: boolean) {
    setEssai(valeur)
    ecrireEssai(valeur)
    setOuverts(new Set())
  }

  function ouvrir(cle: string) {
    setOuverts((precedents) => new Set(precedents).add(cle))
  }

  const toutOuvert = (data.questions ?? [{ numero: "*" }]).every((q) => ouverts.has(q.numero))
  const lienEpreuve = `${
    acces ? epreuveReaderPath(country, lesson.slug) : epreuveDetailPath(country, lesson.slug)
  }#${exerciceAnchorId(exercise.numero_exercice)}`

  return (
    <>
      {/* En-tête : d'où vient l'exercice, et le lien vers l'épreuve complète pour qui a
          besoin du contexte (un exercice qui s'appuie sur une partie précédente). */}
      <div className="relative mb-5 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <p className="mb-2 flex flex-wrap items-center gap-x-2 gap-y-1 font-display text-sm italic text-primary">
              <span className={cn("flex size-6 items-center justify-center rounded-full not-italic", couleurMatiere(lesson.subject_code).puce)}>
                <MatiereIcon className="size-3.5" aria-hidden="true" />
              </span>
              {lesson.subject_label}
              {lesson.year ? ` · ${lesson.year}` : ""}
              {` · ${ORIGINES[lesson.origine] ?? ORIGINES.AUTRE}`}
            </p>
            <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight sm:text-4xl">
              {exercise.titre || `Exercice ${exercise.numero_exercice}`}
              {exercise.points && (
                <span className="ml-3 inline-block translate-y-[-0.2em] rounded-full bg-card px-2.5 py-0.5 align-middle font-sans text-sm font-medium tabular-nums text-muted-foreground shadow-xs">
                  {exercise.points.replace(/\.0+$/, "")} pts
                </span>
              )}
            </h1>
            <p className="mt-2 text-muted-foreground">{lesson.title}</p>
          </div>
          <Button asChild variant="outline" size="sm" className="shrink-0 self-start bg-card">
            <Link to={lienEpreuve}>
              Voir l'épreuve complète
              <ArrowRight className="size-3.5" />
            </Link>
          </Button>
        </div>
      </div>

      {/* Mode de lecture + repère du thème. */}
      <div className="mb-5 flex flex-col gap-3 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:flex-row sm:items-center sm:justify-between sm:p-5">
        {nbSurTheme > 0 ? (
          <p className="flex items-start gap-2.5 text-sm">
            <span className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-gold/20 text-gold-text">
              <Target className="size-3.5" />
            </span>
            <span>
              <span className="font-medium">
                {nbSurTheme === questions.length
                  ? "Tout l'exercice porte"
                  : `${nbSurTheme} question${nbSurTheme > 1 ? "s" : ""} sur ${questions.length} porte${nbSurTheme > 1 ? "nt" : ""}`}{" "}
                sur « {capitaliserTheme(theme.name)} »
              </span>
              {nbSurTheme < questions.length && (
                <span className="text-muted-foreground"> - surlignée{nbSurTheme > 1 ? "s" : ""} ci-dessous.</span>
              )}
            </span>
          </p>
        ) : (
          <p className="text-sm text-muted-foreground">
            Exercice sur « <span className="font-medium text-foreground">{capitaliserTheme(theme.name)}</span> ».
          </p>
        )}
        {acces && (
          <div role="group" aria-label="Mode de lecture" className="flex shrink-0 rounded-full border border-border bg-muted/50 p-1">
            <ModeBouton actif={essai} onClick={() => basculerEssai(true)}>
              <Lightbulb className="size-3.5" />
              Essaie d'abord
            </ModeBouton>
            <ModeBouton actif={!essai} onClick={() => basculerEssai(false)}>
              <Eye className="size-3.5" />
              Tout afficher
            </ModeBouton>
          </div>
        )}
      </div>

      {lesson.introduction_markdown && (
        <details className="group mb-5 rounded-2xl border border-border bg-card">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3 text-sm font-medium sm:px-5">
            Consignes de l'épreuve
            <ChevronDown className="size-4 text-muted-foreground transition-transform group-open:rotate-180" />
          </summary>
          <div className={cn(PROSE, "border-t border-border px-4 py-4 sm:px-5")}>
            <EpreuveMarkdown markdown={lesson.introduction_markdown} />
          </div>
        </details>
      )}

      {data.enonce_intro_markdown && (
        <div className={cn(PROSE, "mb-5 rounded-2xl border border-border bg-card p-4 sm:p-6")}>
          <EpreuveMarkdown markdown={data.enonce_intro_markdown} />
        </div>
      )}

      {essai && acces && !toutOuvert && (
        <p className="mb-3 flex items-center gap-2 text-sm text-muted-foreground">
          <Lightbulb className="size-4 shrink-0 text-gold-text" />
          Cherche chaque question sur ton brouillon, puis dévoile sa correction.
        </p>
      )}

      <div className="flex flex-col gap-4">
        {data.questions ? (
          data.questions.map((q) => (
            <CarteQuestion
              key={q.numero}
              question={q}
              acces={acces}
              masque={essai && !ouverts.has(q.numero)}
              onOuvrir={() => ouvrir(q.numero)}
              surligner={nbSurTheme > 0 && nbSurTheme < questions.length && q.sur_le_theme}
            />
          ))
        ) : (
          <CarteQuestion
            question={{
              numero: "*",
              enonce_markdown: data.enonce_markdown,
              corrige_markdown: data.corrige_markdown,
              sur_le_theme: false,
            }}
            acces={acces}
            masque={essai && !ouverts.has("*")}
            onOuvrir={() => ouvrir("*")}
            surligner={false}
          />
        )}
      </div>

      {acces ? (
        <FinExercice
          exerciseId={exercise.id}
          faitInitial={exercise.fait}
          suivant={suivant}
          lienSuivant={lienSuivant}
          retourListe={retourListe}
          dernier={dernier}
        />
      ) : (
        <div className="mt-6 flex flex-col gap-3 rounded-2xl border border-gold/40 bg-gradient-to-br from-gold/[0.10] via-gold/[0.03] to-transparent p-5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-3">
            <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-gold text-gold-foreground shadow-sm">
              <Crown className="size-5" />
            </span>
            <div>
              <p className="font-display text-base font-semibold">Le corrigé détaillé de chaque question t'attend</p>
              <p className="text-sm text-muted-foreground">
                Rappels de méthode, pièges à éviter et correction pas à pas : tout est inclus dans Jusqu'à l'Examen.
              </p>
            </div>
          </div>
          <Button asChild className="shrink-0">
            <Link to={`/abonnement${cursusId ? `?cursus=${cursusId}` : ""}`}>
              Débloquer
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      )}
    </>
  )
}

function ModeBouton({ actif, onClick, children }: { actif: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={actif}
      className={cn(
        "inline-flex min-h-8 items-center gap-1.5 rounded-full px-3 text-sm font-medium transition-colors",
        actif ? "bg-card text-primary shadow-sm" : "text-muted-foreground hover:text-foreground",
      )}
    >
      {children}
    </button>
  )
}

function CarteQuestion({
  question, acces, masque, onOuvrir, surligner,
}: {
  question: QuestionLecture
  acces: boolean
  masque: boolean
  onOuvrir: () => void
  surligner: boolean
}) {
  const libelle = question.numero === "*" ? "la correction" : `la correction de la question ${question.numero}`
  return (
    <section
      className={cn(
        "relative overflow-hidden rounded-2xl border p-4 sm:p-6",
        surligner
          ? "border-gold/50 bg-gradient-to-br from-gold/[0.10] via-card to-card shadow-md shadow-gold/10"
          : "border-border bg-card shadow-sm",
      )}
    >
      {surligner && (
        <>
          <span aria-hidden className="absolute inset-y-0 left-0 w-1 bg-gold" />
          <span className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-gold px-2.5 py-0.5 text-xs font-semibold text-gold-foreground">
            <Target className="size-3" />
            Sur ton thème
          </span>
        </>
      )}
      <div className={PROSE}>
        <EpreuveMarkdown markdown={question.enonce_markdown} />
      </div>

      <div className="mt-4 border-t border-dashed border-border pt-4">
        {!acces ? (
          <p className="flex items-center gap-2 text-sm text-muted-foreground">
            <Lock className="size-3.5" />
            Correction réservée aux abonnés
          </p>
        ) : masque ? (
          <button
            type="button"
            onClick={onOuvrir}
            className="group inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/5 px-4 py-2 text-sm font-medium text-primary transition-colors hover:bg-primary/10"
          >
            <EyeOff className="size-4 group-hover:hidden" />
            <Eye className="hidden size-4 group-hover:block" />
            Voir {libelle}
          </button>
        ) : (
          <div className="animate-fade-up">
            <p className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-primary">
              <CheckCheck className="size-3.5" aria-hidden="true" />
              Corrigé
            </p>
            <div className={cn(PROSE, "prose-hr:my-8")}>
              <EpreuveMarkdown markdown={question.corrige_markdown ?? ""} directCoursLinks />
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

/**
 * Validation + suite de la file. La validation reste APRÈS les corrigés, comme dans le
 * lecteur (voir ValiderResolution dans EpreuveReaderPage) : c'est là que l'élève a de
 * quoi juger s'il a résolu l'exercice. Une fois validé, l'exercice suivant du thème
 * devient l'action principale.
 */
function FinExercice({
  exerciseId, faitInitial, suivant, lienSuivant, retourListe, dernier,
}: {
  exerciseId: number
  faitInitial: boolean
  suivant?: ThemeExercice
  lienSuivant?: string
  retourListe: string
  dernier: boolean
}) {
  const { isAuthenticated } = useAuth()
  const queryClient = useQueryClient()
  const [fait, setFait] = useState(faitInitial)
  const [enCours, setEnCours] = useState(false)

  async function basculer() {
    const cible = !fait
    setFait(cible)
    setEnCours(true)
    try {
      await marquerExerciceFait(exerciseId, cible)
      // La liste et sa barre d'avancement doivent refléter la validation au retour.
      queryClient.invalidateQueries({ queryKey: ["theme-exercices"] })
    } catch {
      setFait(!cible)
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className="mt-6 rounded-2xl border border-border bg-card p-5 shadow-lg shadow-primary/5 sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        {isAuthenticated ? (
          fait ? (
            <div className="flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <Check className="size-5" />
              </span>
              <div>
                <p className="font-display text-base font-semibold">Exercice validé</p>
                <button
                  type="button"
                  onClick={basculer}
                  disabled={enCours}
                  className="text-xs text-muted-foreground underline underline-offset-4 hover:text-primary disabled:opacity-60"
                >
                  Annuler
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-sm text-muted-foreground">Tu as traité cet exercice ?</span>
              <Button variant="outline" onClick={basculer} disabled={enCours}>
                <Check className="size-4" />
                Je l'ai fait
              </Button>
            </div>
          )
        ) : (
          <p className="text-sm text-muted-foreground">Connecte-toi pour suivre ta progression sur ce thème.</p>
        )}

        {lienSuivant && suivant ? (
          <Button asChild size="lg" variant={fait ? "default" : "outline"} className="shrink-0">
            <Link to={lienSuivant}>
              Exercice suivant du thème
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        ) : dernier ? (
          <Button asChild size="lg" className="shrink-0">
            <Link to={retourListe}>
              <PartyPopper className="size-4" />
              Fin de la liste : retour au thème
            </Link>
          </Button>
        ) : null}
      </div>
    </div>
  )
}
