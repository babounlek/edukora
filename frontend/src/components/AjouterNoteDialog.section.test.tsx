import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

const { saveMarqueEtude, modifierNoteLibre } = vi.hoisted(() => ({
  saveMarqueEtude: vi.fn().mockResolvedValue({}),
  modifierNoteLibre: vi.fn(),
}))
vi.mock("@/api/endpoints", () => ({
  saveMarqueEtude, modifierNoteLibre,
  creerNoteLibre: vi.fn(), envoyerImageNote: vi.fn(), listSubjects: vi.fn(), retirerImageNote: vi.fn(), supprimerNoteLibre: vi.fn(),
}))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/abonneActif", () => ({ useCursusAbonne: () => null }))

import { AjouterNoteDialog } from "./AjouterNoteDialog"

function ouvrir(signet: boolean) {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <AjouterNoteDialog
        open
        onOpenChange={() => {}}
        edition={{
          id: 1, note: "à revoir",
          marque: { cible: { type: "cours", slug: "les-suites" }, cle: "regle", signet, contexte: "Les suites · La règle" },
        }}
      />
    </QueryClientProvider>,
  )
}

describe("modifier la note d'une section depuis Mes notes", () => {
  it("l'enregistre sur la section, sans mise en forme ni photo à proposer", async () => {
    ouvrir(false)
    expect(screen.getByText("Les suites · La règle")).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Gras" })).not.toBeInTheDocument()

    const zone = screen.getByRole("textbox")
    await userEvent.clear(zone)
    await userEvent.type(zone, "raison de la suite")
    await userEvent.click(screen.getByRole("button", { name: "Enregistrer" }))

    await waitFor(() =>
      expect(saveMarqueEtude).toHaveBeenCalledWith({ type: "cours", slug: "les-suites" }, "regle", { note: "raison de la suite" }),
    )
    expect(modifierNoteLibre).not.toHaveBeenCalled()
  })

  it("ne laisse pas vider une note qui n'a pas de signet : elle disparaîtrait sans le dire", async () => {
    ouvrir(false)
    await userEvent.clear(screen.getByRole("textbox"))

    expect(screen.getByRole("button", { name: "Enregistrer" })).toBeDisabled()
  })
})
