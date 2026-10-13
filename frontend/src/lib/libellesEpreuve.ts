import { langueCourante, t, type CleI18n } from "@/lib/i18n"

/**
 * Libellés d'une épreuve que le serveur renvoie déjà rédigés en français (`lesson_type_display`,
 * `origine_display`, `nature_epreuve_display`) : en français on les garde tels quels, source de
 * vérité du backend ; dans une autre langue on les retrouve par leur code. Un code inconnu retombe
 * sur le texte du serveur plutôt que de rien afficher.
 */

const TYPES: Record<string, CleI18n> = {
  FICHE: "ep.type_FICHE",
  CORR: "ep.type_CORR",
  SUJET: "ep.type_SUJET",
}

const ORIGINES: Record<string, CleI18n> = {
  OFFICIEL: "ep.origine_OFFICIEL",
  BLANC: "ep.origine_BLANC",
  ETABLISSEMENT: "ep.origine_ETABLISSEMENT",
  AUTRE: "ep.origine_AUTRE",
  SUJET_ZERO: "ep.origine_SUJET_ZERO",
  INEDITE: "ep.origine_INEDITE",
}

const NATURES: Record<string, CleI18n> = {
  THEORIQUE: "ep.nature_THEORIQUE",
  PRATIQUE: "ep.nature_PRATIQUE",
}

function traduit(table: Record<string, CleI18n>, code: string | null | undefined, affiche: string): string {
  if (langueCourante() === "fr" || !code || !table[code]) return affiche
  return t(table[code])
}

/** « 2 heures » → « 2 hours » : la durée est un texte saisi à la transcription ; seuls les mots
 * français sont remplacés, « 2h » et « 90 min » passent tels quels. */
export function libelleDuree(texte: string): string {
  if (langueCourante() === "fr") return texte
  return texte.replace(/(\d+)\s*heures?/gi, (_m, n: string) => `${n} ${Number(n) === 1 ? "hour" : "hours"}`)
}

export const libelleType = (code: string | null | undefined, affiche: string) => traduit(TYPES, code, affiche)
export const libelleOrigine = (code: string | null | undefined, affiche: string) => traduit(ORIGINES, code, affiche)
export const libelleNature = (code: string | null | undefined, affiche: string) => traduit(NATURES, code, affiche)
