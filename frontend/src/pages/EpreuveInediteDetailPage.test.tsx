import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { Epreuve, TentativeEnCours } from "@/api/types"

const getEpreuveInedite = vi.hoisted(() => vi.fn())
const startTentativeInedite = vi.hoisted(() => vi.fn())
const startExamMode = vi.hoisted(() => vi.fn())
const listPlans = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({ isAuthenticated: false }))
const cursusDeclare = vi.hoisted(() => ({ valeur: null as number | null }))

vi.mock("@/api/endpoints", () => ({
  getEpreuveInedite,
  startTentativeInedite,
  startExamMode,
  listPlans,
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/cursusAccueil", () => ({
  useCursusDeclare: () => cursusDeclare.valeur,
  useInedites: () => ({ data: { count: 4, results: [] } }),
}))
vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <p>{markdown}</p> }))
vi.mock("@/components/ParrainageHint", () => ({ ParrainageHint: () => null }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))

import { EpreuveInediteDetailPage } from "./EpreuveInediteDetailPage"

function cursus(id: number, serie: string) {
  return {
    id, examen: "BAC", examen_display: "BAC", series: { id, code: serie, label: `Série ${serie}` },
    country: { id: 1, code: "CM", label: "Cameroun", dial_code: "+237", currency: "XAF", has_lessons: true },
  }
}

function epreuve(surcharge: Partial<Epreuve> = {}): Epreuve {
  return {
    id: 10, kind: "inedite", slug: "maths-bac-d-ti", title: "Mathématiques BAC D et TI – Épreuve inédite n°1",
    subject: { id: 1, code: "MATHS", label: "Mathématiques", country: { id: 1, code: "CM", label: "Cameroun", dial_code: "+237", currency: "XAF", has_lessons: true } },
    cursus: [cursus(4, "D"), cursus(7, "TI")],
    lesson_type: null, lesson_type_display: "Épreuve inédite", year: null, duree_epreuve: "", duree_minutes: 240, coefficient: "",
    origine: "INEDITE", origine_display: "Épreuve inédite", etablissement: "", institution: "Edukora", nature_epreuve: "",
    nature_epreuve_display: "", themes: [], has_access: false, is_read: false, est_vitrine: false, created_at: "2026-09-01T00:00:00Z",
    exercises_count: 5, related_cours: [], sujet_pdf_url: null, sujet_pdf_disponible: true,
    apercu_enonce_markdown: "Calculer la limite.", apercu_numero_exercice: "1", tentative_en_cours: null, mes_tentatives: null,
    ...surcharge,
  } as Epreuve
}

function enCours(surcharge: Partial<TentativeEnCours> = {}): TentativeEnCours {
  return {
    id: 55, started_at: "2026-10-03T08:00:00Z", exam_mode_started_at: null, echeance: null, mode_papier: false,
    traitees: 0, total: 12, ...surcharge,
  }
}

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/cm/epreuves-inedites/maths-bac-d-ti"]}>
      <Routes>
        <Route path="/cm/epreuves-inedites/:id" element={<EpreuveInediteDetailPage />} />
        <Route path="/inedit/tentative/:id" element={<p>Page de tentative</p>} />
        <Route path="/connexion" element={<p>Page de connexion</p>} />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  getEpreuveInedite.mockReset()
  startTentativeInedite.mockReset()
  startExamMode.mockReset()
  sessionStorage.clear()
  listPlans.mockReset()
  listPlans.mockResolvedValue([])
  auth.isAuthenticated = false
  cursusDeclare.valeur = null
})

