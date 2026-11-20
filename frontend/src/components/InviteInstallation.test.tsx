import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest"

vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }))

import { ecouterInstallation } from "@/lib/installation"
import { InviteInstallation } from "./InviteInstallation"

/** L'évènement que Chrome émet quand l'application est installable : `prompt` ouvre sa fenêtre, `userChoice` dit le choix. */
function annoncerInstallable(choix: "accepted" | "dismissed" = "accepted") {
  const evenement = Object.assign(new Event("beforeinstallprompt", { cancelable: true }), {
    prompt: vi.fn().mockResolvedValue(undefined),
    userChoice: Promise.resolve({ outcome: choix }),
  })
  act(() => {
    window.dispatchEvent(evenement)
  })
  return evenement
}

describe("InviteInstallation", () => {
  beforeAll(() => {
    // jsdom n'a pas matchMedia : « pas déjà installée ».
    window.matchMedia = vi.fn().mockReturnValue({ matches: false }) as unknown as typeof window.matchMedia
    ecouterInstallation()
  })
  beforeEach(() => localStorage.clear())

  it("ne montre rien tant que le navigateur n'a pas dit qu'il peut installer", () => {
    const { container } = render(<InviteInstallation />)
    expect(container).toBeEmptyDOMElement()
  })

  it("propose d'installer, ouvre la fenêtre du navigateur au toucher, puis disparaît", async () => {
    render(<InviteInstallation />)
    const evenement = annoncerInstallable("accepted")
    // La bannière automatique de Chrome est retenue : c'est nous qui choisissons le moment.
    expect(evenement.defaultPrevented).toBe(true)

    fireEvent.click(await screen.findByRole("button", { name: "Installer" }))

    await waitFor(() => expect(evenement.prompt).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(screen.queryByRole("button", { name: "Installer" })).toBeNull())
  })

  it("« Plus tard » la fait disparaître pour de bon sur cet appareil", async () => {
    const { unmount } = render(<InviteInstallation />)
    annoncerInstallable()
    fireEvent.click(await screen.findByRole("button", { name: "Plus tard" }))
    expect(screen.queryByRole("button", { name: "Installer" })).toBeNull()

    unmount()
    render(<InviteInstallation />)
    annoncerInstallable()
    expect(screen.queryByRole("button", { name: "Installer" })).toBeNull()
  })

  it("ne s'affiche pas dans l'application déjà installée", () => {
    window.matchMedia = vi.fn().mockReturnValue({ matches: true }) as unknown as typeof window.matchMedia
    render(<InviteInstallation />)
    annoncerInstallable()
    expect(screen.queryByRole("button", { name: "Installer" })).toBeNull()
  })
})
