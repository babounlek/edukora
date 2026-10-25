import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it } from "vitest"

import type { CoursSectionData } from "@/api/types"

import { CoursSection } from "./CoursSection"

function accroche(texte: string): CoursSectionData {
  return { type: "accroche", body_markdown: texte }
}

function afficher(section: CoursSectionData) {
  return render(
    <MemoryRouter>
      <CoursSection section={section} />
    </MemoryRouter>,
  )
}

describe("CoursSection : accroche", () => {
  it("laisse une accroche courte telle quelle, sans bouton", () => {
    afficher(accroche("Un système, deux inconnues."))

    expect(screen.getByText("Un système, deux inconnues.")).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Lire la suite" })).not.toBeInTheDocument()
  })

  it("replie une accroche longue, qu'on déplie puis qu'on replie", async () => {
    afficher(accroche("Lorem ipsum dolor sit amet. ".repeat(20)))

    const bouton = screen.getByRole("button", { name: "Lire la suite" })
    expect(bouton).toHaveAttribute("aria-expanded", "false")

    await userEvent.click(bouton)
    expect(screen.getByRole("button", { name: "Réduire" })).toHaveAttribute("aria-expanded", "true")

    await userEvent.click(screen.getByRole("button", { name: "Réduire" }))
    expect(screen.getByRole("button", { name: "Lire la suite" })).toBeInTheDocument()
  })
})
