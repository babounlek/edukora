import { useEffect, useState } from "react"
import { flushSync } from "react-dom"

/**
 * Vrai le temps d'une impression, que l'élève passe par un bouton ou par le menu du navigateur (Ctrl+P). De quoi ne
 * construire la feuille imprimée qu'à ce moment-là : ses formules coûteraient à chaque affichage de la page. flushSync,
 * parce que le navigateur photographie la page dès le retour de « beforeprint ».
 */
export function useImpression(): boolean {
  const [enCours, setEnCours] = useState(false)
  useEffect(() => {
    const avant = () => flushSync(() => setEnCours(true))
    const apres = () => setEnCours(false)
    window.addEventListener("beforeprint", avant)
    window.addEventListener("afterprint", apres)
    return () => {
      window.removeEventListener("beforeprint", avant)
      window.removeEventListener("afterprint", apres)
    }
  }, [])
  return enCours
}
