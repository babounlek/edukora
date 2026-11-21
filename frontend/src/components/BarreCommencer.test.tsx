import { act, fireEvent, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const etat = vi.hoisted(() => ({
  seance: {} as Record<string, unknown>,
  commencer: vi.fn(),
}))
const trackEvent = vi.hoisted(() => vi.fn())

vi.mock("@/components/PremiereSeance", () => ({ usePremiereSeance: () => ({ ...etat.seance, commencer: etat.commencer }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent }))

import { BarreCommencer } from "./BarreCommencer"

const BEPC = { id: 14, examen: "BEPC", examen_display: "BEPC", series: null }
const ESSAI = { cursus: 14, subject: 5, subject_label: "Mathématiques", subject_code: "MATHS", theme: 20, theme_name: "identité remarquable", nb_questions: 5 }

/** Un IntersectionObserver de test : on lui dit ce qui est à l'écran, il prévient comme le vrai. */
let prevenir: (entrees: Partial<IntersectionObserverEntry>[]) => void = () => {}
class ObservateurFactice {
  constructor(rappel: (entrees: IntersectionObserverEntry[]) => void) {
    prevenir = (entrees) => rappel(entrees as IntersectionObserverEntry[])
  }
  observe() {}
  disconnect() {}
}

function afficher() {
  return render(
    <MemoryRouter>
      <section data-guide="premiere-seance">Ta première séance</section>
      <section data-fin-vitrine>Prêt à commencer ?</section>
      <BarreCommencer country="cm" />
    </MemoryRouter>,
  )
}

const carte = () => document.querySelector('[data-guide="premiere-seance"]')!
const fin = () => document.querySelector("[data-fin-vitrine]")!
/** La carte du hero est passée au-dessus de l'écran. */
const depasserLaCarte = () =>
  act(() => prevenir([{ target: carte(), isIntersecting: false, boundingClientRect: { bottom: -40 } as DOMRectReadOnly }]))

beforeEach(() => {
  vi.stubGlobal("IntersectionObserver", ObservateurFactice)
  etat.seance = { choisi: BEPC, connecte: false, essaisEnAttente: false, essai: ESSAI, faites: 0, total: 3, lancement: false }
  etat.commencer.mockReset()
  trackEvent.mockReset()
})

afterEach(() => vi.unstubAllGlobals())

describe("BarreCommencer : le bouton qui suit le visiteur sur un téléphone", () => {
  it("absente tant que la carte du hero est à l'écran, ou encore sous l'écran", () => {
    afficher()
    expect(screen.queryByRole("region", { name: "Commencer ta séance" })).toBeNull()

    act(() => prevenir([{ target: carte(), isIntersecting: false, boundingClientRect: { bottom: 900 } as DOMRectReadOnly }]))
    expect(screen.queryByRole("region", { name: "Commencer ta séance" })).toBeNull()
  })

  it("carte dépassée : l'examen, le thème, et la même action que la carte", () => {
    afficher()
    depasserLaCarte()

    expect(screen.getByRole("region", { name: "Commencer ta séance" })).toBeInTheDocument()
    expect(screen.getByText("BEPC · Mathématiques")).toBeInTheDocument()
    expect(screen.getByText("Identité remarquable")).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: /Commencer/ }))
    expect(etat.commencer).toHaveBeenCalledWith(ESSAI)
  })

  it("s'efface en arrivant au dernier bloc, et revient si l'on remonte", () => {
    afficher()
    depasserLaCarte()
    act(() => prevenir([{ target: fin(), isIntersecting: true }]))
    expect(screen.queryByRole("region", { name: "Commencer ta séance" })).toBeNull()

    act(() => prevenir([{ target: fin(), isIntersecting: false }]))
    expect(screen.getByRole("region", { name: "Commencer ta séance" })).toBeInTheDocument()
  })

  it("sans examen choisi : ramène à la question du hero", () => {
    etat.seance = { choisi: null, connecte: false, essaisEnAttente: false, essai: null, faites: 0, total: 0, lancement: false }
    const defiler = vi.fn()
    afficher()
    carte().scrollIntoView = defiler
    depasserLaCarte()

    fireEvent.click(screen.getByRole("button", { name: "Choisir mon examen" }))
    expect(defiler).toHaveBeenCalled()
    expect(etat.commencer).not.toHaveBeenCalled()
  })

  it("toutes les séances gratuites jouées : mène aux abonnements ; aucune séance pour l'examen : pas de barre vide", () => {
    etat.seance = { choisi: BEPC, connecte: false, essaisEnAttente: false, essai: null, faites: 3, total: 3, lancement: false }
    const { unmount } = afficher()
    depasserLaCarte()
    expect(screen.getByRole("link", { name: /Voir les abonnements/ })).toHaveAttribute("href", "/tarifs")
    unmount()

    etat.seance = { choisi: BEPC, connecte: false, essaisEnAttente: false, essai: null, faites: 0, total: 0, lancement: false }
    afficher()
    depasserLaCarte()
    expect(screen.queryByRole("region", { name: "Commencer ta séance" })).toBeNull()
  })
})
