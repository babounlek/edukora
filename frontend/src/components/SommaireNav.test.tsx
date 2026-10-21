import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { SommaireNav } from "./SommaireNav"

class ObservateurFactice {
  observe() {}
  disconnect() {}
  unobserve() {}
}

describe("SommaireNav - clic sur une section", () => {
  beforeEach(() => {
    vi.stubGlobal("IntersectionObserver", ObservateurFactice)
    document.body.innerHTML = ""
    window.history.replaceState(null, "", "/cours/x")
  })

  it("défile jusqu'à la section et met l'adresse à jour sans ajouter d'entrée d'historique", async () => {
    const section = document.createElement("section")
    section.id = "exercices_application"
    section.scrollIntoView = vi.fn()
    document.body.appendChild(section)
    const longueur = window.history.length
    render(<SommaireNav ariaLabel="Plan" entries={[{ id: "exercices_application", short: "Exercises", long: "Exercises" }]} />)

    await userEvent.click(screen.getAllByRole("link", { name: "Exercises" })[0])

    expect(section.scrollIntoView).toHaveBeenCalled()
    expect(window.location.hash).toBe("#exercices_application")
    expect(window.history.length).toBe(longueur)
  })
})
