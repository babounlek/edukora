import { useState, type ReactNode } from "react"
import { Link, useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowLeft, ArrowRight, Check, Crown, FileText, Lock, TrendingUp } from "lucide-react"

import { getThemeExercices, getThemesFrequents, listCursus } from "@/api/endpoints"
import type { Cursus, ThemeExercice } from "@/api/types"
import { useSeo } from "@/lib/seo"
import { themeExerciceLecturePath, themesFrequentsPath } from "@/lib/countryPath"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { subjectShortLabel } from "@/lib/subjectLabel"
import { AnneauFrequence } from "@/components/AnneauFrequence"
import { StatChip } from "@/components/Configurateur"
import { FiltreLigne, PastilleFiltre } from "@/components/FiltresCatalogue"
import { ReviserTabs } from "@/components/ReviserTabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { capitaliserTheme, cn } from "@/lib/utils"

type FiltreOrigine = "tous" | "officiels" | "autres"

const ORIGINES: Record<string, { libelle: string; classe: string }> = {
  OFFICIEL: { libelle: "Sujet officiel", classe: "border-gold/40 bg-gold/10 text-gold-text" },
  BLANC: { libelle: "Examen blanc", classe: "border-border bg-muted text-muted-foreground" },
  ETABLISSEMENT: { libelle: "Établissement", classe: "border-border bg-muted text-muted-foreground" },
  SUJET_ZERO: { libelle: "Sujet zéro", classe: "border-primary/30 bg-primary/10 text-primary" },
  INEDITE: { libelle: "Inédite", classe: "border-primary/30 bg-primary/10 text-primary" },
  AUTRE: { libelle: "Autre", classe: "border-border bg-muted text-muted-foreground" },
}

function libelleCursus(c: Pick<Cursus, "examen_display" | "series">) {
  return `${c.examen_display}${c.series ? ` ${c.series.code}` : ""}`
}

/**
 * Contrepartie du bouton "Exercices" sur ThemesFrequents/ThemesFrequentsPage : liste
 * précisément les exercices qui traitent ce thème (pas toute l'épreuve qui les
 * contient) - chacun renvoie directement au bon passage du corrigé (ancre partagée
 * avec EpreuveReaderPage/EpreuveDetailPage, voir exerciceAnchorId) plutôt que de
 * laisser l'élève rechercher lui-même dans un corrigé entier.
 */
