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
 *
 * Depuis le 2026-10-14, la langue est aussi dans l'URL (voir prefixe.ts) : `/en/...` est la version
 * anglaise, sans préfixe la française. Le préfixe l'emporte sur le choix mémorisé - c'est ce qui rend
 * un lien anglais partageable - mais ne le modifie pas : seul le sélecteur écrit le choix. Sans
 * préfixe, un choix mémorisé « anglais » renvoie vers la version `/en` de la même page.
 */
import { useSyncExternalStore } from "react"

import { fr, type CleAvecPluriel, type CleI18n } from "./fr"
import { basenameDeLangue, cheminDansLangue, cheminInterneDepuisUrl, langueDuChemin } from "./prefixe"

export { basenameDeLangue, cheminDansLangue, cheminInterneDepuisUrl, langueDuChemin, PREFIXE_EN, retirerPrefixeLangue } from "./prefixe"

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
// Vrai quand la page a été renvoyée vers `/en` par le choix mémorisé du navigateur, et non ouverte sur un
// lien `/en` : la différence compte pour un élève dont le cursus est français (voir langueProfil.ts).
let renvoyeeParChoixMemorise = false

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

/** Garde le choix de langue de CE navigateur (les erreurs de stockage sont sans conséquence). */
export function memoriserLangue(cible: Langue): void {
  try {
    localStorage.setItem(LANGUE_STORAGE_KEY, cible)
  } catch {
    /* stockage indisponible (navigation privée...) : le choix vaut pour cette session */
  }
}

/**
 * Bascule la langue. Le dictionnaire est chargé AVANT de basculer : l'interface passe d'une langue
 * à l'autre d'un coup, sans trou en français entre les deux. Rejette si le chargement échoue (réseau) ;
 * la langue précédente reste alors en place.
 *
 * Ne touche pas à l'URL : pour un changement voulu par l'élève, c'est `ouvrirDansLangue` qu'il faut,
 * qui recharge la page sur l'URL de l'autre langue.
 */
export async function definirLangue(cible: Langue, options: { persister?: boolean } = {}): Promise<void> {
  if (!estLangue(cible)) return
  const dictionnaire = await chargerSurcharge(cible)
  langue = cible
  surcharge = dictionnaire
  version += 1
  if (options.persister ?? true) memoriserLangue(cible)
  if (typeof document !== "undefined") document.documentElement.lang = cible
  abonnes.forEach((notifier) => notifier())
}

/**
 * L'URL de la page courante dans une autre langue (même page, même requête, même ancre).
 * `emplacement` est une URL PUBLIQUE (celle de la barre d'adresse) : ses segments sont d'abord ramenés au
 * chemin interne, puis traduits dans la langue cible (`/en/cm/past-papers/x` -> `/cm/epreuves/x`).
 */
export function urlDansLangue(
  cible: Langue,
  emplacement: Pick<Location, "pathname" | "search" | "hash"> = window.location,
): string {
  return `${cheminDansLangue(cheminInterneDepuisUrl(emplacement.pathname), cible)}${emplacement.search}${emplacement.hash}`
}

/** Recharge la page courante dans l'autre langue : le préfixe est la base du routeur, fixée au chargement. */
export function ouvrirDansLangue(cible: Langue): void {
  window.location.assign(urlDansLangue(cible))
}

/**
 * À appeler avant le premier rendu : applique la langue de l'URL (préfixe `/en`), à défaut celle
 * gardée par ce navigateur, sans flash de français. Retourne la `basename` du routeur, qui est
 * toujours celle de l'URL - même si le dictionnaire anglais n'a pas pu être chargé, sans quoi
 * `/en/cm` serait lu comme un pays « en ».
 */
export async function initialiserLangue(): Promise<string> {
  const { pathname, search, hash } = window.location
  const duChemin = langueDuChemin(pathname)
  renvoyeeParChoixMemorise = false
  let cible: Langue = duChemin ?? "fr"
  if (!duChemin && langueStockee() === "en") {
    cible = "en"
    renvoyeeParChoixMemorise = true
    window.history.replaceState(window.history.state, "", `${cheminDansLangue(pathname, "en")}${search}${hash}`)
  }
  if (cible === "en") {
    try {
      await definirLangue("en", { persister: false })
    } catch {
      /* anglais injoignable : on garde le français plutôt que de bloquer l'app */
    }
  }
  return basenameDeLangue(cible)
}

/**
 * La page est-elle en anglais parce que l'URL le dit (lien `/en/...` partagé, favori), et non parce que
 * le navigateur avait mémorisé l'anglais ? Seul le premier cas est un choix explicite à respecter.
 */
export function urlAnglaiseExplicite(): boolean {
  return !renvoyeeParChoixMemorise && langueDuChemin(window.location.pathname) === "en"
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
