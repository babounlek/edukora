import { beforeEach, describe, expect, it, vi } from "vitest"

const apiRequest = vi.hoisted(() => vi.fn())
vi.mock("./client", () => ({ apiRequest, API_BASE_URL: "http://api", getAccessToken: () => null }))

import { getQuizHistoriqueDetail, listQuizEnCours, listQuizHistorique } from "./endpoints"

// apiRequest rend null quand le corps n'est pas du JSON - typiquement le index.html du site servi à la place de
// l'API par un proxy qui ne connaît pas la route. Ces appels doivent alors ÉCHOUER (la page affiche « réessayer »),
// jamais rendre null à un composant qui lit `.results` et plante toute la page.
describe("réponses inattendues de l'historique des quiz", () => {
  beforeEach(() => apiRequest.mockReset())

  it("l'historique refuse une réponse qui n'est pas une page de résultats", async () => {
    apiRequest.mockResolvedValue(null)
    await expect(listQuizHistorique(1)).rejects.toThrow()
  })

  it("la liste en cours refuse une réponse qui n'est pas une liste", async () => {
    apiRequest.mockResolvedValue(null)
    await expect(listQuizEnCours()).rejects.toThrow()
  })

  it("le détail refuse une réponse sans questions", async () => {
    apiRequest.mockResolvedValue(null)
    await expect(getQuizHistoriqueDetail(3)).rejects.toThrow()
  })

  it("laisse passer les réponses bien formées", async () => {
    apiRequest.mockResolvedValueOnce({ count: 0, next: null, previous: null, results: [] })
    apiRequest.mockResolvedValueOnce([])
    await expect(listQuizHistorique(2)).resolves.toMatchObject({ results: [] })
    await expect(listQuizEnCours()).resolves.toEqual([])
    expect(apiRequest).toHaveBeenCalledWith("/quiz/historique/?page=2", expect.anything())
  })
})
