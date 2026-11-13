import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { clearJetonInvite, getJetonInvite, setJetonInvite } from "@/lib/invite"
import { apiRequest, clearAccessToken, setAccessToken } from "./client"

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } })
}

function entetes(fetchMock: ReturnType<typeof vi.fn>, appel = 0): Record<string, string> {
  return fetchMock.mock.calls[appel][1].headers as Record<string, string>
}

describe("apiRequest - jeton d'invité (essai sans compte)", () => {
  let fetchMock: ReturnType<typeof vi.fn>

  beforeEach(() => {
    fetchMock = vi.fn()
    vi.stubGlobal("fetch", fetchMock)
    clearAccessToken()
    clearJetonInvite()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    clearAccessToken()
    clearJetonInvite()
  })

  it("joint le jeton d'invité aux routes inédites quand il n'y a pas de session", async () => {
    setJetonInvite("jeton-invite")
    fetchMock.mockResolvedValueOnce(jsonResponse(200, {}))

    await apiRequest("/inedit/tentatives/1/")

    expect(entetes(fetchMock).Authorization).toBe("Bearer jeton-invite")
  })

  it("ne le joint JAMAIS hors des routes inédites : ailleurs, l'invité reste un visiteur", async () => {
    setJetonInvite("jeton-invite")
    fetchMock.mockImplementation(async () => jsonResponse(200, {}))

    await apiRequest("/catalog/lessons/", { auth: "optional" })
    await apiRequest("/quiz/gratuits/", { auth: "optional" })

    expect(entetes(fetchMock, 0).Authorization).toBeUndefined()
    expect(entetes(fetchMock, 1).Authorization).toBeUndefined()
  })

  it("le joint aux routes d'une séance de quiz, et à elles seules : parcours, plan et bilan restent anonymes", async () => {
    setJetonInvite("jeton-invite")
    fetchMock.mockImplementation(async () => jsonResponse(200, {}))
    const ouvertes = [
      "/quiz/sessions/", "/quiz/sessions/12/", "/quiz/sessions/12/questions/34/answer/",
      "/quiz/sessions/12/questions/34/corrige/", "/quiz/sessions/12/completer/", "/quiz/sessions/12/refaire-ratees/",
      "/quiz/en-cours/", "/quiz/historique/12/", "/quiz/historique/12/rejouer/",
    ]
    const fermees = [
      "/quiz/parcours/", "/quiz/plan-du-jour/", "/quiz/accueil/", "/quiz/historique/", "/quiz/sessions/12/fiche-pdf/",
      "/quiz/essais/", "/auth/me/",
    ]

    for (const chemin of [...ouvertes, ...fermees]) await apiRequest(chemin, { auth: "optional" })

    ouvertes.forEach((_, i) => expect(entetes(fetchMock, i).Authorization).toBe("Bearer jeton-invite"))
    fermees.forEach((_, i) => expect(entetes(fetchMock, ouvertes.length + i).Authorization).toBeUndefined())
  })

  it("préfère la vraie session au jeton d'invité", async () => {
    setJetonInvite("jeton-invite")
    setAccessToken("vrai-jeton") // ouvre une session : l'essai sans compte est terminé
    fetchMock.mockResolvedValueOnce(jsonResponse(200, {}))

    await apiRequest("/inedit/tentatives/1/")

    expect(entetes(fetchMock).Authorization).toBe("Bearer vrai-jeton")
  })

  it("ouvrir une session efface le jeton d'invité (le serveur a transmis la copie au compte)", () => {
    setJetonInvite("jeton-invite")
    setAccessToken("vrai-jeton")
    expect(getJetonInvite()).toBeNull()
  })

  it("joint le jeton d'invité aux trois routes de connexion, pour que la copie passe au compte", async () => {
    setJetonInvite("jeton-invite")
    fetchMock.mockImplementation(async () => jsonResponse(200, { access: "x" }))

    await apiRequest("/auth/otp/verify/", { method: "POST", auth: false, body: {} })
    await apiRequest("/auth/email/verify/", { method: "POST", auth: false, body: {} })
    await apiRequest("/auth/google/", { method: "POST", auth: false, body: {} })

    for (const appel of [0, 1, 2]) expect(entetes(fetchMock, appel)["X-Invite-Token"]).toBe("jeton-invite")
  })

  it("n'envoie pas l'en-tête de rattachement aux autres routes d'authentification", async () => {
    setJetonInvite("jeton-invite")
    fetchMock.mockResolvedValueOnce(jsonResponse(200, {}))

    await apiRequest("/auth/otp/request/", { method: "POST", auth: false, body: {} })

    expect(entetes(fetchMock)["X-Invite-Token"]).toBeUndefined()
  })

  it("un jeton d'invité refusé (401) est oublié, sans tenter de refresh ni signaler de session expirée", async () => {
    setJetonInvite("jeton-perime")
    const expire = vi.fn()
    window.addEventListener("edukamer:session-expired", expire)
    fetchMock.mockResolvedValueOnce(jsonResponse(401, { error: "unauthorized" }))

    await expect(apiRequest("/inedit/tentatives/1/")).rejects.toMatchObject({ status: 401 })

    expect(getJetonInvite()).toBeNull()
    expect(fetchMock).toHaveBeenCalledTimes(1) // aucun appel /auth/token/refresh/
    expect(expire).not.toHaveBeenCalled()
    window.removeEventListener("edukamer:session-expired", expire)
  })

  it("auth « optional » : un jeton d'invité refusé retombe en anonyme", async () => {
    setJetonInvite("jeton-perime")
    fetchMock
      .mockResolvedValueOnce(jsonResponse(401, { error: "unauthorized" }))
      .mockResolvedValueOnce(jsonResponse(200, { id: 3 }))

    const data = await apiRequest("/inedit/epreuves/x/", { auth: "optional" })

    expect(data).toEqual({ id: 3 })
    expect(entetes(fetchMock, 1).Authorization).toBeUndefined()
    expect(getJetonInvite()).toBeNull()
  })
})
