import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, Clock, Crown, RotateCcw } from "lucide-react"

import { getMyProgression, getResumeParcours, listEpreuves, listRevisionsDues } from "@/api/endpoints"
import type { ResumeMatiere } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { SeanceDuJour } from "@/components/SeanceDuJour"
import { epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"

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

  // Même clé de cache que le Header et la page vitrine : un élève qui navigue entre
  // les deux ne repaie pas cette requête.
  const { data: inedites } = useQuery({
    queryKey: ["epreuves-inedites-recente", country],
    queryFn: ({ signal }) => listEpreuves({ country, origine: "INEDITE", ordering: "recent" }, signal),
    enabled: Boolean(country),
  })

  // Les révisions de SON cursus uniquement : l'endpoint les renvoie tous cursus
  // confondus (il servait une page dédiée), or cet écran parle d'un seul examen.
  const revisionsDuCursus = (revisions ?? []).filter((r) => r.cursus === cursusId)
  const lecture = progression?.lessons?.[0]

  return (
    <div className="pb-4">
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

      {resume && resume.length > 0 && (
        <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
          <h2 className="font-display text-lg font-semibold">Où j'en suis</h2>
          <div className="mt-3 flex flex-col gap-2">
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
          <Button asChild variant="ghost" size="sm" className="mt-3">
            <Link to="/parcours">
              Voir toute ma progression
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </section>
      )}

      {/* Le seul bloc "produit" conservé : une inédite n'est pas un argumentaire,
          c'est du contenu neuf que l'abonné a payé pour recevoir - sans ça, il ne sait
          pas qu'il est arrivé. Compact, jamais la grande carte d'aperçu de la vitrine,
          qui sert à convaincre quelqu'un qui n'a pas encore payé. */}
      {inedites && inedites.count > 0 && (
        <section className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
          <Link
            to={`${epreuvesListPath(country)}?origine=INEDITE`}
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

/** Part de savoirs maîtrisés, sur les seuls savoirs qui ont du contenu - un savoir
 * sans contenu n'est pas un échec de l'élève, l'inclure ferait mentir la barre. */
/** Savoirs qui ont du contenu et qui ne sont pas encore maîtrisés - ce qu'il reste
 * réellement à faire dans cette matière. */
function restant(matiere: ResumeMatiere): number {
  return matiere.total - matiere.sans_contenu - matiere.maitrises
}

function partMaitrisee(matiere: ResumeMatiere): number {
  const exploitables = matiere.total - matiere.sans_contenu
  return exploitables > 0 ? matiere.maitrises / exploitables : 0
}

function BarreMatiere({ matiere, cursusId }: { matiere: ResumeMatiere; cursusId: number }) {
  const part = partMaitrisee(matiere)
  const exploitables = matiere.total - matiere.sans_contenu
  return (
    <Link
      // `?cursus=` est requis par ParcoursSubjectPage - même lien que depuis la page
      // Ma progression, sans quoi la page s'ouvre sans savoir quel programme afficher.
      to={`/parcours/${matiere.subject_id}?cursus=${cursusId}`}
      className="group flex items-center gap-3 rounded-lg px-2 py-1.5 transition-colors hover:bg-accent/50"
    >
      <span className="w-32 shrink-0 truncate text-sm font-medium sm:w-44">{matiere.subject_label}</span>
      <span className="h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-muted">
        <span
          className={cn("block h-full rounded-full bg-primary transition-all")}
          style={{ width: `${Math.round(part * 100)}%` }}
        />
      </span>
      <span className="w-16 shrink-0 text-right text-xs tabular-nums text-muted-foreground">
        {matiere.maitrises}/{exploitables}
      </span>
    </Link>
  )
}
