import { QueryClient, QueryObserver } from "@tanstack/react-query"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getMe = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getMe }))

import { rafraichirApresActivation } from "./accesActive"

beforeEach(() => {
  getMe.mockReset().mockResolvedValue({ id: 1, a_un_abonnement_actif: true })
})

describe("rafraichirApresActivation", () => {
  it("oublie les pages verrouillées en mémoire, relit celles affichées et le compte", async () => {
    const client = new QueryClient()
    // Une épreuve lue avant de payer, dans sa version verrouillée, et que plus aucun écran n'affiche.
    client.setQueryData(["epreuve", 12], { verrouillee: true })
    // Le bandeau du haut, affiché en ce moment.
    const relire = vi.fn().mockResolvedValue({ a_reprendre: false })
    const observateur = new QueryObserver(client, { queryKey: ["paiement-a-reprendre"], queryFn: relire })
    const desabonner = observateur.subscribe(() => {})
    await vi.waitFor(() => expect(client.getQueryData(["paiement-a-reprendre"])).toEqual({ a_reprendre: false }))
    const updateUser = vi.fn()

    await rafraichirApresActivation(client, updateUser)

    expect(client.getQueryData(["epreuve", 12])).toBeUndefined()
    await vi.waitFor(() => expect(relire).toHaveBeenCalledTimes(2))
    expect(updateUser).toHaveBeenCalledWith({ id: 1, a_un_abonnement_actif: true })
    desabonner()
  })

  it("ne fait pas échouer l'écran de succès si le compte ne peut pas être relu", async () => {
    getMe.mockRejectedValue(new Error("réseau"))
    const updateUser = vi.fn()

    await expect(rafraichirApresActivation(new QueryClient(), updateUser)).resolves.toBeUndefined()
    expect(updateUser).not.toHaveBeenCalled()
  })
})
