import { useCallback, useEffect, useRef, useState, type ReactNode } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { EpreuveCard } from "@/components/EpreuveCard"
import { Button } from "@/components/ui/button"

interface EpreuveRailProps {
  title: string
  icon: ReactNode
  epreuves: Epreuve[]
  /** Force exactement 3 cartes visibles à la fois (largeur en % du rail, à partir
   * de `sm`) au lieu de la largeur fixe w-72. Sous `sm`, retombe sur w-72 : 3
   * cartes pleines n'y tiendraient pas lisiblement. */
  threePerView?: boolean
}

// Largeur d'une carte (w-72 = 18rem) + l'écart (gap-4 = 1rem) entre deux cartes -
// une flèche avance donc d'une carte pleine à chaque clic, jamais une fraction qui
// laisserait une carte à moitié coupée au bord du rail.
const SCROLL_STEP_PX = 304

/** Rail horizontal d'épreuves mises en avant (gratuites, derniers ajouts...) -
 * disparaît silencieusement si `epreuves` est vide, même patron que
 * SocialProofSection : jamais d'état vide ni de placeholder affiché à la place.
 * Scroll-snap + flèches dédiées plutôt que la barre de défilement native, cachée
 * (voir .no-scrollbar) : le tactile/la molette restent la scroller normalement,
 * les flèches ne sont qu'un raccourci pour la souris/le clavier. */
export function EpreuveRail({ title, icon, epreuves, threePerView }: EpreuveRailProps) {
  const scrollerRef = useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(false)

  const updateScrollState = useCallback(() => {
    const el = scrollerRef.current
    if (!el) return
    setCanScrollLeft(el.scrollLeft > 4)
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 4)
  }, [])

  useEffect(() => {
    updateScrollState()
  }, [epreuves, updateScrollState])

  if (epreuves.length === 0) return null

  function scrollByStep(direction: 1 | -1) {
    const el = scrollerRef.current
    if (!el) return
    const step = threePerView ? el.clientWidth : SCROLL_STEP_PX
    el.scrollBy({ left: direction * step, behavior: "smooth" })
  }

  return (
    <section className="mx-auto max-w-5xl px-4 py-6 sm:px-6">
      <div className="mb-3 flex items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 font-display text-lg font-semibold">
          {icon}
          {title}
        </h2>
        {/* Souris/clavier uniquement : sur tactile (pas de hover), le swipe natif du
            rail suffit déjà - deux flèches en plus n'y ajouteraient rien. */}
        <div className="hidden shrink-0 items-center gap-1 sm:flex">
          <Button
            variant="outline"
            size="icon"
            className="size-8 rounded-full"
            aria-label={`${title} - précédent`}
            disabled={!canScrollLeft}
            onClick={() => scrollByStep(-1)}
          >
            <ChevronLeft className="size-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="size-8 rounded-full"
            aria-label={`${title} - suivant`}
            disabled={!canScrollRight}
            onClick={() => scrollByStep(1)}
          >
            <ChevronRight className="size-4" />
          </Button>
        </div>
      </div>
      <div
        ref={scrollerRef}
        onScroll={updateScrollState}
        className="no-scrollbar -mx-4 flex snap-x snap-mandatory gap-4 overflow-x-auto scroll-smooth px-4 pb-2 sm:-mx-6 sm:px-6"
      >
        {epreuves.map((epreuve) => (
          <EpreuveCard
            key={`${epreuve.kind}-${epreuve.id}`}
            epreuve={epreuve}
            className={
              threePerView
                ? "w-72 shrink-0 snap-start sm:w-[calc((100%-2rem)/3)]"
                : "w-72 shrink-0 snap-start"
            }
          />
        ))}
      </div>
    </section>
  )
}
