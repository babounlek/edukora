import { useEffect, useRef, useState } from "react"

import { cn } from "@/lib/utils"

export interface SommaireEntry {
  /** id de l'élément cible dans la page - sert d'ancre (#id) et de clé de scrollspy. */
  id: string
  /** Libellé de la pastille sticky mobile, où la place est comptée ("Ex. 1"). */
  short: string
  /** Libellé de la sidebar desktop, plus descriptif ("Exercice 1 : Chimie organique"). */
  long: string
  /** Infobulle de la sidebar, quand `long` est déjà une version raccourcie. */
  title?: string
}

interface SommaireNavProps {
  entries: SommaireEntry[]
  ariaLabel: string
}

/**
 * Sommaire de navigation intra-page - sidebar avec scrollspy sur desktop, barre de
 * pastilles sticky en haut sur mobile (même liste, deux présentations responsive
 * plutôt que deux composants séparés). Générique : partagé par les sections d'un Cours
 * (voir CoursSommaire) et les exercices d'une épreuve (voir EpreuveSommaire), qui n'ont
 * en commun que "une liste de blocs ancrés dans la page courante".
 *
 * Chaque `id` doit exister dans le DOM et porter une marge de défilement (scroll-mt-*)
 * suffisante pour ne pas passer sous le Header sticky.
 */
export function SommaireNav({ entries, ariaLabel }: SommaireNavProps) {
  const [activeId, setActiveId] = useState<string | null>(entries[0]?.id ?? null)
  const observerRef = useRef<IntersectionObserver | null>(null)

  useEffect(() => {
    const elements = entries
      .map((entry) => document.getElementById(entry.id))
      .filter((el): el is HTMLElement => el !== null)
    if (elements.length === 0) return

    observerRef.current?.disconnect()
    const observer = new IntersectionObserver(
      (observed) => {
        const visible = observed.filter((o) => o.isIntersecting)
        if (visible.length === 0) return
        const topmost = visible.reduce((a, b) => (a.boundingClientRect.top < b.boundingClientRect.top ? a : b))
        setActiveId(topmost.target.id)
      },
      { rootMargin: "-15% 0px -70% 0px", threshold: 0 },
    )
    elements.forEach((el) => observer.observe(el))
    observerRef.current = observer
    return () => observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entries.map((entry) => entry.id).join("|")])

  if (entries.length === 0) return null

  return (
    <>
      {/* Mobile/tablette : pastilles sticky, défilement horizontal. */}
      <nav
        aria-label={ariaLabel}
        className="not-prose sticky top-0 z-10 -mx-4 mb-6 overflow-x-auto border-b border-border bg-background/95 px-4 py-2.5 backdrop-blur sm:-mx-6 sm:px-6 lg:hidden"
      >
        <ul className="flex w-max gap-1.5">
          {entries.map((entry) => (
            <li key={entry.id}>
              <a
                href={`#${entry.id}`}
                aria-current={activeId === entry.id ? "true" : undefined}
                className={cn(
                  "block whitespace-nowrap rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                  activeId === entry.id
                    ? "border-primary bg-primary text-primary-foreground"
                    : "border-border text-muted-foreground hover:text-foreground",
                )}
              >
                {entry.short}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      {/* Desktop : sidebar persistante avec surbrillance de la section en cours. */}
      <nav aria-label={ariaLabel} className="not-prose sticky top-20 hidden self-start lg:block">
        <ul className="flex flex-col gap-1 border-l border-border pl-3">
          {entries.map((entry) => (
            <li key={entry.id}>
              <a
                href={`#${entry.id}`}
                aria-current={activeId === entry.id ? "true" : undefined}
                title={entry.title ?? entry.long}
                className={cn(
                  "block truncate py-1 text-sm transition-colors",
                  activeId === entry.id
                    ? "font-medium text-primary"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {entry.long}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </>
  )
}
