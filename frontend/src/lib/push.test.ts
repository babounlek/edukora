import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { getPushCle, abonnerPush, desabonnerPush } = vi.hoisted(() => ({
  getPushCle: vi.fn(),
  abonnerPush: vi.fn(() => Promise.resolve({ abonne: true })),
  desabonnerPush: vi.fn(() => Promise.resolve({ abonne: false })),
}))
vi.mock("@/api/endpoints", () => ({ getPushCle, abonnerPush, desabonnerPush }))

import { activerPush, cleEnOctets, desactiverPush, etatPush, oublierPushLocal, pushSupporte } from "./push"

interface FauxAbonnement {
  endpoint: string
  toJSON: () => { endpoint: string; keys: { p256dh: string; auth: string } }
  unsubscribe: ReturnType<typeof vi.fn>
}

function abonnement(): FauxAbonnement {
  return {
    endpoint: "https://push.example.com/abc",
    toJSON: () => ({ endpoint: "https://push.example.com/abc", keys: { p256dh: "kp", auth: "ka" } }),
    unsubscribe: vi.fn(() => Promise.resolve(true)),
  }
}

/** Installe un navigateur « avec push » : un worker enregistré, un PushManager, Notification. */
function navigateurAvecPush(opts: { permission?: NotificationPermission; existant?: FauxAbonnement | null; worker?: boolean } = {}) {
  const { permission = "default", existant = null, worker = true } = opts
  const nouveau = abonnement()
  const pushManager = {
    getSubscription: vi.fn(() => Promise.resolve(existant)),
    subscribe: vi.fn(() => Promise.resolve(nouveau)),
  }
  Object.defineProperty(navigator, "serviceWorker", {
    value: { getRegistration: vi.fn(() => Promise.resolve(worker ? { pushManager } : undefined)) },
    configurable: true,
  })
  vi.stubGlobal("PushManager", class {})
  vi.stubGlobal("Notification", { permission, requestPermission: vi.fn(() => Promise.resolve(permission === "default" ? "granted" : permission)) })
  return { pushManager, nouveau }
}

describe("lib/push", () => {
  beforeEach(() => {
    getPushCle.mockReset()
    abonnerPush.mockClear()
    desabonnerPush.mockClear()
    getPushCle.mockResolvedValue({ actif: true, cle: "BPk" })
  })
  afterEach(() => {
    vi.unstubAllGlobals()
    Reflect.deleteProperty(navigator, "serviceWorker")
  })

  describe("cleEnOctets", () => {
    it("décode une clé base64url", () => {
      // « hello » en base64url sans remplissage.
      expect(Array.from(cleEnOctets("aGVsbG8"))).toEqual([104, 101, 108, 108, 111])
    })

    it("accepte les caractères base64url - et _", () => {
      expect(Array.from(cleEnOctets("-_8"))).toEqual([251, 255])
    })
  })

  describe("etatPush", () => {
    it("est indisponible sans support du navigateur", async () => {
      expect(pushSupporte()).toBe(false)
      expect(await etatPush()).toBe("indisponible")
    })

    it("est indisponible sans service worker enregistré (mode économie de données, serveur de dev)", async () => {
      navigateurAvecPush({ worker: false })
      expect(await etatPush()).toBe("indisponible")
    })

    it("est indisponible quand le serveur n'a pas de clés", async () => {
      navigateurAvecPush()
      getPushCle.mockResolvedValue({ actif: false, cle: "" })
      expect(await etatPush()).toBe("indisponible")
    })

    it("est indisponible quand le serveur ne répond pas", async () => {
      navigateurAvecPush()
      getPushCle.mockRejectedValue(new Error("réseau"))
      expect(await etatPush()).toBe("indisponible")
    })

    it("est refusé quand les notifications sont bloquées", async () => {
      navigateurAvecPush({ permission: "denied" })
      expect(await etatPush()).toBe("refuse")
    })

    it("est inactif sans abonnement, actif avec un", async () => {
      navigateurAvecPush({ permission: "granted" })
      expect(await etatPush()).toBe("inactif")
      navigateurAvecPush({ permission: "granted", existant: abonnement() })
      expect(await etatPush()).toBe("actif")
    })
  })

  describe("activerPush", () => {
    it("demande la permission, abonne l'appareil et l'enregistre sur le serveur", async () => {
      const { pushManager } = navigateurAvecPush()
      expect(await activerPush()).toBe("actif")
      expect(pushManager.subscribe).toHaveBeenCalledWith(expect.objectContaining({ userVisibleOnly: true }))
      expect(abonnerPush).toHaveBeenCalledWith({ endpoint: "https://push.example.com/abc", keys: { p256dh: "kp", auth: "ka" } })
    })

    it("ne s'abonne pas quand l'élève refuse", async () => {
      const { pushManager } = navigateurAvecPush({ permission: "denied" })
      expect(await activerPush()).toBe("refuse")
      expect(pushManager.subscribe).not.toHaveBeenCalled()
      expect(abonnerPush).not.toHaveBeenCalled()
    })

    it("réutilise l'abonnement existant du navigateur", async () => {
      const { pushManager } = navigateurAvecPush({ permission: "granted", existant: abonnement() })
      expect(await activerPush()).toBe("actif")
      expect(pushManager.subscribe).not.toHaveBeenCalled()
    })

    it("est indisponible quand le serveur n'a pas de clés", async () => {
      navigateurAvecPush()
      getPushCle.mockResolvedValue({ actif: false, cle: "" })
      expect(await activerPush()).toBe("indisponible")
      expect(abonnerPush).not.toHaveBeenCalled()
    })
  })

  describe("desactiverPush et oublierPushLocal", () => {
    it("coupe côté serveur puis dans le navigateur", async () => {
      const existant = abonnement()
      navigateurAvecPush({ permission: "granted", existant })
      await desactiverPush()
      expect(desabonnerPush).toHaveBeenCalledWith("https://push.example.com/abc")
      expect(existant.unsubscribe).toHaveBeenCalled()
    })

    it("à la déconnexion, ne désabonne que le navigateur (la session est déjà fermée)", async () => {
      const existant = abonnement()
      navigateurAvecPush({ permission: "granted", existant })
      await oublierPushLocal()
      expect(existant.unsubscribe).toHaveBeenCalled()
      expect(desabonnerPush).not.toHaveBeenCalled()
    })

    it("à la déconnexion, ne plante jamais", async () => {
      Object.defineProperty(navigator, "serviceWorker", {
        value: { getRegistration: () => Promise.reject(new Error("boum")) }, configurable: true,
      })
      vi.stubGlobal("PushManager", class {})
      vi.stubGlobal("Notification", { permission: "granted" })
      await expect(oublierPushLocal()).resolves.toBeUndefined()
    })
  })
})
