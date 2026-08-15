import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { apiRequest, clearAccessToken, setAccessToken } from "./client"

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  })
}

describe('apiRequest - auth: "optional"', () => {
  let fetchMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    fetchMock = vi.fn()
    vi.stubGlobal("fetch", fetchMock)
    setAccessToken("stale-token")
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    clearAccessToken()
  })

  it("retombe en anonyme si le refresh réussit mais que la requête rejouée 401 quand même (compte supprimé, cookie de refresh encore valide)", async () => {
    fetchMock
      // 1. requête initiale avec le token périmé gardé en mémoire
      .mockResolvedValueOnce(jsonResponse(401, { error: "unauthorized" }))
      // 2. refresh : le cookie httpOnly est encore valide, renvoie un nouvel access token
      .mockResolvedValueOnce(jsonResponse(200, { access: "fresh-token" }))
      // 3. requête rejouée avec ce nouveau token : 401 quand même (JWTAuthentication
      //    résout un user_id qui n'existe plus en base, ex. compte supprimé)
      .mockResolvedValueOnce(jsonResponse(401, { error: "unauthorized" }))
      // 4. repli anonyme attendu : la ressource est publique (est_vitrine)
      .mockResolvedValueOnce(jsonResponse(200, { results: [] }))

    const data = await apiRequest("/catalog/lessons/", { auth: "optional" })

    expect(data).toEqual({ results: [] })
    expect(fetchMock).toHaveBeenCalledTimes(4)

    const lastCallHeaders = fetchMock.mock.calls[3][1].headers as Record<string, string>
    expect(lastCallHeaders.Authorization).toBeUndefined()
  })

  it('garde le contrat existant : refresh réussi + requête rejouée réussie ne passe pas par l\'anonyme', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse(401, { error: "unauthorized" }))
      .mockResolvedValueOnce(jsonResponse(200, { access: "fresh-token" }))
      .mockResolvedValueOnce(jsonResponse(200, { results: ["ok"] }))

    const data = await apiRequest("/catalog/lessons/", { auth: "optional" })

    expect(data).toEqual({ results: ["ok"] })
    expect(fetchMock).toHaveBeenCalledTimes(3)
  })

  it('auth stricte (pas "optional") : une requête encore 401 après refresh remonte en ApiError, sans repli anonyme', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse(401, { error: "unauthorized" }))
      .mockResolvedValueOnce(jsonResponse(200, { access: "fresh-token" }))
      .mockResolvedValueOnce(jsonResponse(401, { error: "unauthorized" }))

    await expect(apiRequest("/users/me/", { auth: true })).rejects.toMatchObject({ status: 401 })
    expect(fetchMock).toHaveBeenCalledTimes(3)
  })
})
