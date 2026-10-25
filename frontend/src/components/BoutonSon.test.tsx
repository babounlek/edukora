import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

const jouerRetour = vi.hoisted(() => vi.fn())
vi.mock("@/lib/retours", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/retours")>()),
  jouerRetour,
}))

import { retoursActifs } from "@/lib/retours"
import { BoutonSon } from "./BoutonSon"

beforeEach(() => {
  localStorage.clear()
  jouerRetour.mockReset()
})

describe("BoutonSon", () => {
  it("propose de couper le son quand il est actif (le cas par défaut)", () => {
    render(<BoutonSon />)
    expect(screen.getByRole("button", { name: "Couper le son" })).toHaveAttribute("aria-pressed", "true")
  })

  it("coupe puis réactive, avec un aperçu à la réactivation, et garde le réglage du compte", async () => {
    render(<BoutonSon />)

    await userEvent.click(screen.getByRole("button", { name: "Couper le son" }))
    expect(retoursActifs()).toBe(false)
    expect(jouerRetour).not.toHaveBeenCalled()

    await userEvent.click(screen.getByRole("button", { name: "Activer le son" }))
    expect(retoursActifs()).toBe(true)
    expect(jouerRetour).toHaveBeenCalledWith("juste")
  })

  it("reflète un son déjà coupé dans « Sons et vibrations » du compte", () => {
    localStorage.setItem("edukora.retours", "0")
    render(<BoutonSon />)
    expect(screen.getByRole("button", { name: "Activer le son" })).toHaveAttribute("aria-pressed", "false")
  })
})
