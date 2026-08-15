import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { ErrorBoundary } from "./ErrorBoundary"

const CHUNK_RELOAD_ATTEMPTED_KEY = "edukamer_chunk_reload_attempted"

function ThrowError({ message }: { message: string }): never {
  throw new Error(message)
}

describe("ErrorBoundary", () => {
  let reloadMock: ReturnType<typeof vi.fn>
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>

  beforeEach(() => {
    sessionStorage.clear()
    // jsdom expose les méthodes de `location` (reload, assign...) comme non
    // reconfigurables sur l'objet Location natif - ni vi.spyOn() ni
    // Object.defineProperty() ne peuvent les remplacer directement ("Cannot
    // redefine property"). vi.stubGlobal() contourne le problème en substituant
    // globalThis.location tout entier par un objet neuf, plutôt que de tenter de
    // muter l'original.
    reloadMock = vi.fn()
    vi.stubGlobal("location", { ...window.location, reload: reloadMock })
    // React (et notre propre componentDidCatch) logguent l'erreur interceptée sur
    // console.error par conception - attendu ici, pas un signal d'échec du test.
    consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    consoleErrorSpy.mockRestore()
    sessionStorage.clear()
  })

  it("affiche les enfants normalement en l'absence d'erreur", () => {
    render(
      <ErrorBoundary>
        <p>Contenu normal</p>
      </ErrorBoundary>,
    )
    expect(screen.getByText("Contenu normal")).toBeInTheDocument()
  })

  it("affiche un message générique pour une erreur non liée au chargement d'un chunk", () => {
    render(
      <ErrorBoundary>
        <ThrowError message="Boom" />
      </ErrorBoundary>,
    )

    expect(screen.getByText("Une erreur inattendue est survenue")).toBeInTheDocument()
    expect(reloadMock).not.toHaveBeenCalled()
  })

  it("recharge automatiquement une seule fois sur un échec de chargement de chunk", () => {
    render(
      <ErrorBoundary>
        <ThrowError message="Failed to fetch dynamically imported module: /assets/Page.js" />
      </ErrorBoundary>,
    )

    expect(reloadMock).toHaveBeenCalledTimes(1)
    expect(sessionStorage.getItem(CHUNK_RELOAD_ATTEMPTED_KEY)).toBe("1")
    // Rien à afficher pendant ce court instant : la page est censée se recharger.
    expect(screen.queryByText(/nouvelle version/i)).not.toBeInTheDocument()
  })

  it("n'insiste pas indéfiniment - affiche un message manuel si le rechargement automatique a déjà eu lieu", () => {
    sessionStorage.setItem(CHUNK_RELOAD_ATTEMPTED_KEY, "1")

    render(
      <ErrorBoundary>
        <ThrowError message="Failed to fetch dynamically imported module: /assets/Page.js" />
      </ErrorBoundary>,
    )

    expect(reloadMock).not.toHaveBeenCalled()
    expect(screen.getByText("Une nouvelle version de l'app est disponible")).toBeInTheDocument()
  })

  it("le bouton \"Recharger la page\" réinitialise le repère de rechargement et recharge", async () => {
    const user = userEvent.setup()
    sessionStorage.setItem(CHUNK_RELOAD_ATTEMPTED_KEY, "1")

    render(
      <ErrorBoundary>
        <ThrowError message="Boom" />
      </ErrorBoundary>,
    )

    await user.click(screen.getByRole("button", { name: /recharger la page/i }))

    expect(reloadMock).toHaveBeenCalledTimes(1)
    expect(sessionStorage.getItem(CHUNK_RELOAD_ATTEMPTED_KEY)).toBeNull()
  })
})