export function ThemeExercicesPage() {
  const { country = "", tagId } = useParams<{ country: string; tagId: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const subjectCode = searchParams.get("subject") ?? ""
  const cursusId = searchParams.get("cursus") ?? ""
  const [filtreOrigine, setFiltreOrigine] = useState<FiltreOrigine>("tous")

  const { data, isLoading } = useQuery({
    queryKey: ["theme-exercices", cursusId, tagId, subjectCode],
    queryFn: ({ signal }) => getThemeExercices(Number(cursusId), Number(tagId), subjectCode, signal),
    enabled: Boolean(cursusId && tagId && subjectCode),
    // Garde la liste précédente pendant un changement d'examen ou de matière : les
    // pastilles de sélection ne clignotent pas, seule la liste se met à jour.
    placeholderData: (precedent) => precedent,
  })

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })

  // Fréquence du thème pour la sélection COURANTE, lue dans le classement (même clé de
  // cache que ThemesFrequentsPage : aucun appel de plus en venant de là). Les params
  // pct/nb/total du lien ne servent que de repli : ils décrivent la sélection d'origine
  // et sont retirés dès que l'élève en change (voir changerSelection).
  const { data: classement } = useQuery({
    queryKey: ["themes-frequents", Number(cursusId), subjectCode],
    queryFn: ({ signal }) => getThemesFrequents(Number(cursusId), subjectCode, signal),
    enabled: Boolean(cursusId && subjectCode),
  })
  const themeClasse = classement?.disponible
    ? classement.themes.find((t) => t.id === Number(tagId))
    : undefined
  const rang = themeClasse && classement ? classement.themes.indexOf(themeClasse) + 1 : undefined
  const frequence = themeClasse
    ? { pct: themeClasse.frequence_pct, nb: themeClasse.nb_epreuves, total: classement!.nb_sessions_disponibles }
    : searchParams.get("pct")
      ? {
          pct: Number(searchParams.get("pct")),
          nb: Number(searchParams.get("nb")) || undefined,
          total: Number(searchParams.get("total")) || undefined,
        }
      : undefined

  useSeo({
    title: data ? `Exercices sur « ${capitaliserTheme(data.tag)} »` : "Exercices par thème",
    description: data ? `Tous les exercices corrigés qui traitent "${capitaliserTheme(data.tag)}".` : undefined,
  })

  function changerSelection(cursus: string, subject: string) {
    setSearchParams({ cursus, subject }, { replace: true })
    setFiltreOrigine("tous")
  }

  // Examens et matières où ce thème est réellement traité - jamais une combinaison vide.
  const contextes = data?.contextes ?? []
  const parCursus = new Map<number, number>()
  for (const c of contextes) parCursus.set(c.cursus_id, (parCursus.get(c.cursus_id) ?? 0) + c.nb_exercices)
  const examens = cursusList
    .filter((c) => parCursus.has(c.id))
    .sort(
      (x, y) =>
        x.examen_display.localeCompare(y.examen_display, "fr") ||
        (x.series?.code ?? "").localeCompare(y.series?.code ?? "", "fr"),
    )
  const matieres = contextes.filter((c) => String(c.cursus_id) === cursusId)
  const cursusCourant = cursusList.find((c) => String(c.id) === cursusId)
  const matiereCourante = contextes.find((c) => c.subject_code === subjectCode)
  const MatiereIcon = subjectIcon(subjectCode)

  const exercices = data?.exercices ?? []
  const nbOfficiels = exercices.filter((e) => e.origine === "OFFICIEL").length
  const nbAutres = exercices.length - nbOfficiels
  const exercicesFiltres = exercices.filter((e) =>
    filtreOrigine === "tous" ? true : filtreOrigine === "officiels" ? e.origine === "OFFICIEL" : e.origine !== "OFFICIEL",
  )
  const nbVerrouilles = exercices.filter((e) => !e.has_access).length
  // Chaque exercice s'ouvre SEUL (ThemeExerciceLecturePage), jamais au milieu de
  // l'épreuve entière : la sélection voyage pour que la page suive la même file.
  const lienLecture = (e: ThemeExercice) =>
    `${themeExerciceLecturePath(country, tagId ?? "", e.exercise_id)}?subject=${subjectCode}&cursus=${cursusId}`

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <ReviserTabs />

      <Link
        to={`${themesFrequentsPath(country)}?subject=${subjectCode}&cursus=${cursusId}`}
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-3.5" />
        Retour au classement
      </Link>

      {/* Hero : même gabarit que /epreuves et /themes-frequents, avec la fréquence du
          thème en anneau - la raison de s'entraîner dessus, avant la liste. */}
      <div className="relative mb-6 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.09] via-primary/[0.03] to-gold/[0.06] p-5 sm:p-8">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <p className="mb-2 font-display text-sm italic text-primary">
              Exercices par thème
              {matiereCourante ? ` · ${matiereCourante.subject_label}` : ""}
              {cursusCourant ? ` · ${libelleCursus(cursusCourant)}` : ""}
            </p>
            <h1 className="font-display text-2xl font-semibold leading-[1.15] tracking-tight text-balance sm:text-4xl">
              {data ? capitaliserTheme(data.tag) : <Skeleton className="h-10 w-72" />}
            </h1>
            <p className="mt-2 max-w-xl text-muted-foreground">
              Tous les exercices corrigés qui traitent ce thème. Chacun t'emmène directement au bon passage du
              corrigé.
            </p>

            <div className="mt-4 flex flex-wrap gap-2 sm:mt-5">
              {data && (
                <StatChip icon={<FileText className="size-3.5 text-primary" />}>
                  <span className="font-medium tabular-nums">{data.total}</span>
                  <span className="text-muted-foreground">exercice{data.total > 1 ? "s" : ""} corrigé{data.total > 1 ? "s" : ""}</span>
                </StatChip>
              )}
              {rang && (
                <StatChip icon={<Crown className="size-3.5 text-gold-text" />}>
                  <span className="font-medium">N°{rang}</span>
                  <span className="text-muted-foreground">du classement</span>
                </StatChip>
              )}
            </div>
          </div>

          {frequence && (
            <div className="flex shrink-0 items-center gap-4 rounded-2xl border border-gold/30 bg-card/80 p-4 shadow-sm sm:flex-col sm:gap-2 sm:px-6 sm:text-center">
              <AnneauFrequence pct={frequence.pct} dore grand />
              <div>
                <p className="text-sm font-medium">des sessions officielles</p>
                {frequence.nb && frequence.total && (
                  <p className="text-xs tabular-nums text-muted-foreground">
                    {frequence.nb} sur {frequence.total}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sélection : mêmes pastilles que /epreuves et /themes-frequents, limitées aux
          examens et matières où ce thème est réellement traité. */}
      {examens.length > 1 || matieres.length > 1 ? (
        <div className="mb-6 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:p-6">
          <p className="font-display text-lg font-semibold">Ton examen, ta matière</p>
          <p className="text-sm text-muted-foreground">Ce thème est aussi traité ailleurs : change de sélection.</p>
          <FiltreLigne titre="Examen">
            {examens.map((c) => {
              const actif = String(c.id) === cursusId
              // Garde la matière en cours si elle existe dans cet examen, sinon la plus fournie.
              const matiere =
                contextes.find((x) => x.cursus_id === c.id && x.subject_code === subjectCode) ??
                contextes.find((x) => x.cursus_id === c.id)!
              return (
                <PastilleFiltre key={c.id} actif={actif} onClick={() => changerSelection(String(c.id), matiere.subject_code)}>
                  {libelleCursus(c)}
                  <CompteurPastille actif={actif}>{parCursus.get(c.id)}</CompteurPastille>
                </PastilleFiltre>
              )
            })}
          </FiltreLigne>
          <FiltreLigne titre="Matière">
            {matieres.map((m) => {
              const Icon = subjectIcon(m.subject_code)
              const actif = m.subject_code === subjectCode
              return (
                <PastilleFiltre key={m.subject_code} actif={actif} onClick={() => changerSelection(cursusId, m.subject_code)}>
                  <span className={cn("flex size-5 items-center justify-center rounded-full", couleurMatiere(m.subject_code).puce)}>
                    <Icon className="size-3" aria-hidden="true" />
                  </span>
                  {subjectShortLabel(m.subject_code, m.subject_label)}
                  <CompteurPastille actif={actif}>{m.nb_exercices}</CompteurPastille>
                </PastilleFiltre>
              )
            })}
          </FiltreLigne>
        </div>
      ) : null}

      {isLoading ? (
        <div className="flex flex-col gap-3">
          <Skeleton className="h-24 w-full rounded-2xl" />
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-xl" />
          ))}
        </div>
      ) : !data || data.exercices.length === 0 ? (
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border px-6 py-14 text-center">
          <span className="flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
            <FileText className="size-5" />
          </span>
          <p className="text-muted-foreground">Aucun exercice trouvé pour ce thème dans cette sélection.</p>
        </div>
      ) : (
        <>
          <AvancementFile exercices={data.exercices} faits={data.faits} total={data.total} lien={lienLecture} />

          {nbVerrouilles > 0 && (
            <div className="mb-6 flex flex-col gap-3 rounded-2xl border border-gold/40 bg-gradient-to-br from-gold/[0.10] via-gold/[0.03] to-transparent p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
              <div className="flex items-start gap-3">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-gold text-gold-foreground shadow-sm">
                  <Crown className="size-5" />
                </span>
                <div>
                  <p className="font-display text-base font-semibold">
                    {nbVerrouilles === data.total
                      ? `Les ${data.total} corrigés de ce thème t'attendent`
                      : `${nbVerrouilles} corrigé${nbVerrouilles > 1 ? "s" : ""} sur ${data.total} réservé${nbVerrouilles > 1 ? "s" : ""} aux abonnés`}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Débloque-les tous avec Jusqu'à l'Examen, et suis ta progression exercice par exercice.
                  </p>
                </div>
              </div>
              <Button asChild className="shrink-0">
                <Link to={`/abonnement?cursus=${cursusId}`}>
                  Débloquer
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
            </div>
          )}

          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <h2 className="flex items-center gap-2.5 font-display text-xl font-semibold">
              <span className={cn("flex size-8 items-center justify-center rounded-lg", couleurMatiere(subjectCode).puce)}>
                <MatiereIcon className="size-4" aria-hidden="true" />
              </span>
              Les exercices
            </h2>
            {nbOfficiels > 0 && nbAutres > 0 && (
              <div role="group" aria-label="Filtrer par origine" className="flex flex-wrap gap-1.5">
                <PastilleFiltre actif={filtreOrigine === "tous"} onClick={() => setFiltreOrigine("tous")}>
                  Tous
                  <CompteurPastille actif={filtreOrigine === "tous"}>{exercices.length}</CompteurPastille>
                </PastilleFiltre>
                <PastilleFiltre actif={filtreOrigine === "officiels"} onClick={() => setFiltreOrigine("officiels")}>
                  Sujets officiels
                  <CompteurPastille actif={filtreOrigine === "officiels"}>{nbOfficiels}</CompteurPastille>
                </PastilleFiltre>
                <PastilleFiltre actif={filtreOrigine === "autres"} onClick={() => setFiltreOrigine("autres")}>
                  Blancs et autres
                  <CompteurPastille actif={filtreOrigine === "autres"}>{nbAutres}</CompteurPastille>
                </PastilleFiltre>
              </div>
            )}
          </div>

          <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
            {exercicesFiltres.map((exercice) => (
              <LigneExercice key={exercice.exercise_id} exercice={exercice} lien={lienLecture(exercice)} />
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

function CompteurPastille({ actif, children }: { actif: boolean; children: ReactNode }) {
  return (
    <span
      className={cn(
        "rounded-full px-1.5 text-[0.7rem] font-semibold tabular-nums",
        actif ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground",
      )}
    >
      {children}
    </span>
  )
}

function LigneExercice({ exercice, lien }: { exercice: ThemeExercice; lien: string }) {
  const origine = ORIGINES[exercice.origine] ?? ORIGINES.AUTRE
  return (
    <li
      className={cn(
        "flex items-center gap-3 px-4 py-3.5 transition-colors sm:gap-4 sm:px-5",
        // Un exercice fait s'efface sans disparaître : il reste consultable, mais ne
        // dispute plus l'attention à ceux qui restent.
        exercice.fait ? "bg-muted/30" : "hover:bg-accent/40",
      )}
    >
      <EtatFait exercice={exercice} />
      <span className="hidden w-14 shrink-0 font-display text-lg font-semibold tabular-nums text-foreground/80 sm:block">
        {exercice.lesson_year ?? "-"}
      </span>
      <div className="min-w-0 flex-1">
        <p className={cn("line-clamp-2 font-medium leading-snug sm:line-clamp-1", exercice.fait && "text-muted-foreground")}>{exercice.lesson_title}</p>
        <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
          <span>Exercice {exercice.numero_exercice}</span>
          {exercice.lesson_year && <span className="sm:hidden">· {exercice.lesson_year}</span>}
          <span className={cn("rounded-full border px-2 py-0.5 text-[0.7rem] font-medium", origine.classe)}>
            {origine.libelle}
          </span>
        </div>
      </div>
      <Button asChild size="sm" variant={exercice.has_access ? "default" : "outline"} className="shrink-0">
        <Link to={lien}>
          {exercice.has_access ? (
            <>
              {exercice.fait ? "Revoir" : "Lire"}
              <ArrowRight className="size-3.5" />
            </>
          ) : (
            <>
              <Lock className="size-3.5" />
              Aperçu
            </>
          )}
        </Link>
      </Button>
    </li>
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
  exercices, faits, total, lien,
}: {
  exercices: ThemeExercice[]
  faits: number
  total: number
  lien: (e: ThemeExercice) => string
}) {
  const suivant = exercices.find((e) => !e.fait && e.has_access)
  const termine = total > 0 && faits >= total
  const pctFait = total > 0 ? Math.round((faits / total) * 100) : 0

  return (
    <div className="mb-6 rounded-2xl border border-border bg-card p-4 shadow-lg shadow-primary/5 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-4">
          <span
            className={cn(
              "flex size-12 shrink-0 items-center justify-center rounded-2xl",
              termine ? "bg-primary text-primary-foreground" : "bg-primary/10 text-primary",
            )}
          >
            {termine ? <Check className="size-6" /> : <TrendingUp className="size-5" />}
          </span>
          <div className="min-w-0">
            <p className="font-display text-lg font-semibold">
              {termine ? "Thème bouclé" : (
                <>
                  <span className="tabular-nums">{faits}</span> exercice{faits > 1 ? "s" : ""} traité{faits > 1 ? "s" : ""} sur{" "}
                  <span className="tabular-nums">{total}</span>
                </>
              )}
            </p>
            <p className="mt-0.5 text-sm text-muted-foreground">
              {termine
                ? "Tu as traité tous les exercices de ce thème. Il reviendra en révision au bon moment."
                : "Chaque exercice se valide à la fin de son corrigé, une fois que tu l'as lu."}
            </p>
          </div>
        </div>
        {suivant && (
          <Button asChild size="lg" className="shrink-0">
            <Link to={lien(suivant)}>
              {faits > 0 ? "Continuer" : "Commencer"}
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        )}
      </div>
      {/* Barre pleine largeur plutôt qu'un pourcentage : sur 33 exercices, "12 %" ne
          dit rien, une barre qui avance se lit d'un coup d'œil. */}
      <div className="mt-4 h-2 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-gradient-to-r from-primary to-primary/70 transition-all duration-500"
          style={{ width: `${pctFait}%` }}
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
 * L'état d'une ligne - un INDICATEUR, jamais un contrôle.
 *
 * C'était une case à cocher : on pouvait donc valider treize exercices sans en avoir
 * ouvert un seul, et le compteur sur lequel l'élève juge son avancement ne mesurait
 * plus rien. La validation a été déplacée à la fin du corrigé, dans le lecteur (voir
 * ValiderResolution) - le seul endroit où il a de quoi répondre à "tu l'as traité ?".
 *
 * Volontairement pas un bouton : rien à cliquer ici, donc rien qui laisse croire
 * qu'on peut cocher depuis la liste. Pour revenir sur une validation, on rouvre
 * l'exercice - là où on voit ce qu'on annule. Un exercice verrouillé montre un cadenas
 * dans la même colonne, pour que toutes les lignes restent alignées.
 */
function EtatFait({ exercice }: { exercice: ThemeExercice }) {
  if (!exercice.has_access) {
    return (
      <span
        role="img"
        aria-label="Réservé aux abonnés"
        title="Réservé aux abonnés"
        className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground"
      >
        <Lock className="size-3.5" />
      </span>
    )
  }
  return (
    <span
      role="img"
      aria-label={exercice.fait ? "Exercice validé" : "Exercice pas encore traité"}
      title={exercice.fait ? "Validé" : "Pas encore traité"}
      className={cn(
        "flex size-8 shrink-0 items-center justify-center rounded-full border",
        exercice.fait
          ? "border-primary bg-primary text-primary-foreground"
          : "border-dashed border-primary/40 text-transparent",
      )}
    >
      <Check className="size-4" />
    </span>
  )
}
