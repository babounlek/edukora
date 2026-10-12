import { afterEach, describe, expect, it, vi } from "vitest"

import { enregistrerDateServeur, maintenantServeur, reinitialiserHorlogeServeur } from "@/lib/horlogeServeur"

afterEach(() => {
  reinitialiserHorlogeServeur()
  vi.useRealTimers()
})

describe("horlogeServeur", () => {
  it("n'applique aucun écart tant qu'aucune réponse n'a été mesurée", () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date("2026-10-12T10:00:00Z"))
    expect(maintenantServeur()).toBe(Date.now())
  })

  it("rattrape un téléphone en retard de 5 minutes", () => {
    vi.useFakeTimers()
    // Le serveur est à 10:05:00 ; le téléphone affiche 10:00:00.
    vi.setSystemTime(new Date("2026-10-12T10:00:00Z"))
    const debut = Date.now()
    enregistrerDateServeur("Mon, 12 Oct 2026 10:05:00 GMT", debut, debut)
    // 10:05:00 tronqué à la seconde -> +0,5 s en moyenne.
    expect(maintenantServeur() - Date.now()).toBe(5 * 60_000 + 500)
  })

  it("rattrape un téléphone en avance", () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date("2026-10-12T10:10:00Z"))
    const debut = Date.now()
    enregistrerDateServeur("Mon, 12 Oct 2026 10:05:00 GMT", debut, debut)
    expect(maintenantServeur() - Date.now()).toBe(-(5 * 60_000 - 500))
  })

  it("ignore une réponse trop lente : elle peut venir d'un cache", () => {
    enregistrerDateServeur("Mon, 12 Oct 2026 10:05:00 GMT", 0, 6_000)
    expect(maintenantServeur() - Date.now()).toBe(0)
  })

  it("ignore un en-tête absent ou illisible", () => {
    enregistrerDateServeur(null, 0, 0)
    enregistrerDateServeur("pas une date", 0, 0)
    expect(maintenantServeur() - Date.now()).toBe(0)
  })
})
