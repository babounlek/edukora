import { describe, expect, it } from "vitest"

import type { Epreuve } from "@/api/types"
import { choisirMiniDeLaSemaine, numeroDeSemaine } from "@/components/MiniDeLaSemaine"

const mini = (id: number, extra: Partial<Epreuve> = {}) =>
  ({ id, title: `Mini ${id}`, has_access: true, is_read: false, ...extra }) as Epreuve

describe("numeroDeSemaine", () => {
  it("change le lundi, pas le dimanche", () => {
    const dimanche = Date.UTC(2026, 10, 1, 23, 0) // dimanche 1er novembre 2026
    const lundi = Date.UTC(2026, 10, 2, 0, 30) // lundi 2 novembre 2026
    const mardi = Date.UTC(2026, 10, 3, 12, 0)
    expect(numeroDeSemaine(lundi)).toBe(numeroDeSemaine(dimanche) + 1)
    expect(numeroDeSemaine(mardi)).toBe(numeroDeSemaine(lundi))
  })
})

describe("choisirMiniDeLaSemaine", () => {
  it("ne propose rien sans mini ouverte", () => {
    expect(choisirMiniDeLaSemaine([], 5)).toBeNull()
    expect(choisirMiniDeLaSemaine([mini(1, { has_access: false })], 5)).toBeNull()
  })

  it("tourne sur les minis ouvertes, triées par id", () => {
    const minis = [mini(30), mini(10), mini(20, { has_access: false }), mini(40)]
    expect(choisirMiniDeLaSemaine(minis, 0)?.mini.id).toBe(10)
    expect(choisirMiniDeLaSemaine(minis, 1)?.mini.id).toBe(30)
    expect(choisirMiniDeLaSemaine(minis, 2)?.mini.id).toBe(40)
    expect(choisirMiniDeLaSemaine(minis, 3)?.mini.id).toBe(10)
  })

  it("déjà faite : propose la prochaine pas encore faite", () => {
    const minis = [mini(1), mini(2, { is_read: true }), mini(3, { is_read: true }), mini(4)]
    const choix = choisirMiniDeLaSemaine(minis, 1)
    expect(choix?.mini.id).toBe(2)
    expect(choix?.autre?.id).toBe(4)
  })

  it("tout est fait : la mini de la semaine reste, sans autre proposition", () => {
    const minis = [mini(1, { is_read: true }), mini(2, { is_read: true })]
    const choix = choisirMiniDeLaSemaine(minis, 0)
    expect(choix?.mini.id).toBe(1)
    expect(choix?.autre).toBeNull()
  })
})
