import { renderHook } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

const { auth } = vi.hoisted(() => ({ auth: { current: {} as { isAuthenticated: boolean; user: unknown } } }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth.current }))

import { useAbonneActif } from "./abonneActif"

const CURSUS = { id: 7, examen: "GCE_OL" }

function pour(isAuthenticated: boolean, user: unknown) {
  auth.current = { isAuthenticated, user }
  return renderHook(() => useAbonneActif()).result.current
}

describe("useAbonneActif", () => {
  it("vrai pour un compte connecté, abonné, avec un examen préparé", () => {
    expect(pour(true, { a_un_abonnement_actif: true, cursus_prepare: CURSUS })).toBe(true)
  })

  it("faux pour un visiteur, un compte sans abonnement, ou sans examen préparé : ils gardent le choix d'examen", () => {
    expect(pour(false, null)).toBe(false)
    expect(pour(true, { a_un_abonnement_actif: false, cursus_prepare: CURSUS })).toBe(false)
    expect(pour(true, { a_un_abonnement_actif: true, cursus_prepare: null })).toBe(false)
  })
})
