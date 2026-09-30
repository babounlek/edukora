import { Link } from "react-router-dom"
import { ArrowRight, ChevronRight, Compass, TrendingUp } from "lucide-react"

import type { Accueil, PhaseExamen, ResumeMatiere, Trajectoire } from "@/api/types"
import { phraseTrajectoire } from "@/lib/trajectoire"
import { Button } from "@/components/ui/button"
import { AnneauProgression, BarreSegmentee, Ecrin, LegendeProgression } from "@/components/Progression"
import { themesFrequentsPath } from "@/lib/countryPath"
import { pourcent } from "@/lib/maitrise"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { cn } from "@/lib/utils"

/**
 * "Où j'en suis" : l'anneau pondéré, la trajectoire, et les deux matières où il y a le
 * plus à faire.
 *
 * L'anneau ne compte plus chaque savoir à égalité : il pèse par coefficient et par
 * fréquence à l'examen (voir quiz.services.poids_savoir) - "prêt sur 61 % de ce qui
 * tombe vraiment" est le seul chiffre que l'élève veut. Le compte brut reste dessous
 * pour qu'il puisse le vérifier.
 *
 * La trajectoire (voir quiz.accueil.trajectoire) dit où mène le rythme des trois
 * dernières semaines. Honnête dans les trois cas : sans rythme mesurable elle ne
 * projette rien ; quand ça suffit elle le dit ; quand ça ne suffit pas elle dit
 * calmement ce qui manque, en séances par semaine - jamais "tu es en retard".
 */
export function OuJenSuis({
  accueil, cursusId, country,
}: { accueil: Accueil; cursusId: number; country: string }) {
  const { preparation, trajectoire, resume, phase } = accueil
  if (!preparation) return null

  const matieres = [...resume]
    .filter((m) => m.total > m.sans_contenu)
    // Les matières où il reste le plus à faire d'abord : part maîtrisée croissante, puis
    // volume restant décroissant, puis l'alphabet pour rester stable d'une visite à l'autre.
    .sort(
      (a, b) =>
        partMaitrisee(a) - partMaitrisee(b) || restant(b) - restant(a) || a.subject_label.localeCompare(b.subject_label, "fr"),
    )
    .slice(0, 2)

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6" aria-label="Où j'en suis">
      <Ecrin variante="sobre">
        <div className="flex items-center justify-between gap-4">
          <div className="min-w-0">
            <h2 className="font-display">
              <span className="flex items-center gap-2 font-sans text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                <TrendingUp className="size-3.5" />
                Ta progression
              </span>
              <span className="mt-2 block text-2xl font-semibold leading-tight tracking-tight sm:text-3xl">
                Où j'en suis
              </span>
            </h2>
            <p className="mt-1.5 text-sm text-muted-foreground">
              <span className="font-semibold tabular-nums text-foreground">{pourcent(preparation.ponderee)} %</span> de ce qui
              tombe vraiment à l'examen ·{" "}
              <span className="tabular-nums">{preparation.maitrises}</span> savoir{preparation.maitrises > 1 ? "s" : ""} sur{" "}
              <span className="tabular-nums">{preparation.exploitables}</span>
            </p>
          </div>
          <AnneauProgression part={preparation.ponderee} />
        </div>

        {trajectoire && phase !== "apres" && <BlocTrajectoire trajectoire={trajectoire} phase={phase} country={country} />}

        {matieres.length > 0 && (
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            {matieres.map((matiere) => (
              <BarreMatiere key={matiere.subject_id} matiere={matiere} cursusId={cursusId} />
            ))}
          </div>
        )}
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <LegendeProgression />
          <Button asChild variant="outline" size="sm" className="group rounded-full">
            <Link to="/parcours">
              Voir toute ma progression
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </Button>
        </div>
      </Ecrin>
    </section>
  )
}

/**
 * La phrase et la barre de trajectoire. La barre montre trois choses sans les nommer :
 * ce qui est acquis (plein), ce que le rythme actuel ajouterait d'ici le jour J
 * (clair), et le repère "l'essentiel" (le trait). Même pourcentage que l'anneau.
 */
