import { afterEach, describe, expect, it } from "vitest"

import { FILTERS_SESSION_KEY, oublierFiltresMemorises, requeteSansFiltresDeLangue } from "./filtresListe"

afterEach(() => sessionStorage.clear())

describe("requeteSansFiltresDeLangue", () => {
  it("retire l'examen et la matière, garde le reste", () => {
    expect(requeteSansFiltresDeLangue("?cursus=14&subject=MATHS&search=suites&ordering=annee")).toBe(
      "?search=suites&ordering=annee",
    )
  })

  it("retire aussi « tout » (élargissement au-delà de l'examen déclaré)", () => {
    expect(requeteSansFiltresDeLangue("?tout=1&nature=SUJET")).toBe("?nature=SUJET")
  })

  it("une requête vide ou sans filtre de langue reste telle quelle", () => {
    expect(requeteSansFiltresDeLangue("")).toBe("")
    expect(requeteSansFiltresDeLangue("?q=2")).toBe("?q=2")
    expect(requeteSansFiltresDeLangue("?cursus=14")).toBe("")
  })
})

describe("oublierFiltresMemorises", () => {
  it("vide la dernière recherche filtrée de la session", () => {
    sessionStorage.setItem(FILTERS_SESSION_KEY, "cursus=14&subject=MATHS")
    oublierFiltresMemorises()
    expect(sessionStorage.getItem(FILTERS_SESSION_KEY)).toBeNull()
  })
})
