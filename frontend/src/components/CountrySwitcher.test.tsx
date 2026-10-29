import { render } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { pays } = vi.hoisted(() => ({ pays: { liste: [] as unknown[] } }))
vi.mock("@/context/CountryContext", () => ({
  useCountry: () => ({ country: "cm", countries: pays.liste, setCountry: vi.fn() }),
}))

import { CountrySwitcher } from "./Header"

const cm = { id: 1, code: "CM", label: "Cameroun", has_lessons: true }
const sn = { id: 2, code: "SN", label: "Sénégal", has_lessons: true }
const ci = { id: 3, code: "CI", label: "Côte d'Ivoire", has_lessons: false }

function afficher() {
  return render(
    <MemoryRouter>
      <CountrySwitcher />
    </MemoryRouter>,
  )
}

describe("CountrySwitcher - masqué tant qu'un seul pays est ouvert", () => {
  beforeEach(() => {
    pays.liste = []
  })

  it("rien sans liste de pays", () => {
    expect(afficher().container.textContent).toBe("")
  })

  it("rien avec un seul pays qui a du contenu, même si d'autres existent en base sans contenu", () => {
    pays.liste = [cm, ci]
    expect(afficher().container.textContent).toBe("")
  })

  it("réapparaît dès qu'un second pays a du contenu", () => {
    pays.liste = [cm, sn]
    expect(afficher().container.querySelector("[role=combobox]")).not.toBeNull()
  })
})
