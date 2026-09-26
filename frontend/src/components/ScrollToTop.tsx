import { useEffect, useRef } from "react"
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

  // Bug réel corrigé le 2026-08-17 : `navigationType` figure dans les dépendances de
  // l'effet ci-dessous (il faut sa valeur à jour), mais il ne doit jamais le
  // DÉCLENCHER. setSearchParams(..., { replace: true }) - c'est-à-dire tout changement
  // de filtre du catalogue - le fait passer de "PUSH" à "REPLACE" : la dépendance
  // changeait, l'effet se relançait, et le scroll était arraché alors que le pathname
  // n'avait pas bougé d'un octet. D'où un symptôme trompeur, "seul le PREMIER clic sur
  // un filtre remonte en haut de page" : au second, le type valait déjà "REPLACE" et la
  // dépendance ne changeait plus. Ce garde sur le pathname précédent rétablit
  // l'intention déjà écrite dans la docstring ci-dessus.
  // `null` au départ (et non `pathname`) : le tout premier rendu doit compter comme un
  // changement, pour conserver le comportement au chargement initial.
  const previousPathname = useRef<string | null>(null)

  useEffect(() => {
    if (previousPathname.current === pathname) return
    const premierRendu = previousPathname.current === null
    previousPathname.current = pathname
    if (navigationType !== "POP") {
      window.scrollTo(0, 0)
    }
    // Un changement de page ne déplace pas le focus tout seul : au clavier ou au lecteur
    // d'écran on resterait sur le lien cliqué, dans un contenu qui n'existe plus. On le
    // pose sur le contenu (sans scroller - le scroll est réglé ci-dessus). Pas au tout
    // premier rendu : rien n'a changé, le navigateur démarre déjà en haut de la page.
    if (!premierRendu) {
      document.getElementById("contenu")?.focus({ preventScroll: true })
    }
  }, [pathname, navigationType])

  return null
}
