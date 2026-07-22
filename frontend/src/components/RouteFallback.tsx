import { Skeleton } from "@/components/ui/skeleton"

// Fallback affiché pendant le téléchargement du chunk d'une route (voir App.tsx,
// React.lazy) - générique par nature puisqu'on ne sait pas encore quelle page arrive,
// mais garde le même langage visuel (Skeleton) que le chargement de données propre à
// chaque page, pour ne pas introduire un deuxième style de "loading" dans l'app.
export function RouteFallback() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Skeleton className="mb-3 h-8 w-2/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="mt-2 h-4 w-full" />
      <Skeleton className="mt-2 h-4 w-3/4" />
    </div>
  )
}
