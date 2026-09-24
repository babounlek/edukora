import { type CSSProperties, useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, ChevronRight, Compass, GraduationCap, RotateCcw, SlidersHorizontal } from "lucide-react"

import { getResumeParcours, listMySubscriptions } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ResumeMatiere, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { AnneauProgression, BarreSegmentee, Ecrin, LegendeProgression } from "@/components/Progression"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { subjectIcon } from "@/lib/subjectIcon"
import { pourcent } from "@/lib/maitrise"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

/** Savoirs qui ont du contenu : les seuls qui comptent dans un pourcentage. Un savoir
 * sans contenu n'est pas un échec de l'élève - l'inclure ferait mentir la barre, et
 * donnerait un chiffre différent de celui de l'accueil pour la même matière. */
function exploitables(matiere: ResumeMatiere): number {
  return matiere.total - matiere.sans_contenu
}

function libelleCursus(sub: Subscription): string {
  return `${sub.cursus.examen_display}${sub.cursus.series ? ` ${sub.cursus.series.code}` : ""}`
}

/** Une carte matière : son pourcentage en grand, la barre maîtrisé / en révision / à
 * découvrir, et ce qui l'attend en révision. Même lecture que sur l'accueil. */
function CarteMatiere({
  matiere, cursusId, className, style,
}: { matiere: ResumeMatiere; cursusId: number; className?: string; style?: CSSProperties }) {
  const utiles = exploitables(matiere)
  const sansContenu = utiles === 0
  const SubjectIcon = subjectIcon(matiere.subject_code)

  return (
    <Link
      to={`/parcours/${matiere.subject_id}?cursus=${cursusId}`}
      style={style}
      className={cn(
        "group flex h-full flex-col rounded-2xl border bg-card p-5 transition-all duration-300",
        // Une matière "à venir" reste visible (la structure du programme ne doit pas
        // disparaître) mais se lit d'emblée comme en retrait : pointillés, pas
        // d'élévation au survol.
        sansContenu
          ? "border-dashed border-border/80 bg-muted/20"
          : "border-border/70 hover:-translate-y-1 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/[0.07]",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <span
          className={cn(
            "flex size-10 shrink-0 items-center justify-center rounded-xl transition-colors",
            sansContenu
              ? "bg-muted text-muted-foreground"
              : "bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground",
          )}
        >
          <SubjectIcon className="size-5" aria-hidden="true" />
        </span>
        {sansContenu ? (
          <span className="rounded-full border border-border px-2.5 py-0.5 text-[11px] font-medium text-muted-foreground">
            Contenu à venir
          </span>
        ) : (
          <span className="font-display text-2xl font-semibold leading-none tabular-nums">
            {pourcent(matiere.maitrises / utiles)}
            <span className="ml-px text-xs font-medium text-muted-foreground">%</span>
          </span>
        )}
      </div>

      <h3 className={cn("mt-4 font-display text-lg font-semibold leading-snug", sansContenu && "text-muted-foreground")}>
        {matiere.subject_label}
      </h3>

      {!sansContenu && (
        <div className="mt-auto pt-4">
          <BarreSegmentee
            maitrises={matiere.maitrises}
            enRevision={matiere.en_revision}
            enCours={matiere.en_cours}
            exploitables={utiles}
          />
          <div className="mt-3 flex items-center justify-between gap-2 text-xs text-muted-foreground">
            <span className="tabular-nums">
              {matiere.maitrises}/{utiles} savoir{utiles > 1 ? "s" : ""} maîtrisé{matiere.maitrises > 1 ? "s" : ""}
            </span>
            <span className="flex items-center gap-1.5">
              {matiere.en_revision > 0 && (
                <span className="inline-flex items-center gap-1 rounded-full bg-gold/15 px-2 py-0.5 font-medium text-gold-foreground dark:text-gold">
                  <RotateCcw className="size-3" />
                  {matiere.en_revision} à réviser
                </span>
              )}
              <ChevronRight className="size-4 shrink-0 text-muted-foreground/50 transition-all group-hover:translate-x-0.5 group-hover:text-primary" />
            </span>
          </div>
        </div>
      )}
    </Link>
  )
}

/** Un compteur du haut de page : le chiffre en grand, sa couleur rappelle celle du
 * segment correspondant dans les barres. */
function Compteur({ valeur, libelle, pastille }: { valeur: number; libelle: string; pastille: string }) {
  return (
    <div className="rounded-2xl border border-border/70 bg-background/70 px-3 py-3 backdrop-blur-sm sm:px-4">
      <p className="flex items-center gap-1.5 whitespace-nowrap text-[11px] text-muted-foreground sm:text-xs">
        <span className={cn("inline-block size-2 shrink-0 rounded-full", pastille)} />
        {libelle}
      </p>
      <p className="mt-1 font-display text-2xl font-semibold tabular-nums sm:text-3xl">{valeur}</p>
    </div>
  )
}

function Squelette() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <Skeleton className="mb-10 h-72 w-full rounded-3xl" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-44 w-full rounded-2xl" />
        ))}
      </div>
    </div>
  )
}

