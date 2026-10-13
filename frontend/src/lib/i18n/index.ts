/**
 * Internationalisation de l'interface (français / anglais) - décision du 2026-10-13, pour accueillir
 * le GCE (sous-système anglophone).
 *
 * Volontairement maison plutôt que react-i18next : l'app tient à son poids de départ (réseaux
 * lents, mode économie de données) et n'a besoin que de clés, de variables et de pluriels. Le
 * français est dans le paquet principal (fr.ts) ; l'anglais est un import dynamique, jamais
 * téléchargé par qui n'en veut pas.
 *
 * Deux façons de traduire :
 *  - dans un composant : `const { t, tn } = useI18n()` - se redessine au changement de langue ;
 *  - hors composant (formateurs, libellés) : `t(...)` directement, qui lit la langue courante.
 *
 * La langue est choisie par l'élève (sélecteur), gardée dans localStorage et, connecté, sur son
 * compte (User.langue). Un visiteur anonyme est en français tant qu'il n'a pas choisi : pas de
 * détection par le navigateur - décision du 2026-10-13.
 */
import { useSyncExternalStore } from "react"

import { fr, type CleAvecPluriel, type CleI18n } from "./fr"

export type { CleI18n, CleAvecPluriel } from "./fr"

export type Langue = "fr" | "en"
export const LANGUES: readonly Langue[] = ["fr", "en"]
export const LANGUE_STORAGE_KEY = "edukamer_langue"

type Dictionnaire = Partial<Record<CleI18n, string>>
type Variables = Record<string, string | number>

let langue: Langue = "fr"
// Surcharge de la langue active ; vide en français (la source fr.ts suffit).
let surcharge: Dictionnaire = {}
// Incrémenté à chaque changement : l'instantané que lit useSyncExternalStore.
let version = 0
const abonnes = new Set<() => void>()

export function estLangue(valeur: unknown): valeur is Langue {
  return valeur === "fr" || valeur === "en"
}

/** La langue gardée par ce navigateur, ou null (rien de choisi, ou stockage indisponible). */
export function langueStockee(): Langue | null {
  try {
    const valeur = localStorage.getItem(LANGUE_STORAGE_KEY)
    return estLangue(valeur) ? valeur : null
  } catch {
    return null
  }
}

async function chargerSurcharge(cible: Langue): Promise<Dictionnaire> {
  return cible === "en" ? (await import("./en")).en : {}
}

/**
 * Bascule la langue. Le dictionnaire est chargé AVANT de basculer : l'interface passe d'une langue
 * à l'autre d'un coup, sans trou en français entre les deux. Rejette si le chargement échoue (réseau) ;
 * la langue précédente reste alors en place.
 */
export async function definirLangue(cible: Langue, options: { persister?: boolean } = {}): Promise<void> {
  if (!estLangue(cible)) return
  const dictionnaire = await chargerSurcharge(cible)
  langue = cible
  surcharge = dictionnaire
  version += 1
  if (options.persister ?? true) {
    try {
      localStorage.setItem(LANGUE_STORAGE_KEY, cible)
    } catch {
      /* stockage indisponible (navigation privée...) : le choix vaut pour cette session */
    }
  }
  if (typeof document !== "undefined") document.documentElement.lang = cible
  abonnes.forEach((notifier) => notifier())
}

/** À appeler avant le premier rendu : applique la langue gardée, sans flash de français. */
export async function initialiserLangue(): Promise<void> {
  const gardee = langueStockee()
  if (!gardee || gardee === "fr") return
  try {
    await definirLangue(gardee, { persister: false })
  } catch {
    /* anglais injoignable : on reste en français plutôt que de bloquer l'app */
  }
}

export function langueCourante(): Langue {
  return langue
}

function interpoler(gabarit: string, variables?: Variables): string {
  if (!variables) return gabarit
  return gabarit.replace(/\{(\w+)\}/g, (brut, nom: string) => (nom in variables ? String(variables[nom]) : brut))
}

/** Texte d'une clé dans la langue courante ; à défaut de traduction, le français. */
export function t(cle: CleI18n, variables?: Variables): string {
  return interpoler(surcharge[cle] ?? fr[cle], variables)
}

/** Pluriel : lit `<base>_one` ou `<base>_other` selon `n` ; `{n}` est toujours disponible. */
export function tn(base: CleAvecPluriel, n: number, variables?: Variables): string {
  const categorie = new Intl.PluralRules(langue).select(n) === "one" ? "one" : "other"
  return t(`${base}_${categorie}` as CleI18n, { n, ...variables })
}

/** Locale BCP 47 pour Intl (dates, mois) dans la langue courante. */
export function localeCourante(): string {
  return langue === "en" ? "en-GB" : "fr-FR"
}

function abonner(notifier: () => void): () => void {
  abonnes.add(notifier)
  return () => {
    abonnes.delete(notifier)
  }
}

/** Dans un composant : donne `t`/`tn` et redessine le composant quand la langue change. */
export function useI18n() {
  useSyncExternalStore(abonner, () => version)
  return { t, tn, langue, setLangue: definirLangue }
}
