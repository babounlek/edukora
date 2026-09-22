import { type CSSProperties, useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, BookOpen, CheckCircle2, Compass, RotateCcw, SlidersHorizontal } from "lucide-react"

import { getResumeParcours, listMySubscriptions } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ResumeMatiere, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Eyebrow, StatChip } from "@/components/Configurateur"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { subjectIcon } from "@/lib/subjectIcon"
import { tauxBarClassName } from "@/lib/maitrise"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

/** Une carte matière - même gabarit que CoursCard (icône badge, hover surélevé) : le
 * parcours doit se reconnaître comme un outil de la plateforme, pas une page à part. */
function CarteMatiere({
  matiere, cursusId, className, style,
}: { matiere: ResumeMatiere; cursusId: string; className?: string; style?: CSSProperties }) {
  const sansContenu = matiere.sans_contenu === matiere.total
  const pourcentage = matiere.total > 0 ? Math.round((100 * matiere.maitrises) / matiere.total) : 0
  const SubjectIcon = subjectIcon(matiere.subject_code)

  return (
    <Link to={`/parcours/${matiere.subject_id}?cursus=${cursusId}`} className={className} style={style}>
      <Card
        className={cn(
          "group h-full overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5",
          sansContenu && "opacity-60",
        )}
      >
        <CardContent className="flex h-full flex-col gap-3 p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <SubjectIcon className="size-4.5" aria-hidden="true" />
            </div>
            <ArrowRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-primary" />
          </div>

          <div>
            <h3 className="font-display font-medium leading-snug">{matiere.subject_label}</h3>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {sansContenu
                ? "Contenu à venir"
                : `${matiere.maitrises}/${matiere.total} savoir${matiere.total > 1 ? "s" : ""} maîtrisé${matiere.maitrises > 1 ? "s" : ""}`}
            </p>
          </div>

          {!sansContenu && (
            <div className="mt-auto flex flex-col gap-2">
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className={cn("h-full rounded-full transition-all", tauxBarClassName(pourcentage))}
                  style={{ width: `${pourcentage}%` }}
                />
              </div>
              {matiere.en_revision > 0 && (
                <Badge variant="outline" className="w-fit shrink-0">
                  {matiere.en_revision} à réviser
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}

export function ParcoursPage() {
  useSeo({
    title: "Ton parcours",
    description: "Toutes tes matières, avec ce qu'il te reste à découvrir, réviser ou maîtriser.",
  })

  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const navigate = useNavigate()

  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [selectedCursus, setSelectedCursus] = useState("")
  const [matieres, setMatieres] = useState<ResumeMatiere[] | null>(null)
  const [subscriptionsLoaded, setSubscriptionsLoaded] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/parcours" } })
      return
    }
    listMySubscriptions()
      .then((subs) => {
        const active = subs.filter((sub) => sub.is_active)
        setSubscriptions(active)
        if (active.length > 0) setSelectedCursus(String(active[0].cursus.id))
      })
      .catch(() => setError("Impossible de charger tes abonnements."))
      .finally(() => setSubscriptionsLoaded(true))
  }, [authLoading, isAuthenticated, navigate])

  useEffect(() => {
    if (!selectedCursus) return
    setMatieres(null)
    getResumeParcours(Number(selectedCursus))
      .then(setMatieres)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Impossible de charger tes matières."))
  }, [selectedCursus])

  if (authLoading || !subscriptionsLoaded) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <Skeleton className="mb-8 h-56 w-full rounded-2xl" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  if (subscriptions.length === 0) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col items-center px-4 py-20 text-center">
        <span className="mb-4 flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary ring-4 ring-primary/5">
          <Compass className="size-5" />
        </span>
        <p className="font-display text-lg font-semibold">Aucun abonnement actif</p>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          Le parcours te montre exactement ce qu'il te reste à travailler, matière par matière - il te faut un
          abonnement actif pour y accéder.
        </p>
        <Button asChild className="mt-5">
          <Link to="/tarifs">Voir les tarifs</Link>
        </Button>
      </div>
    )
  }

  // Statistiques du hero calculées sur les seules matières ayant du contenu : une
  // matière "à venir" ne doit compter ni dans le nombre de savoirs à maîtriser, ni
  // fausser un total qui semblerait alors ne jamais progresser.
  const matieresAvecContenu = matieres?.filter((m) => m.sans_contenu !== m.total) ?? []
  const totalSavoirs = matieresAvecContenu.reduce((sum, m) => sum + m.total, 0)
  const totalMaitrises = matieresAvecContenu.reduce((sum, m) => sum + m.maitrises, 0)
  const totalARevoir = matieresAvecContenu.reduce((sum, m) => sum + m.en_revision, 0)

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
        <div className="relative max-w-2xl">
          <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Compass className="size-5" />
          </div>
          <Eyebrow>Programme officiel, dans l'ordre</Eyebrow>
          <h1 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">Ton parcours</h1>
          <p className="mt-3 max-w-md text-lg font-medium leading-snug text-foreground/90">
            Toutes tes matières, avec ce qu'il te reste à découvrir, réviser ou maîtriser.
          </p>

          {matieresAvecContenu.length > 0 && (
            <div className="mt-5 flex flex-wrap gap-2">
              <StatChip icon={<BookOpen className="size-3.5 text-primary" />}>
                {/* Total de TOUTES les matières du programme (avec et sans contenu,
                    comme les cartes ci-dessous) et non matieresAvecContenu : "au
                    programme" doit correspondre à ce qui est effectivement affiché,
                    pas seulement à la portion déjà couverte. */}
                <span className="font-medium">{matieres?.length ?? 0}</span>
                <span className="text-muted-foreground">
                  matière{(matieres?.length ?? 0) > 1 ? "s" : ""} au programme
                </span>
              </StatChip>
              <StatChip icon={<CheckCircle2 className="size-3.5 text-success" />}>
                <span className="font-medium">
                  {totalMaitrises}/{totalSavoirs}
                </span>
                <span className="text-muted-foreground">savoirs maîtrisés</span>
              </StatChip>
              {totalARevoir > 0 && (
                <StatChip icon={<RotateCcw className="size-3.5 text-gold" />}>
                  <span className="font-medium">{totalARevoir}</span>
                  <span className="text-muted-foreground">à réviser</span>
                </StatChip>
              )}
            </div>
          )}
        </div>
      </div>

      {subscriptions.length > 1 && (
        <div className="mb-6">
          <Select value={selectedCursus} onValueChange={setSelectedCursus}>
            <SelectTrigger className="w-full sm:w-72">
              <SelectValue placeholder="Choisir un cursus" />
            </SelectTrigger>
            <SelectContent>
              {subscriptions.map((sub) => (
                <SelectItem key={sub.cursus.id} value={String(sub.cursus.id)}>
                  {sub.cursus.examen_display}
                  {sub.cursus.series ? ` - Série ${sub.cursus.series.code}` : ""}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {!matieres ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-2xl" />
          ))}
        </div>
      ) : matieres.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          Le programme officiel de ce cursus n'est pas encore disponible.
        </p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {matieres.map((matiere, index) => (
            <CarteMatiere
              key={matiere.subject_id}
              matiere={matiere}
              cursusId={selectedCursus}
              className="animate-fade-up"
              style={{ animationDelay: `${Math.min(index, 8) * 60}ms` }}
            />
          ))}
        </div>
      )}

      {error && <p className="mt-4 text-sm text-destructive">{error}</p>}

      {/* Secondaire par rapport aux matières du parcours (pas de fond primary plein,
          pas dans la grille), mais doit se remarquer en bas de page : bordure pleine +
          badge icône reprennent le langage visuel des CarteMatiere ci-dessus, bouton
          plein plutôt qu'outline pour un vrai second CTA. */}
      <div className="mt-8 flex flex-col items-center gap-4 rounded-2xl border border-primary/15 bg-primary/[0.04] p-5 text-center sm:flex-row sm:text-left sm:p-6">
        <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <SlidersHorizontal className="size-5" aria-hidden="true" />
        </div>
        <div className="flex-1">
          <p className="font-display font-medium">Entraînement libre</p>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Choisis toi-même la matière, le mode et le nombre de questions, sans suivre le parcours.
          </p>
        </div>
        <Button asChild className="w-full shrink-0 sm:w-auto">
          <Link to="/quiz">
            Configurer une séance
            <ArrowRight className="ml-1.5 size-4" />
          </Link>
        </Button>
      </div>
    </div>
  )
}
