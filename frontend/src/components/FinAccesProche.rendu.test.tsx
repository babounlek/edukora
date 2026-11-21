import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { Accueil } from "@/api/types"

const etat = vi.hoisted(() => ({ abonnements: [] as unknown[], maintenant: 0 }))
const trackEvent = vi.hoisted(() => vi.fn())

vi.mock("@/lib/changerCursusPrepare", () => ({ useCursusAbonnes: () => etat.abonnements }))
vi.mock("@/lib/horlogeServeur", () => ({ maintenantServeur: () => etat.maintenant }))
vi.mock("@/lib/analytics", () => ({ trackEvent }))
vi.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ user: { id: 1, profil_actif: { id: 30 }, cursus_prepare: { id: 14 } } }),
}))
// Le partage aux parents a ses propres tests : ici, seulement ce que la ligne lui transmet.
vi.mock("@/components/BoutonParents", () => ({
  BoutonParents: ({ examen, contenu }: { examen?: string; contenu?: string }) => (
    <button type="button">Montrer à mes parents ({examen} ; {contenu})</button>
  ),
}))

import { FinAccesProche } from "./FinAccesProche"

const BEPC = { id: 14, examen: "BEPC", examen_display: "BEPC", series: null }
const abonnement = (fin: Date, profil = 30, cursus = BEPC) => ({
  id: 1, cursus, profil: { id: profil, prenom: "Guyguy" }, expires_at: fin.toISOString(), is_active: true,
})
const accueil = (resume: Partial<Accueil["resume"][number]>[] = []) => ({ resume }) as unknown as Accueil

function afficher(donnees = accueil()) {
  return render(<MemoryRouter><FinAccesProche accueil={donnees} /></MemoryRouter>)
}

beforeEach(() => {
  etat.maintenant = new Date(2026, 11, 10, 17, 30).getTime()
  etat.abonnements = []
  trackEvent.mockReset()
})

describe("FinAccesProche : la fin de l'accès annoncée sur l'accueil d'un abonné", () => {
  it("à trois jours : la date, ce qu'il a construit, et les deux gestes possibles", () => {
    etat.abonnements = [abonnement(new Date(2026, 11, 13, 9, 0))]
    afficher(accueil([{ maitrises: 20, en_revision: 12 }, { maitrises: 0, en_revision: 1 }]))

    expect(screen.getByText("Ton accès se termine le 13 décembre")).toBeInTheDocument()
    expect(screen.getByText("Ce que tu as construit est gardé : 20 thèmes maîtrisés et 13 thèmes en révision.")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: /Prolonger/ })).toHaveAttribute("href", "/abonnement?cursus=14&profil=30")
    // Le message tout prêt pour les parents dit la date.
    expect(screen.getByRole("button", { name: "Montrer à mes parents (BEPC ; continuer après le 13 décembre)" })).toBeInTheDocument()
    // Jamais de décompte : une date, pas « plus que 3 jours ».
    expect(screen.queryByText(/plus que|jours? restant/i)).toBeNull()
  })

  it("le jour même, et sans rien de construit : une phrase qui rassure, pas une phrase à zéro", () => {
    etat.abonnements = [abonnement(new Date(2026, 11, 10, 23, 0))]
    afficher(accueil([{ maitrises: 0, en_revision: 0 }]))

    expect(screen.getByText("Ton accès se termine aujourd'hui")).toBeInTheDocument()
    expect(screen.getByText("Ta progression est gardée. Rien n'est prélevé automatiquement.")).toBeInTheDocument()
  })

  it("rien à plus d'une semaine de la fin", () => {
    etat.abonnements = [abonnement(new Date(2026, 11, 18, 9, 0))]
    const { container } = afficher()
    expect(container).toBeEmptyDOMElement()
  })

  it("rien pour l'abonnement d'un autre enfant ou d'un autre examen du compte", () => {
    etat.abonnements = [
      abonnement(new Date(2026, 11, 12, 9, 0), 31),
      abonnement(new Date(2026, 11, 12, 9, 0), 30, { ...BEPC, id: 20 }),
    ]
    const { container } = afficher()
    expect(container).toBeEmptyDOMElement()
  })
})
