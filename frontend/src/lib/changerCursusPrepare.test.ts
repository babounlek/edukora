import { describe, expect, it } from "vitest"

import type { Subscription } from "@/api/types"
import { abonnementsDeLExamenPrepare } from "@/lib/changerCursusPrepare"

// Seuls `id` et `cursus.id` comptent pour la sélection ; le reste de l'objet n'est pas lu.
const abo = (id: number, cursusId: number) => ({ id, cursus: { id: cursusId } }) as unknown as Subscription
const ids = (liste: Subscription[]) => liste.map((s) => s.cursus.id)

describe("abonnementsDeLExamenPrepare", () => {
  const bacC = abo(253, 20)
  const bepc = abo(258, 14)

  it("ne garde que l'examen préparé quand le profil a payé deux examens", () => {
    expect(ids(abonnementsDeLExamenPrepare([bacC, bepc], 14, null))).toEqual([14])
    expect(ids(abonnementsDeLExamenPrepare([bacC, bepc], 20, null))).toEqual([20])
  })

  it("admet en plus le cursus d'un lien direct ?cursus=", () => {
    expect(ids(abonnementsDeLExamenPrepare([bacC, bepc], 14, "20")).sort()).toEqual([14, 20])
  })

  it("un lien direct vers un cursus sans abonnement ne change rien", () => {
    expect(ids(abonnementsDeLExamenPrepare([bacC, bepc], 14, "99"))).toEqual([14])
  })

  it("se replie sur tous les abonnements quand l'examen préparé n'est pas déclaré", () => {
    expect(ids(abonnementsDeLExamenPrepare([bacC, bepc], null, null))).toEqual([20, 14])
    expect(ids(abonnementsDeLExamenPrepare([bacC, bepc], undefined, null))).toEqual([20, 14])
  })

  it("se replie sur tous les abonnements quand l'examen préparé n'a pas d'abonnement actif", () => {
    expect(ids(abonnementsDeLExamenPrepare([bacC, bepc], 22, null))).toEqual([20, 14])
  })

  it("rend une liste vide inchangée", () => {
    expect(abonnementsDeLExamenPrepare([], 14, null)).toEqual([])
  })
})
