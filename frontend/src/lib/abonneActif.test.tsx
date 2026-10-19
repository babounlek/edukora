import { renderHook } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

const { auth } = vi.hoisted(() => ({ auth: { current: {} as { isAuthenticated: boolean; user: unknown } } }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth.current }))

import { useAbonneActif, useCursusAbonne } from "./abonneActif"

const CURSUS = { id: 7, examen: "GCE_OL" }

function pour(isAuthenticated: boolean, user: unknown) {
  auth.current = { isAuthenticated, user }
  return renderHook(() => useAbonneActif()).result.current
}

describe("useAbonneActif", () => {
  it("vrai pour le profil actif abonné à l'examen qu'il prépare", () => {
    expect(pour(true, { abonne_profil_actif: true, cursus_prepare: CURSUS })).toBe(true)
  })

  it("faux pour un visiteur, un profil non abonné (même si le compte l'est), ou sans examen préparé", () => {
    expect(pour(false, null)).toBe(false)
    expect(pour(true, { a_un_abonnement_actif: true, abonne_profil_actif: false, cursus_prepare: CURSUS })).toBe(false)
    expect(pour(true, { abonne_profil_actif: true, cursus_prepare: null })).toBe(false)
  })
})

describe("useCursusAbonne", () => {
  it("donne l'examen du profil actif abonné, sinon null", () => {
    auth.current = { isAuthenticated: true, user: { abonne_profil_actif: true, cursus_prepare: CURSUS } }
    expect(renderHook(() => useCursusAbonne()).result.current).toBe(7)
    auth.current = { isAuthenticated: true, user: { abonne_profil_actif: false, cursus_prepare: CURSUS } }
    expect(renderHook(() => useCursusAbonne()).result.current).toBeNull()
  })
})
