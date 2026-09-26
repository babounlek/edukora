import { useEffect, useState } from "react"

/**
 * Vrai tant que la requête média correspond ("(min-width: 640px)"). Sert aux rares cas où
 * la présentation change de STRUCTURE selon la largeur (un bloc replié sur téléphone, déplié
 * ailleurs), là où une simple classe responsive ne suffit pas.
 *
 * Faux au premier rendu côté serveur/tests (pas de matchMedia) : le mobile est le cas le
 * plus contraint, autant qu'il soit le comportement par défaut.
 */
export function useMediaQuery(requete: string): boolean {
  const [correspond, setCorrespond] = useState(() =>
    typeof window !== "undefined" && typeof window.matchMedia === "function" ? window.matchMedia(requete).matches : false,
  )
  useEffect(() => {
    if (typeof window.matchMedia !== "function") return
    const liste = window.matchMedia(requete)
    const maj = () => setCorrespond(liste.matches)
    maj()
    liste.addEventListener("change", maj)
    return () => liste.removeEventListener("change", maj)
  }, [requete])
  return correspond
}
