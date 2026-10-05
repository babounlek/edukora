import { useEffect } from "react"

// La palette de recherche vit dans l'en-tête (voir Header), mais d'autres endroits doivent pouvoir
// l'ouvrir (la barre d'onglets de ReviserTabs). Un évènement DOM plutôt qu'un état remonté : ils
// n'ont aucun ancêtre commun utile, et l'ouverture est un simple « demande » sans réponse.
const EVENEMENT_OUVRIR = "edukamer:ouvrir-recherche"

/** Demande l'ouverture de la palette de recherche, de n'importe où dans l'application. */
export function demanderOuvertureRecherche() {
  window.dispatchEvent(new Event(EVENEMENT_OUVRIR))
}

/**
 * Ouvre la recherche au clavier : « / » (hors d'un champ de saisie - on ne vole jamais la touche à
 * quelqu'un qui écrit) et Ctrl/⌘+K (de n'importe où, y compris dans un champ) - ainsi que sur
 * demande explicite (voir demanderOuvertureRecherche).
 */
export function useRaccourciRecherche(ouvrir: () => void) {
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.defaultPrevented) return
      const cible = event.target as HTMLElement | null
      const dansUnChamp =
        cible !== null &&
        (cible.tagName === "INPUT" || cible.tagName === "TEXTAREA" || cible.tagName === "SELECT" || cible.isContentEditable)
      const ctrlK = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k"
      const barre = event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey && !dansUnChamp
      if (ctrlK || barre) {
        event.preventDefault()
        ouvrir()
      }
    }
    window.addEventListener("keydown", onKeyDown)
    window.addEventListener(EVENEMENT_OUVRIR, ouvrir)
    return () => {
      window.removeEventListener("keydown", onKeyDown)
      window.removeEventListener(EVENEMENT_OUVRIR, ouvrir)
    }
  }, [ouvrir])
}
