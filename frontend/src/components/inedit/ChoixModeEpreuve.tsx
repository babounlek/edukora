import { BookOpen, FileText, Info, Timer } from "lucide-react"

import { formatDureeMinutes } from "@/lib/duration"
import { formatPoints } from "@/lib/notation"
import { cn } from "@/lib/utils"
import { mots, type Unite } from "@/lib/vocabulaire"

interface ChoixModeEpreuveProps {
  titre: string
  dureeMinutes: number | null
  // Cette durée n'est pas celle de l'épreuve : déduite des autres sessions de la même annale
  // (voir simulations.cadre.duree_minutes_pour_lesson côté backend), jamais présentée comme sûre.
  dureeEstimee?: boolean
  bareme: number | null
  nbExercices: number
  nbQuestions: number
  unite?: Unite
  papierDisponible: boolean
  // false : le choix s'insère dans une page qui porte déjà le titre et les faits de
  // l'épreuve (la fiche), pas de second h1 ni de répétition de la durée et du barème.
  entete?: boolean
  onExamen: () => void
  onPapier: () => void
  onLibre: () => void
}

function Option({
  icone: Icone, titre, points, onClick, principale,
}: {
  icone: typeof Timer
  titre: string
  points: string[]
  onClick: () => void
  principale?: boolean
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex flex-col items-start gap-2 rounded-2xl border p-4 text-left transition-colors focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
        principale ? "border-primary bg-primary/5 hover:bg-primary/10" : "border-border hover:bg-accent/40",
      )}
    >
      <span className="flex items-center gap-2 font-display text-base font-semibold">
        <Icone className="size-4 shrink-0 text-primary" aria-hidden="true" />
        {titre}
      </span>
      <ul className="flex list-disc flex-col gap-0.5 pl-5 text-sm text-muted-foreground">
        {points.map((point) => (
          <li key={point}>{point}</li>
        ))}
      </ul>
    </button>
  )
}

/**
 * Le briefing : avant de commencer, ce que l'épreuve demande (durée, barème, volume) et trois
 * façons de la passer. Avant, le mode examen se cachait dans un petit bouton de la barre
 * d'actions et l'élève « faisait l'examen » sans jamais le passer en conditions réelles.
 */
export function ChoixModeEpreuve({
  titre, dureeMinutes, dureeEstimee, bareme, nbExercices, nbQuestions, papierDisponible, unite = "question",
  entete = true, onExamen, onPapier, onLibre,
}: ChoixModeEpreuveProps) {
  const m = mots(unite)
  const faits = [
    dureeMinutes ? `${dureeEstimee ? "≈ " : ""}${formatDureeMinutes(dureeMinutes)}` : null,
    bareme ? `${formatPoints(bareme)} points` : null,
    // Pour une annale, les exercices SONT les unités : on ne les compte pas deux fois.
    ...(unite === "exercice"
      ? [mots("exercice").compte(nbExercices)]
      : [`${nbExercices} exercice${nbExercices > 1 ? "s" : ""}`, m.compte(nbQuestions)]),
  ].filter(Boolean)

  return (
    <section
      aria-labelledby="choix-mode"
      className={cn(entete ? "mb-8 rounded-3xl border border-border bg-card p-5 sm:p-6" : "w-full")}
    >
      {entete && (
        <>
          <h1 id="choix-mode" className="font-display text-2xl font-semibold leading-tight">
            {titre}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">{faits.join(" · ")}</p>
          {dureeMinutes && dureeEstimee && (
            <p className="mt-1 flex items-start gap-1.5 text-xs text-muted-foreground">
              <Info className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
              Durée estimée : cette annale n'annonce pas sa durée, {formatDureeMinutes(dureeMinutes)} est celle des autres
              sessions de cette épreuve.
            </p>
          )}
        </>
      )}
      <h2 id={entete ? undefined : "choix-mode"} className={cn("text-sm font-semibold", entete && "mt-5")}>
        Comment veux-tu la passer ?
      </h2>
      <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {dureeMinutes && (
          <Option
            principale
            icone={Timer}
            titre="Conditions réelles"
            onClick={onExamen}
            points={[
              `Chrono de ${formatDureeMinutes(dureeMinutes)}, sans pause`,
              "Corrigé masqué jusqu'à la fin",
              "Copie rendue toute seule à zéro",
            ]}
          />
        )}
        {dureeMinutes && papierDisponible && (
          <Option
            icone={FileText}
            titre="Sur papier"
            onClick={onPapier}
            points={[
              "Tu imprimes le sujet et tu composes à la main",
              "Même chrono, même corrigé masqué",
              `À l'écran : le chrono et ta liste d'${m.pluriel}`,
            ]}
          />
        )}
        <Option
          icone={BookOpen}
          titre="Entraînement libre"
          onClick={onLibre}
          points={["Sans chrono, à ton rythme", "Corrigé accessible à tout moment", "Ta note est marquée « entraînement »"]}
        />
      </div>
    </section>
  )
}
