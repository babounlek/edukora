import { useEffect, useRef, type ReactNode } from "react"

import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

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
  useI18n()
  const groupe = useRef<HTMLDivElement>(null)
  const dernierActif = useRef<Element | null>(null)
  // La pastille choisie était parfois hors de l'écran dans cette rangée qui défile (la matière « Mathematics » présélectionnée,
  // cachée à gauche : test élève Gogo). On la ramène au centre de la rangée UNE fois par choix, sans jamais toucher à la page ni
  // reprendre la main sur un élève qui fait glisser la rangée lui-même.
  useEffect(() => {
    const rangee = groupe.current
    const actif = rangee?.querySelector<HTMLElement>('[aria-pressed="true"]')
    if (!rangee || !actif || actif === dernierActif.current) return
    dernierActif.current = actif
    if (rangee.scrollWidth <= rangee.clientWidth || typeof rangee.scrollTo !== "function") return
    rangee.scrollTo({ left: Math.max(0, actif.offsetLeft - rangee.clientWidth / 2 + actif.clientWidth / 2) })
  })
  return (
    <div className="mt-4">
      <p className="mb-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{titre}</p>
      <div
        ref={groupe}
        role="group"
        aria-label={t("gl.filtrer_par", { titre: titre.toLowerCase() })}
        className="-mx-1 flex gap-1.5 overflow-x-auto px-1 pb-1.5 [scrollbar-width:none] sm:flex-wrap sm:overflow-visible sm:pb-0 [&::-webkit-scrollbar]:hidden"
      >
        {children}
      </div>
    </div>
  )
}

export function PastilleFiltre({
  actif, onClick, disabled, title, children,
}: { actif: boolean; onClick: () => void; disabled?: boolean; title?: string; children: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={actif}
      disabled={disabled}
      title={title}
      className={cn(
        "inline-flex min-h-9 shrink-0 items-center gap-1.5 whitespace-nowrap rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors",
        actif
          ? "border-primary bg-primary text-primary-foreground shadow-sm"
          : "border-border text-muted-foreground hover:border-primary/40 hover:text-primary",
        disabled && "cursor-not-allowed border-dashed opacity-60 hover:border-border hover:text-muted-foreground",
      )}
    >
      {children}
    </button>
  )
}
