import { act, render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { InstallPrompt } from "./InstallPrompt"

const VISIT_COUNT_KEY = "edukamer_visit_count"
const DISMISSED_KEY = "edukamer_install_prompt_dismissed"

const DESKTOP_UA =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
const IOS_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"

function setUserAgent(ua: string) {
  Object.defineProperty(window.navigator, "userAgent", { value: ua, configurable: true })
}

function stubMatchMedia(standalone: boolean) {
  vi.stubGlobal(
    "matchMedia",
    vi.fn().mockImplementation((query: string) => ({
      matches: query === "(display-mode: standalone)" ? standalone : false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  )
}

function dispatchBeforeInstallPrompt(outcome: "accepted" | "dismissed" = "accepted") {
  const event = new Event("beforeinstallprompt", { cancelable: true }) as Event & {
    prompt: () => Promise<void>
    userChoice: Promise<{ outcome: string }>
  }
  event.prompt = vi.fn().mockResolvedValue(undefined)
  event.userChoice = Promise.resolve({ outcome })
  act(() => {
    window.dispatchEvent(event)
  })
  return event
}

describe("InstallPrompt", () => {
  beforeEach(() => {
    localStorage.clear()
    setUserAgent(DESKTOP_UA)
    stubMatchMedia(false)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    localStorage.clear()
  })

  it("ne s'affiche jamais à la toute première visite, même avec un signal d'installabilité", () => {
    render(<InstallPrompt />)
    dispatchBeforeInstallPrompt()

    expect(screen.queryByRole("button", { name: /fermer/i })).not.toBeInTheDocument()
    expect(localStorage.getItem(VISIT_COUNT_KEY)).toBe("1")
  })

  it("ne s'affiche pas à la 2e visite sans aucun signal d'installabilité (ni beforeinstallprompt, ni iOS)", () => {
    localStorage.setItem(VISIT_COUNT_KEY, "1")
    render(<InstallPrompt />)

    expect(screen.queryByRole("button", { name: /fermer/i })).not.toBeInTheDocument()
  })

  it("sur iOS, dès la 2e visite, affiche les instructions manuelles sans bouton Installer", () => {
    setUserAgent(IOS_UA)
    localStorage.setItem(VISIT_COUNT_KEY, "1")
    render(<InstallPrompt />)

    expect(screen.getByText(/partager/i)).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Installer" })).not.toBeInTheDocument()
  })

  it("sur Android/Chrome, affiche le bouton Installer une fois beforeinstallprompt reçu à la 2e visite", () => {
    localStorage.setItem(VISIT_COUNT_KEY, "1")
    render(<InstallPrompt />)
    dispatchBeforeInstallPrompt()

    expect(screen.getByRole("button", { name: "Installer" })).toBeInTheDocument()
  })

  it("cliquer Installer déclenche prompt(), referme la bannière et retient le refus futur", async () => {
    const user = userEvent.setup()
    localStorage.setItem(VISIT_COUNT_KEY, "1")
    render(<InstallPrompt />)
    const event = dispatchBeforeInstallPrompt("accepted")

    await user.click(screen.getByRole("button", { name: "Installer" }))

    expect(event.prompt).toHaveBeenCalledTimes(1)
    expect(screen.queryByRole("button", { name: "Installer" })).not.toBeInTheDocument()
    expect(localStorage.getItem(DISMISSED_KEY)).toBe("1")
  })

  it("cliquer Fermer masque la bannière et retient le refus - elle ne réapparaît pas au remontage suivant", () => {
    localStorage.setItem(VISIT_COUNT_KEY, "1")
    const { unmount } = render(<InstallPrompt />)
    dispatchBeforeInstallPrompt()

    act(() => {
      screen.getByRole("button", { name: /fermer/i }).click()
    })

    expect(screen.queryByRole("button", { name: /fermer/i })).not.toBeInTheDocument()
    expect(localStorage.getItem(DISMISSED_KEY)).toBe("1")

    unmount()
    render(<InstallPrompt />)
    dispatchBeforeInstallPrompt()
    expect(screen.queryByRole("button", { name: /fermer/i })).not.toBeInTheDocument()
  })

  it("ne s'affiche jamais en mode standalone (déjà installé)", () => {
    stubMatchMedia(true)
    localStorage.setItem(VISIT_COUNT_KEY, "1")
    render(<InstallPrompt />)
    dispatchBeforeInstallPrompt()

    expect(screen.queryByRole("button", { name: /fermer/i })).not.toBeInTheDocument()
    // Le compteur de visites lui-même ne doit pas bouger : déjà installée, cette
    // bannière n'a plus aucune raison d'être suivie.
    expect(localStorage.getItem(VISIT_COUNT_KEY)).toBe("1")
  })

  it("l'évènement appinstalled masque la bannière et retient l'installation, même sans passer par notre bouton", () => {
    localStorage.setItem(VISIT_COUNT_KEY, "1")
    render(<InstallPrompt />)
    dispatchBeforeInstallPrompt()
    expect(screen.getByRole("button", { name: "Installer" })).toBeInTheDocument()

    act(() => {
      window.dispatchEvent(new Event("appinstalled"))
    })

    expect(screen.queryByRole("button", { name: /fermer/i })).not.toBeInTheDocument()
    expect(localStorage.getItem(DISMISSED_KEY)).toBe("1")
  })
})
