import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMySubscriptions = vi.hoisted(() => vi.fn())
const getResumeParcours = vi.hoisted(() => vi.fn())
const getBilanPeriode = vi.hoisted(() => vi.fn())

const BEPC = { id: 14, examen: "BEPC", examen_display: "BEPC", series: null }
const BAC_C = { id: 20, examen: "BAC", examen_display: "BAC", series: { id: 3, code: "C", label: "Série C" } }

const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  user: {
    id: 1,
    profil_actif: { id: 9 },
    cursus_prepare: { id: 14, examen_display: "BEPC", series: null } as unknown,
  },
}))

vi.mock("@/api/endpoints", () => ({ listMySubscriptions, getResumeParcours, getBilanPeriode }))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/lib/seo", () => ({ useSeo: vi.fn() }))

import { ParcoursPage } from "./ParcoursPage"

const abonnement = (id: number, cursus: typeof BEPC | typeof BAC_C, profilId = 9) => ({
  id,
  cursus,
  profil: { id: profilId },
  is_active: true,
})

function afficher() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const arbre = () => (
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/parcours"]}>
        <ParcoursPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
  const rendu = render(arbre())
  return { ...rendu, rerenderPage: () => rendu.rerender(arbre()) }
}

describe("ParcoursPage (Ma progression) - pastilles d'examen", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    auth.user.cursus_prepare = { id: 14, examen_display: "BEPC", series: null }
    listMySubscriptions.mockResolvedValue([
      abonnement(253, BAC_C),
      abonnement(258, BEPC),
      abonnement(260, BAC_C, 15), // autre profil du compte : jamais proposé
    ])
    getResumeParcours.mockResolvedValue([])
    getBilanPeriode.mockRejectedValue(new Error("pas de bilan"))
  })

  it("ne montre que l'examen préparé quand le profil a payé BEPC et BAC C", async () => {
    afficher()
    await waitFor(() => expect(getResumeParcours).toHaveBeenCalledWith(14))
    expect(await screen.findByText("BEPC")).toBeTruthy()
    expect(screen.queryByText("BAC C")).toBeNull()
    expect(getResumeParcours).not.toHaveBeenCalledWith(20)
  })

  it("suit l'examen préparé quand l'élève le change depuis le bandeau", async () => {
    const { rerenderPage } = afficher()
    expect(await screen.findByText("BEPC")).toBeTruthy()

    auth.user.cursus_prepare = { id: 20, examen_display: "BAC", series: { id: 3, code: "C", label: "Série C" } }
    rerenderPage()

    expect(await screen.findByText("BAC C")).toBeTruthy()
    expect(screen.queryByText("BEPC")).toBeNull()
    await waitFor(() => expect(getResumeParcours).toHaveBeenLastCalledWith(20))
  })

  it("garde le sélecteur quand aucun examen n'est préparé", async () => {
    auth.user.cursus_prepare = null
    afficher()
    expect(await screen.findByRole("button", { name: "BEPC" })).toBeTruthy()
    expect(screen.getByRole("button", { name: "BAC C" })).toBeTruthy()
  })
})

const matiere = (surcharges: Record<string, unknown>) => ({
  subject_id: 1, subject_code: "MATHS", subject_label: "Mathématiques", total: 100, sans_contenu: 0,
  maitrises: 0, en_revision: 0, en_cours: 0, a_decouvrir: 100, poids_total: 1, poids_maitrise: 0, ...surcharges,
})

describe("ParcoursPage (Ma progression) - ce que disent les chiffres à un élève qui démarre", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    auth.user.cursus_prepare = { id: 14, examen_display: "BEPC", series: null }
    listMySubscriptions.mockResolvedValue([abonnement(258, BEPC)])
    getBilanPeriode.mockRejectedValue(new Error("pas de bilan"))
  })

  it("une matière jamais ouverte est « À découvrir », une matière travaillée sans maîtrise est « En cours »", async () => {
    getResumeParcours.mockResolvedValue([
      matiere({ subject_id: 1, subject_label: "Anglais" }),
      matiere({ subject_id: 2, subject_label: "Mathématiques", en_revision: 30, en_cours: 2 }),
      matiere({ subject_id: 3, subject_label: "Physique", maitrises: 25, en_revision: 4 }),
    ])
    afficher()

    const anglais = (await screen.findByRole("link", { name: /Anglais/ })).textContent
    expect(anglais).toContain("À découvrir")
    expect(anglais).toContain("100 savoirs à découvrir")
    expect(anglais).not.toMatch(/0\s*%|abonne-toi/)

    const maths = screen.getByRole("link", { name: /Mathématiques/ }).textContent
    expect(maths).toContain("En cours")
    expect(maths).toContain("32 savoirs travaillés sur 100")
    expect(maths).not.toMatch(/(^|\D)0\s*%/)

    const physique = screen.getByRole("link", { name: /Physique/ }).textContent
    expect(physique).toContain("25")
    expect(physique).toContain("25/100 savoirs maîtrisés")
  })

  it("sous 10 %, le haut de page dit le palier suivant, pas « N sur 300 »", async () => {
    getResumeParcours.mockResolvedValue([
      matiere({ subject_id: 1, subject_label: "Anglais" }),
      matiere({ subject_id: 2, subject_label: "Mathématiques", en_revision: 30, en_cours: 2 }),
      matiere({ subject_id: 3, subject_label: "Physique", maitrises: 6, en_revision: 4 }),
    ])
    afficher()

    expect((await screen.findAllByText(/Savoirs maîtrisés : 6\. Prochain palier : 10\./)).length).toBeGreaterThan(0)
  })

  it("au-delà, il garde le compte « maîtrisés sur total »", async () => {
    getResumeParcours.mockResolvedValue([matiere({ subject_id: 3, subject_label: "Physique", maitrises: 40, en_revision: 4 })])
    afficher()

    await screen.findByRole("link", { name: /Physique/ })
    expect(screen.queryByText(/Prochain palier/)).toBeNull()
  })

  it("montre le bilan par matière quand l'élève a de l'activité", async () => {
    getResumeParcours.mockResolvedValue([matiere({ subject_id: 2, en_cours: 3 })])
    getBilanPeriode.mockResolvedValue({
      a_de_l_activite: true, abonnement_actif: true, debut: "2026-10-24", fin: "2026-11-13", seances: 3, questions: 54,
      taux_reussite: 50, taux_avant: null, meilleure_serie: 5, jours_actifs: 3, themes_consolides_total: 0,
      themes_consolides: [], matieres: [{ subject_id: 2, subject_label: "Mathématiques", questions: 19, taux_avant: null, taux_periode: 47 }],
    })
    afficher()

    expect(await screen.findByText("Par matière")).toBeTruthy()
    expect(screen.getByText("47 %")).toBeTruthy()
    expect(getBilanPeriode).toHaveBeenCalledWith(14, expect.anything())
  })
})
