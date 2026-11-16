import { useLocation } from "react-router-dom"

import { ACCUEIL_PAYS_RE, CoquilleAccueil } from "@/components/CoquilleAccueil"
import { Skeleton } from "@/components/ui/skeleton"
import { accueilEleveProbable } from "@/lib/indiceAccueil"

// Fallback affiché pendant le téléchargement du chunk d'une route (voir App.tsx,
// React.lazy) - générique par nature puisqu'on ne sait pas encore quelle page arrive,
// mais garde le même langage visuel (Skeleton) que le chargement de données propre à
// chaque page, pour ne pas introduire un deuxième style de "loading" dans l'app.
//
// Hauteur minimale d'un écran : sans elle, ce squelette ne fait qu'une centaine de pixels, le pied de
// page s'affiche juste dessous, puis il est poussé hors de l'écran dès que la vraie page arrive
// (décalage de mise en page mesuré à 0,6 à 0,95 sur l'accueil, une épreuve et /tarifs ; seuil « mauvais »
// de Google : 0,25). Avec un écran entier réservé, le pied de page démarre sous la ligne de flottaison et
// son déplacement ne compte plus. svh : la hauteur de l'écran sans la barre d'adresse mobile.
//
// Sur l'accueil d'un pays, le hero du visiteur à la place du squelette : index.html l'affiche déjà (coquille
// statique), et le remplacer par des barres grises le temps du téléchargement ferait clignoter le titre. Pas pour un
// élève abonné, dont l'accueil est une autre page (voir lib/indiceAccueil).
export function RouteFallback() {
  const { pathname } = useLocation()
  if (ACCUEIL_PAYS_RE.test(pathname) && !accueilEleveProbable()) return <CoquilleAccueil />
  return <SqueletteDePage />
}

/** Le squelette générique, aussi montré à un abonné probable pendant que sa session se retrouve (voir CataloguePage). */
export function SqueletteDePage() {
  return (
    <div className="mx-auto min-h-[100svh] max-w-3xl px-4 py-8 sm:px-6">
      <Skeleton className="mb-3 h-8 w-2/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="mt-2 h-4 w-full" />
      <Skeleton className="mt-2 h-4 w-3/4" />
    </div>
  )
}
