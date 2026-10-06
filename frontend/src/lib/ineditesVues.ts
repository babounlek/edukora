import { useSyncExternalStore } from "react"

/**
 * La dernière épreuve inédite que cette personne a vue passer : tant qu'elle n'a pas regardé
 * la plus récente, l'entrée de menu qui les contient porte un point or. Sans cette mémoire le
 * point restait allumé en permanence, pulsant, sans jamais dire pourquoi - ce qui est le
 * contraire d'un signal de nouveauté.
 *
 * Le point se rallume tout seul quand une inédite plus récente est publiée : on mémorise l'id
 * de la plus récente VUE, pas un simple « déjà vu ». Même mécanique de magasin externe que
 * cursusPrepare.ts : écrire met à jour, sur la page en cours, tous les composants qui lisent.
 */
const CLE = "edukamer_inedites_vues"

function lire(): number | null {
  try {
    const brut = localStorage.getItem(CLE)
    const id = brut ? Number(brut) : NaN
    return Number.isInteger(id) && id > 0 ? id : null
  } catch {
    return null
  }
}

let valeur = lire()
const abonnes = new Set<() => void>()

function abonner(rappel: () => void) {
  abonnes.add(rappel)
  return () => {
    abonnes.delete(rappel)
  }
}

/** Retient `id` comme dernière inédite vue - sans effet si une plus récente l'est déjà. */
export function marquerIneditesVues(id: number) {
  if (valeur !== null && valeur >= id) return
  try {
    localStorage.setItem(CLE, String(id))
  } catch {
    // stockage indisponible (navigation privée) : le point se rallumera à la page suivante,
    // ce n'est jamais une raison d'interrompre la lecture.
  }
  valeur = id
  abonnes.forEach((rappel) => rappel())
}

export function useIneditesVues(): number | null {
  return useSyncExternalStore(abonner, () => valeur, () => null)
}

/** Les inédites sont-elles « nouvelles » pour cette personne ? `derniereId` : la plus récente
 * publiée (ids croissants : une inédite plus récente a toujours un id plus grand). */
export function ineditesNouvelles(derniereId: number | undefined, vue: number | null): boolean {
  return derniereId !== undefined && (vue === null || derniereId > vue)
}
