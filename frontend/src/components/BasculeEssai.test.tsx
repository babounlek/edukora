import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it } from "vitest"

import { BasculeEssai, lireEssaiEpreuve, useEssaiEpreuve } from "./BasculeEssai"

function Lecteur() {
  const [essai, setEssai] = useEssaiEpreuve()
  return (
    <>
      <BasculeEssai essai={essai} onChange={setEssai} />
      <p>{essai ? "corrigés repliés" : "corrigés ouverts"}</p>
    </>
  )
}

beforeEach(() => {
  localStorage.clear()
})

describe("« Essaie d'abord » dans le lecteur d'épreuve", () => {
  it("est éteint par défaut : le corrigé reste ouvert tant que l'élève n'a rien demandé", () => {
    render(<Lecteur />)

    expect(screen.getByText("corrigés ouverts")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Tout afficher" })).toHaveAttribute("aria-pressed", "true")
    expect(screen.getByRole("button", { name: "Essaie d'abord" })).toHaveAttribute("aria-pressed", "false")
  })

  it("se choisit d'un geste et se retient d'une visite à l'autre", async () => {
    const premiere = render(<Lecteur />)
    await userEvent.click(screen.getByRole("button", { name: "Essaie d'abord" }))

    expect(screen.getByText("corrigés repliés")).toBeInTheDocument()
    expect(lireEssaiEpreuve()).toBe(true)
    premiere.unmount()

    render(<Lecteur />)
    expect(screen.getByText("corrigés repliés")).toBeInTheDocument()
  })

  it("revenir à « Tout afficher » se retient aussi", async () => {
    localStorage.setItem("edukora_epreuve_essai_dabord", "1")
    render(<Lecteur />)

    await userEvent.click(screen.getByRole("button", { name: "Tout afficher" }))

    expect(screen.getByText("corrigés ouverts")).toBeInTheDocument()
    expect(lireEssaiEpreuve()).toBe(false)
  })

  it("ne touche pas à la préférence du lecteur par thème, qui a sa propre clé", async () => {
    localStorage.setItem("edukora_exercice_essai_dabord", "0")
    render(<Lecteur />)

    await userEvent.click(screen.getByRole("button", { name: "Essaie d'abord" }))

    expect(localStorage.getItem("edukora_exercice_essai_dabord")).toBe("0")
  })
})
