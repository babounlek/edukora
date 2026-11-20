import { createRef } from "react"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { lireReprise, oublierReprise, retenirReprise } from "@/lib/repriseLecture"
import { RepriseLecture } from "./RepriseLecture"

describe("position retenue dans un cours", () => {
  beforeEach(() => localStorage.clear())

  it("retient la section et la part parcourue, par cours", () => {
    retenirReprise("thales", "exemple_resolu", 0.4)
    retenirReprise("pythagore", "regle", 0.2)

    expect(lireReprise("thales")).toMatchObject({ section: "exemple_resolu", part: 0.4 })
    expect(lireReprise("pythagore")).toMatchObject({ section: "regle", part: 0.2 })
    expect(lireReprise("inconnu")).toBeNull()
  })

  it("ne propose rien pour un cours à peine ouvert, et oublie un cours lu jusqu'au bout", () => {
    retenirReprise("thales", "prerequis", 0.03)
    expect(lireReprise("thales")).toBeNull()

    retenirReprise("thales", "regle", 0.5)
    retenirReprise("thales", "synthese", 0.97)
    expect(lireReprise("thales")).toBeNull()
  })

  it("oublie les cours les plus anciens au-delà de trente", () => {
    for (let i = 0; i < 31; i++) retenirReprise(`cours-${i}`, "regle", 0.5, 1000 + i)

    expect(lireReprise("cours-0")).toBeNull()
    expect(lireReprise("cours-30")).not.toBeNull()
  })

  it("s'oublie à la demande", () => {
    retenirReprise("thales", "regle", 0.5)
    oublierReprise("thales")
    expect(lireReprise("thales")).toBeNull()
  })
})

describe("RepriseLecture", () => {
  const defiler = vi.fn()

  beforeEach(() => {
    localStorage.clear()
    defiler.mockReset()
    Element.prototype.scrollIntoView = defiler
  })

  function afficher(actif = true) {
    const ref = createRef<HTMLElement>()
    return render(
      <div>
        <RepriseLecture cibleRef={ref} cle="thales" pret actif={actif} />
        <article ref={ref}>
          <section id="regle"><h2>La règle</h2></section>
          <section id="exemple_resolu"><h2>Exemple résolu</h2></section>
        </article>
      </div>,
    )
  }

  it("propose de reprendre à la section où l'élève en était, et y mène", async () => {
    retenirReprise("thales", "exemple_resolu", 0.42)
    afficher()

    expect(screen.getByText("Tu en étais à « Exemple résolu », 42 % du cours.")).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Reprendre" }))

    // Le bandeau se retire d'abord, le défilement part ensuite (voir RepriseLecture.reprendre).
    await waitFor(() => expect(defiler).toHaveBeenCalledTimes(1))
    expect(screen.queryByRole("button", { name: "Reprendre" })).toBeNull()
  })

  it("« Relire depuis le début » écarte la proposition et oublie la position", () => {
    retenirReprise("thales", "exemple_resolu", 0.42)
    afficher()

    fireEvent.click(screen.getByRole("button", { name: "Relire depuis le début" }))

    expect(screen.queryByRole("button", { name: "Reprendre" })).toBeNull()
    expect(lireReprise("thales")).toBeNull()
    expect(defiler).not.toHaveBeenCalled()
  })

  it("ne propose rien pour un cours jamais ouvert, une section disparue, ou une page ouverte sur une ancre", () => {
    afficher()
    expect(screen.queryByRole("button", { name: "Reprendre" })).toBeNull()

    retenirReprise("thales", "section_supprimee", 0.5)
    afficher()
    expect(screen.queryByRole("button", { name: "Reprendre" })).toBeNull()

    retenirReprise("thales", "regle", 0.5)
    afficher(false)
    expect(screen.queryByRole("button", { name: "Reprendre" })).toBeNull()
  })
})
