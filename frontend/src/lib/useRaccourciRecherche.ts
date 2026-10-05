import { useEffect } from "react"

/**
 * Ouvre la recherche au clavier : « / » (hors d'un champ de saisie - on ne vole jamais la touche à
 * quelqu'un qui écrit) et Ctrl/⌘+K (de n'importe où, y compris dans un champ).
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
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [ouvrir])
}
