import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it, vi } from "vitest"

import type { CarnetEntree } from "@/api/types"
import { CarteNote } from "./CarteNote"

// Le partage lit le compte connecté : sans rapport avec ce qui est vérifié ici.
vi.mock("@/components/BoutonPartager", () => ({ BoutonPartager: () => null }))

const marque = {
  genre: "marque", id: 1, type: "cours", cle: "regle", titre: "Les suites", slug: "les-suites", country: "CM",
  matiere: "Mathématiques", matiere_id: 3, citation: "", note: "à revoir", signet: false, compris: false,
  revision_due: null, epingle: false, updated_at: "2026-11-20T10:00:00Z",
} as CarnetEntree

describe("CarteNote", () => {
  it("laisse modifier la note posée sur une section, pas seulement une note libre", async () => {
    const onModifier = vi.fn()
    render(
      <MemoryRouter>
        <ul>
          <CarteNote entree={marque} dansDossier onEpingler={() => {}} onModifier={onModifier} onRetirer={() => {}} />
        </ul>
      </MemoryRouter>,
    )

    await userEvent.click(screen.getByRole("button", { name: "Autres actions" }))
    await userEvent.click(await screen.findByRole("menuitem", { name: "Modifier cette note" }))

    expect(onModifier).toHaveBeenCalled()
  })
})
