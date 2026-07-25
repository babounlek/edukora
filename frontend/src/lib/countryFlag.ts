/**
 * Emoji drapeau à partir d'un code ISO 3166-1 alpha-2 (ex: "cm" -> "🇨🇲") - dérivé à la
 * volée via les Regional Indicator Symbols Unicode, sans donnée à stocker ni maintenir.
 */
export function countryFlagEmoji(code: string): string {
  const upper = code.toUpperCase()
  if (upper.length !== 2) return ""
  const codePoints = [...upper].map((char) => 0x1f1e6 + (char.charCodeAt(0) - 65))
  return String.fromCodePoint(...codePoints)
}
