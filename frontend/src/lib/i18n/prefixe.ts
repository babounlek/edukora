/**
 * La langue dans l'URL : le français n'a pas de préfixe (`/cm/epreuves`, les liens déjà en circulation
 * restent valides), l'anglais est sous `/en` ET a ses propres segments (`/en/cm/past-papers`, voir
 * segments.ts). Une URL dit donc la langue de la page : un lien anglais partagé s'ouvre en anglais
 * chez le destinataire, quelle que soit sa préférence, et les moteurs de recherche voient deux pages
 * distinctes (voir BalisesDeRoute).
 *
 * Le routeur anglais (historiqueAnglais.ts) retire le préfixe et traduit les segments à la frontière :
 * tous les `<Link>`, `navigate()` et `<Navigate>` restent écrits avec le chemin INTERNE français et
 * aucun lien n'est à réécrire. Le préfixe est fixé au chargement de la page ; changer de langue
 * recharge la page sur l'URL de l'autre langue (voir ouvrirDansLangue).
 *
 * Vocabulaire : un chemin « interne » est celui du routeur (français, sans préfixe) ; une URL « publique »
 * est celle de la barre d'adresse. Pour tout ce qui sort du routeur (liens absolus, partage, canonical),
 * passer un chemin interne à `cheminDansLangue`.
 */
import { cheminAnglais, cheminInterne, separerCible } from "./segments"

export type LangueUrl = "fr" | "en"

export const PREFIXE_EN = "/en"

const PREFIXE_EN_RE = /^\/en(?=\/|$)/

/** Langue annoncée par un chemin complet (`/en/cm` -> "en"), ou null quand il n'a pas de préfixe. */
export function langueDuChemin(pathname: string): LangueUrl | null {
  return PREFIXE_EN_RE.test(pathname) ? "en" : null
}

/** Le chemin sans préfixe de langue (`/en/cm/cours` -> `/cm/cours`, `/en` -> `/`). */
export function retirerPrefixeLangue(pathname: string): string {
  const reste = pathname.replace(PREFIXE_EN_RE, "")
  return reste === "" ? "/" : reste
}

/** La `basename` du routeur pour une langue : "" en français, "/en" en anglais. */
export function basenameDeLangue(langue: LangueUrl): string {
  return langue === "en" ? PREFIXE_EN : ""
}

/**
 * Chemin INTERNE de l'application placé dans une langue : `("/cm/cours", "en")` -> `/en/cm/lessons`.
 * Pour tout ce qui sort du routeur : liens absolus, partage, canonical. Accepte une query et une ancre.
 * Idempotent pour le préfixe : un chemin déjà préfixé n'est pas préfixé deux fois (mais il doit rester
 * INTERNE : un chemin déjà traduit en anglais n'est pas retraduit, voir cheminInterneDepuisUrl).
 */
export function cheminDansLangue(chemin: string, langue: LangueUrl): string {
  const nu = retirerPrefixeLangue(chemin)
  if (langue !== "en") return nu
  const { pathname, reste } = separerCible(nu)
  const traduit = cheminAnglais(pathname)
  return `${traduit === "/" ? PREFIXE_EN : `${PREFIXE_EN}${traduit}`}${reste}`
}

/**
 * Le chemin interne d'un chemin PUBLIC (celui de la barre d'adresse) : `/en/cm/lessons` -> `/cm/cours`.
 * Un chemin français est déjà interne. À utiliser pour tout ce qui lit `window.location`.
 */
export function cheminInterneDepuisUrl(pathname: string): string {
  const nu = retirerPrefixeLangue(pathname)
  return langueDuChemin(pathname) === "en" ? cheminInterne(nu) : nu
}
