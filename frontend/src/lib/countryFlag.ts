/**
 * Classe CSS `flag-icons` (ex: "fi fi-cm") pour afficher le drapeau d'un pays de façon
 * fiable partout - contrairement aux émojis drapeau (regional indicator symbols), que
 * Windows ne rend pas par défaut (police système Segoe UI Emoji sans ces glyphes,
 * contrairement à macOS/iOS/Android) : flag-icons s'appuie sur des SVG embarqués, pas
 * sur une police système.
 */
export function countryFlagClassName(code: string): string {
  return `fi fi-${code.toLowerCase()}`
}
