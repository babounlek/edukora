import { describe, expect, it } from "vitest"

import type { NiveauXp } from "@/api/types"
import { aChangeDeNiveau, libelleNiveau, nomNiveau, partVersSuivant, pointsRestants } from "./niveau"

const malin: NiveauXp = { rang: 2, xp_total: 110, seuil: 60, seuil_suivant: 200 }
const sommet: NiveauXp = { rang: 5, xp_total: 1300, seuil: 1000, seuil_suivant: null }

describe("niveau", () => {
  it("nomme chaque rang, et borne les rangs hors liste", () => {
    expect(nomNiveau(1)).toBe("Débutant")
    expect(nomNiveau(3)).toBe("Costaud")
    expect(nomNiveau(0)).toBe("Débutant")
    expect(nomNiveau(9)).toBe("Champion")
    expect(libelleNiveau(malin)).toBe("Niveau 2 · Malin")
  })

  it("dit où l'on en est entre deux paliers", () => {
    expect(partVersSuivant(malin)).toBe(36) // (110 - 60) / (200 - 60)
    expect(pointsRestants(malin)).toBe(90)
  })

  it("au sommet : barre pleine, rien à atteindre", () => {
    expect(partVersSuivant(sommet)).toBe(100)
    expect(pointsRestants(sommet)).toBeNull()
  })

  it("détecte le passage d'un palier grâce au gain du quiz", () => {
    expect(aChangeDeNiveau({ ...malin, xp_total: 65 }, 10)).toBe(true) // 55 avant : sous le seuil de 60
    expect(aChangeDeNiveau({ ...malin, xp_total: 80 }, 10)).toBe(false) // 70 avant : déjà niveau 2
    expect(aChangeDeNiveau({ ...malin, xp_total: 65 }, 0)).toBe(false)
    expect(aChangeDeNiveau({ rang: 1, xp_total: 20, seuil: 0, seuil_suivant: 60 }, 20)).toBe(false) // le niveau 1 se « franchit » jamais
  })
})
