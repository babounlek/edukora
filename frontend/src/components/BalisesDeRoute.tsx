import { useEffect } from "react"
import { useLocation } from "react-router-dom"

import { SITE_URL } from "@/lib/site"

// Pages propres à un compte ou à une session : aucun intérêt à les indexer, et rien de public
// à y lire pour un robot (elles renvoient à la connexion ou affichent un écran vide).
const PREFIXES_PRIVES = [
  "/connexion",
  "/compte",
  "/mes-acces",
  "/mes-paiements",
  "/abonnement",
  "/qui-etudie",
  "/historique",
  "/carnet",
  "/quiz",
  "/parcours",
  "/revision",
  "/inedit",
  "/simulation",
]

export function estRoutePrivee(pathname: string): boolean {
  return PREFIXES_PRIVES.some((p) => pathname === p || pathname.startsWith(`${p}/`))
}

function upsertTag(selector: string, create: () => HTMLElement, attr: string, value: string) {
  let tag = document.head.querySelector<HTMLElement>(selector)
  if (!tag) {
    tag = create()
    document.head.appendChild(tag)
  }
  tag.setAttribute(attr, value)
}

/**
 * index.html pose un canonical et un og:url sur « / » : sans mise à jour à chaque navigation,
 * toutes les pages d'une SPA se déclarent équivalentes à l'accueil, et Googlebot (qui exécute
 * le JS) peut n'en retenir qu'une. Posé ici pour toutes les routes plutôt que page par page,
 * pour qu'aucune n'oublie de le faire. Sans la query string : les filtres du catalogue ne
 * créent pas de nouvelles pages.
 */
export function BalisesDeRoute() {
  const { pathname } = useLocation()

  useEffect(() => {
    const url = `${SITE_URL}${pathname === "/" ? "/" : pathname.replace(/\/$/, "")}`
    upsertTag(
      'link[rel="canonical"]',
      () => {
        const l = document.createElement("link")
        l.setAttribute("rel", "canonical")
        return l
      },
      "href",
      url,
    )
    upsertTag(
      'meta[property="og:url"]',
      () => {
        const m = document.createElement("meta")
        m.setAttribute("property", "og:url")
        return m
      },
      "content",
      url,
    )
  }, [pathname])

  useEffect(() => {
    if (!estRoutePrivee(pathname)) return
    const tag = document.createElement("meta")
    tag.setAttribute("name", "robots")
    tag.setAttribute("content", "noindex, follow")
    document.head.appendChild(tag)
    // Retire sa propre balise, jamais celle d'une autre page (voir useSeo, noindex).
    return () => tag.remove()
  }, [pathname])

  return null
}
