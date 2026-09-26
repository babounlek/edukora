import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

/**
 * Les deux briques de filtre partagées par /epreuves et /cours : les deux catalogues doivent
 * se piloter de la même façon, donc se composer des mêmes pièces.
 */

/**
 * Une rangée de filtres avec son titre. Sur téléphone, une seule ligne qu'on fait glisser
 * (six lignes de pastilles à traverser repoussaient les résultats sous le pli) ; dès `sm`,
 * elle passe à la ligne et tout reste visible - jamais de carrousel à la souris, dont la
 * molette ne défile pas horizontalement.
 */
export function FiltreLigne({ titre, children }: { titre: string; children: ReactNode }) {
  return (
    <div className="mt-4">
      <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{titre}</p>
      <div
        role="group"
        aria-label={`Filtrer par ${titre.toLowerCase()}`}
        className="-mx-1 flex gap-1.5 overflow-x-auto px-1 pb-1.5 [scrollbar-width:none] sm:flex-wrap sm:overflow-visible sm:pb-0 [&::-webkit-scrollbar]:hidden"
      >
        {children}
      </div>
    </div>
  )
}

export function PastilleFiltre({
  actif, onClick, children,
}: { actif: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={actif}
      className={cn(
        "inline-flex min-h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
        actif
          ? "border-primary bg-primary text-primary-foreground shadow-sm"
          : "border-border text-muted-foreground hover:border-primary/40 hover:text-primary",
      )}
    >
      {children}
    </button>
  )
}
