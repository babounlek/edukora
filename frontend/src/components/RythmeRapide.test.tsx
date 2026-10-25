import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { EtatXp } from "@/api/types"

const definirObjectifXp = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ definirObjectifXp }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))

import { libelleRythme } from "@/lib/rythme"
import { RythmeRapide } from "./RythmeRapide"

const etat: EtatXp = { xp: 5, objectif: 20, atteint: false, objectifs_possibles: [10, 20, 30] }

function afficher(onChange = vi.fn()) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <RythmeRapide etat={etat} onChange={onChange}>5 / 20 points</RythmeRapide>
    </QueryClientProvider>,
  )
  return onChange
}

beforeEach(() => definirObjectifXp.mockReset())

describe("RythmeRapide", () => {
  it("dit le rythme actuel dans le nom du bouton", () => {
    afficher()
    expect(screen.getByRole("button", { name: /actuellement : Régulier · 20 points/ })).toBeInTheDocument()
  })

  it("propose les trois rythmes et enregistre celui qu'on choisit", async () => {
    const nouvel = { ...etat, objectif: 30 }
    definirObjectifXp.mockResolvedValue(nouvel)
    const onChange = afficher()

    await userEvent.click(screen.getByRole("button", { name: /Changer mon rythme/ }))
    expect(await screen.findByRole("menuitem", { name: /Tranquille · 10 points/ })).toBeInTheDocument()
    await userEvent.click(screen.getByRole("menuitem", { name: /Intense · 30 points/ }))

    expect(definirObjectifXp).toHaveBeenCalledWith(30)
    expect(onChange).toHaveBeenCalledWith(nouvel)
  })

  it("ne rappelle pas le serveur pour le rythme déjà choisi", async () => {
    afficher()
    await userEvent.click(screen.getByRole("button", { name: /Changer mon rythme/ }))
    await userEvent.click(await screen.findByRole("menuitem", { name: /Régulier · 20 points/ }))
    expect(definirObjectifXp).not.toHaveBeenCalled()
  })

  it("nomme chaque rythme avec ses points", () => {
    expect(libelleRythme(10)).toBe("Tranquille · 10 points")
    expect(libelleRythme(45)).toBe("45 points")
  })
})