export function ParcoursPage() {
  useSeo({
    title: "Ma progression",
    description: "Toutes tes matières, avec ce qu'il te reste à découvrir, réviser ou maîtriser.",
  })

  const { isAuthenticated, isLoading: authLoading, user } = useAuth()
  const navigate = useNavigate()
  const [cursusChoisi, setCursusChoisi] = useState<number | null>(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) navigate("/connexion", { state: { from: "/parcours" } })
  }, [authLoading, isAuthenticated, navigate])

  const { data: subscriptions, isError: erreurAbonnements } = useQuery({
    queryKey: ["mes-abonnements"],
    queryFn: listMySubscriptions,
    enabled: isAuthenticated,
  })
  const actifs = subscriptions?.filter((sub) => sub.is_active) ?? []

  // Le cursus affiché par défaut : celui que l'élève a déclaré préparer, s'il y est
  // abonné, sinon son premier abonnement actif.
  //
  // Sans attendre la liste des abonnements quand le compte dit déjà en avoir un :
  // la page enchaînait session → abonnements → résumé, trois allers-retours en file
  // alors que le troisième ne dépend presque jamais du deuxième. Le résumé part donc
  // en même temps que les abonnements - et sous la même clé de cache que l'accueil
  // (voir AccueilEleve), si bien qu'en venant de "Voir toute ma progression" il est
  // déjà là. Dans le cas rare où le cursus déclaré n'est pas celui de l'abonnement,
  // la correction arrive avec la liste.
  const prepare = user?.cursus_prepare?.id ?? null
  const parDefaut = subscriptions
    ? actifs.find((sub) => sub.cursus.id === prepare)?.cursus.id ?? actifs[0]?.cursus.id ?? null
    : user?.a_un_abonnement_actif ? prepare : null
  const cursusId = cursusChoisi ?? parDefaut

  const { data: matieres, error: erreurResume } = useQuery({
    queryKey: ["parcours-resume", cursusId],
    queryFn: () => getResumeParcours(Number(cursusId)),
    enabled: isAuthenticated && cursusId !== null,
  })

  if (authLoading || !subscriptions) {
    if (erreurAbonnements) {
      return <p className="mx-auto max-w-5xl px-4 py-10 text-sm text-destructive sm:px-6">Impossible de charger tes abonnements.</p>
    }
    return <Squelette />
  }

  if (actifs.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <Ecrin className="text-center">
          <span className="mx-auto mb-4 flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
            <Compass className="size-5" />
          </span>
          <p className="font-display text-xl font-semibold">Aucun abonnement actif</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">
            Le parcours te montre exactement ce qu'il te reste à travailler, matière par matière - il te faut un
            abonnement actif pour y accéder.
          </p>
          <Button asChild className="mt-5 rounded-full px-6">
            <Link to="/tarifs">Voir les tarifs</Link>
          </Button>
        </Ecrin>
      </div>
    )
  }

  // Statistiques du haut de page sur les seuls savoirs qui ont du contenu - même
  // règle que chaque carte, pour que le total soit bien la somme de ce qu'on voit.
  const totalExploitables = matieres?.reduce((somme, m) => somme + exploitables(m), 0) ?? 0
  const totalMaitrises = matieres?.reduce((somme, m) => somme + m.maitrises, 0) ?? 0
  const totalARevoir = matieres?.reduce((somme, m) => somme + m.en_revision, 0) ?? 0
  const totalEnCours = matieres?.reduce((somme, m) => somme + m.en_cours, 0) ?? 0
  const totalADecouvrir = Math.max(0, totalExploitables - totalMaitrises - totalARevoir - totalEnCours)
  const abonnementAffiche = actifs.find((sub) => sub.cursus.id === cursusId)

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <Ecrin>
        <div className="flex items-start justify-between gap-6">
          <div className="min-w-0">
            <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
              <Compass className="size-3.5" />
              Programme officiel, dans l'ordre
            </p>
            <h1 className="mt-2 font-display text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl">
              Ma progression
            </h1>
            <p className="mt-3 max-w-md text-base leading-snug text-muted-foreground sm:text-lg">
              Toutes tes matières, avec ce qu'il te reste à découvrir, réviser ou maîtriser.
            </p>
          </div>
          {totalExploitables > 0 && (
            <AnneauProgression
              part={totalMaitrises / totalExploitables}
              className="hidden sm:block sm:size-32 [&>span]:text-3xl"
            />
          )}
        </div>

        {/* Plusieurs abonnements : un sélecteur segmenté, visible d'un coup d'œil,
            plutôt qu'une liste déroulante qui cache les autres choix. Un seul : le
            cursus en pastille, pour que l'élève sache de quel programme on parle. */}
        <div className="mt-5 flex flex-wrap items-center gap-2">
          {actifs.length > 1 ? (
            <div role="group" aria-label="Cursus" className="inline-flex flex-wrap rounded-full border border-border/80 bg-muted/60 p-1">
              {actifs.map((sub) => (
                <button
                  key={sub.cursus.id}
                  type="button"
                  aria-pressed={sub.cursus.id === cursusId}
                  onClick={() => setCursusChoisi(sub.cursus.id)}
                  className={cn(
                    "rounded-full px-3.5 py-1 text-xs font-medium transition-all",
                    sub.cursus.id === cursusId
                      ? "bg-background text-primary shadow-sm ring-1 ring-primary/25"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  {libelleCursus(sub)}
                </button>
              ))}
            </div>
          ) : (
            abonnementAffiche && (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-border/80 bg-background/70 px-3 py-1 text-xs font-medium text-muted-foreground">
                <GraduationCap className="size-3.5 text-primary" />
                {libelleCursus(abonnementAffiche)}
              </span>
            )
          )}
        </div>

        {matieres && totalExploitables > 0 && (
          <>
            <div className="mt-6 flex items-center gap-4 sm:hidden">
              <AnneauProgression part={totalMaitrises / totalExploitables} />
              <p className="text-sm text-muted-foreground">
                <span className="font-semibold tabular-nums text-foreground">{totalMaitrises}</span> savoir
                {totalMaitrises > 1 ? "s" : ""} maîtrisé{totalMaitrises > 1 ? "s" : ""} sur{" "}
                <span className="tabular-nums">{totalExploitables}</span>
              </p>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-3">
              <Compteur valeur={totalMaitrises} libelle="Maîtrisés" pastille="bg-primary" />
              <Compteur valeur={totalARevoir} libelle="En révision" pastille="bg-gold" />
              <Compteur valeur={totalEnCours} libelle="En cours" pastille="bg-info" />
              <Compteur valeur={totalADecouvrir} libelle="À découvrir" pastille="bg-muted ring-1 ring-border" />
            </div>
            <BarreSegmentee
              className="mt-4 h-2.5"
              maitrises={totalMaitrises}
              enRevision={totalARevoir}
              enCours={totalEnCours}
              exploitables={totalExploitables}
            />
          </>
        )}
      </Ecrin>

      <div className="mt-10 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-semibold tracking-tight">Tes matières</h2>
          <p className="mt-1 text-sm text-muted-foreground">Ouvre une matière pour voir ses savoirs, un par un.</p>
        </div>
        <LegendeProgression />
      </div>

      {!matieres ? (
        erreurResume ? null : (
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-44 w-full rounded-2xl" />
            ))}
          </div>
        )
      ) : matieres.length === 0 ? (
        <p className="mt-5 text-sm text-muted-foreground">
          Le programme officiel de ce cursus n'est pas encore disponible.
        </p>
      ) : (
        <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {matieres.map((matiere, index) => (
            <CarteMatiere
              key={matiere.subject_id}
              matiere={matiere}
              cursusId={Number(cursusId)}
              className="animate-fade-up"
              style={{ animationDelay: `${Math.min(index, 8) * 60}ms` }}
            />
          ))}
        </div>
      )}

      {erreurResume && (
        <p className="mt-4 text-sm text-destructive">
          {erreurResume instanceof ApiError ? erreurResume.message : "Impossible de charger tes matières."}
        </p>
      )}

      {/* Secondaire par rapport aux matières du parcours, mais doit se remarquer en
          bas de page : même écrin que le reste, en version sobre, et un vrai bouton
          plutôt qu'un lien. */}
      <Ecrin variante="sobre" className="mt-10">
        <div className="flex flex-col items-center gap-4 text-center sm:flex-row sm:text-left">
          <span className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <SlidersHorizontal className="size-5" aria-hidden="true" />
          </span>
          <div className="flex-1">
            <p className="font-display text-lg font-semibold">Entraînement libre</p>
            <p className="mt-0.5 text-sm text-muted-foreground">
              Choisis toi-même la matière, le mode et le nombre de questions, sans suivre le parcours.
            </p>
          </div>
          <Button asChild className="group w-full shrink-0 rounded-full px-6 shadow-md shadow-primary/20 sm:w-auto">
            <Link to="/quiz">
              Configurer une séance
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </Button>
        </div>
      </Ecrin>
    </div>
  )
}
