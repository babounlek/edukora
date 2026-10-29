import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { campagne, abonne, declare } = vi.hoisted(() => ({
  campagne: { valeur: null as unknown },
  abonne: { valeur: false },
  declare: { valeur: null as number | null },
}))
vi.mock("@/lib/campagne", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/campagne")>()),
  useCampagne: () => campagne.valeur,
}))
vi.mock("@/lib/abonneActif", () => ({ useAbonneActif: () => abonne.valeur }))
vi.mock("@/lib/cursusAccueil", () => ({ useCursusDeclare: () => declare.valeur }))

import { BandeauCampagneFin } from "./BandeauCampagneFin"

const dans = (jours: number) => new Date(Date.now() + jours * 86_400_000).toISOString()
const CAMPAGNE = { nom: "Offre fondateurs", nom_en: "", pourcentage: 30, fin: dans(20), cursus: [] as number[] }

function afficher(chemin = "/cours/derivees") {
  return render(
    <MemoryRouter initialEntries={[chemin]}>
      <BandeauCampagneFin />
    </MemoryRouter>,
  )
}

describe("BandeauCampagneFin", () => {
  beforeEach(() => {
    sessionStorage.clear()
    campagne.valeur = CAMPAGNE
    abonne.valeur = false
    declare.valeur = null
  })

  it("visible pour un visiteur sur une page de cours, avec lien vers les tarifs", () => {
    afficher()
    expect(screen.getByRole("status").textContent).toContain("Offre fondateurs : −30 %")
    expect(screen.getByRole("link").getAttribute("href")).toBe("/tarifs")
  })

  it("absent sans campagne, pour un abonné, et sur les pages qui montrent déjà l'offre ou qu'il ne faut pas gêner", () => {
    campagne.valeur = null
    expect(afficher().container.textContent).toBe("")
    campagne.valeur = CAMPAGNE
    abonne.valeur = true
    expect(afficher().container.textContent).toBe("")
    abonne.valeur = false
    for (const chemin of ["/cm", "/tarifs", "/cm/epreuves/x/lire", "/connexion"]) {
      expect(afficher(chemin).container.textContent).toBe("")
    }
  })

  it("absent pour un élève dont l'examen n'est pas concerné, présent s'il l'est ou s'il n'en a pas déclaré", () => {
    campagne.valeur = { ...CAMPAGNE, cursus: [7] }
    declare.valeur = 3
    expect(afficher().container.textContent).toBe("")
    declare.valeur = 7
    expect(afficher().container.textContent).not.toBe("")
    declare.valeur = null
    expect(afficher().container.textContent).not.toBe("")
  })

  it("annonce l'urgence seulement dans la dernière semaine", () => {
    campagne.valeur = { ...CAMPAGNE, fin: dans(2) }
    afficher()
    expect(screen.getByRole("status").textContent).toContain("Plus que")
  })
})
