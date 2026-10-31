import { t, type CleI18n } from "@/lib/i18n"

/**
 * Interrupteur de la mascotte de l'écran de résultat de quiz (proposition C1 de la synthèse Guyguy du 2026-10-25).
 * Le registre de langue (« grand frère ») doit être validé avec de vrais élèves de Douala et Yaoundé avant d'être
 * généralisé : tant que ce n'est pas fait, on peut la couper d'un seul endroit. Le frontend est un build statique :
 * changer la valeur demande un rebuild de l'image caddy (`VITE_MASCOTTE=0` à la construction suffit, sans toucher au code).
 */
export const MASCOTTE_ACTIVE = import.meta.env.VITE_MASCOTTE !== "0"

export type SituationMascotte = "record" | "serie" | "succes" | "moyen" | "faible"

/** Nombre de variantes de phrase par situation dans fr.ts / en.ts (clés `mascotte.<situation>_1` à `_N`). */
export const VARIANTES_MASCOTTE = 3

/** Série de jours à partir de laquelle la mascotte la relève. */
export const SERIE_MASCOTTE_MIN = 3

export interface ContexteMascotte {
  pourcentage: number
  recordBattu?: boolean
  /** Série de jours en cours (élève connecté seulement). */
  serieJours?: number
}

/** La situation la plus parlante d'abord : un record ou une série valent mieux qu'un simple pourcentage. */
export function situationMascotte({ pourcentage, recordBattu, serieJours }: ContexteMascotte): SituationMascotte {
  if (recordBattu) return "record"
  if (serieJours !== undefined && serieJours >= SERIE_MASCOTTE_MIN) return "serie"
  if (pourcentage >= 70) return "succes"
  if (pourcentage >= 40) return "moyen"
  return "faible"
}

/** Une phrase au hasard parmi les variantes de la situation ; `hasard` (dans [0, 1[) est injectable pour les tests. */
export function phraseMascotte(situation: SituationMascotte, contexte: ContexteMascotte, hasard = Math.random()): string {
  const rang = Math.min(VARIANTES_MASCOTTE, Math.floor(hasard * VARIANTES_MASCOTTE) + 1)
  return t(`mascotte.${situation}_${rang}` as CleI18n, { n: contexte.serieJours ?? 0 })
}

/** L'humeur du dessin pour chaque situation (voir .mascotte-* dans index.css). */
export type HumeurMascotte = "fete" | "content" | "courage"

export function humeurMascotte(situation: SituationMascotte): HumeurMascotte {
  if (situation === "record" || situation === "serie") return "fete"
  return situation === "succes" ? "content" : "courage"
}

export type SituationJourMascotte = "atteint" | "serie" | "debut" | "reste"

/** Variantes de rappel par situation du jour (clés `mascotte.jour_<situation>_1` à `_N`). */
export const VARIANTES_JOUR_MASCOTTE = 2

/** Où en est l'élève aujourd'hui : objectif atteint, série en cours, rien encore fait, ou il reste des points. */
export function situationJourMascotte(etat: { xp: number; atteint: boolean }, serie: { jours: number }): SituationJourMascotte {
  if (etat.atteint) return "atteint"
  if (serie.jours >= SERIE_MASCOTTE_MIN) return "serie"
  return etat.xp === 0 ? "debut" : "reste"
}

/** Le rappel simple de l'accueil : jamais de reproche, seulement ce qu'il reste à aller chercher. */
export function phraseJourMascotte(
  situation: SituationJourMascotte, etat: { xp: number; objectif: number }, serie: { jours: number }, hasard = Math.random(),
): string {
  const rang = Math.min(VARIANTES_JOUR_MASCOTTE, Math.floor(hasard * VARIANTES_JOUR_MASCOTTE) + 1)
  return t(`mascotte.jour_${situation}_${rang}` as CleI18n, { n: serie.jours, reste: Math.max(0, etat.objectif - etat.xp) })
}
