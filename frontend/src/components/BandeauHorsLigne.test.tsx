import { act, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it } from "vitest"

import { BandeauHorsLigne } from "./BandeauHorsLigne"

function reseau(enLigne: boolean) {
  Object.defineProperty(window.navigator, "onLine", { value: enLigne, configurable: true })
  act(() => {
    window.dispatchEvent(new Event(enLigne ? "online" : "offline"))
  })
}

afterEach(() => reseau(true))

describe("BandeauHorsLigne", () => {
  it("reste invisible tant que le réseau est là", () => {
    const { container } = render(<BandeauHorsLigne />)
    expect(container).toBeEmptyDOMElement()
  })

  it("apparaît quand le réseau tombe et disparaît à son retour", () => {
    render(<BandeauHorsLigne />)

    reseau(false)
    expect(screen.getByRole("status")).toHaveTextContent("Tu es hors connexion")

    reseau(true)
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
  })
})
