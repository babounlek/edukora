import { useEffect, useState } from "react"

/**
 * Un nombre qui monte de 0 à `cible` en `dureeMs` - le compteur d'XP de l'écran de fin de
 * séance. Pour qui a demandé moins de mouvement (prefers-reduced-motion), ou si la cible
 * est 0, renvoie la valeur finale tout de suite : l'information est la même, sans animation.
 */
export function useCompteur(cible: number, dureeMs = 900): number {
  const [valeur, setValeur] = useState(() => (reduireMouvement() || cible <= 0 ? cible : 0))

  useEffect(() => {
    if (reduireMouvement() || cible <= 0) {
      setValeur(cible)
      return
    }
    let image = 0
    const debut = performance.now()
    const etape = (maintenant: number) => {
      const avancement = Math.min(1, (maintenant - debut) / dureeMs)
      // Décélération : la fin du compte ralentit, comme un compteur qui "se pose".
      setValeur(Math.round(cible * (1 - (1 - avancement) ** 3)))
      if (avancement < 1) image = requestAnimationFrame(etape)
    }
    image = requestAnimationFrame(etape)
    return () => cancelAnimationFrame(image)
  }, [cible, dureeMs])

  return valeur
}

function reduireMouvement(): boolean {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches === true
}
