import type { Cursus } from "@/api/types"
import { langueCourante } from "@/lib/i18n"

/** Joint des éléments à la française : "C", "C et E", "C, D et E". */
function joinFr(items: string[]): string {
  if (items.length <= 1) return items.join("")
  if (items.length === 2) return items.join(" et ")
  return `${items.slice(0, -1).join(", ")} et ${items[items.length - 1]}`
}

// Ordre pédagogique (collège -> intermédiaire -> lycée), pas alphabétique : le champ
// `examen` trie autrement ("BAC" < "BEPC" < "PROBATOIRE").
// Le GCE (sous-système anglophone) suit les trois diplômes francophones : un code absent de
// cette liste (indexOf = -1) passerait sinon en tête.
export const EXAMEN_ORDER = ["BEPC", "PROBATOIRE", "BAC", "GCE_OL", "GCE_AL", "AUTRE"]

/**
 * Les cursus dans l'ordre du parcours scolaire (BEPC, Probatoire, BAC, puis le GCE), puis par série. L'API les renvoie
 * dans l'ordre alphabétique du champ `examen` (« BAC » < « BEPC »), qui ouvrait une rangée de pastilles sur « BAC A » et
 * reléguait le BEPC en sixième position (test élève P1). Ne modifie pas la liste reçue.
 */
export function trierCursus<T extends { examen: string; series: { code: string } | null }>(liste: T[]): T[] {
  const rang = (examen: string) => {
    const i = EXAMEN_ORDER.indexOf(examen)
    return i === -1 ? EXAMEN_ORDER.length : i
  }
  return [...liste].sort(
    (a, b) => rang(a.examen) - rang(b.examen) || (a.series?.code ?? "").localeCompare(b.series?.code ?? ""),
  )
}

/** Le cursus relève-t-il du GCE (sous-système anglophone) ? Pas de séries : on y choisit ses matières. */
export function estGce(cursus: { examen: string } | null | undefined): boolean {
  return cursus?.examen === "GCE_OL" || cursus?.examen === "GCE_AL"
}

/** Les séries du GCE (branche technique) s'écrivent par leur libellé court (« Technical »), pas par leur code interne. */
export function codeSerieAffiche(series: { code: string; label: string }): string {
  return series.code.startsWith("GCE_") ? series.label : series.code
}

/**
 * Diplômes réellement présents dans cette liste de cursus, dédupliqués par code
 * interne (`examen`) et triés dans l'ordre pédagogique - jamais un texte fixe : la
 * plupart des pays n'ont pas de Probatoire, et certains renomment un niveau (BFEM au
 * lieu de BEPC au Sénégal) - voir `examen_display`, déjà résolu par pays côté API.
 */
export function examCodesFor(cursus: Cursus[]): { code: string; label: string }[] {
  const byCode = new Map<string, string>()
  for (const c of cursus) {
    if (!byCode.has(c.examen)) byCode.set(c.examen, c.examen_display)
  }
  return Array.from(byCode.entries())
    .sort(([a], [b]) => EXAMEN_ORDER.indexOf(a) - EXAMEN_ORDER.indexOf(b))
    .map(([code, label]) => ({ code, label }))
}

/** « Série C » / « Séries C, D et E » pour l'en-tête d'une épreuve ou d'un cours : le libellé accordé
 * par l'API, ou à défaut `Série` + la liste brute (réponse d'un backend plus ancien). */
export function libelleSerieEntete(header: { serie: string | null; serie_libelle?: string | null }): string | null {
  return traduireLibelleSerie(header.serie_libelle ?? (header.serie ? `Série ${header.serie}` : null))
}

/** « BAC - Série A », « Séries C, D et E » : libellés de série rédigés en français par l'API,
 * traduits ici hors français (seuls les mots « Série(s) » et « et » changent). */
export function traduireLibelleSerie<T extends string | null | undefined>(libelle: T): T {
  if (!libelle || langueCourante() === "fr") return libelle
  return libelle.replace(/\bSéries\b/g, "Series").replace(/\bSérie\b/g, "Series").replace(/ et (?=[A-Z]{1,2}\b)/g, " and ") as T
}

/** Mêmes niveaux que `examCodesFor`, sans le code interne (ex: badges d'affichage). */
export function examLevelsFor(cursus: Cursus[]): string[] {
  return examCodesFor(cursus).map((e) => e.label)
}

/** "le BEPC, le Probatoire et le BAC" - pour une phrase en prose (ex: meta description). */
export function joinExamLevelsFr(levels: string[]): string {
  return joinFr(levels.map((level) => `le ${level}`))
}

/** Comme `joinExamLevelsFr`, dans la langue courante : "the BEPC, the Probatoire and the BAC" en anglais. */
export function joinExamLevelsProse(levels: string[]): string {
  if (langueCourante() !== "en") return joinExamLevelsFr(levels)
  return new Intl.ListFormat("en-GB", { style: "long", type: "conjunction" }).format(levels.map((level) => `the ${level}`))
}

/**
 * Regroupe les cursus par examen pour ne pas répéter le diplôme quand une épreuve
 * concerne plusieurs séries : "BAC C et E" plutôt que deux badges "BAC C" / "BAC E".
 */
export function formatCursusGroups(cursus: Cursus[]): { key: string; label: string }[] {
  const groups = new Map<string, { examenDisplay: string; series: string[] }>()

  for (const c of cursus) {
    if (!groups.has(c.examen)) groups.set(c.examen, { examenDisplay: c.examen_display, series: [] })
    if (c.series) groups.get(c.examen)!.series.push(codeSerieAffiche(c.series))
  }

  return Array.from(groups.entries()).map(([examen, { examenDisplay, series }]) => ({
    key: examen,
    label: series.length > 0 ? `${examenDisplay} ${joinFr(series)}` : examenDisplay,
  }))
}
