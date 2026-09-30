import { useEffect, useMemo } from "react"
import { Link } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, Clock, Crown } from "lucide-react"

import { getAccueil } from "@/api/endpoints"
import type { Accueil } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { DepuisLaDerniereFois } from "@/components/DepuisLaDerniereFois"
import { Moments } from "@/components/Moments"
import { OuJenSuis } from "@/components/OuJenSuis"
import { InviteRappels } from "@/components/RappelsEmail"
import { TeteAccueil } from "@/components/TeteAccueil"
import { ecrireAccueilEnCache, lireAccueilEnCache } from "@/lib/accueilCache"
import { marquerAffichageAccueil } from "@/lib/accueilChrono"
import { epreuvesListPath } from "@/lib/countryPath"
import { requeteInedites, useCursusAccueil, useInedites } from "@/lib/cursusAccueil"

/**
 * L'accueil d'un élève ABONNÉ, en trois zones et pas plus :
 *
 *   1. Aujourd'hui (TeteAccueil) : qui il est, où il en est, une phrase de coach, et
 *      LE bouton - au-dessus du pli, y compris sur téléphone.
 *   2. Depuis la dernière fois (DepuisLaDerniereFois) : ce qui a bougé, puis ce qu'il
 *      y a à reprendre (deux révisions au plus, une lecture ouverte).
 *   3. Où j'en suis (OuJenSuis) : l'anneau pondéré, la trajectoire d'ici le jour J, les
 *      deux matières les plus en retard.
 *
 * Tout vient d'UNE requête (voir getAccueil et quiz.accueil côté backend), rendue en
 * un seul passage : plus de blocs qui apparaissent un à un ni de page qui saute. La
 * dernière version connue est gardée dans le navigateur (voir lib/accueilCache) pour
 * s'afficher avant la réponse - et hors connexion.
 *
 * Un VISITEUR et un élève NON abonné continuent de voir la page vitrine complète (voir
 * CataloguePage) : pour le second, c'est sa page de conversion. La vitrine reste aussi
 * ce que voient les robots d'indexation.
 */
export function AccueilEleve({ country }: { country: string }) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const cursusId = user?.cursus_prepare?.id
  const userId = user?.id

  // Le chrono du seul chiffre qui juge cette page : le délai jusqu'à "Commencer".
  useEffect(() => {
    marquerAffichageAccueil()
  }, [])

  const enCache = useMemo(
    () => (userId && cursusId ? lireAccueilEnCache(userId, cursusId) : null),
    [userId, cursusId],
  )

  const { data, isError } = useQuery({
    queryKey: ["accueil", cursusId],
    queryFn: async ({ signal }) => {
      const accueil = await getAccueil(signal)
      // Les blocs qui vivent aussi ailleurs lisent leurs clés habituelles : on les
      // alimente ici pour qu'aucun n'ait à refaire sa propre requête (la séance et ses
      // mutations sous "plan-du-jour", le bilan de semaine, le résumé du parcours que
      // la page Ma progression réutilise en arrivant depuis "Voir toute ma progression").
      queryClient.setQueryData(["plan-du-jour"], accueil.plan)
      if (accueil.bilan_semaine) queryClient.setQueryData(["bilan-periode", cursusId, 7], accueil.bilan_semaine)
      queryClient.setQueryData(["parcours-resume", cursusId], accueil.resume)
      if (userId && cursusId) ecrireAccueilEnCache(userId, cursusId, accueil)
      return accueil
    },
    // La version en cache s'affiche tout de suite, et le serveur est TOUJOURS
    // interrogé au montage (staleTime 0, contre 60 s par défaut) : un accueil rouvert
    // deux minutes après la séance doit déjà dire "Séance faite" - c'est précisément la
    // page dont la donnée bouge entre deux ouvertures.
    initialData: enCache?.data,
    initialDataUpdatedAt: enCache?.date,
    staleTime: 0,
    enabled: Boolean(cursusId),
  })

  // Les inédites de SON cursus uniquement - même clé de cache que la vitrine.
  const cursusAccueil = useCursusAccueil(country)
  const { data: inedites } = useInedites(country, cursusAccueil)

  if (!data || !cursusId) {
    return isError ? <ErreurAccueil /> : <SqueletteAccueil />
  }

  return (
    <div className="pb-4">
      <TeteAccueil accueil={data} country={country} />
      <Moments accueil={data} userId={userId} />
      {/* Proposé une fois, quand l'élève sait ce qu'on lui rappellerait : après sa
          première séance. */}
      {!data.premiers_pas && <InviteRappels />}
      <DepuisLaDerniereFois depuis={data.depuis} revisions={data.revisions} lecture={data.lecture} />
      <OuJenSuis accueil={data} cursusId={cursusId} country={country} />
      <LigneInedites accueil={data} country={country} inedites={inedites} cursusAccueil={cursusAccueil} />
    </div>
  )
}

