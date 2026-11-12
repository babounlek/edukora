import { describe, expect, it } from "vitest"

import type { Plan } from "@/api/types"
import {
  JOURS_PAR_MOIS, MOIS_PAR_DEFAUT, dateFinAcces, estAuMois, moisValides, prixTotal, prixTotalReference,
} from "./tarifs"

const mensuel = (surcharges: Partial<Plan> = {}) =>
  ({ duration_mode: "MENSUEL", effective_price: 2000, prix_reference: 2000, mois_max: 7, ...surcharges }) as Plan

describe("tarification au mois", () => {
  it("reconnaît un plan vendu au mois", () => {
    expect(estAuMois(mensuel())).toBe(true)
    expect(estAuMois({ duration_mode: "JUSQUA_EXAMEN" } as Plan)).toBe(false)
  })

  it("le total est le prix du mois multiplié par le nombre de mois", () => {
    expect(prixTotal(mensuel(), 1)).toBe(2000)
    expect(prixTotal(mensuel(), 5)).toBe(10000)
    expect(prixTotal(mensuel({ effective_price: 1440 }), 3)).toBe(4320)
  })

  it("le prix barré se calcule sur le prix de référence, pas sur le prix promotionnel", () => {
    const enCampagne = mensuel({ effective_price: 1800, prix_reference: 2000 })
    expect(prixTotal(enCampagne, 3)).toBe(5400)
    expect(prixTotalReference(enCampagne, 3)).toBe(6000)
  })

  it("un plan qui ne se vend pas au mois ne se multiplie pas", () => {
    const ancien = { duration_mode: "JUSQUA_EXAMEN", effective_price: 15000, prix_reference: 15000 } as Plan
    expect(prixTotal(ancien, 4)).toBe(15000)
    expect(prixTotalReference(ancien, 4)).toBe(15000)
  })

  it("ramène le nombre de mois à ce que le plan autorise", () => {
    const plan = mensuel({ mois_max: 7 })
    expect(moisValides(plan, 3)).toBe(3)
    expect(moisValides(plan, 0)).toBe(1)
    expect(moisValides(plan, -4)).toBe(1)
    expect(moisValides(plan, 12)).toBe(7)
    expect(moisValides(plan, Number.POSITIVE_INFINITY)).toBe(7)
    expect(moisValides(plan, Number.NaN)).toBe(MOIS_PAR_DEFAUT)
    expect(moisValides(plan, 2.6)).toBe(3)
  })

  it("le défaut ne dépasse jamais le maximum : il en reste parfois moins de trois", () => {
    expect(moisValides(mensuel({ mois_max: 2 }), Number.NaN)).toBe(2)
    expect(moisValides(mensuel({ mois_max: 1 }), 5)).toBe(1)
  })

  it("un plan qui ne se vend pas au mois s'achète en une fois", () => {
    expect(moisValides({ duration_mode: "FIXE", mois_max: 1 } as Plan, 6)).toBe(1)
  })

  it("l'accès prend fin trente jours par mois après aujourd'hui", () => {
    const depuis = new Date(2026, 10, 11, 12, 0, 0)
    const fin = dateFinAcces(3, depuis)
    expect(fin.getTime() - depuis.getTime()).toBe(3 * JOURS_PAR_MOIS * 86_400_000)
    expect(depuis.getDate()).toBe(11) // la date de départ n'est pas modifiée
  })
})
