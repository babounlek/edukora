import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, Compass } from "lucide-react"

import { getResumeParcours, listMySubscriptions } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ResumeMatiere, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { tauxBarClassName } from "@/lib/maitrise"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

function CarteMatiere({ matiere, cursusId }: { matiere: ResumeMatiere; cursusId: string }) {
  const sansContenu = matiere.sans_contenu === matiere.total
  const pourcentage = matiere.total > 0 ? Math.round((100 * matiere.maitrises) / matiere.total) : 0

  return (
    <Link
      to={`/parcours/${matiere.subject_id}?cursus=${cursusId}`}
      className={cn(
        "group flex flex-col gap-3 rounded-xl border border-border bg-card p-5 shadow-xs transition-colors hover:border-primary/40",
        sansContenu && "opacity-60",
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <p className="font-display font-semibold">{matiere.subject_label}</p>
        <ArrowRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
      </div>

      {sansContenu ? (
        <p className="text-xs text-muted-foreground">Contenu à venir</p>
      ) : (
        <>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div
              className={cn("h-full rounded-full", tauxBarClassName(pourcentage))}
              style={{ width: `${pourcentage}%` }}
            />
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span>
              {matiere.maitrises}/{matiere.total} savoir{matiere.total > 1 ? "s" : ""} maîtrisé
              {matiere.maitrises > 1 ? "s" : ""}
            </span>
            {matiere.en_revision > 0 && (
              <Badge variant="outline" className="shrink-0">
                {matiere.en_revision} à réviser
              </Badge>
            )}
          </div>
        </>
      )}
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
      <div className="mx-auto max-w-3xl px-4 py-10">
        <Skeleton className="mb-3 h-8 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    )
  }

  if (subscriptions.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 text-center">
        <Compass className="mx-auto mb-3 size-8 text-muted-foreground" />
        <p className="font-display text-lg font-medium">Aucun abonnement actif</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Le parcours suit le programme officiel de ton cursus - il te faut un abonnement actif pour en avoir un.
        </p>
        <Button asChild className="mt-4">
          <Link to="/tarifs">Voir les tarifs</Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-10">
      <div className="mb-2 flex items-center gap-2">
        <Compass className="size-6 text-primary" />
        <h1 className="font-display text-3xl font-semibold">Ton parcours</h1>
      </div>
      <p className="mb-6 text-muted-foreground">
        Toutes tes matières, avec ce qu'il te reste à découvrir, réviser ou maîtriser.
      </p>

      {subscriptions.length > 1 && (
        <select
          value={selectedCursus}
          onChange={(e) => setSelectedCursus(e.target.value)}
          className="mb-6 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
        >
          {subscriptions.map((sub) => (
            <option key={sub.cursus.id} value={sub.cursus.id}>
              {sub.cursus.examen_display}
              {sub.cursus.series ? ` - Série ${sub.cursus.series.code}` : ""}
            </option>
          ))}
        </select>
      )}

      {!matieres ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
      ) : matieres.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          Le programme officiel de ce cursus n'est pas encore disponible.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {matieres.map((matiere) => (
            <CarteMatiere key={matiere.subject_id} matiere={matiere} cursusId={selectedCursus} />
          ))}
        </div>
      )}

      {error && <p className="mt-4 text-sm text-destructive">{error}</p>}

      {/* Discret plutôt qu'un bouton : le parcours est désormais l'entrée de nav
          (voir Header.tsx), la config libre (matière/mode/nombre de questions, sans
          suivre le programme) devient une option secondaire, pas une destination
          concurrente. */}
      <p className="mt-8 text-center text-sm text-muted-foreground">
        Envie de t'entraîner librement, sans suivre le parcours ?{" "}
        <Link to="/quiz" className="font-medium text-primary hover:underline">
          Entraînement libre
        </Link>
      </p>
    </div>
  )
}
