import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeAll, describe, expect, it, vi } from "vitest"

import type { Epreuve, MesTentatives } from "@/api/types"

import { EpreuveCard } from "./EpreuveCard"
import { EpreuveListRow } from "./EpreuveListRow"

// useIsTruncated (titre tronqué) observe la taille de l'élément : jsdom n'a pas ResizeObserver.
beforeAll(() => {
  vi.stubGlobal("ResizeObserver", class { observe() {} unobserve() {} disconnect() {} })
})

const pays = { id: 1, code: "CM", label: "Cameroun", dial_code: "+237", currency: "XAF", has_lessons: true }

function inedite(surcharge: Partial<Epreuve> = {}): Epreuve {
  return {
    id: 10, kind: "inedite", slug: "maths-bac-d", title: "Mathématiques BAC D – Épreuve inédite n°1",
    subject: { id: 1, code: "MATHS", label: "Mathématiques", country: pays }, cursus: [],
    lesson_type: null, lesson_type_display: "Épreuve inédite", year: null, duree_epreuve: "", duree_minutes: 240, coefficient: "",
    origine: "INEDITE", origine_display: "Épreuve inédite", etablissement: "", institution: "Edukora", nature_epreuve: "",
    nature_epreuve_display: "", themes: [], has_access: true, is_read: false, est_vitrine: false, created_at: "2026-09-01T00:00:00Z",
    exercises_count: 5, related_cours: [], sujet_pdf_url: null, sujet_pdf_disponible: true,
    apercu_enonce_markdown: null, apercu_numero_exercice: null, mes_tentatives: null,
    ...surcharge,
  } as Epreuve
}

const mes = (surcharge: Partial<MesTentatives>): MesTentatives => ({
  en_cours: false, nb_terminees: 0, meilleure_note: null, bareme: null, ...surcharge,
})

function carte(epreuve: Epreuve) {
  return render(<MemoryRouter><EpreuveCard epreuve={epreuve} /></MemoryRouter>)
}

describe("EpreuveCard, épreuve inédite", () => {
  it("invite à composer une épreuve jamais ouverte", () => {
    carte(inedite())
    expect(screen.getByText("Composer l'épreuve")).toBeInTheDocument()
    expect(screen.queryByText(/Faite/)).not.toBeInTheDocument()
  })

  it("dit la note de la meilleure copie et propose de la refaire", () => {
    carte(inedite({ is_read: true, mes_tentatives: mes({ nb_terminees: 2, meilleure_note: 12.5, bareme: 20 }) }))
    expect(screen.getByText("Faite · 12,5 / 20")).toBeInTheDocument()
    expect(screen.getByText("Refaire l'épreuve")).toBeInTheDocument()
    // « Lu » est le mot des corrigés : une copie a une note, pas une lecture.
    expect(screen.queryByText("Lu")).not.toBeInTheDocument()
  })

  it("propose de reprendre une copie en cours, avant de la refaire", () => {
    carte(inedite({ mes_tentatives: mes({ en_cours: true, nb_terminees: 1, meilleure_note: 8, bareme: 20 }) }))
    expect(screen.getByText("Reprendre l'épreuve")).toBeInTheDocument()
  })

  it("invite un visiteur à essayer gratuitement une épreuve offerte", () => {
    carte(inedite({ has_access: false, est_vitrine: true }))
    expect(screen.getByText("Essayer gratuitement")).toBeInTheDocument()
    expect(screen.getByText("Gratuit")).toBeInTheDocument()
  })

  it("garde « Voir l'aperçu » pour qui n'a pas accès", () => {
    carte(inedite({ has_access: false }))
    expect(screen.getByText("Voir l'aperçu")).toBeInTheDocument()
  })
})

describe("EpreuveListRow, épreuve inédite", () => {
  it("montre la note, ou « En cours » pour une copie ouverte", () => {
    const { unmount } = render(
      <MemoryRouter>
        <EpreuveListRow epreuve={inedite({ is_read: true, mes_tentatives: mes({ nb_terminees: 1, meilleure_note: 14, bareme: 20 }) })} />
      </MemoryRouter>,
    )
    expect(screen.getByText("Faite · 14 / 20")).toBeInTheDocument()
    unmount()

    render(<MemoryRouter><EpreuveListRow epreuve={inedite({ mes_tentatives: mes({ en_cours: true }) })} /></MemoryRouter>)
    expect(screen.getByText("En cours")).toBeInTheDocument()
  })
})
