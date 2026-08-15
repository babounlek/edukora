import type { CoursSectionData } from "@/api/types"
import { COURS_SECTION_LABELS } from "@/components/CoursSection"
import { SommaireNav, type SommaireEntry } from "@/components/SommaireNav"

interface CoursSommaireProps {
  sections: CoursSectionData[]
}

/**
 * Sommaire de navigation dans un Cours - n'affiche que les types réellement présents
 * dans ce Cours (voir COURS_SECTION_LABELS, jamais "accroche" qui n'est pas une section
 * navigable). La présentation responsive (pastilles sticky / sidebar scrollspy) vit
 * dans SommaireNav, partagé avec le sommaire d'exercices d'une épreuve.
 *
 * `long` reprend volontairement le libellé court : la sidebar fait 200px, et les
 * libellés longs ("Ce qu'il faut retenir") y passeraient à la ligne.
 */
export function CoursSommaire({ sections }: CoursSommaireProps) {
  const entries: SommaireEntry[] = sections.flatMap((section) => {
    const label = COURS_SECTION_LABELS[section.type]
    return label ? [{ id: section.type, short: label.short, long: label.short }] : []
  })

  return <SommaireNav entries={entries} ariaLabel="Sommaire du cours" />
}
