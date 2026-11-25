import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { beforeEach, describe, expect, it, vi } from "vitest"

const getAvisSeance = vi.hoisted(() => vi.fn())
const trackEvent = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ getAvisSeance }))
vi.mock("@/lib/analytics", () => ({ trackEvent }))

import { AvisSeance } from "./AvisSeance"

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <AvisSeance subjectId={4} themeId={9} />
    </QueryClientProvider>,
  )
}

describe("AvisSeance", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    getAvisSeance.mockResolvedValue({ demander: true })
  })

  it("« oui » part en un toucher, avec la matière et le thème de la séance", async () => {
    afficher()
    await userEvent.click(await screen.findByRole("button", { name: "Oui" }))

    expect(trackEvent).toHaveBeenCalledWith("seance_avis", { avis: "oui", subject_id: 4, theme_id: 9 })
    expect(screen.getByRole("status")).toHaveTextContent("Merci")
  })

  it("« non » demande un motif dans une liste fermée avant de partir", async () => {
    afficher()
    await userEvent.click(await screen.findByRole("button", { name: "Non" }))
    expect(trackEvent).not.toHaveBeenCalled()
    await userEvent.click(screen.getByRole("button", { name: "Trop difficile" }))

    expect(trackEvent).toHaveBeenCalledWith("seance_avis", { avis: "non", motif: "trop_difficile", subject_id: 4, theme_id: 9 })
  })

  it("ne demande rien quand le serveur ne le demande pas", async () => {
    getAvisSeance.mockResolvedValue({ demander: false })
    afficher()

    await vi.waitFor(() => expect(getAvisSeance).toHaveBeenCalled())
    expect(screen.queryByRole("button")).not.toBeInTheDocument()
  })
})
