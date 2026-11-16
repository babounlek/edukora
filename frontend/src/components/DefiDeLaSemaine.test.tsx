import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { DefiSemaine } from "@/api/types"

const { getDefiSemaine } = vi.hoisted(() => ({ getDefiSemaine: vi.fn() }))
vi.mock("@/api/endpoints", () => ({ getDefiSemaine }))

import { DefiDeLaSemaine } from "./DefiDeLaSemaine"

const defi = (extra: Partial<DefiSemaine> = {}): DefiSemaine => ({
  epreuve_id: 7, slug: "mini-bac-c-1", titre: "Mini-inédite Mathématiques BAC C n°1", duree_minutes: 30,
  debut: "2026-11-09", fin: "2026-11-15", jours_restants: 4, releve: false, resultat_ouvert: false, bande: null, precedent: null,
  ...extra,
})

async function afficher(valeur: DefiSemaine | null, rangee = false) {
  getDefiSemaine.mockResolvedValue({ defi: valeur })
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>
        <DefiDeLaSemaine country="cm" cursusId={4} rangee={rangee} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("DefiDeLaSemaine", () => {
  beforeEach(() => getDefiSemaine.mockReset())

  it("propose le défi avec les jours restants quand il n'est pas relevé", async () => {
    await afficher(defi())
    expect(await screen.findByText("Mini-inédite Mathématiques BAC C n°1")).toBeTruthy()
    expect(screen.getByText(/Encore 4 jours/)).toBeTruthy()
    expect(getDefiSemaine).toHaveBeenCalledWith(4, expect.anything())
  })

  it("en rangée du bloc « À continuer » : un seul lien, vers la fiche, avec le même état", async () => {
    await afficher(defi({ releve: true, resultat_ouvert: false }), true)
    const lien = await screen.findByRole("link", { name: /Mini-inédite Mathématiques BAC C n°1/ })
    expect(lien.getAttribute("href")).toContain("mini-bac-c-1")
    expect(lien.textContent).toContain("Défi relevé")
    expect(screen.getAllByRole("link")).toHaveLength(1)
    expect(screen.queryByText("Toutes les minis")).toBeNull()
  })

  it("annonce le dernier jour", async () => {
    await afficher(defi({ jours_restants: 0 }))
    expect(await screen.findByText("Dernier jour pour le relever")).toBeTruthy()
  })

  it("dit « relevé » et promet la position pour dimanche avant le dimanche", async () => {
    await afficher(defi({ releve: true }))
    expect(await screen.findByText(/Défi relevé · ta position parmi les participants, dimanche/)).toBeTruthy()
  })

  it("donne la bande le dimanche, sans rang ni chiffre", async () => {
    await afficher(defi({ releve: true, resultat_ouvert: true, jours_restants: 0, bande: { disponible: true, bande: "quart" } }))
    expect(await screen.findByText(/quart supérieur des participants/)).toBeTruthy()
  })

  it("se contente de « relevé » le dimanche quand la cohorte est trop petite", async () => {
    await afficher(defi({ releve: true, resultat_ouvert: true, jours_restants: 0, bande: { disponible: false, bande: null } }))
    expect(await screen.findByText("Défi relevé")).toBeTruthy()
  })

  it("rappelle la semaine dernière quand l'élève y a pris part", async () => {
    await afficher(defi({ precedent: { titre: "Mini 0", bande: { disponible: true, bande: "moitie" } } }))
    expect(await screen.findByText(/Semaine dernière : la moitié supérieure/)).toBeTruthy()
  })

  it("ne montre rien sans défi", async () => {
    await afficher(null)
    await vi.waitFor(() => expect(getDefiSemaine).toHaveBeenCalled())
    expect(screen.queryByText("Défi de la semaine")).toBeNull()
  })
})
