import { useEffect } from "react"
import { useLocation, useNavigationType } from "react-router-dom"

/**
 * BrowserRouter ne remet jamais le scroll en haut de page tout seul - contrairement
 * à une navigation classique multi-pages. Sans ça, ouvrir une épreuve depuis le bas
 * d'une liste déjà scrollée atterrit au milieu de la page suivante.
 *
 * Ne force le scroll que sur un vrai changement de contenu (PUSH/REPLACE, ex. clic
 * sur un lien), jamais sur un retour navigateur (POP) - le navigateur restaure déjà
 * nativement la position de scroll précédente dans ce cas (scrollRestoration="auto"
 * par défaut), qu'il ne faut pas écraser.
 *
 * `pathname` seul (pas la query string) : changer un filtre sur le catalogue reste
 * sur le même contenu, pas une nouvelle page - inutile d'y arracher le scroll.
 */
export function ScrollToTop() {
  const { pathname } = useLocation()
  const navigationType = useNavigationType()

  useEffect(() => {
    if (navigationType !== "POP") {
      window.scrollTo(0, 0)
    }
  }, [pathname, navigationType])

  return null
}
