import type { Cursus } from "@/api/types"

/** Joint des éléments à la française : "C", "C et E", "C, D et E". */
function joinFr(items: string[]): string {
  if (items.length <= 1) return items.join("")
  if (items.length === 2) return items.join(" et ")
  return `${items.slice(0, -1).join(", ")} et ${items[items.length - 1]}`
}

// Ordre pédagogique (collège -> intermédiaire -> lycée), pas alphabétique : le champ
// `examen` trie autrement ("BAC" < "BEPC" < "PROBATOIRE").
const EXAMEN_ORDER = ["BEPC", "PROBATOIRE", "BAC", "AUTRE"]

/**
 * Niveaux d'examen réellement présents dans cette liste de cursus, dédupliqués par
 * code interne (`examen`) et triés dans l'ordre pédagogique - jamais un texte fixe :
 * la plupart des pays n'ont pas de Probatoire, et certains renomment un niveau (BFEM
 * au lieu de BEPC au Sénégal) - voir `examen_display`, déjà résolu par pays côté API.
 */
export function examLevelsFor(cursus: Cursus[]): string[] {
  const byCode = new Map<string, string>()
  for (const c of cursus) {
    if (!byCode.has(c.examen)) byCode.set(c.examen, c.examen_display)
  }
  return Array.from(byCode.entries())
    .sort(([a], [b]) => EXAMEN_ORDER.indexOf(a) - EXAMEN_ORDER.indexOf(b))
    .map(([, display]) => display)
}

/** "le BEPC, le Probatoire et le BAC" - pour une phrase en prose (ex: meta description). */
export function joinExamLevelsFr(levels: string[]): string {
  return joinFr(levels.map((level) => `le ${level}`))
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
