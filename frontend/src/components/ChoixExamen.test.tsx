import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { beforeEach, describe, expect, it, vi } from "vitest"

const { auth, listCursus, mutate, toast } = vi.hoisted(() => ({
  auth: { isAuthenticated: false, user: null as unknown },
  listCursus: vi.fn(),
  mutate: vi.fn(),
  toast: { success: vi.fn(), error: vi.fn() },
}))
vi.mock("@/api/endpoints", () => ({ listCursus }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/changerCursusPrepare", () => ({ useChangerCursusPrepare: () => ({ mutate, isPending: false }) }))
vi.mock("sonner", () => ({ toast }))

import type { Cursus } from "@/api/types"
import {
  lireCursusPrepareEnAttente,
  memoriserCursusPrepareEnAttente,
  oublierCursusPrepareEnAttente,
} from "@/lib/cursusPrepare"
import { LigneExamenChoisi, PastilleExamen, SelecteurExamen } from "./ChoixExamen"

const BEPC = { id: 1, examen: "BEPC", examen_display: "BEPC", series: null, langue: "fr", country: { code: "CM" } }
const BAC_C = { id: 2, examen: "BAC", examen_display: "BAC", series: { code: "C", label: "C" }, langue: "fr", country: { code: "CM" } }
const GCE = { id: 3, examen: "GCE_OL", examen_display: "GCE O Level", series: null, langue: "en", country: { code: "CM" } }

function afficher(ui: React.ReactNode) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>{ui}</QueryClientProvider>,
  )
}

describe("examen choisi : rappel à l'écran", () => {
  beforeEach(() => {
    localStorage.clear()
    mutate.mockClear()
    toast.success.mockClear()
    listCursus.mockResolvedValue([BEPC, BAC_C, GCE])
    auth.isAuthenticated = false
    auth.user = null
    listCursus.mockClear()
    // Le magasin du visiteur est un module (valeur en mémoire) : vider le localStorage ne suffit pas à repartir sans déclaration.
    oublierCursusPrepareEnAttente()
  })

  describe("PastilleExamen", () => {
    it("un visiteur qui a choisi son examen le voit dans l'en-tête", async () => {
      memoriserCursusPrepareEnAttente(2)
      afficher(<PastilleExamen />)
      expect(await screen.findByRole("button", { name: /BAC C/ })).toBeTruthy()
    })

    it("sans examen déclaré : rien (c'est le bandeau qui le demande)", async () => {
      afficher(<PastilleExamen />)
      await waitFor(() => expect(listCursus).not.toHaveBeenCalled())
      expect(screen.queryByRole("button")).toBeNull()
    })

    it("un compte sans abonnement la voit aussi, d'après son examen déclaré", async () => {
      auth.isAuthenticated = true
      auth.user = { id: 1, cursus_prepare: BEPC, a_un_abonnement_actif: false }
      afficher(<PastilleExamen />)
      expect(await screen.findByRole("button", { name: /BEPC/ })).toBeTruthy()
    })

    it("un abonné ne la voit pas : sa pastille est sur l'accueil et son abonnement dans le menu du compte", () => {
      auth.isAuthenticated = true
      auth.user = { id: 1, cursus_prepare: BEPC, a_un_abonnement_actif: true }
      afficher(<PastilleExamen />)
      expect(screen.queryByRole("button")).toBeNull()
    })
  })

  describe("SelecteurExamen", () => {
    it("un visiteur change d'examen : le choix est gardé dans le navigateur et confirmé", async () => {
      memoriserCursusPrepareEnAttente(1)
      afficher(
        <SelecteurExamen>
          <button type="button">ouvrir</button>
        </SelecteurExamen>,
      )
      await userEvent.click(screen.getByRole("button", { name: "ouvrir" }))
      // Les examens de la langue de l'interface seulement : le GCE n'y est pas.
      expect(await screen.findByRole("menuitem", { name: "BAC C" })).toBeTruthy()
      expect(screen.queryByRole("menuitem", { name: /GCE/ })).toBeNull()

      await userEvent.click(screen.getByRole("menuitem", { name: "BAC C" }))

      expect(lireCursusPrepareEnAttente()).toBe(2)
      expect(toast.success).toHaveBeenCalledTimes(1)
      expect(mutate).not.toHaveBeenCalled()
    })

    it("un compte connecté l'écrit sur son compte, sans rien garder dans le navigateur", async () => {
      auth.isAuthenticated = true
      auth.user = { id: 1, cursus_prepare: BEPC, a_un_abonnement_actif: false }
      afficher(
        <SelecteurExamen>
          <button type="button">ouvrir</button>
        </SelecteurExamen>,
      )
      await userEvent.click(screen.getByRole("button", { name: "ouvrir" }))
      await userEvent.click(await screen.findByRole("menuitem", { name: "BAC C" }))

      expect(mutate).toHaveBeenCalledWith(2)
      expect(lireCursusPrepareEnAttente()).toBeNull()
    })

    it("re-choisir l'examen déjà actif ne fait rien", async () => {
      memoriserCursusPrepareEnAttente(1)
      afficher(
        <SelecteurExamen>
          <button type="button">ouvrir</button>
        </SelecteurExamen>,
      )
      await userEvent.click(screen.getByRole("button", { name: "ouvrir" }))
      await userEvent.click(await screen.findByRole("menuitem", { name: "BEPC" }))

      expect(toast.success).not.toHaveBeenCalled()
      expect(lireCursusPrepareEnAttente()).toBe(1)
    })
  })

  describe("LigneExamenChoisi", () => {
    it("dit ce que la personne prépare et propose de le changer", () => {
      afficher(<LigneExamenChoisi cursus={BAC_C as unknown as Cursus} />)
      expect(screen.getByText("Tu prépares : BAC C")).toBeTruthy()
      expect(screen.getByRole("button", { name: /changer/ })).toBeTruthy()
      expect(screen.queryByText(/autre langue/)).toBeNull()
    })

    it("un examen de l'autre langue que l'interface : on dit pourquoi les listes ne sont pas réduites", () => {
      afficher(<LigneExamenChoisi cursus={GCE as unknown as Cursus} />)
      expect(screen.getByText(/autre langue que l'interface/)).toBeTruthy()
    })
  })
})
