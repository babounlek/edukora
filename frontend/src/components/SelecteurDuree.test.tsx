import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"

import type { Plan } from "@/api/types"
import { SelecteurDuree } from "./SelecteurDuree"

const plan = (surcharges: Partial<Plan> = {}) =>
  ({
    id: 1, duration_mode: "MENSUEL", price: 2000, effective_price: 2000, prix_reference: 2000, mois_max: 7, campagne: null,
    ...surcharges,
  }) as Plan

describe("SelecteurDuree", () => {
  it("propose de 1 au nombre maximal de mois, et marque celui qui est choisi", () => {
    render(<SelecteurDuree plan={plan()} mois={3} onChoisir={vi.fn()} />)
    const choix = screen.getAllByRole("radio")
    expect(choix).toHaveLength(7)
    expect(choix[2]).toHaveAttribute("aria-checked", "true")
    expect(choix[0]).toHaveAttribute("aria-checked", "false")
  })

  it("écrit le total en toutes lettres : mois × prix du mois", () => {
    render(<SelecteurDuree plan={plan()} mois={5} onChoisir={vi.fn()} />)
    expect(screen.getByText(/10\s000 FCFA/)).toBeInTheDocument()
    expect(screen.getByText(/5 mois × 2\s000 FCFA par mois/)).toBeInTheDocument()
    expect(screen.getByText(/Accès jusqu'au/)).toBeInTheDocument()
    expect(screen.getByText(/rien à renouveler/i)).toBeInTheDocument()
  })

  it("remonte le choix de l'élève", async () => {
    const onChoisir = vi.fn()
    render(<SelecteurDuree plan={plan()} mois={3} onChoisir={onChoisir} />)
    await userEvent.setup().click(screen.getAllByRole("radio")[4])
    expect(onChoisir).toHaveBeenCalledWith(5)
  })

  it("le raccourci « jusqu'à l'examen » choisit tous les mois qui restent", async () => {
    const onChoisir = vi.fn()
    render(<SelecteurDuree plan={plan({ mois_max: 7 })} mois={3} onChoisir={onChoisir} />)
    await userEvent.setup().click(screen.getByRole("button", { name: /Jusqu'à l'examen \(7 mois\)/ }))
    expect(onChoisir).toHaveBeenCalledWith(7)
  })

  it("dit que le dernier mois couvre l'examen quand on prend tout", () => {
    render(<SelecteurDuree plan={plan({ mois_max: 4 })} mois={4} onChoisir={vi.fn()} />)
    expect(screen.getByText(/tout le temps qui reste/i)).toBeInTheDocument()
  })

  it("il n'y a pas de choix à faire quand il ne reste qu'un mois", () => {
    render(<SelecteurDuree plan={plan({ mois_max: 1 })} mois={1} onChoisir={vi.fn()} />)
    expect(screen.queryAllByRole("radio")).toHaveLength(0)
    expect(screen.getByText(/Il te reste un mois/)).toBeInTheDocument()
  })

  it("montre le prix barré et la date limite pendant une campagne", () => {
    const enCampagne = plan({
      effective_price: 1800,
      prix_reference: 2000,
      campagne: { id: 1, nom: "Offre fondateurs", nom_en: "", pourcentage: 10, debut: "2026-11-01T00:00:00Z", fin: "2026-11-30T22:59:59Z" },
    })
    render(<SelecteurDuree plan={enCampagne} mois={3} onChoisir={vi.fn()} />)
    expect(screen.getByText(/5\s400 FCFA/)).toBeInTheDocument()
    expect(screen.getByText(/au lieu de 6\s000 FCFA/)).toBeInTheDocument()
    expect(screen.getByText(/Offre fondateurs \(−10 %\)/)).toBeInTheDocument()
  })

  it("n'annonce aucun rabais famille : hors campagne, le prix du mois est celui du plan", () => {
    render(<SelecteurDuree plan={plan()} mois={2} onChoisir={vi.fn()} />)
    expect(screen.queryByText(/Enfant supplémentaire/)).not.toBeInTheDocument()
    expect(screen.queryByText(/au lieu de/)).not.toBeInTheDocument()
    expect(screen.getByText(/4\s000 FCFA/)).toBeInTheDocument()
  })
})
