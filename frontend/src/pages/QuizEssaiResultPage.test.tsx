import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { QuizQuestion, QuizSession } from "@/api/types"

const auth = vi.hoisted(() => ({ isAuthenticated: false }))
vi.mock("@/api/endpoints", () => ({ startQuizEssai: vi.fn() }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/retours", () => ({ jouerRetour: vi.fn() }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
// Le compteur qui monte est de l'animation : le test lit la valeur finale.
vi.mock("@/lib/useCompteur", () => ({ useCompteur: (cible: number) => cible }))

import { memoriserDefi } from "@/lib/defiEssai"
import { memoriserEssai, memoriserRecord } from "@/lib/quizEssai"
import { QuizEssaiResultPage } from "./QuizEssaiResultPage"

function qcm(id: number, juste: boolean): QuizQuestion {
  return {
    id, ordre: id, enonce_markdown: `Q${id}`, type_reponse: "QCM", choix: [], subject_label: "Maths", theme: "identités",
    theme_id: 77, subject_code: "MATH",
    reponse: { reponse_choisie: "A", resultat_declare: "", est_correcte: juste, xp_gagne: 0 },
  } as QuizQuestion
}

function essai(justes: boolean[]): QuizSession {
  const questions = justes.map((juste, i) => qcm(i + 1, juste))
  return {
    id: 0, essai: true, mode: "PRATIQUE", cursus: 1, subject: 2, cursus_display: "BEPC",
    started_at: "2026-10-25T10:00:00Z", completed_at: null, total_questions: questions.length, questions,
  }
}

function afficher() {
  render(
    <MemoryRouter>
      <QuizEssaiResultPage />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  sessionStorage.clear()
  localStorage.clear()
  auth.isAuthenticated = false
})

describe("QuizEssaiResultPage : le gain du visiteur", () => {
  it("montre les points que l'essai aurait rapportés, et dit qu'ils ne sont pas gardés", async () => {
    memoriserEssai(essai([true, true, true, false, false]))
    afficher()

    expect(await screen.findByText("Ce quiz t'aurait rapporté")).toBeInTheDocument()
    expect(screen.getByText("+30 points")).toBeInTheDocument()
    expect(screen.getByText(/Ceux-ci ne sont pas gardés/)).toBeInTheDocument()
  })

  it("ne propose pas de créer un compte à qui est déjà connecté", async () => {
    auth.isAuthenticated = true
    memoriserEssai(essai([true, true, false]))
    afficher()

    await screen.findByText("Ce quiz t'aurait rapporté")
    expect(screen.queryByText(/Ceux-ci ne sont pas gardés/)).not.toBeInTheDocument()
    expect(screen.queryByRole("link", { name: "Créer mon compte" })).not.toBeInTheDocument()
  })

  it("garde le record sur l'appareil et annonce le suivant", async () => {
    memoriserEssai(essai([true, true, true, false, false]))
    afficher()
    await screen.findByText("+30 points")
    // Premier essai : pas d'exploit à annoncer, mais le record est gardé pour la prochaine fois.
    expect(screen.queryByText(/Nouveau record/)).not.toBeInTheDocument()
    expect(localStorage.getItem("edukora:records-essai")).toContain('"reussies":3')
  })

  it("annonce un record battu", async () => {
    memoriserRecord(essai([true, false, false, false, false]), 1, 5)
    memoriserEssai(essai([true, true, true, true, false]))
    afficher()

    expect(await screen.findByText("Nouveau record ! Ton précédent : 1 / 5.")).toBeInTheDocument()
  })

  it("rappelle le record à battre quand on ne l'a pas dépassé", async () => {
    memoriserRecord(essai([true, true, true, true, false]), 4, 5)
    memoriserEssai(essai([true, false, false, false, false]))
    afficher()

    expect(await screen.findByText("Ton record sur ce thème : 4 / 5. Refais l'essai pour le battre.")).toBeInTheDocument()
  })

  it("compare le résultat au défi d'un camarade", async () => {
    memoriserDefi({ reussies: 2, total: 5 })
    memoriserEssai(essai([true, true, true, false, false]))
    afficher()

    expect(await screen.findByText("Défi relevé : tu fais mieux que ton camarade (3/5 contre 2/5) !")).toBeInTheDocument()
  })

  it("dit quand le camarade a fait mieux", async () => {
    memoriserDefi({ reussies: 5, total: 5 })
    memoriserEssai(essai([true, false, false, false, false]))
    afficher()

    expect(await screen.findByText("Ton camarade a fait mieux (5/5 contre 1/5). Refais l'essai pour le battre !")).toBeInTheDocument()
  })

  it("ne parle d'aucun défi quand on n'en a pas reçu", async () => {
    memoriserEssai(essai([true, false, false, false, false]))
    afficher()

    await screen.findByText("Ce quiz t'aurait rapporté")
    expect(screen.queryByRole("status")).not.toBeInTheDocument()
  })

  it("dit « Sans faute ! » pour un 5/5", async () => {
    memoriserEssai(essai([true, true, true, true, true]))
    afficher()

    expect(await screen.findByRole("heading", { name: "Sans faute !" })).toBeInTheDocument()
  })

  it("ne dit pas « Sans faute » pour un 4/5", async () => {
    memoriserEssai(essai([true, true, true, true, false]))
    afficher()

    await screen.findByText("Ce quiz t'aurait rapporté")
    expect(screen.queryByRole("heading", { name: /Sans faute/ })).not.toBeInTheDocument()
  })
})
