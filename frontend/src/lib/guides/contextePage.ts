import { useEffect, useSyncExternalStore } from "react"

/**
 * Ce que la PAGE sait et que le guide doit dire : le libellé réel du bouton, les étapes réellement
 * proposées, le mode de lecture réellement actif. Un guide écrit une fois pour toutes ne peut pas
 * décrire une séance qui change chaque jour (deux ou trois étapes, « Reprendre » plutôt que
 * « Commencer », un quiz express ou non) : la page publie ce qu'elle affiche, les textes dynamiques
 * (voir textes.ts) s'en servent, et une aide ne raconte jamais autre chose que ce qui est à l'écran.
 *
 * Un petit magasin externe (même mécanique que etat.ts) : la page qui publie et le composant qui
 * affiche l'aide n'ont aucun lien de parenté.
 */

export type ContextePage = Record<string, unknown>

const valeurs = new Map<string, ContextePage>()
const abonnes = new Set<() => void>()

function notifier() {
  abonnes.forEach((rappel) => rappel())
}

function abonner(rappel: () => void) {
  abonnes.add(rappel)
  return () => {
    abonnes.delete(rappel)
  }
}

/** Pour les tests, et pour une page qui disparaît. */
export function retirerContextePage(cle: string) {
  if (valeurs.delete(cle)) notifier()
}

export function reinitialiserContextesPage() {
  valeurs.clear()
  notifier()
}

/**
 * À appeler depuis la page qui porte la fonctionnalité. Republie seulement quand le contenu change
 * (comparaison sur sa forme sérialisée : la page peut passer un objet neuf à chaque rendu) et retire
 * sa publication en quittant l'écran.
 */
export function usePublierContextePage(cle: string, contexte: ContextePage | null) {
  const serialise = contexte === null ? null : JSON.stringify(contexte)
  useEffect(() => {
    if (serialise === null) {
      retirerContextePage(cle)
      return
    }
    valeurs.set(cle, JSON.parse(serialise) as ContextePage)
    notifier()
    return () => retirerContextePage(cle)
  }, [cle, serialise])
}

/** Ce que la page a publié sous cette clé, ou undefined quand elle n'est pas à l'écran. */
export function useContextePage(cle: string | undefined): ContextePage | undefined {
  return useSyncExternalStore(
    abonner,
    () => (cle ? valeurs.get(cle) : undefined),
    () => undefined,
  )
}
