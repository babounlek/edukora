import { describe, expect, it } from "vitest"

import { CONTENU_DE_LECTURE } from "./contenuDeLecture"

describe("CONTENU_DE_LECTURE", () => {
  it.each([
    "/catalog/lessons/mathematiques-bepc-2026/",
    "/catalog/cours/limites-de-suites/",
    "/access/read/mathematiques-bepc-2026/",
    "/access/cours/read/limites-de-suites/",
  ])("garde %s", (chemin) => {
    expect(CONTENU_DE_LECTURE.test(chemin)).toBe(true)
  })

  it.each([
    "/catalog/lessons/",
    "/catalog/cours/",
    "/catalog/lessons/mathematiques-bepc-2026/related/",
    "/auth/me/",
    "/auth/token/refresh/",
    "/access/etude/",
    "/subscriptions/mes-abonnements/",
    "/payments/transactions/",
    "/quiz/plan-du-jour/",
    "/inedit/tentatives/12/",
  ])("ne garde jamais %s", (chemin) => {
    expect(CONTENU_DE_LECTURE.test(chemin)).toBe(false)
  })
})
