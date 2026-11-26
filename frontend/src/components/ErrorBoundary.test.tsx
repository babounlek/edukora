import type { ReactNode } from "react"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes, useNavigate } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { Sentry } from "@/lib/sentry"
import { ErrorBoundary } from "./ErrorBoundary"

const CHUNK_RELOAD_ATTEMPTED_KEY = "edukamer_chunk_reload_attempted"

function ThrowError({ message }: { message: string }): never {
  throw new Error(message)
}

/** Un lien de l'en-tête, hors du filet : il reste cliquable quand la page est en erreur. */
function Aller({ vers }: { vers: string }) {
  const navigate = useNavigate()
  return (
    <button type="button" onClick={() => navigate(vers)}>
      Aller vers {vers}
    </button>
  )
}

function afficherRoutes(depart: string, pages: Record<string, ReactNode>) {
  return render(
    <MemoryRouter initialEntries={[depart]}>
      {Object.keys(pages).map((chemin) => (
        <Aller key={chemin} vers={chemin} />
      ))}
      <ErrorBoundary reinitialiserSurNavigation>
        <Routes>
          {Object.entries(pages).map(([chemin, element]) => (
            <Route key={chemin} path={chemin} element={element} />
          ))}
        </Routes>
      </ErrorBoundary>
    </MemoryRouter>,
  )
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

  describe("sous le routeur, avec reinitialiserSurNavigation", () => {
    it("efface l'erreur quand l'élève change de page, sans recharger", async () => {
      const user = userEvent.setup()
      afficherRoutes("/casse", {
        "/casse": <ThrowError message="Boom" />,
        "/ok": <p>Page OK</p>,
      })
      expect(screen.getByText("Une erreur inattendue est survenue")).toBeInTheDocument()

      await user.click(screen.getByRole("button", { name: "Aller vers /ok" }))

      expect(await screen.findByText("Page OK")).toBeInTheDocument()
      expect(screen.queryByText("Une erreur inattendue est survenue")).not.toBeInTheDocument()
      expect(reloadMock).not.toHaveBeenCalled()
    })

    it("une page d'arrivée qui plante aussi garde l'écran d'erreur, sans planter une seconde fois", async () => {
      const user = userEvent.setup()
      const capture = vi.spyOn(Sentry, "captureException")
      afficherRoutes("/ok", {
        "/ok": <p>Page OK</p>,
        "/casse": <ThrowError message="Boom" />,
        "/casse-aussi": <ThrowError message="Re-boom" />,
      })

      // Arrivée sur une page qui plante : l'adresse et l'erreur changent dans le même rendu, l'erreur reste.
      await user.click(screen.getByRole("button", { name: "Aller vers /casse" }))
      expect(screen.getByText("Une erreur inattendue est survenue")).toBeInTheDocument()
      expect(capture).toHaveBeenCalledTimes(1)

      // D'une page en erreur à une autre qui plante : effacée une fois, interceptée une fois.
      await user.click(screen.getByRole("button", { name: "Aller vers /casse-aussi" }))
      expect(screen.getByText("Une erreur inattendue est survenue")).toBeInTheDocument()
      expect(capture).toHaveBeenCalledTimes(2)
      expect(capture.mock.calls[1][0]).toMatchObject({ message: "Re-boom" })
      capture.mockRestore()
    })

    it("un chunk encore introuvable sur la page suivante ne relance pas de rechargement en boucle", async () => {
      const user = userEvent.setup()
      sessionStorage.setItem(CHUNK_RELOAD_ATTEMPTED_KEY, "1")
      afficherRoutes("/a", {
        "/a": <ThrowError message="Failed to fetch dynamically imported module: /assets/A.js" />,
        "/b": <ThrowError message="Failed to fetch dynamically imported module: /assets/B.js" />,
      })
      expect(screen.getByText("Une nouvelle version de l'app est disponible")).toBeInTheDocument()

      await user.click(screen.getByRole("button", { name: "Aller vers /b" }))

      expect(screen.getByText("Une nouvelle version de l'app est disponible")).toBeInTheDocument()
      expect(reloadMock).not.toHaveBeenCalled()
    })
  })
})
