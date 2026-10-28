import { useCallback, useEffect, useId, useRef, useState, type ReactNode, type RefObject } from "react"
import { ChevronDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * Les deux briques de filtre partagées par /epreuves et /cours : les deux catalogues doivent
 * se piloter de la même façon, donc se composer des mêmes pièces.
 */

/**
 * Une rangée de pastilles qui défile sur téléphone et passe à la ligne dès `sm`. Une rangée qui défile ne dit pas qu'elle
 * défile : un enfant ne devinait pas qu'il y avait d'autres matières (ou d'autres examens) après la troisième pastille.
 * Deux indices, sur téléphone seulement : un fondu à droite tant qu'il reste de la suite, et un bouton « Tout voir »
 * (voir BoutonToutVoir) qui déplie la rangée sur plusieurs lignes, « Réduire » la remettant sur une seule.
 *
 * Utilisé par FiltreLigne (catalogues) et par le bandeau « Choisis ton examen » : même geste partout.
 */
const FONDU_DROITE = "[mask-image:linear-gradient(to_right,black_calc(100%-2.5rem),transparent)]"

/**
 * Le fondu seul : pour une barre qui défile à toutes les largeurs (barre des exercices, sommaire d'un cours), sans « Tout voir ».
 * Renvoie `fondu` (classe à poser sur le conteneur qui défile, vide quand tout est visible ou en bout de course) et `onScroll`.
 * `actif` à faux gèle la mesure (rangée dépliée).
 */
export function useFonduDefilement(ref: RefObject<HTMLElement | null>, actif = true) {
  const [deborde, setDeborde] = useState(false)
  const [fin, setFin] = useState(true)

  const mesurer = useCallback(() => {
    const element = ref.current
    // Dépliée, une rangée passe à la ligne et ne déborde plus : on garde alors la dernière mesure pour que « Réduire » reste là.
    if (!element || !actif) return
    setDeborde(element.scrollWidth > element.clientWidth + 1)
    setFin(element.scrollLeft + element.clientWidth >= element.scrollWidth - 2)
  }, [ref, actif])

  // Le contenu arrive après le chargement des données : on mesure à chaque rendu (un état identique ne refait pas de rendu),
  // et quand la largeur change (rotation du téléphone).
  useEffect(() => {
    mesurer()
    const element = ref.current
    if (!element || typeof ResizeObserver === "undefined") return
    const observateur = new ResizeObserver(mesurer)
    observateur.observe(element)
    // Le contenu peut s'élargir sans que le conteneur change de taille (un compteur qui arrive dans un bouton) : on observe
    // aussi ses enfants directs.
    Array.from(element.children).forEach((enfant) => observateur.observe(enfant))
    return () => observateur.disconnect()
  })

  return { deborde, fin, onScroll: mesurer, fondu: deborde && !fin ? FONDU_DROITE : "" }
}

export function useRangeeDefilante() {
  const ref = useRef<HTMLDivElement>(null)
  const id = useId()
  const [deplie, setDeplie] = useState(false)
  const { deborde, fin, onScroll } = useFonduDefilement(ref, !deplie)

  return {
    ref,
    id,
    deborde,
    deplie,
    onScroll,
    basculer: () => setDeplie((d) => !d),
    /** Les classes de la rangée : `base` porte la mise en page propre à l'appelant (marges, écarts). */
    classe: (base: string) =>
      cn(
        base,
        "sm:flex-wrap sm:overflow-visible sm:pb-0",
        deplie ? "flex-wrap" : "overflow-x-auto pb-1.5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden",
        deborde && !fin && !deplie && `${FONDU_DROITE} sm:[mask-image:none]`,
      ),
  }
}

/** « Tout voir » / « Réduire » : n'apparaît que sur téléphone, et seulement si la rangée déborde. */
export function BoutonToutVoir({ rangee }: { rangee: ReturnType<typeof useRangeeDefilante> }) {
  useI18n()
  if (!rangee.deborde && !rangee.deplie) return null
  return (
    <button
      type="button"
      onClick={rangee.basculer}
      aria-expanded={rangee.deplie}
      aria-controls={rangee.id}
      className="inline-flex shrink-0 items-center gap-1 text-xs font-semibold text-primary sm:hidden"
    >
      {rangee.deplie ? t("gl.reduire") : t("gl.tout_voir")}
      <ChevronDown className={cn("size-3.5 transition-transform", rangee.deplie && "rotate-180")} aria-hidden="true" />
    </button>
  )
}

/**
 * Une rangée de filtres avec son titre. Sur téléphone, une seule ligne qu'on fait glisser
 * (six lignes de pastilles à traverser repoussaient les résultats sous le pli), avec de quoi comprendre qu'elle
 * glisse ; dès `sm`, elle passe à la ligne et tout reste visible - jamais de carrousel à la souris, dont la
 * molette ne défile pas horizontalement.
 */
export function FiltreLigne({ titre, children }: { titre: string; children: ReactNode }) {
  useI18n()
  const rangee = useRangeeDefilante()
  const dernierActif = useRef<Element | null>(null)
  // La pastille choisie était parfois hors de l'écran dans cette rangée qui défile (la matière « Mathematics » présélectionnée,
  // cachée à gauche : test élève Gogo). On la ramène au centre de la rangée UNE fois par choix, sans jamais toucher à la page ni
  // reprendre la main sur un élève qui fait glisser la rangée lui-même.
  useEffect(() => {
    const element = rangee.ref.current
    const actif = element?.querySelector<HTMLElement>('[aria-pressed="true"]')
    if (!element || !actif || actif === dernierActif.current) return
    dernierActif.current = actif
    if (element.scrollWidth <= element.clientWidth || typeof element.scrollTo !== "function") return
    element.scrollTo({ left: Math.max(0, actif.offsetLeft - element.clientWidth / 2 + actif.clientWidth / 2) })
  })
  return (
    <div className="mt-4">
      <div className="mb-1.5 flex items-center justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">{titre}</p>
        <BoutonToutVoir rangee={rangee} />
      </div>
      <div
        ref={rangee.ref}
        id={rangee.id}
        role="group"
        aria-label={t("gl.filtrer_par", { titre: titre.toLowerCase() })}
        onScroll={rangee.onScroll}
        className={rangee.classe("-mx-1 flex gap-1.5 px-1")}
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
