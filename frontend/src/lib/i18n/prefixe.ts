/**
 * La langue dans l'URL : le français n'a pas de préfixe (`/cm/epreuves`, les liens déjà en circulation
 * restent valides), l'anglais est sous `/en` (`/en/cm/epreuves`). Une URL dit donc la langue de la
 * page : un lien anglais partagé s'ouvre en anglais chez le destinataire, quelle que soit sa
 * préférence, et les moteurs de recherche voient deux pages distinctes (voir BalisesDeRoute).
 *
 * Le préfixe est la `basename` du routeur (App.tsx) : tous les `<Link>`, `navigate()` et `<Navigate>`
 * l'ajoutent d'eux-mêmes, aucun lien n'est à réécrire. Il est donc fixé au chargement de la page ;
 * changer de langue recharge la page sur l'URL de l'autre langue (voir changerLangue).
 *
 * Ce module ne dépend de rien d'autre dans i18n : il est importable partout, y compris hors React.
 */

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
 * Chemin de l'application (sans préfixe) placé dans une langue : `("/cm/cours", "en")` ->
 * `/en/cm/cours`. Pour tout ce qui sort du routeur : liens absolus, partage, canonical.
 * Idempotent : un chemin déjà préfixé n'est pas préfixé deux fois.
 */
export function cheminDansLangue(chemin: string, langue: LangueUrl): string {
  const nu = retirerPrefixeLangue(chemin)
  if (langue !== "en") return nu
  return nu === "/" ? PREFIXE_EN : `${PREFIXE_EN}${nu}`
}
