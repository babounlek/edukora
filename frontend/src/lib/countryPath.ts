/**
 * Forme des URLs par pays (`/cm`, `/cm/cours`, ...) - point d'entrée unique pour ce
 * schéma, pour qu'un changement de convention ne touche qu'un seul fichier.
 */

export const DEFAULT_COUNTRY_CODE = "cm"
export const COUNTRY_STORAGE_KEY = "edukamer_country"

const COUNTRY_SEGMENT_RE = /^\/([a-z]{2})(\/|$)/

/** Extrait le code pays du premier segment d'un chemin (`/cm/cours` -> "cm"), ou null. */
export function extractCountryFromPath(pathname: string): string | null {
  return COUNTRY_SEGMENT_RE.exec(pathname)?.[1] ?? null
}

/** Remplace le segment pays d'un chemin déjà préfixé ; sans préfixe, retourne le chemin tel quel. */
export function replaceCountryInPath(pathname: string, newCountry: string): string {
  return COUNTRY_SEGMENT_RE.test(pathname)
    ? pathname.replace(COUNTRY_SEGMENT_RE, `/${newCountry}$2`)
    : pathname
}

export function catalogueHomePath(country: string): string {
  return `/${country}`
}

export function coursListPath(country: string): string {
  return `/${country}/cours`
}
