import { useEffect } from "react"
import { useLocation } from "react-router-dom"

import { cheminDansLangue, useI18n } from "@/lib/i18n"
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

/** URL absolue publique d'une page, dans une langue. `pathname` est celui du routeur (sans préfixe de langue). */
export function urlPublique(pathname: string, langue: "fr" | "en"): string {
  const chemin = cheminDansLangue(pathname, langue)
  return `${SITE_URL}${chemin === "/" ? "/" : chemin.replace(/\/$/, "")}`
}

const LOCALE_OG = { fr: "fr_FR", en: "en_GB" } as const

/**
 * index.html pose un canonical et un og:url sur « / » : sans mise à jour à chaque navigation,
 * toutes les pages d'une SPA se déclarent équivalentes à l'accueil, et Googlebot (qui exécute
 * le JS) peut n'en retenir qu'une. Posé ici pour toutes les routes plutôt que page par page,
 * pour qu'aucune n'oublie de le faire. Sans la query string : les filtres du catalogue ne
 * créent pas de nouvelles pages.
 *
 * Chaque page existe en français (sans préfixe) et en anglais (`/en`) : le canonical est celui de la
 * langue de la page, et les balises hreflang déclarent l'autre version aux moteurs de recherche.
 */
export function BalisesDeRoute() {
  const { pathname } = useLocation()
  const { langue } = useI18n()

  useEffect(() => {
    const url = urlPublique(pathname, langue)
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
    upsertTag(
      'meta[property="og:locale"]',
      () => {
        const m = document.createElement("meta")
        m.setAttribute("property", "og:locale")
        return m
      },
      "content",
      LOCALE_OG[langue],
    )
  }, [pathname, langue])

  // Les deux versions de la page, déclarées l'une à l'autre (le français est la version par défaut).
  // Les pages privées n'en ont pas : elles ne sont pas indexées.
  useEffect(() => {
    if (estRoutePrivee(pathname)) return
    const balises = (
      [
        ["fr", urlPublique(pathname, "fr")],
        ["en", urlPublique(pathname, "en")],
        ["x-default", urlPublique(pathname, "fr")],
      ] as const
    ).map(([hreflang, href]) => {
      const l = document.createElement("link")
      l.setAttribute("rel", "alternate")
      l.setAttribute("hreflang", hreflang)
      l.setAttribute("href", href)
      document.head.appendChild(l)
      return l
    })
    return () => balises.forEach((l) => l.remove())
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
