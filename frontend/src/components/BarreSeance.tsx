import { Link, useLocation } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, ListChecks } from "lucide-react"

import { getPlanDuJour } from "@/api/endpoints"
import type { EtapeSeance } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { lienEtape, ouvrirEtapeDeSeance } from "@/lib/seance"
import { Button } from "@/components/ui/button"

interface PositionDansLaSeance {
  numero: number
  total: number
  suivante: EtapeSeance | null
  lienSuivante: string | null
  ouvrirSuivante: () => void
}

/**
 * Où l'élève en est dans sa séance du jour, déduit de la page qu'il lit : si l'adresse
 * est celle d'une étape cours/exercice de la séance en cours, on renvoie sa position et
 * l'étape d'après. Sinon null - un cours ouvert hors séance, une séance déjà terminée
 * ou verrouillée n'affichent rien, jamais un fil d'Ariane qui ne mène nulle part.
 *
 * Lit le même cache que l'accueil (["plan-du-jour"]) : aucune requête de plus tant que
 * l'élève enchaîne ses étapes.
 */
export function usePositionDansLaSeance(): PositionDansLaSeance | null {
  const { pathname } = useLocation()
  const { isAuthenticated } = useAuth()
  const { country } = useCountry()
  const queryClient = useQueryClient()
  const lecteur = pathname.endsWith("/lire")

  const { data: plan } = useQuery({
    queryKey: ["plan-du-jour"],
    queryFn: ({ signal }) => getPlanDuJour(signal),
    enabled: isAuthenticated && lecteur,
  })

  if (!lecteur || !plan || plan.etat !== "plan_pret" || !plan.seance || plan.seance.verrouillee) return null
  const etapes = plan.seance.etapes
  const index = etapes.findIndex((e) =>
    e.type === "cours"
      ? pathname === `/cours/${e.slug}/lire`
      : e.type === "exercice" && pathname.endsWith(`/epreuves/${e.lesson_slug}/lire`),
  )
  if (index < 0) return null

  const suivante = etapes[index + 1] ?? null
  return {
    numero: index + 1,
    total: etapes.length,
    suivante,
    lienSuivante: suivante ? lienEtape(suivante, country, plan) : null,
    ouvrirSuivante: () => suivante && ouvrirEtapeDeSeance(queryClient, suivante),
  }
}

/**
 * "Séance du jour · étape 1/3 - Continuer" sous l'en-tête pendant la lecture d'une
 * étape : l'élève qui a quitté « Aujourd'hui » sait qu'il est toujours dans sa séance,
 * et où elle continue, sans repasser par l'accueil.
 */
export function BarreSeance() {
  const position = usePositionDansLaSeance()
  if (!position) return null

  return (
    <div role="region" aria-label="Séance du jour" className="border-b border-primary/20 bg-primary/5">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-2 sm:px-6">
        <ListChecks className="size-4 shrink-0 text-primary" />
        <p className="min-w-0 flex-1 truncate text-sm">
          <span className="font-semibold">Séance du jour</span>
          <span className="text-muted-foreground"> · étape {position.numero}/{position.total}</span>
        </p>
        {position.suivante && position.lienSuivante && (
          <Link
            to={position.lienSuivante}
            onClick={position.ouvrirSuivante}
            className="flex shrink-0 items-center gap-1 text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            Continuer
            <ArrowRight className="size-3.5" />
          </Link>
        )}
      </div>
    </div>
  )
}

/**
 * En bas d'un cours ou d'un exercice de la séance : le bouton principal devient l'étape
 * d'après. Sans lui, l'élève qui finit sa lecture doit deviner qu'il faut retourner à
 * l'accueil pour la suite.
 */
export function EtapeSuivante() {
  const position = usePositionDansLaSeance()
  if (!position?.suivante || !position.lienSuivante) return null
  const { suivante } = position

  return (
    <section className="mx-auto mt-10 max-w-3xl rounded-2xl border border-primary/30 bg-primary/5 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
        Séance du jour · étape {position.numero}/{position.total} terminée
      </p>
      <p className="mt-1 font-display text-lg font-semibold">Étape suivante : {suivante.libelle}</p>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <Button asChild size="lg" className="rounded-full">
          <Link to={position.lienSuivante} onClick={position.ouvrirSuivante}>
            {suivante.type === "quiz" ? "Passer au quiz" : "Continuer"}
            <ArrowRight />
          </Link>
        </Button>
        <span className="text-xs text-muted-foreground">{suivante.duree_min} min</span>
      </div>
    </section>
  )
}
