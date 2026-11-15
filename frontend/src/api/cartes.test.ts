import { describe, expect, it, vi } from "vitest"

const { apiRequest } = vi.hoisted(() => ({ apiRequest: vi.fn(() => Promise.resolve({})) }))
vi.mock("@/api/client", async (importOriginal) => ({ ...(await importOriginal<object>()), apiRequest }))

import { noterCarte } from "@/api/endpoints"

describe("noterCarte", () => {
  it("passe un objet : le client le sérialise lui-même (une chaîne JSON serait doublement encodée et refusée)", async () => {
    await noterCarte("derivees", "regle", false)
    expect(apiRequest).toHaveBeenCalledWith("/quiz/cartes/cours/derivees/regle/", { method: "POST", body: { savais: false } })
  })
})
