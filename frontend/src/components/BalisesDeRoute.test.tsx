import { render } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, describe, expect, it } from "vitest"

import { BalisesDeRoute, estRoutePrivee } from "@/components/BalisesDeRoute"
import { SITE_URL } from "@/lib/site"

afterEach(() => {
  document.head.querySelectorAll('link[rel="canonical"], meta[property="og:url"], meta[name="robots"]').forEach((n) => n.remove())
})

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

  it("marque une page privée en noindex et retire la balise au départ", () => {
    const { unmount } = render(
      <MemoryRouter initialEntries={["/mes-acces"]}>
        <BalisesDeRoute />
      </MemoryRouter>,
    )
    expect(document.head.querySelector('meta[name="robots"]')?.getAttribute("content")).toContain("noindex")
    unmount()
    expect(document.head.querySelector('meta[name="robots"]')).toBeNull()
  })
})