describe("fiche d'une épreuve inédite, pour un visiteur", () => {
  it("place le bouton d'accès avant l'aperçu, et l'envoie acheter avec le chemin de retour", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve())
    afficher()

    const bouton = await screen.findByRole("link", { name: "Débloquer l'accès" })
    const apercu = screen.getByText("Calculer la limite.")
    expect(bouton.compareDocumentPosition(apercu) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()

    const params = new URL(bouton.getAttribute("href") ?? "", "http://x").searchParams
    expect(params.get("duree")).toBe("examen")
    expect(params.get("retour")).toBe("/cm/epreuves-inedites/maths-bac-d-ti")
  })

  it("dit ce que l'abonnement ouvre, sa formule la moins chère et sa durée", async () => {
    listPlans.mockResolvedValue([
      { id: 1, name: "Mensuel", inclut_inedit: false, effective_price: 1000, duration_mode: "FIXE", effective_duration_days: 30 },
      { id: 2, name: "Jusqu'à l'Examen", inclut_inedit: true, effective_price: 15000, duration_mode: "JUSQUA_EXAMEN", effective_duration_days: 240 },
      { id: 3, name: "Cher", inclut_inedit: true, effective_price: 20000, duration_mode: "JUSQUA_EXAMEN", effective_duration_days: 240 },
    ])
    getEpreuveInedite.mockResolvedValue(epreuve())
    afficher()

    expect(await screen.findByText("Incluse dans l'abonnement BAC - Série D")).toBeInTheDocument()
    expect(screen.getByText(/Les 4 épreuves inédites/)).toBeInTheDocument()
    expect(screen.getByText(/Tous les corrigés d'annales/)).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText(/15.000.FCFA/)).toBeInTheDocument())
    expect(screen.getByText(/paiement unique, valable jusqu'à ton examen/)).toBeInTheDocument()
    expect(screen.queryByText(/par enfant/)).not.toBeInTheDocument()
  })

  it("achète le cursus déclaré quand l'épreuve en couvre plusieurs, le premier sinon", async () => {
    cursusDeclare.valeur = 7
    getEpreuveInedite.mockResolvedValue(epreuve())
    const { unmount } = afficher()
    const declare = await screen.findByRole("link", { name: "Débloquer l'accès" })
    expect(new URL(declare.getAttribute("href") ?? "", "http://x").searchParams.get("cursus")).toBe("7")
    expect(screen.getByText("Incluse dans l'abonnement BAC - Série TI")).toBeInTheDocument()
    unmount()

    cursusDeclare.valeur = 99
    afficher()
    const parDefaut = await screen.findByRole("link", { name: "Débloquer l'accès" })
    expect(new URL(parDefaut.getAttribute("href") ?? "", "http://x").searchParams.get("cursus")).toBe("4")
  })

  it("propose à un abonné déconnecté de se connecter plutôt que d'acheter", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve())
    afficher()

    await userEvent.click(await screen.findByRole("link", { name: "Te connecter" }))

    expect(await screen.findByText("Page de connexion")).toBeInTheDocument()
  })

  it("ne propose pas de se connecter à quelqu'un qui l'est déjà", async () => {
    auth.isAuthenticated = true
    getEpreuveInedite.mockResolvedValue(epreuve())
    afficher()

    await screen.findByRole("link", { name: "Débloquer l'accès" })
    expect(screen.queryByRole("link", { name: "Te connecter" })).not.toBeInTheDocument()
  })
})

describe("fiche d'une épreuve inédite offerte (vitrine)", () => {
  it("invite un visiteur à l'essayer gratuitement, et le ramène sur la fiche après sa connexion", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ est_vitrine: true }))
    afficher()

    expect(await screen.findByText(/Cette épreuve est offerte/)).toBeInTheDocument()
    expect(screen.getByText("Gratuite")).toBeInTheDocument()
    expect(screen.queryByRole("link", { name: "Débloquer l'accès" })).not.toBeInTheDocument()
    expect(screen.queryByText(/Incluse dans l'abonnement/)).not.toBeInTheDocument()

    await userEvent.click(screen.getByRole("link", { name: "Essayer gratuitement" }))
    expect(await screen.findByText("Page de connexion")).toBeInTheDocument()
  })

  it("garde l'abonnement accessible à côté, sans le mettre en avant", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ est_vitrine: true }))
    afficher()

    const lien = await screen.findByRole("link", { name: /Voir l'abonnement : les 4 épreuves inédites/ })
    expect(new URL(lien.getAttribute("href") ?? "", "http://x").searchParams.get("retour")).toBe("/cm/epreuves-inedites/maths-bac-d-ti")
  })

  it("donne à un compte connecté, abonné ou non, le choix du mode comme sur une épreuve payante", async () => {
    auth.isAuthenticated = true
    getEpreuveInedite.mockResolvedValue(epreuve({ est_vitrine: true, has_access: true }))
    afficher()

    expect(await screen.findByText("Comment veux-tu la passer ?")).toBeInTheDocument()
    expect(screen.getByText("Gratuite")).toBeInTheDocument()
  })
})

