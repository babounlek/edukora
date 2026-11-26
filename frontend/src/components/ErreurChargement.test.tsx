import { describe, expect, it } from "vitest"

import { ApiError } from "@/api/client"
import { estIntrouvable, messagePourEleve } from "./ErreurChargement"

describe("messagePourEleve", () => {
  it("garde une réponse métier du serveur, écrite pour l'élève", () => {
    expect(messagePourEleve(new ApiError(400, { detail: "Ce quiz est déjà terminé." }))).toBe("Ce quiz est déjà terminé.")
  })

  it("écarte le 404 brut de Django, les refus génériques et les pannes du serveur", () => {
    expect(messagePourEleve(new ApiError(404, { detail: "No QuizSession matches the given query." }))).toBeUndefined()
    expect(messagePourEleve(new ApiError(403, { detail: "You do not have permission." }))).toBeUndefined()
    expect(messagePourEleve(new ApiError(502, null))).toBeUndefined()
  })

  it("rien pour une erreur qui n'est pas une réponse de l'API (coupure réseau)", () => {
    expect(messagePourEleve(new TypeError("Failed to fetch"))).toBeUndefined()
  })
})

describe("estIntrouvable", () => {
  it("vrai seulement pour un 404", () => {
    expect(estIntrouvable(new ApiError(404, null))).toBe(true)
    expect(estIntrouvable(new ApiError(500, null))).toBe(false)
    expect(estIntrouvable(new TypeError("Failed to fetch"))).toBe(false)
  })
})
