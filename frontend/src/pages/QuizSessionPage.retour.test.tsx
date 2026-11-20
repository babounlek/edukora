import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const revealQuizEssaiCorrige = vi.hoisted(() => vi.fn())
const answerQuizEssai = vi.hoisted(() => vi.fn())

vi.mock("@/api/endpoints", () => ({ revealQuizEssaiCorrige, answerQuizEssai }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))
vi.mock("@/lib/retours", () => ({ jouerRetour: vi.fn(), retoursActifs: () => true, definirRetoursActifs: vi.fn() }))
// KaTeX et le rendu Markdown complet n'ont rien à voir ici : le texte brut suffit.
vi.mock("@/components/EpreuveMarkdown", () => ({ EpreuveMarkdown: ({ markdown }: { markdown: string }) => <div>{markdown}</div> }))
vi.mock("@/components/BoutonPartager", () => ({ BoutonPartager: () => null }))
vi.mock("@/components/ObjectifXp", () => ({ ObjectifXp: () => null }))
vi.mock("@/components/QuizFichePdfButtons", () => ({ QuizFichePdfButtons: () => null }))

import { jouerRetour } from "@/lib/retours"
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
    return screen.findByRole("button", { name: "Je l'avais" })
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

describe("QuizSessionPage : le pont vers les exercices du thème", () => {
  beforeEach(() => {
    sessionStorage.clear()
    Element.prototype.scrollIntoView = vi.fn()
  })
  afterEach(() => sessionStorage.clear())

  it("s'ouvre dans le même onglet : un lien de l'application, sans nouvel onglet", async () => {
    // Test élève Gogo : le lien s'ouvrait dans un nouvel onglet, sans signe visible.
    const repondue = (id: number) =>
      question(id, {
        corrige_markdown: "Le corrigé", theme_id: 7, subject_code: "MATHS",
        reponse: { est_correcte: true, resultat_declare: "REUSSI", xp_gagne: 0 },
      })
    poserEssai([repondue(1), repondue(2)])
    afficher()

    const lien = await screen.findByRole("link", { name: /Exercices corrigés/ })

    expect(lien).toHaveAttribute("href", "/cm/themes-frequents/7/exercices?subject=MATHS&cursus=14")
    expect(lien).not.toHaveAttribute("target")
  })
})

describe("QuizSessionPage : la correction d'un QCM", () => {
  beforeEach(() => {
    sessionStorage.clear()
    Element.prototype.scrollIntoView = vi.fn()
  })
  afterEach(() => sessionStorage.clear())

  const qcm = (est_correcte: boolean) =>
    question(1, {
      type_reponse: "QCM",
      choix: [{ lettre: "a", texte: "$1$" }, { lettre: "b", texte: "$2$" }],
      reponse_correcte: "b",
      corrige_markdown: "Le corrigé",
      reponse: { reponse_choisie: est_correcte ? "b" : "a", resultat_declare: "", est_correcte, xp_gagne: 0 },
    })

  it("reste repliée après une erreur, avec un bouton qui dit à quoi il sert", async () => {
    // Ouverte d'office, elle faisait trois écrans avant la question suivante (test élève Guyguy).
    poserEssai([qcm(false)])
    afficher()

    const resume = await screen.findByText("Comprendre mon erreur")
    expect(resume.closest("details")).not.toHaveAttribute("open")
  })

  it("reste repliée après une bonne réponse, avec son libellé habituel", async () => {
    poserEssai([qcm(true)])
    afficher()

    const resume = await screen.findByText("Comprendre la correction")
    expect(resume.closest("details")).not.toHaveAttribute("open")
  })
})

describe("QuizSessionPage : la série de bonnes réponses s'entend", () => {
  const qcm = (id: number, repondue: boolean) =>
    question(id, {
      type_reponse: "QCM",
      choix: [{ lettre: "a", texte: "Choix A" }, { lettre: "b", texte: "Choix B" }],
      ...(repondue
        ? { reponse_correcte: "b", reponse: { reponse_choisie: "b", resultat_declare: "", est_correcte: true, xp_gagne: 0 } }
        : {}),
    })

  beforeEach(() => {
    sessionStorage.clear()
    Element.prototype.scrollIntoView = vi.fn()
    vi.mocked(jouerRetour).mockClear()
    answerQuizEssai.mockReset()
    answerQuizEssai.mockImplementation((_cursus: number, id: number) => Promise.resolve(qcm(id, true)))
  })
  afterEach(() => sessionStorage.clear())

  async function repondreALaDerniere(dejaJustes: number) {
    const questions = Array.from({ length: dejaJustes }, (_, i) => qcm(i + 1, true))
    poserEssai([...questions, qcm(dejaJustes + 1, false)])
    afficher()
    await screen.findByText(`Énoncé ${dejaJustes + 1}`)
    fireEvent.click(screen.getByRole("button", { name: /Choix B/ }))
    await waitFor(() => expect(jouerRetour).toHaveBeenCalled())
  }

  it("la troisième bonne réponse d'affilée sonne plus haut que la première", async () => {
    await repondreALaDerniere(2)

    expect(jouerRetour).toHaveBeenCalledWith("juste", { serie: 3 })
    expect(screen.getByText("3 bonnes réponses d'affilée, tu es en feu.")).toBeInTheDocument()
  })

  it("la cinquième est un palier : son à part et phrase à elle", async () => {
    await repondreALaDerniere(4)

    expect(jouerRetour).toHaveBeenCalledWith("palier")
    expect(screen.getByText("5 d'affilée ! Rien ne t'arrête.")).toBeInTheDocument()
    expect(screen.queryByText(/tu es en feu/)).not.toBeInTheDocument()
  })
})
