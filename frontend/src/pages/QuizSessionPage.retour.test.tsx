import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const revealQuizEssaiCorrige = vi.hoisted(() => vi.fn())
const answerQuizEssai = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ revealQuizEssaiCorrige, answerQuizEssai }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/retours", () => ({ jouerRetour: vi.fn() }))
vi.mock("@/lib/quizEnCours", () => ({
  memoriserQuizEnCours: vi.fn(),
  oublierQuizEnCours: vi.fn(),
  useCleQuizEnCours: () => null,
}))
// KaTeX et le rendu Markdown complet n'ont rien à voir ici : le texte brut suffit.
vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <div>{markdown}</div> }))
vi.mock("@/components/BoutonPartager", () => ({ BoutonPartager: () => null }))
vi.mock("@/components/ObjectifXp", () => ({ ObjectifXp: () => null }))
vi.mock("@/components/QuizFichePdfButtons", () => ({ QuizFichePdfButtons: () => null }))

import { QuizSessionPage } from "./QuizSessionPage"

const CLE_ESSAI = "edukora:quiz-essai"

function question(id: number, extra = {}) {
  return {
    id,
    ordre: id,
    enonce_markdown: `Énoncé ${id}`,
    type_reponse: "OUVERTE",
    choix: [],
    subject_label: "Mathématiques",
    theme: "Identité remarquable",
    ...extra,
  }
}

function poserEssai(questions: unknown[]) {
  sessionStorage.setItem(
    CLE_ESSAI,
    JSON.stringify({
      id: 0,
      mode: "PRATIQUE",
      cursus: 14,
      subject: 1,
      cursus_display: "BEPC",
      started_at: "2026-10-19T10:00:00Z",
      completed_at: null,
      total_questions: questions.length,
      essai: true,
      questions,
    }),
  )
}

function afficher() {
  return render(
    <MemoryRouter initialEntries={["/quiz/essai"]}>
      <QuizSessionPage essai />
    </MemoryRouter>,
  )
}

describe("QuizSessionPage : le retour après l'auto-évaluation est amené à l'écran", () => {
  const defiler = vi.fn()

  beforeEach(() => {
    sessionStorage.clear()
    defiler.mockReset()
    revealQuizEssaiCorrige.mockReset()
    answerQuizEssai.mockReset()
    Element.prototype.scrollIntoView = defiler
    revealQuizEssaiCorrige.mockResolvedValue({ corrige_markdown: "Le corrigé", reponse_correcte: "" })
    answerQuizEssai.mockImplementation((_cursus: number, id: number) =>
      Promise.resolve(question(id, { corrige_markdown: "Le corrigé", reponse: { est_correcte: true, resultat_declare: "REUSSI", xp_gagne: 0 } })),
    )
  })
  afterEach(() => sessionStorage.clear())

  async function jusquAuxBoutons() {
    afficher()
    fireEvent.click(await screen.findByRole("button", { name: /Voir la correction/ }))
    return screen.findByRole("button", { name: "Réussi" })
  }

  it("fait défiler jusqu'au message dès que la réponse est enregistrée", async () => {
    poserEssai([question(1), question(2)])
    fireEvent.click(await jusquAuxBoutons())

    await waitFor(() => expect(defiler).toHaveBeenCalledTimes(1))
    expect(defiler).toHaveBeenCalledWith(expect.objectContaining({ block: "nearest" }))
  })

  it("ne fait pas sauter la page à l'ouverture d'une question déjà répondue", async () => {
    const repondue = (id: number) =>
      question(id, { corrige_markdown: "Le corrigé", reponse: { est_correcte: true, resultat_declare: "REUSSI", xp_gagne: 0 } })
    poserEssai([repondue(1), repondue(2)])
    afficher()

    // Tout est répondu : la page s'ouvre sur la dernière question, message de retour déjà affiché.
    await screen.findByText("Énoncé 2")
    await waitFor(() => expect(screen.getByRole("status")).not.toBeEmptyDOMElement())
    expect(defiler).not.toHaveBeenCalled()
  })
})
