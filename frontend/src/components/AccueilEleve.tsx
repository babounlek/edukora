import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, ChevronRight, Clock, Crown, RotateCcw, TrendingUp } from "lucide-react"

import { getBilanPeriode, getMyProgression, getResumeParcours, listRevisionsDues } from "@/api/endpoints"
import type { ResumeMatiere } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { HeroAujourdhui } from "@/components/HeroAujourdhui"
import { SeanceDuJour } from "@/components/SeanceDuJour"
import { TaSemaine } from "@/components/TaSemaine"
import { AnneauProgression, BarreSegmentee, Ecrin, LegendeProgression } from "@/components/Progression"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { pourcent } from "@/lib/maitrise"
import { subjectIcon } from "@/lib/subjectIcon"
import { cn } from "@/lib/utils"
import { epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"
import { requeteInedites, useCursusAccueil, useInedites } from "@/lib/cursusAccueil"

/**
 * L'accueil d'un élève ABONNÉ : sa séance, ses lectures, ses révisions, sa
 * progression. Rien d'autre.
 *
 * La page /cm restait un argumentaire de vente jusqu'en bas pour quelqu'un qui avait
 * déjà payé : "Lire un corrigé gratuitement", "Un exemple plutôt qu'une promesse",
 * la preuve sociale, et surtout "Qu'est-ce que tu prépares ?" - qui lui redemandait à
 * chaque visite une information affichée deux centimètres plus haut dans son compte à
 * rebours. Convaincre quelqu'un de déjà convaincu, ce n'est pas neutre : c'est du
 * bruit à la place de ses affaires.
 *
 * Un VISITEUR et un élève NON abonné continuent de voir la page vitrine complète,
 * inchangée (voir CataloguePage) : pour le second, c'est sa page de conversion, et la
 * lui retirer coûterait des abonnements. La vitrine reste aussi ce que voient les
 * robots d'indexation, qui n'ont jamais de session - /cm est la page la plus
 * référencée du site et son contenu indexé ne bouge pas d'un octet.
 */
export function AccueilEleve({ country }: { country: string }) {
  const { user } = useAuth()
  const cursusId = user?.cursus_prepare?.id

  const { data: progression } = useQuery({
    queryKey: ["progression"],
    queryFn: ({ signal }) => getMyProgression(signal),
  })

  const { data: revisions } = useQuery({
    queryKey: ["revisions-dues"],
    queryFn: ({ signal }) => listRevisionsDues(signal),
  })

  const { data: resume } = useQuery({
    queryKey: ["parcours-resume", cursusId],
    queryFn: () => getResumeParcours(Number(cursusId)),
    enabled: Boolean(cursusId),
  })

  // Même clé que TaSemaine : une seule requête pour les deux.
  const { data: semaine } = useQuery({
    queryKey: ["bilan-periode", cursusId, 7],
    queryFn: ({ signal }) => getBilanPeriode(Number(cursusId), signal, 7),
    enabled: Boolean(cursusId),
    retry: false,
  })

  // Les inédites de SON cursus uniquement (voir useInedites) - même clé de cache que
  // la page vitrine pour le même cursus, donc aucune requête en plus entre les deux.
  const cursusAccueil = useCursusAccueil(country)
  const { data: inedites } = useInedites(country, cursusAccueil)

  // Les révisions de SON cursus uniquement : l'endpoint les renvoie tous cursus
  // confondus (il servait une page dédiée), or cet écran parle d'un seul examen.
  const revisionsDuCursus = (revisions ?? []).filter((r) => r.cursus === cursusId)
  const lecture = progression?.lessons?.[0]
  // La préparation d'ensemble, sur les seuls savoirs qui ont du contenu (même règle que
  // EnTeteProgression) : un savoir sans contenu n'est pas un échec de l'élève.
  const exploitables = (resume ?? []).reduce((somme, m) => somme + m.total - m.sans_contenu, 0)
  const preparation = resume && exploitables > 0
    ? resume.reduce((somme, m) => somme + m.maitrises, 0) / exploitables
    : null

  return (
    <div className="pb-4">
      <HeroAujourdhui preparation={preparation} seancesSemaine={semaine?.seances} />
      <SeanceDuJour country={country} />

      {lecture && (
        <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
          <Link
            // getMyProgression ne renvoie jamais que des Lesson classiques - slug
            // toujours renseigné (même garde que sur la page vitrine).
            to={epreuveReaderPath(lecture.subject.country.code.toLowerCase(), lecture.slug as string)}
            className="group flex items-center gap-3 rounded-2xl border border-border bg-card px-5 py-4 transition-colors hover:border-primary/40"
          >
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <BookOpen className="size-5" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Reprendre ma lecture
              </span>
              <span className="block truncate font-display font-medium">{lecture.title}</span>
            </span>
            <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
          </Link>
        </section>
      )}

      {revisionsDuCursus.length > 0 && (
        <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
          <h2 className="flex items-center gap-2 font-display text-lg font-semibold">
            <RotateCcw className="size-4 shrink-0 text-primary" />
            À réviser
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Des thèmes déjà ratés une fois. Les revoir maintenant, c'est ce qui les fait tenir jusqu'au jour J.
          </p>
          <ul className="mt-3 flex flex-col gap-1.5">
            {/* Plafonné : cette page doit donner une direction, pas une liste de
                corvées. Le reste vit dans Ma progression. */}
            {revisionsDuCursus.slice(0, 4).map((revision) => (
              <li key={revision.id}>
                <Link
                  to={`/quiz?cursus=${revision.cursus}&theme=${revision.theme_id}`}
                  className="group flex items-center gap-2.5 rounded-lg border border-border bg-card px-3 py-2.5 text-sm transition-colors hover:border-primary/40"
                >
                  <span className="min-w-0 flex-1 truncate font-medium">{revision.theme}</span>
                  <span className="shrink-0 text-xs text-muted-foreground">{revision.subject_label}</span>
                  {/* Un retard se dit, il ne se reproche pas : gris comme le reste,
                      jamais en rouge (même règle que le compte à rebours). */}
                  {revision.jours_retard > 0 && (
                    <span className="shrink-0 text-xs text-muted-foreground">
                      +{revision.jours_retard} j
                    </span>
                  )}
                  <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
                </Link>
              </li>
            ))}
          </ul>
          {revisionsDuCursus.length > 4 && (
            <p className="mt-2 text-xs text-muted-foreground">
              et {revisionsDuCursus.length - 4} autre{revisionsDuCursus.length - 4 > 1 ? "s" : ""}.
            </p>
          )}
        </section>
      )}

      {cursusId && <TaSemaine cursusId={Number(cursusId)} className="mx-auto max-w-5xl px-4 pt-8 sm:px-6" />}

      {resume && resume.some((m) => m.total > m.sans_contenu) && (
        <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
          <Ecrin variante="sobre">
            <div>
              <EnTeteProgression resume={resume} />
              <div className="mt-6 grid gap-3 sm:grid-cols-2">
                {/* Les matières les moins avancées d'abord - c'est là qu'il y a quelque
                    chose à faire. Voir la page Ma progression pour la liste entière. */}
                {[...resume]
                  .filter((m) => m.total > m.sans_contenu)
                  .sort(
                    (a, b) =>
                      partMaitrisee(a) - partMaitrisee(b) ||
                      // Au démarrage, TOUTES les matières sont à 0 et le premier critère
                      // ne départage rien : sans ce second tri, les quatre affichées
                      // étaient celles que la base renvoyait en premier. À défaut de
                      // connaître les coefficients ici (ils vivent côté serveur, voir
                      // _coefficient_par_subject), on montre les matières où il reste le
                      // plus à faire, puis l'ordre alphabétique pour rester stable d'une
                      // visite à l'autre.
                      restant(b) - restant(a) ||
                      a.subject_label.localeCompare(b.subject_label, "fr"),
                  )
                  .slice(0, 4)
                  .map((matiere) => (
                    <BarreMatiere key={matiere.subject_id} matiere={matiere} cursusId={Number(cursusId)} />
                  ))}
              </div>
              <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
                <LegendeProgression />
                <Button asChild variant="outline" size="sm" className="group rounded-full">
                  <Link to="/parcours">
                    Voir toute ma progression
                    <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
                  </Link>
                </Button>
              </div>
            </div>
          </Ecrin>
        </section>
      )}

      {/* Le seul bloc "produit" conservé : une inédite n'est pas un argumentaire,
          c'est du contenu neuf que l'abonné a payé pour recevoir - sans ça, il ne sait
          pas qu'il est arrivé. Compact, jamais la grande carte d'aperçu de la vitrine,
          qui sert à convaincre quelqu'un qui n'a pas encore payé. */}
      {inedites && inedites.count > 0 && (
        <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
          <Link
            to={`${epreuvesListPath(country)}?${requeteInedites(cursusAccueil)}`}
            className="group flex items-center gap-3 rounded-2xl border border-gold/30 bg-gold/5 px-5 py-4 transition-colors hover:border-gold/60"
          >
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold">
              <Crown className="size-5" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
                {inedites.count} épreuve{inedites.count > 1 ? "s" : ""} inédite{inedites.count > 1 ? "s" : ""}
              </span>
              <span className="block truncate font-display font-medium">
                {inedites.results[0]?.title ?? "Des sujets originaux, chronométrés"}
              </span>
            </span>
            <Clock className="size-4 shrink-0 text-muted-foreground" />
            <ArrowRight className="size-4 shrink-0 text-gold transition-transform group-hover:translate-x-0.5" />
          </Link>
        </section>
      )}
    </div>
  )
}

/** Savoirs qui ont du contenu et qui ne sont pas encore maîtrisés - ce qu'il reste
 * réellement à faire dans cette matière. */
function restant(matiere: ResumeMatiere): number {
  return matiere.total - matiere.sans_contenu - matiere.maitrises
}

/** Part de savoirs maîtrisés, sur les seuls savoirs qui ont du contenu - un savoir
 * sans contenu n'est pas un échec de l'élève, l'inclure ferait mentir la barre. */
function partMaitrisee(matiere: ResumeMatiere): number {
  const exploitables = matiere.total - matiere.sans_contenu
  return exploitables > 0 ? matiere.maitrises / exploitables : 0
}

/**
 * Le titre et un seul chiffre d'ensemble, sur TOUTES les matières (pas seulement les
 * quatre affichées) : les barres disent où agir, l'anneau dit où l'on en est. Même
 * règle que les barres - seuls les savoirs qui ont du contenu comptent.
 */
function EnTeteProgression({ resume }: { resume: ResumeMatiere[] }) {
  const maitrises = resume.reduce((somme, m) => somme + m.maitrises, 0)
  const exploitables = resume.reduce((somme, m) => somme + m.total - m.sans_contenu, 0)
  const part = exploitables > 0 ? maitrises / exploitables : 0
  return (
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
          <span className="font-semibold tabular-nums text-foreground">{maitrises}</span> savoir
          {maitrises > 1 ? "s" : ""} maîtrisé{maitrises > 1 ? "s" : ""} sur{" "}
          <span className="tabular-nums">{exploitables}</span> au programme
        </p>
      </div>
      <AnneauProgression part={part} />
    </div>
  )
}

/**
 * Une matière : son pourcentage en grand, puis une barre en trois segments -
 * maîtrisé, en révision, à découvrir. La barre à un seul segment restait vide pour
 * presque tout le monde au démarrage ; les segments montrent que le travail en cours
 * compte déjà, même avant la première maîtrise.
 */
function BarreMatiere({ matiere, cursusId }: { matiere: ResumeMatiere; cursusId: number }) {
  const exploitables = matiere.total - matiere.sans_contenu
  const Icone = subjectIcon(matiere.subject_code)
  return (
    <Link
      // `?cursus=` est requis par ParcoursSubjectPage - même lien que depuis la page
      // Ma progression, sans quoi la page s'ouvre sans savoir quel programme afficher.
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
