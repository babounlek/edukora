import { formatDureeMinutes } from "@/lib/duration"
import { langueCourante, t, tn, type CleI18n } from "@/lib/i18n"

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

/** « 2h30 », « 2 h », « 2 heures », « 150 min » → un nombre de minutes ; null pour un texte libre (« 3 h maximum »). */
function minutesDeDuree(texte: string): number | null {
  const brut = texte.trim().toLowerCase()
  const heures = brut.match(/^(\d+)\s*(?:h|heures?|hours?)\s*(?:et\s*)?(\d{1,2})?\s*(?:min(?:utes?)?)?$/)
  if (heures) return Number(heures[1]) * 60 + Number(heures[2] ?? 0)
  const minutes = brut.match(/^(\d+)\s*(?:min(?:utes?)?|mn)$/)
  return minutes ? Number(minutes[1]) : null
}

/** « 2 heures » → « 2 hours » : la durée est un texte saisi à la transcription ; seuls les mots
 * français sont remplacés, « 2h » et « 90 min » passent tels quels. */
export function libelleDuree(texte: string): string {
  // Un seul format pour toutes les épreuves (« 2 h 30 », « 2 h », « 45 min ») : la liste mélangeait « 150 min », « 2h30 »,
  // « 2h00 » et « 2h » pour des durées voisines (test élève Gogo).
  const minutes = minutesDeDuree(texte)
  if (minutes !== null) return formatDureeMinutes(minutes)
  if (langueCourante() === "fr") return texte
  return texte.replace(/(\d+)\s*heures?/gi, (_m, n: string) => `${n} ${Number(n) === 1 ? "hour" : "hours"}`)
}

// Niveau d'un exercice d'application de cours : saisi en minuscules par le skill (facile / moyen /
// approfondissement), avec les variantes vues dans le corpus (moyenne, faible, élevée…).
const NIVEAUX_EXERCICE: Record<string, CleI18n> = {
  facile: "cs.niv_facile",
  faible: "cs.niv_facile",
  moyen: "cs.niv_moyen",
  moyenne: "cs.niv_moyen",
  approfondissement: "cs.niv_approfondissement",
  difficile: "cs.niv_difficile",
  eleve: "cs.niv_difficile",
  elevee: "cs.niv_difficile",
}

/** « approfondissement » → « Challenge » en anglais ; en français, la valeur saisie telle quelle (le badge la met en
 * capitale). Une valeur inconnue s'affiche brute plutôt que de disparaître. */
export function libelleNiveauExercice(niveau: string): string {
  if (langueCourante() === "fr") return niveau
  const code = niveau.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase().trim()
  return NIVEAUX_EXERCICE[code] ? t(NIVEAUX_EXERCICE[code]) : niveau
}

// « **Exercice 3 (7 points)** » : l'en-tête que la transcription met en tête d'un exercice (voir
// EpreuveExercise.enonce_intro_markdown). Les épreuves GCE l'ont reçu en français ; en anglais on le réécrit à
// l'affichage (« Exercise 3 (7 marks) »). Seulement s'il est tel quel en début de texte : le reste du préambule
// (la consigne de l'exercice) n'est jamais touché.
const ENTETE_EXERCICE = /^\*\*Exercice\s+([^\s()*]+)\s*(?:\((\d+(?:[.,]\d+)?)\s*points?\))?\*\*/

export function libelleEnteteExercice(markdown: string): string {
  if (langueCourante() === "fr") return markdown
  return markdown.replace(ENTETE_EXERCICE, (_tout, exercice: string, points: string | undefined) =>
    // Sans barème (« **Exercice 1** ») : « Exercise 1 » seul.
    points === undefined
      ? `**${t("ed.exercice_n", { n: exercice })}**`
      : `**${tn("ed.entete_exercice", Number(points.replace(",", ".")), { ex: exercice })}**`,
  )
}

const TITRE_EXERCICE = /^Exercice\s+(\S+)$/

/** Le titre d'un exercice (« Exercice 4 ») tel que le serveur l'a lu dans l'énoncé : un contenu anglais (GCE) porte
 * parfois l'en-tête français des données. Hors français, « Exercise 4 ». Les autres titres sont gardés tels quels. */
export function libelleTitreExercice(titre: string): string {
  if (langueCourante() === "fr") return titre
  const trouve = TITRE_EXERCICE.exec(titre.trim())
  return trouve ? t("ed.exercice_n", { n: trouve[1] }) : titre
}

export const libelleType = (code: string | null | undefined, affiche: string) => traduit(TYPES, code, affiche)
export const libelleOrigine = (code: string | null | undefined, affiche: string) => traduit(ORIGINES, code, affiche)
export const libelleNature = (code: string | null | undefined, affiche: string) => traduit(NATURES, code, affiche)
