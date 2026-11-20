import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const refaireErreurs = vi.hoisted(() => vi.fn())
vi.mock("@/api/endpoints", () => ({ refaireErreurs }))

import { BilanErreurs } from "./BilanErreurs"

function afficher(bilan: { corrigees: number; restantes: number | null } | undefined, acces = true) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/resultat"]}>
        <Routes>
          <Route path="/resultat" element={<BilanErreurs bilan={bilan} cursus={14} acces={acces} />} />
          <Route path="/quiz/session/:id" element={<p>Quiz lancé</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe("BilanErreurs", () => {
  beforeEach(() => refaireErreurs.mockReset())

  it("dit ce que le quiz a corrigé et ce qu'il reste, puis enchaîne sur les suivantes", async () => {
    refaireErreurs.mockResolvedValue({ id: 77 })
    afficher({ corrigees: 3, restantes: 7 })

    expect(screen.getByText("3 erreurs corrigées")).toBeTruthy()
    expect(screen.getByText("Il t'en reste 7 à corriger.")).toBeTruthy()
    fireEvent.click(screen.getByRole("button", { name: "Corriger les suivantes" }))

    await waitFor(() => expect(refaireErreurs).toHaveBeenCalledWith({ cursus: 14 }))
    expect(await screen.findByText("Quiz lancé")).toBeTruthy()
  })

  it("fête la liste vide, sans bouton", () => {
    afficher({ corrigees: 1, restantes: 0 })

    expect(screen.getByText("1 erreur corrigée")).toBeTruthy()
    expect(screen.getByText(/Ta liste d'erreurs est vide/)).toBeTruthy()
    expect(screen.queryByRole("button")).toBeNull()
  })

  it("renvoie à la liste, sans bouton refusé, qui n'a pas l'accès à cet examen", () => {
    afficher({ corrigees: 2, restantes: 4 }, false)

    expect(screen.queryByRole("button")).toBeNull()
    expect(screen.getByRole("link", { name: "Voir mes erreurs" }).getAttribute("href")).toBe("/erreurs")
  })

  it("n'affiche rien quand le quiz n'a rien corrigé", () => {
    const { container } = afficher({ corrigees: 0, restantes: null })
    expect(container.querySelector("section")).toBeNull()
    expect(afficher(undefined).container.querySelector("section")).toBeNull()
  })
})
