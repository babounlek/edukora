import { render } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it } from "vitest"

import { BalisesDeRoute, estRoutePrivee } from "@/components/BalisesDeRoute"
import { definirLangue } from "@/lib/i18n"
import { SITE_URL } from "@/lib/site"

afterEach(async () => {
  document.head
    .querySelectorAll('link[rel="canonical"], link[rel="alternate"], meta[property="og:url"], meta[property="og:locale"], meta[name="robots"]')
    .forEach((n) => n.remove())
  await definirLangue("fr", { persister: false })
})

const alternates = () =>
  Object.fromEntries(
    [...document.head.querySelectorAll('link[rel="alternate"][hreflang]')].map((l) => [l.getAttribute("hreflang"), l.getAttribute("href")]),
  )

describe("estRoutePrivee", () => {
  it("reconnaît les pages de compte et de session, pas le contenu public", () => {
    expect(estRoutePrivee("/compte")).toBe(true)
    expect(estRoutePrivee("/quiz/session/12")).toBe(true)
    expect(estRoutePrivee("/cm/epreuves")).toBe(false)
    expect(estRoutePrivee("/tarifs")).toBe(false)
    // « /quiz » ne doit pas masquer un chemin voisin qui commence par les mêmes lettres.
    expect(estRoutePrivee("/quizz-public")).toBe(false)
  })
})

describe("BalisesDeRoute", () => {
  it("pose le canonical de la page courante, sans la query string", () => {
    render(
      <MemoryRouter initialEntries={["/cm/epreuves?cursus=3"]}>
        <BalisesDeRoute />
      </MemoryRouter>,
    )
    expect(document.head.querySelector('link[rel="canonical"]')?.getAttribute("href")).toBe(`${SITE_URL}/cm/epreuves`)
    expect(document.head.querySelector('meta[property="og:url"]')?.getAttribute("content")).toBe(`${SITE_URL}/cm/epreuves`)
    expect(document.head.querySelector('meta[name="robots"]')).toBeNull()
  })

  it("déclare les deux versions de la page (hreflang) et la locale française", () => {
    render(
      <MemoryRouter initialEntries={["/cm/epreuves"]}>
        <BalisesDeRoute />
      </MemoryRouter>,
    )
    expect(alternates()).toEqual({
      fr: `${SITE_URL}/cm/epreuves`,
      en: `${SITE_URL}/en/cm/past-papers`,
      "x-default": `${SITE_URL}/cm/epreuves`,
    })
    expect(document.head.querySelector('meta[property="og:locale"]')?.getAttribute("content")).toBe("fr_FR")
  })

  it("en anglais : canonical sous /en, locale en_GB, mêmes alternates (chemin du routeur sans préfixe)", async () => {
    await definirLangue("en", { persister: false })
    render(
      <MemoryRouter initialEntries={["/cm/epreuves"]}>
        <BalisesDeRoute />
      </MemoryRouter>,
    )
    expect(document.head.querySelector('link[rel="canonical"]')?.getAttribute("href")).toBe(`${SITE_URL}/en/cm/past-papers`)
    expect(document.head.querySelector('meta[property="og:url"]')?.getAttribute("content")).toBe(`${SITE_URL}/en/cm/past-papers`)
    expect(document.head.querySelector('meta[property="og:locale"]')?.getAttribute("content")).toBe("en_GB")
    expect(alternates().en).toBe(`${SITE_URL}/en/cm/past-papers`)
    expect(alternates().fr).toBe(`${SITE_URL}/cm/epreuves`)
  })

  it("l'accueil anglais est /en, sans barre finale", async () => {
    await definirLangue("en", { persister: false })
    render(
      <MemoryRouter initialEntries={["/"]}>
        <BalisesDeRoute />
      </MemoryRouter>,
    )
    expect(document.head.querySelector('link[rel="canonical"]')?.getAttribute("href")).toBe(`${SITE_URL}/en`)
    expect(alternates().fr).toBe(`${SITE_URL}/`)
  })

  it("marque une page privée en noindex et retire la balise au départ", () => {
    const { unmount } = render(
      <MemoryRouter initialEntries={["/mes-acces"]}>
        <BalisesDeRoute />
      </MemoryRouter>,
    )
    expect(document.head.querySelector('meta[name="robots"]')?.getAttribute("content")).toContain("noindex")
    expect(alternates()).toEqual({})
    unmount()
    expect(document.head.querySelector('meta[name="robots"]')).toBeNull()
  })
})
