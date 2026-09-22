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

export function catalogueHomePath(country: string): string {
  return `/${country}`
}

// Page de recherche/filtrage du catalogue complet - distincte de l'accueil depuis la
// scission accueil/catalogue (l'accueil ne montre plus qu'un aperçu). Même segment
// que epreuveDetailPath/epreuveReaderPath ci-dessous, sans slug : la liste est la
// racine naturelle de ce sous-chemin.
export function epreuvesListPath(country: string): string {
  return `/${country}/epreuves`
}

export function coursListPath(country: string): string {
  return `/${country}/cours`
}

// Page dédiée au classement complet des thèmes fréquents (voir ThemesFrequents.tsx,
// qui n'en montre qu'un aperçu tronqué sur /epreuves) - utilisable seule, avec ses
// propres filtres matière/cursus en query params, pas seulement depuis l'aperçu.
export function themesFrequentsPath(country: string): string {
  return `/${country}/themes-frequents`
}

// Exercices concernés par un thème précis (voir ThemeExercicesPage) - id de Tag dans
// l'URL, pas son nom : évite tout souci d'encodage/collision sur des noms de thème qui
// contiennent des espaces ou des caractères accentués.
export function themeExercicesPath(country: string, tagId: number): string {
  return `/${country}/themes-frequents/${tagId}/exercices`
}

export function epreuveDetailPath(country: string, slug: string): string {
  return `/${country}/epreuves/${slug}`
}

export function epreuveReaderPath(country: string, slug: string): string {
  return `/${country}/epreuves/${slug}/lire`
}

// Pas de lecteur direct pour une épreuve inédite (contrairement à epreuveReaderPath) -
// composer une épreuve inédite crée une tentative (POST), jamais un simple GET, donc
// la fiche détail reste toujours l'étape intermédiaire, accès ou non (voir
// EpreuveInediteDetailPage.tsx).
// slugOrId : le slug (voir EpreuveInedite.slug, motif SEO/partage - même raison que
// epreuveDetailPath ci-dessus) si connu, sinon un repli sur l'id numérique - jamais
// un lien cassé pour un appelant qui n'a encore que l'id (voir EpreuveInediteListItem,
// qui n'expose pas de slug).
export function epreuveInediteDetailPath(country: string, slugOrId: string | number): string {
  return `/${country}/epreuves-inedites/${slugOrId}`
}

// Pas de préfixe pays ici (contrairement aux épreuves ci-dessus) - seule la forme
// slug a été demandée pour les URLs de Cours, voir l'audit UX.
export function coursDetailPath(slug: string): string {
  return `/cours/${slug}`
}

export function coursReaderPath(slug: string): string {
  return `/cours/${slug}/lire`
}
