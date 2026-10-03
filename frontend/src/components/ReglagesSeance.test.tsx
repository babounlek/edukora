import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { etatPush, activerPush, desactiverPush } = vi.hoisted(() => ({
  etatPush: vi.fn(),
  activerPush: vi.fn(),
  desactiverPush: vi.fn(() => Promise.resolve()),
}))
vi.mock("@/lib/push", () => ({ etatPush, activerPush, desactiverPush }))
vi.mock("@/api/endpoints", () => ({ definirObjectifXp: vi.fn(), getObjectifXp: vi.fn() }))
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }))

import { InterrupteurPush, InvitePush } from "./ReglagesSeance"

function afficher(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}

beforeEach(() => {
  etatPush.mockReset()
  activerPush.mockReset()
  desactiverPush.mockClear()
  localStorage.clear()
})

describe("InterrupteurPush", () => {
  it("ne montre rien quand les notifications ne peuvent pas exister", async () => {
    etatPush.mockResolvedValue("indisponible")
    const { container } = afficher(<InterrupteurPush />)
    await waitFor(() => expect(etatPush).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it("active les notifications au clic", async () => {
    etatPush.mockResolvedValue("inactif")
    activerPush.mockResolvedValue("actif")
    afficher(<InterrupteurPush />)
    const interrupteur = await screen.findByRole("switch", { name: "Un rappel sur cet appareil" })
    expect(interrupteur).toHaveAttribute("aria-checked", "false")
    fireEvent.click(interrupteur)
    await waitFor(() => expect(screen.getByRole("switch")).toHaveAttribute("aria-checked", "true"))
  })

  it("coupe les notifications quand elles sont actives", async () => {
    etatPush.mockResolvedValue("actif")
    afficher(<InterrupteurPush />)
    fireEvent.click(await screen.findByRole("switch"))
    await waitFor(() => expect(screen.getByRole("switch")).toHaveAttribute("aria-checked", "false"))
    expect(desactiverPush).toHaveBeenCalled()
  })

  it("explique et bloque l'interrupteur quand le navigateur refuse", async () => {
    etatPush.mockResolvedValue("refuse")
    afficher(<InterrupteurPush />)
    expect(await screen.findByRole("switch")).toBeDisabled()
    expect(screen.getByText(/bloquées dans ton navigateur/)).toBeInTheDocument()
  })
})

describe("InvitePush", () => {
  it("propose d'activer quand c'est possible, et s'écarte pour de bon", async () => {
    etatPush.mockResolvedValue("inactif")
    const { unmount } = afficher(<InvitePush />)
    fireEvent.click(await screen.findByRole("button", { name: "Non merci" }))
    expect(screen.queryByText(/ton heure habituelle/)).not.toBeInTheDocument()
    unmount()

    afficher(<InvitePush />)
    expect(screen.queryByText(/ton heure habituelle/)).not.toBeInTheDocument()
  })

  it("ne s'affiche pas à qui ne peut pas ou a déjà dit non au navigateur", async () => {
    for (const etat of ["indisponible", "refuse", "actif"]) {
      etatPush.mockResolvedValue(etat)
      const { container, unmount } = afficher(<InvitePush />)
      await waitFor(() => expect(etatPush).toHaveBeenCalled())
      expect(container).toBeEmptyDOMElement()
      unmount()
      etatPush.mockClear()
    }
  })

  it("active au clic puis disparaît", async () => {
    etatPush.mockResolvedValue("inactif")
    activerPush.mockResolvedValue("actif")
    afficher(<InvitePush />)
    fireEvent.click(await screen.findByRole("button", { name: "Activer" }))
    await waitFor(() => expect(screen.queryByText(/ton heure habituelle/)).not.toBeInTheDocument())
    expect(activerPush).toHaveBeenCalled()
  })
})
