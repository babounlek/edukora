import { lazy, Suspense } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, Lightbulb } from "lucide-react"

import type { CarteReponseRecherche } from "@/api/types"
import { IndiceAcces } from "@/components/recherche/ResultatRecherche"
import { Skeleton } from "@/components/ui/skeleton"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { cibleResultat } from "@/lib/recherche"
import { cn } from "@/lib/utils"

// Le rendu Markdown + KaTeX est lourd : il ne se charge que quand une carte s'affiche.
const EpreuveMarkdown = lazy(() => import("@/components/EpreuveMarkdown").then((m) => ({ default: m.EpreuveMarkdown })))

/**
 * La réponse à une question courte (« loi d'ohm », « théorème de thalès ») : la RÈGLE du cours qui y répond,
 * lisible sans ouvrir le cours. C'est la section « règle » que l'aperçu public du cours montre déjà à un
 * visiteur - rien de payant ici. Le lien mène au cours entier.
 */
export function CarteReponse({
  carte, country, onChoisir,
}: {
  carte: CarteReponseRecherche
  country: string
  onChoisir?: () => void
}) {
  const couleur = couleurMatiere(carte.matiere.code)
  return (
    <section
      aria-labelledby="carte-reponse-titre"
      className="animate-fade-up relative mt-6 overflow-hidden rounded-2xl border border-border bg-card p-5 shadow-sm sm:p-6"
    >
      <span className={cn("absolute inset-y-0 left-0 w-1.5", couleur.barre)} aria-hidden="true" />
      <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
        <Lightbulb className="size-3.5" aria-hidden="true" />
        La réponse en bref
      </p>
      <h2 id="carte-reponse-titre" className="mt-2 font-display text-xl font-semibold leading-snug sm:text-2xl">
        {carte.titre}
      </h2>
      <p className="mt-1 text-xs text-muted-foreground">
        {[carte.matiere.label, carte.cursus.slice(0, 3).map((c) => c.label).join(", ")].filter(Boolean).join(" · ")}
      </p>
      <div className="mt-4 text-[0.95rem] leading-relaxed [&_.katex-display]:overflow-x-auto [&_.katex-display]:py-1">
        <Suspense fallback={<Skeleton className="h-16 w-full" />}>
          <EpreuveMarkdown markdown={carte.regle_md} />
        </Suspense>
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <Link
          to={cibleResultat(country, carte)}
          onClick={onChoisir}
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:underline"
        >
          Lire le cours en entier
          <ArrowRight className="size-4" aria-hidden="true" />
        </Link>
        <IndiceAcces resultat={carte} />
      </div>
    </section>
  )
}