describe("fiche d'une épreuve inédite, pour un abonné", () => {
  beforeEach(() => {
    auth.isAuthenticated = true
  })

  it("propose le choix du mode sur la fiche, sans bouton « Commencer » intermédiaire", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true }))
    afficher()

    expect(await screen.findByText("Comment veux-tu la passer ?")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Conditions réelles/ })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Sur papier/ })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Entraînement libre/ })).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Commencer cette épreuve" })).not.toBeInTheDocument()
  })

  it("n'offre plus d'ouvrir le sujet en PDF avant d'avoir commencé", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true, sujet_pdf_disponible: true }))
    afficher()

    await screen.findByText("Comment veux-tu la passer ?")
    expect(screen.queryByRole("button", { name: /PDF/ })).not.toBeInTheDocument()
  })

  it("l'entraînement libre ouvre la copie sans repasser par le briefing", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true }))
    startTentativeInedite.mockResolvedValue({ id: 70 })
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: /Entraînement libre/ }))

    expect(await screen.findByText("Page de tentative")).toBeInTheDocument()
    expect(startTentativeInedite).toHaveBeenCalledWith(10)
    expect(startExamMode).not.toHaveBeenCalled()
    expect(sessionStorage.getItem("inedit-libre-70")).toBe("1")
  })

  it("les conditions réelles ne lancent le chrono qu'après confirmation", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true }))
    startTentativeInedite.mockResolvedValue({ id: 71 })
    startExamMode.mockResolvedValue({ id: 71 })
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: /Conditions réelles/ }))
    expect(startTentativeInedite).not.toHaveBeenCalled()
    expect(await screen.findByText("Passer l'épreuve en conditions réelles ?")).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: /Lancer le chrono/ }))

    expect(await screen.findByText("Page de tentative")).toBeInTheDocument()
    expect(startExamMode).toHaveBeenCalledWith(71, { papier: false })
  })

  it("sur papier : même confirmation, mode papier", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true }))
    startTentativeInedite.mockResolvedValue({ id: 72 })
    startExamMode.mockResolvedValue({ id: 72 })
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: /Sur papier/ }))
    await userEvent.click(await screen.findByRole("button", { name: /Lancer le chrono/ }))

    await waitFor(() => expect(startExamMode).toHaveBeenCalledWith(72, { papier: true }))
  })

  it("sans durée connue, un seul bouton : commencer en libre", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true, duree_minutes: null }))
    startTentativeInedite.mockResolvedValue({ id: 73 })
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: "Commencer cette épreuve" }))

    expect(await screen.findByText("Page de tentative")).toBeInTheDocument()
    expect(sessionStorage.getItem("inedit-libre-73")).toBe("1")
    expect(screen.queryByText("Comment veux-tu la passer ?")).not.toBeInTheDocument()
  })

  it("traite une copie jamais engagée comme un départ : le choix du mode, pas une reprise", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true, tentative_en_cours: enCours() }))
    afficher()

    expect(await screen.findByText("Comment veux-tu la passer ?")).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: /Reprendre/ })).not.toBeInTheDocument()
  })

  it("rappelle les passages déjà rendus et la meilleure note", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({
      has_access: true,
      mes_tentatives: { en_cours: false, nb_terminees: 2, meilleure_note: 12.5, bareme: 20 },
    }))
    afficher()

    expect(await screen.findByText("Déjà rendue 2 fois · meilleure note 12,5 / 20.")).toBeInTheDocument()
  })

  it("reprend la copie entamée sans rien créer", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true, tentative_en_cours: enCours({ traitees: 3 }) }))
    afficher()

    await userEvent.click(await screen.findByRole("button", { name: "Reprendre cette épreuve" }))

    expect(await screen.findByText("Page de tentative")).toBeInTheDocument()
    expect(startTentativeInedite).not.toHaveBeenCalled()
    expect(screen.queryByText("Comment veux-tu la passer ?")).not.toBeInTheDocument()
  })

  it("annonce l'avancement, et ne recommence qu'après confirmation", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({ has_access: true, tentative_en_cours: enCours({ traitees: 3 }) }))
    startTentativeInedite.mockResolvedValue({ id: 71 })
    afficher()

    expect(await screen.findByText(/3 sur 12 traitées/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole("button", { name: /Recommencer à zéro/ }))
    expect(startTentativeInedite).not.toHaveBeenCalled()

    await userEvent.click(await screen.findByRole("button", { name: "Recommencer" }))

    await waitFor(() => expect(startTentativeInedite).toHaveBeenCalledWith(10, { nouvelle: true }))
  })

  it("n'offre pas de recommencer tant que le chrono tourne, et dit ce qu'il reste", async () => {
    getEpreuveInedite.mockResolvedValue(epreuve({
      has_access: true,
      tentative_en_cours: enCours({
        traitees: 2, exam_mode_started_at: new Date().toISOString(), echeance: new Date(Date.now() + 90 * 60_000).toISOString(),
      }),
    }))
    afficher()

    expect(await screen.findByRole("button", { name: "Reprendre cette épreuve" })).toBeInTheDocument()
    expect(screen.getByText(/Chrono en cours : il te reste 1:[23]\d:\d\d/)).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: /Recommencer/ })).not.toBeInTheDocument()
  })
})
