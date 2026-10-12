import { Link } from "react-router-dom"
import { Compass } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath, epreuvesListPath } from "@/lib/countryPath"
import { useSeo } from "@/lib/seo"

/**
 * Le serveur répond 200 pour toute URL (repli sur index.html, voir le Caddyfile) : sans
 * `noindex`, une URL cassée serait indexée comme une vraie page.
 */
export function NotFoundPage() {
  const { country } = useCountry()
  useSeo({ title: "Page introuvable", noindex: true })

  return (
    <div className="mx-auto flex max-w-xl flex-col items-center gap-4 px-4 py-20 text-center sm:px-6">
      <span className="flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        <Compass className="size-7" aria-hidden="true" />
      </span>
      <h1 className="font-display text-2xl font-semibold">Cette page n'existe pas</h1>
      <p className="text-muted-foreground">
        Le lien est peut-être ancien ou mal recopié. Retourne à l'accueil ou cherche directement une épreuve.
      </p>
      <div className="mt-2 flex flex-wrap justify-center gap-3">
        <Button asChild className="min-h-11 rounded-full">
          <Link to={catalogueHomePath(country)}>Retour à l'accueil</Link>
        </Button>
        <Button asChild variant="outline" className="min-h-11 rounded-full">
          <Link to={epreuvesListPath(country)}>Chercher une épreuve</Link>
        </Button>
      </div>
    </div>
  )
}
