import { afterEach, describe, expect, it, vi } from "vitest"

import { ApiError, NetworkError, apiRequest } from "@/api/client"

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe("apiRequest : pannes réseau", () => {
  it("lève une NetworkError (et jamais une ApiError) quand le serveur est injoignable", async () => {
    // Les écrans à file hors ligne reconnaissent « pas de réponse » à !(err instanceof ApiError).
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")))
    const err = (await apiRequest("/x/", { auth: false }).catch((e) => e)) as Error & { timedOut?: boolean }
    expect(err).toBeInstanceOf(NetworkError)
    expect(err).not.toBeInstanceOf(ApiError)
    expect(err.message).toMatch(/Connexion instable/)
  })

  it("abandonne une requête qui ne répond pas dans le délai", async () => {
    vi.useFakeTimers()
    vi.stubGlobal(
      "fetch",
      vi.fn((_url: string, init: RequestInit) =>
        new Promise((_resolve, reject) => {
          init.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")))
        }),
      ),
    )
    const promesse = apiRequest("/x/", { auth: false }).catch((e) => e)
    await vi.advanceTimersByTimeAsync(26_000)
    const err = (await promesse) as Error & { timedOut?: boolean }
    expect(err).toBeInstanceOf(NetworkError)
    expect(err.timedOut).toBe(true)
  })

  it("laisse passer l'annulation voulue par l'appelant", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((_url: string, init: RequestInit) =>
        new Promise((_resolve, reject) => {
          init.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")))
        }),
      ),
    )
    const controller = new AbortController()
    const promesse = apiRequest("/x/", { auth: false, signal: controller.signal }).catch((e) => e)
    controller.abort()
    const err = (await promesse) as Error & { timedOut?: boolean }
    expect(err).not.toBeInstanceOf(NetworkError)
    expect(err.name).toBe("AbortError")
  })

  it("traduit le message anglais de limitation de débit", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Request was throttled. Expected available in 30 seconds." }), {
          status: 429,
          headers: { "content-type": "application/json" },
        }),
      ),
    )
    const err = (await apiRequest("/x/", { auth: false }).catch((e) => e)) as Error & { timedOut?: boolean }
    expect(err).toBeInstanceOf(ApiError)
    expect(err.message).toMatch(/Trop de demandes/)
  })
})

describe("apiRequest : heure du serveur", () => {
  it("aligne l'horloge d'affichage sur l'en-tête Date de la réponse", async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date("2026-10-12T10:00:00Z"))
    const { maintenantServeur, reinitialiserHorlogeServeur } = await import("@/lib/horlogeServeur")
    // Téléphone en retard de 7 minutes sur le serveur.
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response("{}", {
          status: 200,
          headers: { "content-type": "application/json", date: "Mon, 12 Oct 2026 10:07:00 GMT" },
        }),
      ),
    )
    await apiRequest("/x/", { auth: false })
    expect(maintenantServeur() - Date.now()).toBe(7 * 60_000 + 500)
    reinitialiserHorlogeServeur()
  })
})