/**
 * Le seul bloc "produit" conservé, réduit à une ligne : une inédite n'est pas un
 * argumentaire, c'est du contenu neuf que l'abonné a payé pour recevoir - sans ça, il
 * ne sait pas qu'il est arrivé.
 */
function LigneInedites({
  country, inedites, cursusAccueil,
}: {
  accueil: Accueil
  country: string
  inedites: ReturnType<typeof useInedites>["data"]
  cursusAccueil: ReturnType<typeof useCursusAccueil>
}) {
  if (!inedites || inedites.count === 0) return null
  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
      <Link
        to={`${epreuvesListPath(country)}?${requeteInedites(cursusAccueil)}`}
        className="group flex items-center gap-3 rounded-2xl border border-gold/30 bg-gold/5 px-5 py-3.5 transition-colors hover:border-gold/60"
      >
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
          <Crown className="size-4" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
            {inedites.count} épreuve{inedites.count > 1 ? "s" : ""} inédite{inedites.count > 1 ? "s" : ""}
          </span>
          <span className="block truncate text-sm font-medium">
            {inedites.results[0]?.title ?? "Des sujets originaux, chronométrés"}
          </span>
        </span>
        <Clock className="size-4 shrink-0 text-muted-foreground" />
        <ArrowRight className="size-4 shrink-0 text-gold-text transition-transform group-hover:translate-x-0.5" />
      </Link>
    </section>
  )
}

/**
 * Le squelette a la HAUTEUR du contenu qu'il remplace (la tête avec sa bande et son
 * bouton, puis deux blocs) : quand la réponse arrive, rien ne saute. Sans animation
 * de balayage - un téléphone d'entrée de gamme n'a pas besoin de ça pour attendre.
 */
export function SqueletteAccueil() {
  return (
    <div className="pb-4" aria-busy="true" aria-label="Chargement de ton accueil">
      <div className="mx-auto max-w-5xl px-4 pt-5 sm:px-6 sm:pt-6">
        <div className="overflow-hidden rounded-3xl border border-border/70 bg-card">
          <div className="h-44 bg-primary/10 sm:h-40" />
          <div className="space-y-4 p-5 sm:p-8">
            <div className="h-4 w-24 rounded bg-muted" />
            <div className="h-9 w-3/4 rounded bg-muted" />
            <div className="flex gap-2">
              <div className="h-7 w-24 rounded-full bg-muted" />
              <div className="h-7 w-16 rounded-full bg-muted" />
            </div>
            <div className="h-12 w-52 rounded-full bg-muted" />
          </div>
        </div>
      </div>
      <div className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
        <div className="h-36 rounded-3xl border border-border/70 bg-card" />
      </div>
      <div className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
        <div className="h-64 rounded-3xl border border-border/70 bg-card" />
      </div>
    </div>
  )
}

function ErreurAccueil() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <p className="text-sm text-muted-foreground">
        Impossible de charger ton accueil pour le moment. Vérifie ta connexion, puis{" "}
        <button type="button" onClick={() => window.location.reload()} className="underline underline-offset-4 hover:text-primary">
          réessaie
        </button>
        .
      </p>
    </div>
  )
}
