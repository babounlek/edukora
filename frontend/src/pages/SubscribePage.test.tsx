import { fireEvent, render, screen, waitFor, within } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MemoryRouter, Route, Routes, useNavigate } from "react-router-dom"
import { beforeEach, describe, expect, it, vi } from "vitest"

const listMyInscriptionsInedites = vi.hoisted(() => vi.fn())
const getPaymentConfig = vi.hoisted(() => vi.fn())
const listProfils = vi.hoisted(() => vi.fn())
const listPlans = vi.hoisted(() => vi.fn())
const initiatePayment = vi.hoisted(() => vi.fn())
const listMySubscriptions = vi.hoisted(() => vi.fn())
const auth = vi.hoisted(() => ({
  isAuthenticated: true,
  isLoading: false,
  user: { phone_number: "677000000" } as { phone_number: string; profil_actif?: { id: number; prenom: string } },
}))

vi.mock("@/api/endpoints", () => ({
  checkPaymentStatus: vi.fn(),
  initiatePayment,
  listCursus: vi.fn(() => Promise.resolve([])),
  listPlans,
  listProfils,
  listMySubscriptions,
  listMyInscriptionsInedites,
  getPaymentConfig,
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))
vi.mock("@/lib/analytics", () => ({ trackEvent: vi.fn() }))
vi.mock("@/lib/sentry", () => ({ Sentry: { captureException: vi.fn() } }))
vi.mock("@/components/BilanDePeriode", () => ({ BilanDePeriode: () => null }))
vi.mock("@/components/CodeRevendeur", () => ({ CodeRevendeur: () => null }))
vi.mock("@/components/ManualPaymentPanel", () => ({ ManualPaymentPanel: () => null }))

import { SubscribePage } from "./SubscribePage"

const RETOUR = "/cm/epreuves-inedites/maths-bac-d"

function inscription(cursusId: number, actif = true) {
  return { id: 1, cursus: { id: cursusId }, profil: { id: 1, prenom: "Awa" }, expires_at: "2027-06-01T00:00:00Z", is_active: actif }
}

function afficher(url: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[url]}>
        <Routes>
          <Route path="/abonnement" element={<SubscribePage />} />
          <Route path="/cm/epreuves-inedites/:id" element={<p>Fiche de l'épreuve</p>} />
          <Route path="/connexion" element={<p>Page de connexion</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  listMyInscriptionsInedites.mockReset()
  getPaymentConfig.mockReset()
  getPaymentConfig.mockResolvedValue({ campay_active: true })
  listProfils.mockReset()
  listProfils.mockResolvedValue([])
  listPlans.mockReset()
  listPlans.mockResolvedValue([])
  initiatePayment.mockReset()
  listMySubscriptions.mockReset()
  listMySubscriptions.mockResolvedValue([])
  auth.isAuthenticated = true
  auth.isLoading = false
  auth.user = { phone_number: "677000000" }
})

describe("SubscribePage : pour quel enfant le parent paie", () => {
  it("nomme l'enfant ACTIF quand le lien ne porte pas de profil et que le compte en a plusieurs", async () => {
    auth.user = { phone_number: "677000000", profil_actif: { id: 2, prenom: "Junior" } }
    listProfils.mockResolvedValue([{ id: 1, prenom: "Awa" }, { id: 2, prenom: "Junior" }])
    afficher("/abonnement?cursus=4&duree=examen")

    expect(await screen.findByText(/Abonnement pour Junior/)).toBeInTheDocument()
  })

  it("laisse le parent choisir l'enfant à abonner quand le compte en a plusieurs", async () => {
    auth.user = { phone_number: "677000000", profil_actif: { id: 2, prenom: "Junior" } }
    listProfils.mockResolvedValue([{ id: 1, prenom: "Awa" }, { id: 2, prenom: "Junior" }])
    afficher("/abonnement?cursus=4&mois=3")

    const awa = await screen.findByRole("radio", { name: "Awa" })
    const junior = screen.getByRole("radio", { name: "Junior" })
    // Le profil actif est présélectionné, comme avant.
    expect(junior).toHaveAttribute("aria-checked", "true")
    expect(awa).toHaveAttribute("aria-checked", "false")

    fireEvent.click(awa)

    expect(await screen.findByText(/Abonnement pour Awa/)).toBeInTheDocument()
    expect(screen.getByRole("radio", { name: "Awa" })).toHaveAttribute("aria-checked", "true")
  })

  it("n'affiche pas de sélecteur sur un compte à un seul profil", async () => {
    auth.user = { phone_number: "677000000", profil_actif: { id: 1, prenom: "Awa" } }
    listProfils.mockResolvedValue([{ id: 1, prenom: "Awa" }])
    afficher("/abonnement?cursus=4&mois=3")

    await waitFor(() => expect(listProfils).toHaveBeenCalled())
    await screen.findByText(/Paiement sécurisé/)
    expect(screen.queryByRole("radio", { name: "Awa" })).not.toBeInTheDocument()
  })

  it("ne nomme personne sur un compte à un seul profil", async () => {
    auth.user = { phone_number: "677000000", profil_actif: { id: 1, prenom: "Awa" } }
    listProfils.mockResolvedValue([{ id: 1, prenom: "Awa" }])
    afficher("/abonnement?cursus=4&duree=examen")

    await waitFor(() => expect(listProfils).toHaveBeenCalled())
    await screen.findByText(/Paiement sécurisé/)
    expect(screen.queryByText(/Abonnement pour/)).not.toBeInTheDocument()
  })
})

describe("SubscribePage : retour vers l'épreuve qui a motivé l'achat", () => {
  it("ramène un abonné déjà actif sur ce cursus à son épreuve, sans lui montrer d'offre", async () => {
    listMyInscriptionsInedites.mockResolvedValue([inscription(4)])
    afficher(`/abonnement?cursus=4&duree=examen&retour=${encodeURIComponent(RETOUR)}`)

    expect(await screen.findByText("Fiche de l'épreuve")).toBeInTheDocument()
  })

  it("reste sur l'offre quand l'abonnement actif porte sur un autre cursus ou est échu", async () => {
    listMyInscriptionsInedites.mockResolvedValue([inscription(9), inscription(4, false)])
    afficher(`/abonnement?cursus=4&duree=examen&retour=${encodeURIComponent(RETOUR)}`)

    await waitFor(() => expect(listMyInscriptionsInedites).toHaveBeenCalled())
    expect(screen.queryByText("Fiche de l'épreuve")).not.toBeInTheDocument()
  })

  it("ne redirige jamais sans `retour` : un abonné qui vient prolonger doit voir l'offre", async () => {
    listMyInscriptionsInedites.mockResolvedValue([inscription(4)])
    afficher("/abonnement?cursus=4&duree=examen")

    await screen.findByText(/Paiement sécurisé/)
    expect(listMyInscriptionsInedites).not.toHaveBeenCalled()
    expect(screen.queryByText("Fiche de l'épreuve")).not.toBeInTheDocument()
  })

  it("refuse un `retour` qui sort du site", async () => {
    listMyInscriptionsInedites.mockResolvedValue([inscription(4)])
    afficher(`/abonnement?cursus=4&duree=examen&retour=${encodeURIComponent("https://evil.example/x")}`)

    await screen.findByText(/Paiement sécurisé/)
    expect(listMyInscriptionsInedites).not.toHaveBeenCalled()
  })

  it("renvoie un visiteur vers la connexion", async () => {
    auth.isAuthenticated = false
    afficher(`/abonnement?cursus=4&duree=examen&retour=${encodeURIComponent(RETOUR)}`)

    expect(await screen.findByText("Page de connexion")).toBeInTheDocument()
    expect(listMyInscriptionsInedites).not.toHaveBeenCalled()
  })

  it("remplace /abonnement dans l'historique : « retour » depuis la connexion revient à l'épreuve", async () => {
    auth.isAuthenticated = false
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    function Retour() {
      const navigate = useNavigate()
      return <button onClick={() => navigate(-1)}>Retour</button>
    }
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter initialEntries={[RETOUR, "/abonnement?cursus=4"]} initialIndex={1}>
          <Routes>
            <Route path="/abonnement" element={<SubscribePage />} />
            <Route path="/cm/epreuves-inedites/:id" element={<p>Fiche de l'épreuve</p>} />
            <Route path="/connexion" element={<><p>Page de connexion</p><Retour /></>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await screen.findByText("Page de connexion")
    fireEvent.click(screen.getByText("Retour"))

    expect(await screen.findByText("Fiche de l'épreuve")).toBeInTheDocument()
    expect(screen.queryByText("Page de connexion")).not.toBeInTheDocument()
  })
})

describe("SubscribePage : interrupteur Campay (CAMPAY_ACTIVE)", () => {
  it("propose Campay en recommandé, le paiement manuel restant replié, quand il est actif", async () => {
    afficher("/abonnement?cursus=4&duree=examen")

    expect(await screen.findByText("Recommandé")).toBeInTheDocument()
    expect(screen.getByText(/Des difficultés avec Campay/)).toBeInTheDocument()
    expect(screen.queryByText(/momentanément indisponible/)).not.toBeInTheDocument()
  })

  it("ne montre plus que le paiement manuel, déjà déplié, quand Campay est coupé", async () => {
    getPaymentConfig.mockResolvedValue({ campay_active: false })
    afficher("/abonnement?cursus=4&duree=examen")

    expect(await screen.findByText(/momentanément indisponible/)).toBeInTheDocument()
    expect(screen.getByText("Orange Money")).toBeInTheDocument()
    expect(screen.getByText("MTN MoMo")).toBeInTheDocument()
    expect(screen.queryByText("Recommandé")).not.toBeInTheDocument()
    expect(screen.queryByText(/Des difficultés avec Campay/)).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/Numéro Mobile Money/)).not.toBeInTheDocument()
  })

  it("retombe sur Campay actif si l'état ne peut pas être lu (le backend refuse de toute façon)", async () => {
    getPaymentConfig.mockRejectedValue(new Error("réseau"))
    afficher("/abonnement?cursus=4&duree=examen")

    expect(await screen.findByText("Recommandé")).toBeInTheDocument()
  })
})

function planAuMois(surcharges: Record<string, unknown> = {}) {
  return {
    id: 11, name: "BEPC - Au mois", cursus: { id: 4 }, product_type: "ABONNEMENT", price: 2000, duration_mode: "MENSUEL",
    duration_days: 30, effective_duration_days: 30, effective_price: 2000, prix_reference: 2000, campagne: null,
    inclut_inedit: true, mois_max: 7, ...surcharges,
  }
}

describe("SubscribePage : l'élève choisit le nombre de mois", () => {
  beforeEach(() => {
    listPlans.mockResolvedValue([planAuMois()])
  })

  it("propose un trimestre d'office et écrit le total en toutes lettres", async () => {
    afficher("/abonnement?cursus=4")

    expect(await screen.findByText("Pour combien de mois ?")).toBeInTheDocument()
    expect(screen.getByRole("radio", { name: /^3/ })).toHaveAttribute("aria-checked", "true")
    expect(screen.getByText("3 mois × 2 000 FCFA par mois")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Payer 6 000 FCFA/ })).toBeInTheDocument()
  })

  it("reprend la durée choisie sur la page des tarifs (?mois=)", async () => {
    afficher("/abonnement?cursus=4&mois=5")

    expect(await screen.findByText("5 mois × 2 000 FCFA par mois")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Payer 10 000 FCFA/ })).toBeInTheDocument()
  })

  it("un ancien lien duree=examen prend tous les mois qui restent", async () => {
    afficher("/abonnement?cursus=4&duree=examen")

    expect(await screen.findByText("7 mois × 2 000 FCFA par mois")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Payer 14 000 FCFA/ })).toBeInTheDocument()
  })

  it("ne laisse jamais choisir plus de mois que ce qui reste avant l'examen", async () => {
    listPlans.mockResolvedValue([planAuMois({ mois_max: 2 })])
    afficher("/abonnement?cursus=4&mois=9")

    expect(await screen.findByText("2 mois × 2 000 FCFA par mois")).toBeInTheDocument()
    expect(within(screen.getByRole("radiogroup")).getAllByRole("radio")).toHaveLength(2)
  })

  it("change le total quand l'élève touche un autre mois", async () => {
    afficher("/abonnement?cursus=4")
    await screen.findByText("Pour combien de mois ?")

    fireEvent.click(screen.getByRole("radio", { name: /^6/ }))

    expect(await screen.findByText("6 mois × 2 000 FCFA par mois")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Payer 12 000 FCFA/ })).toBeInTheDocument()
  })

  it("envoie le nombre de mois au paiement", async () => {
    initiatePayment.mockResolvedValue({ status: "FAILED" })
    afficher("/abonnement?cursus=4&mois=4")
    await screen.findByText("4 mois × 2 000 FCFA par mois")

    fireEvent.change(await screen.findByLabelText(/Numéro Mobile Money/), { target: { value: "677123456" } })
    fireEvent.click(screen.getByRole("button", { name: /Payer 8 000 FCFA/ }))

    await waitFor(() => expect(initiatePayment).toHaveBeenCalledTimes(1))
    expect(initiatePayment).toHaveBeenCalledWith(expect.objectContaining({ planId: 11, mois: 4 }))
  })

  it("annonce la date de fin à partir de l'accès en cours quand l'enfant prolonge", async () => {
    const dans200Jours = new Date(Date.now() + 200 * 86_400_000).toISOString()
    listMySubscriptions.mockResolvedValue([
      { id: 1, is_active: true, cursus: { id: 4 }, profil: { id: 1 }, expires_at: dans200Jours },
    ])
    afficher("/abonnement?cursus=4&mois=3")

    expect(await screen.findByText(/Ton accès actuel est prolongé jusqu'au/)).toBeInTheDocument()
  })

  it("annonce une date à partir d'aujourd'hui pour un premier achat", async () => {
    afficher("/abonnement?cursus=4&mois=3")

    expect(await screen.findByText(/^Accès jusqu'au/)).toBeInTheDocument()
    expect(screen.queryByText(/Ton accès actuel est prolongé/)).not.toBeInTheDocument()
  })

  it("déduit le crédit parrainage du total, pas du prix d'un mois", async () => {
    auth.user = { phone_number: "677000000", credit_parrainage_disponible: 1000 } as typeof auth.user
    afficher("/abonnement?cursus=4&mois=3")

    expect(await screen.findByRole("button", { name: /Payer 5 000 FCFA/ })).toBeInTheDocument()
  })
})
