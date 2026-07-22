import type { Cursus } from "@/api/types"

/** Joint des éléments à la française : "C", "C et E", "C, D et E". */
function joinFr(items: string[]): string {
  if (items.length <= 1) return items.join("")
  if (items.length === 2) return items.join(" et ")
  return `${items.slice(0, -1).join(", ")} et ${items[items.length - 1]}`
}

/**
 * Regroupe les cursus par examen pour ne pas répéter le diplôme quand une épreuve
 * concerne plusieurs séries : "BAC C et E" plutôt que deux badges "BAC C" / "BAC E".
 */
export function formatCursusGroups(cursus: Cursus[]): { key: string; label: string }[] {
  const groups = new Map<string, { examenDisplay: string; series: string[] }>()

  for (const c of cursus) {
    if (!groups.has(c.examen)) groups.set(c.examen, { examenDisplay: c.examen_display, series: [] })
    if (c.series) groups.get(c.examen)!.series.push(c.series.code)
  }

  return Array.from(groups.entries()).map(([examen, { examenDisplay, series }]) => ({
    key: examen,
    label: series.length > 0 ? `${examenDisplay} ${joinFr(series)}` : examenDisplay,
  }))
}
