import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { describe, expect, it } from "vitest"

import type { Cours } from "@/api/types"

import { CoursCard } from "./CoursCard"
import { CoursListRow } from "./CoursListRow"

const pays = { id: 1, code: "CM", label: "Cameroun", dial_code: "+237", currency: "XAF", has_lessons: true }

function cours(surcharge: Partial<Cours> = {}): Cours {
  return {
    id: 1, slug: "derivation", titre: "Dériver une fonction composée",
    subject: { id: 1, code: "MATHS", label: "Mathématiques", country: pays }, cursus: [],
    sous_theme: "", duree_estimee_min: null, tags: [], has_access: true, is_read: false, est_vitrine: false,
    apercu_contenu: { has_exemple_resolu: false, exercices_count: 0 }, created_at: "2026-09-01T00:00:00Z",
    ...surcharge,
  }
}

const tombeSouvent = { frequence_pct: 80, nb_epreuves: 8, nb_sessions: 10, theme: "dérivation" }

describe("CoursCard, repère « tombe souvent »", () => {
  it("annonce le fait chiffré, pas un ordre", () => {
    render(<MemoryRouter><CoursCard cours={cours({ tombe_souvent: tombeSouvent })} /></MemoryRouter>)

    expect(screen.getByText("Tombé dans 8 épreuves sur 10")).toBeInTheDocument()
  })

  it("n'affiche rien pour un cours sans fréquence : l'absence ne dit pas « sans importance »", () => {
    render(<MemoryRouter><CoursCard cours={cours({ tombe_souvent: null })} /></MemoryRouter>)
    render(<MemoryRouter><CoursCard cours={cours()} /></MemoryRouter>)

    expect(screen.queryByText(/Tombé dans/)).not.toBeInTheDocument()
  })
})

describe("CoursListRow, repère « tombe souvent »", () => {
  it("porte le chiffre en libellé accessible de l'étoile", () => {
    render(<MemoryRouter><CoursListRow cours={cours({ tombe_souvent: tombeSouvent })} /></MemoryRouter>)

    expect(screen.getByRole("img", { name: "Tombé dans 8 épreuves sur 10" })).toBeInTheDocument()
  })

  it("n'a pas d'étoile sans fréquence", () => {
    render(<MemoryRouter><CoursListRow cours={cours()} /></MemoryRouter>)

    expect(screen.queryByRole("img")).not.toBeInTheDocument()
  })
})
