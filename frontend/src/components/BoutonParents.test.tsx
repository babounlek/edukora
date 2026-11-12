import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { BoutonParents } from "./BoutonParents"

vi.mock("@/context/AuthContext", () => ({ useAuth: () => ({ user: { referral_code: "GUY123" } }) }))
vi.mock("@/api/endpoints", async (importOriginal) => ({
  ...(await importOriginal<object>()),
  getCampagneEnCours: vi.fn().mockResolvedValue(null),
}))

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <BoutonParents examen="BEPC" contenu="lire le corrigé de « SVT BEPC 2025 »" />
    </QueryClientProvider>,
  )
}

describe("BoutonParents", () => {
  const partager = vi.fn().mockResolvedValue(undefined)

  beforeEach(() => {
    partager.mockClear()
    Object.defineProperty(navigator, "share", { value: partager, configurable: true })
    window.matchMedia = vi.fn().mockReturnValue({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() }) as never
  })

  afterEach(() => {
    // @ts-expect-error nettoyage d'un champ posé pour le test
    delete navigator.share
  })

  it("partage la page des prix avec un message écrit pour les parents, au nom de l'élève", async () => {
    afficher()
    await userEvent.click(screen.getByRole("button", { name: "Montrer à mes parents" }))

    await waitFor(() => expect(partager).toHaveBeenCalledTimes(1))
    const { text } = partager.mock.calls[0][0] as { text: string }
    expect(text).toContain("Bonjour, je prépare le BEPC")
    expect(text).toContain("lire le corrigé de « SVT BEPC 2025 »")
    expect(text).toContain("2 000 FCFA par mois")
    expect(text).toContain("Mobile Money")
    expect(text).toContain("WhatsApp +237 689 49 26 25")
    expect(text).toMatch(/\/tarifs\?ref=GUY123$/)
  })
})
