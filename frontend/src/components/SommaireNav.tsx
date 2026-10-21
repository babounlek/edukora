import { useEffect, useRef, useState, type MouseEvent } from "react"

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
  /**
   * Repères de groupe englobant cette entrée, du plus large au plus précis
   * ("Partie A", "I. Activités Numériques") - absent ou vide pour une entrée hors
   * de tout groupe (comportement plat inchangé, voir EpreuveSommaire). Ignoré par le
   * scrollspy et la barre mobile (voir buildSidebarRows) : seule la sidebar desktop
   * matérialise ce chemin en en-têtes non cliquables.
   */
  groupPath?: string[]
}

interface SidebarRow {
  key: string
  depth: number
  label: string
  entry?: SommaireEntry
}

/**
 * Aplati `entries` en lignes de sidebar (en-tête de groupe non cliquable + entrée),
 * en n'insérant un en-tête que lorsque le chemin de groupe change par rapport à
 * l'entrée précédente - deux entrées consécutives du même groupe ne le répètent
 * donc pas (voir EpreuveSommaire, "Partie A" > "I." > Exercice 1/2 : le groupe
 * n'apparaît qu'une fois, pas devant chaque exercice qu'il contient).
 */
function buildSidebarRows(entries: SommaireEntry[]): SidebarRow[] {
  const rows: SidebarRow[] = []
  let precedent: string[] = []
  entries.forEach((entry, index) => {
    const chemin = entry.groupPath ?? []
    let commun = 0
    while (commun < chemin.length && commun < precedent.length && chemin[commun] === precedent[commun]) {
      commun += 1
    }
    for (let profondeur = commun; profondeur < chemin.length; profondeur += 1) {
      rows.push({ key: `${entry.id}-groupe-${index}-${profondeur}`, depth: profondeur, label: chemin[profondeur] })
    }
    rows.push({ key: entry.id, depth: chemin.length, label: entry.long, entry })
    precedent = chemin
  })
  return rows
}

/**
 * Un clic sur le sommaire fait défiler jusqu'à la section et met l'adresse à jour SANS ajouter d'entrée à l'historique :
 * avec le comportement natif d'une ancre, chaque clic en ajoutait une et « Retour » demandait plusieurs essais pour quitter
 * le cours (test élève Gogo). Sans cible dans la page, le lien natif reprend la main.
 */
function allerALaSection(evenement: MouseEvent<HTMLAnchorElement>, id: string) {
  const cible = document.getElementById(id)
  if (!cible) return
  evenement.preventDefault()
  const reduit = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
  cible.scrollIntoView({ behavior: reduit ? "auto" : "smooth", block: "start" })
  window.history.replaceState(window.history.state, "", `#${id}`)
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
 * suffisante pour ne pas passer sous le Header sticky (72 px) ni, sous `lg`, sous la barre
 * de pastilles qui le prolonge (≈ 57 px) : scroll-mt-36 en dessous de `lg`, scroll-mt-24 au-delà.
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

  const rows = buildSidebarRows(entries)

  return (
    <>
      {/* Mobile/tablette : pastilles sticky, défilement horizontal. top-[72px] = la hauteur
          exacte du Header collant (z-40, même hauteur en mobile et en desktop, voir Header.tsx) :
          avec top-0, la barre se collait SOUS le header et ses pastilles étaient recouvertes. */}
      <nav
        aria-label={ariaLabel}
        className="not-prose sticky top-[72px] z-10 -mx-4 mb-6 overflow-x-auto border-b border-border bg-background/95 px-4 py-2.5 backdrop-blur sm:-mx-6 sm:px-6 lg:hidden"
      >
        <ul className="flex w-max gap-1.5">
          {entries.map((entry) => (
            <li key={entry.id}>
              <a
                href={`#${entry.id}`}
                onClick={(e) => allerALaSection(e, entry.id)}
                aria-current={activeId === entry.id ? "true" : undefined}
                className={cn(
                  "flex min-h-9 items-center whitespace-nowrap rounded-full border px-3.5 py-1 text-xs font-medium transition-colors",
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

      {/* Desktop : sidebar persistante avec surbrillance de la section en cours. Les
          en-têtes de groupe (voir buildSidebarRows) ne sont jamais des ancres : pas de
          lien, juste un séparateur visuel indenté selon sa profondeur. */}
      <nav aria-label={ariaLabel} className="not-prose sticky top-20 hidden self-start lg:block">
        <ul className="flex flex-col gap-1 border-l border-border pl-3">
          {rows.map((row) =>
            !row.entry ? (
              <li
                key={row.key}
                style={{ paddingLeft: row.depth * 12 }}
                className="truncate pt-2.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground/80 first:pt-0"
              >
                {row.label}
              </li>
            ) : (
              <li key={row.key} style={{ paddingLeft: row.depth * 12 }}>
                <a
                  href={`#${row.entry.id}`}
                  onClick={(e) => allerALaSection(e, row.entry!.id)}
                  aria-current={activeId === row.entry.id ? "true" : undefined}
                  title={row.entry.title ?? row.entry.long}
                  className={cn(
                    "block truncate py-1 text-sm transition-colors",
                    activeId === row.entry.id
                      ? "font-medium text-primary"
                      : "text-muted-foreground hover:text-foreground",
                  )}
                >
                  {row.entry.long}
                </a>
              </li>
            ),
          )}
        </ul>
      </nav>
    </>
  )
}
