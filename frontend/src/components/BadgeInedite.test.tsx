import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { BadgeInedite } from "./BadgeInedite"

describe("BadgeInedite", () => {
  it("inédite : fond doré plein", () => {
    render(<BadgeInedite />)
    const badge = screen.getByText("Épreuve inédite")
    expect(badge.className).toContain("bg-gold")
    expect(badge.className).not.toContain("bg-gold/10")
  })

  it("mini-inédite : contour doré, jamais le vert de « Gratuite », avec son explication", () => {
    render(<BadgeInedite mini />)
    const badge = screen.getByText("Mini-inédite")
    expect(badge.className).toContain("border-gold")
    expect(badge.className).not.toContain("bg-success")
    expect(badge.getAttribute("title")).toMatch(/abonnés/)
  })

  it("les deux badges se distinguent par leur apparence, pas seulement par leur texte", () => {
    const { container: a } = render(<BadgeInedite />)
    const { container: b } = render(<BadgeInedite mini />)
    expect(a.querySelector("[data-slot=badge]")!.className).not.toBe(b.querySelector("[data-slot=badge]")!.className)
  })
})