function BlocTrajectoire({
  trajectoire, phase, country,
}: { trajectoire: Trajectoire; phase: PhaseExamen; country: string }) {
  const actuelle = pourcent(trajectoire.couverture_actuelle)
  const projetee = trajectoire.couverture_projetee === null ? null : pourcent(trajectoire.couverture_projetee)
  const cible = pourcent(trajectoire.cible)
  return (
    <div className="mt-5 rounded-2xl border border-border/70 bg-background/70 p-4">
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
        <Compass className="size-3.5 text-primary" />
        D'ici le jour J
      </p>
      <p className="mt-2 text-sm leading-snug">{phraseTrajectoire(trajectoire, phase)}</p>
      {!trajectoire.atteignable && trajectoire.couverture_projetee !== null && (
        <p className="mt-1 text-sm text-muted-foreground">
          <Link to={themesFrequentsPath(country)} className="underline underline-offset-4 hover:text-primary">
            Les thèmes qui tombent le plus
          </Link>
          , d'abord.
        </p>
      )}
      <div
        className="relative mt-3 h-2.5 overflow-visible rounded-full bg-muted"
        role="img"
        aria-label={
          projetee === null
            ? `${actuelle} % acquis, repère à ${cible} %`
            : `${actuelle} % acquis, ${projetee} % projetés le jour J, repère à ${cible} %`
        }
      >
        {projetee !== null && (
          <div
            className="absolute inset-y-0 left-0 rounded-full bg-primary/30 transition-[width] duration-700"
            style={{ width: `${Math.max(projetee, actuelle)}%` }}
          />
        )}
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-primary transition-[width] duration-700"
          style={{ width: `${actuelle}%` }}
        />
        <div aria-hidden className="absolute -top-1 bottom-[-0.25rem] w-0.5 rounded bg-gold" style={{ left: `${cible}%` }} />
      </div>
      <div className="relative mt-1.5 h-4 text-[0.65rem] text-muted-foreground">
        <span className="absolute left-0">aujourd'hui {actuelle} %</span>
        <span className="absolute -translate-x-1/2 whitespace-nowrap" style={{ left: `${cible}%` }}>
          l'essentiel
        </span>
      </div>
    </div>
  )
}

/** Savoirs qui ont du contenu et qui ne sont pas encore maîtrisés. */
function restant(matiere: ResumeMatiere): number {
  return matiere.total - matiere.sans_contenu - matiere.maitrises
}

/** Part de savoirs maîtrisés, sur les seuls savoirs qui ont du contenu. */
function partMaitrisee(matiere: ResumeMatiere): number {
  const exploitables = matiere.total - matiere.sans_contenu
  return exploitables > 0 ? matiere.maitrises / exploitables : 0
}

/**
 * Une matière : son pourcentage en grand, puis une barre en trois segments -
 * maîtrisé, en révision, à découvrir (voir Progression.BarreSegmentee).
 */
function BarreMatiere({ matiere, cursusId }: { matiere: ResumeMatiere; cursusId: number }) {
  const exploitables = matiere.total - matiere.sans_contenu
  const Icone = subjectIcon(matiere.subject_code)
  return (
    <Link
      // `?cursus=` est requis par ParcoursSubjectPage.
      to={`/parcours/${matiere.subject_id}?cursus=${cursusId}`}
      className="group rounded-2xl border border-border/70 bg-background/70 p-4 transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-md hover:shadow-primary/[0.06]"
    >
      <div className="flex items-center justify-between gap-3">
        <span className="flex min-w-0 items-center gap-2.5">
          <span className={cn("flex size-8 shrink-0 items-center justify-center rounded-lg", couleurMatiere(matiere.subject_code).puce)}>
            <Icone className="size-4" />
          </span>
          <span className="min-w-0 truncate text-sm font-semibold">{matiere.subject_label}</span>
        </span>
        <span className="shrink-0 font-display text-xl font-semibold tabular-nums">
          {pourcent(partMaitrisee(matiere))}
          <span className="ml-px text-xs font-medium text-muted-foreground">%</span>
        </span>
      </div>
      <BarreSegmentee
        className="mt-3"
        maitrises={matiere.maitrises}
        enRevision={matiere.en_revision}
        enCours={matiere.en_cours}
        exploitables={exploitables}
      />
      <div className="mt-2.5 flex items-center justify-between gap-2 text-xs text-muted-foreground">
        <span className="tabular-nums">
          {matiere.maitrises}/{exploitables} maîtrisés
          {matiere.en_revision > 0 && <> · {matiere.en_revision} en révision</>}
        </span>
        <ChevronRight className="size-4 shrink-0 text-muted-foreground/50 transition-all group-hover:translate-x-0.5 group-hover:text-primary" />
      </div>
    </Link>
  )
}
