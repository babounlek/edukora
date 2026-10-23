import { useEffect, useState } from "react"
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Link, MemoryRouter, useLocation } from "react-router-dom"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const { auth } = vi.hoisted(() => ({
  auth: {
    current: {
      isAuthenticated: false,
      isLoading: false,
      user: null as null | { id: number; cursus_prepare: { id: number } | null; profil_actif: { id: number } },
    },
  },
}))
vi.mock("@/context/AuthContext", () => ({ useAuth: () => auth.current }))
vi.mock("@/context/CountryContext", () => ({ useCountry: () => ({ country: "cm" }) }))

import { definirModeExamen } from "@/lib/modeExamen"
import { memoriserCursusPrepareEnAttente, oublierCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { definirLangue } from "@/lib/i18n"
import {
  lireEtat, ouvrirCentre, ouvrirGuide, reinitialiserEtat, signalerOnboarding,
} from "@/lib/guides/etat"
import { cleDeLIdentite, lireDonnees, memoriser, reinitialiserStockage } from "@/lib/guides/store"
import { AideContextuelle, BoutonAide } from "./AideContextuelle"
import { GuideHost } from "./GuideHost"

const ELEVE = { id: 7, cursus_prepare: { id: 1 }, profil_actif: { id: 3 } }

/** Une page minimale qui porte les mêmes cibles que l'accueil réel (SeanceDuJour). */
function PageAccueil({ avecSeance = true }: { avecSeance?: boolean }) {
  return (
    <main>
      <h1>Accueil</h1>
      {avecSeance && (
        <>
          <a href="#commencer" data-guide="seance-commencer">Commencer</a>
          <div data-guide="seance-parcours">Ton parcours</div>
          <BoutonAide guide="seance-du-jour" />
          <AideContextuelle guide="seance-du-jour" />
        </>
      )}
      <Link to="/cm/cours">Aller aux cours</Link>
      <button type="button">Un bouton de la page</button>
    </main>
  )
}

/** Une page dont la séance du jour n'arrive qu'après le premier rendu, comme l'accueil réel. */
const chargement = { arrive: () => {} }
function PageQuiCharge() {
  const [pret, setPret] = useState(false)
  useEffect(() => {
    chargement.arrive = () => setPret(true)
  }, [])
  return pret ? <a href="#commencer" data-guide="seance-commencer">Commencer</a> : null
}

function Chemin() {
  return <span data-testid="chemin">{useLocation().pathname}</span>
}

function monter(chemin = "/cm", options: { avecSeance?: boolean } = {}) {
  return render(
    <MemoryRouter initialEntries={[chemin]}>
      <PageAccueil avecSeance={options.avecSeance} />
      <Chemin />
      <GuideHost />
    </MemoryRouter>,
  )
}

const carte = () => screen.queryByRole("dialog", { name: /.+/ })

beforeEach(async () => {
  localStorage.clear()
  reinitialiserStockage()
  reinitialiserEtat()
  oublierCursusPrepareEnAttente()
  definirModeExamen(false)
  await definirLangue("fr", { persister: false })
  auth.current = { isAuthenticated: true, isLoading: false, user: ELEVE }
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe("tutoriel de bienvenue (élève)", () => {
  it("s'affiche à la première visite de l'accueil, sans bloquer la page", async () => {
    monter()
    expect(await screen.findByText("Bienvenue sur EduKora")).toBeInTheDocument()
    expect(screen.getByText("Étape 1 sur 3")).toBeInTheDocument()
    // Non modal : la page derrière reste utilisable et lisible pour les lecteurs d'écran.
    expect(carte()).toHaveAttribute("aria-modal", "false")
    fireEvent.click(screen.getByRole("button", { name: "Un bouton de la page" }))
    expect(screen.getByText("Bienvenue sur EduKora")).toBeInTheDocument()
  })

  it("avance et recule d'étape, et met la cible en évidence", async () => {
    monter()
    await screen.findByText("Bienvenue sur EduKora")
    fireEvent.click(screen.getByRole("button", { name: "Suivant" }))
    expect(screen.getByText("Ta séance du jour")).toBeInTheDocument()
    expect(screen.getByText("Étape 2 sur 3")).toBeInTheDocument()
    expect(document.querySelector('[data-guide="seance-commencer"]')).toHaveAttribute("data-guide-actif", "true")

    fireEvent.click(screen.getByRole("button", { name: "Suivant" }))
    expect(screen.getByText("Trois étapes, dans l'ordre")).toBeInTheDocument()
    expect(document.querySelector('[data-guide="seance-commencer"]')).not.toHaveAttribute("data-guide-actif")
    expect(document.querySelector('[data-guide="seance-parcours"]')).toHaveAttribute("data-guide-actif", "true")

    fireEvent.click(screen.getByRole("button", { name: "Précédent" }))
    expect(screen.getByText("Ta séance du jour")).toBeInTheDocument()
  })

  it("terminé jusqu'au bout : mémorisé, et ne revient pas à la visite suivante", async () => {
    const { unmount } = monter()
    await screen.findByText("Bienvenue sur EduKora")
    fireEvent.click(screen.getByRole("button", { name: "Suivant" }))
    fireEvent.click(screen.getByRole("button", { name: "Suivant" }))
    fireEvent.click(screen.getByRole("button", { name: "Terminer" }))
    expect(carte()).toBeNull()
    expect(lireDonnees("7:3").guides.bienvenue).toMatchObject({ statut: "termine", version: 1 })
    // Les marques de mise en évidence ne traînent pas.
    expect(document.querySelector("[data-guide-actif]")).toBeNull()

    unmount()
    reinitialiserEtat() // une nouvelle visite : la page se recharge
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
  })

  it("« Passer » à n'importe quelle étape l'écarte, sans le compter comme un échec", async () => {
    const { unmount } = monter()
    await screen.findByText("Bienvenue sur EduKora")
    fireEvent.click(screen.getByRole("button", { name: "Suivant" }))
    fireEvent.click(screen.getByRole("button", { name: "Passer" }))
    expect(carte()).toBeNull()
    expect(lireDonnees("7:3").guides.bienvenue.statut).toBe("ignore")

    unmount()
    reinitialiserEtat()
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
  })

  it("se parcourt entièrement au clavier", async () => {
    const utilisateur = userEvent.setup()
    memoriser("7:3", "bienvenue", 1, "termine")
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    act(() => ouvrirGuide("bienvenue", { explicite: true }))
    const dialogue = await screen.findByRole("dialog", { name: "Bienvenue sur EduKora" })
    expect(dialogue).toHaveFocus()
    await utilisateur.tab()
    expect(screen.getByRole("button", { name: "Passer" })).toHaveFocus()
    await utilisateur.tab()
    expect(screen.getByRole("button", { name: "Suivant" })).toHaveFocus()
    await utilisateur.keyboard("{Enter}")
    expect(screen.getByText("Étape 2 sur 3")).toBeInTheDocument()
  })

  it("une cible masquée compte comme absente : son étape est sautée", async () => {
    const { container } = monter()
    await screen.findByText("Bienvenue sur EduKora")
    const cible = container.querySelector<HTMLElement>('[data-guide="seance-parcours"]')!
    // Cible masquée : l'élève ne la voit pas, le guide ne doit pas la désigner.
    cible.style.display = "none"
    fireEvent.click(screen.getByRole("button", { name: "Suivant" }))
    expect(screen.getByText("Ta séance du jour")).toBeInTheDocument()
    expect(screen.getByText("Étape 2 sur 2")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Terminer" })).toBeInTheDocument()
  })

  it("Échap le ferme", async () => {
    monter()
    await screen.findByText("Bienvenue sur EduKora")
    fireEvent.keyDown(document, { key: "Escape" })
    expect(carte()).toBeNull()
    expect(lireDonnees("7:3").guides.bienvenue.statut).toBe("ignore")
  })

  it("reste proposable après une version majeure plus récente", async () => {
    memoriser("7:3", "bienvenue", 0, "termine") // l'élève avait vu une ancienne version
    monter()
    expect(await screen.findByText("Bienvenue sur EduKora")).toBeInTheDocument()
  })

  it("saute l'étape de la séance quand son bouton n'est pas à l'écran, sans bulle posée au hasard", async () => {
    // Le bouton de séance arrive avec les données : au départ, rien ne l'attend à l'écran.
    monter("/cm", { avecSeance: false })
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
  })

  it("attend que la séance du jour soit arrivée à l'écran, puis se lance", async () => {
    render(
      <MemoryRouter initialEntries={["/cm"]}>
        <PageQuiCharge />
        <GuideHost />
      </MemoryRouter>,
    )
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
    await act(async () => {
      chargement.arrive()
    })
    expect(await screen.findByText("Bienvenue sur EduKora")).toBeInTheDocument()
  })
})

describe("tutoriel du visiteur", () => {
  beforeEach(() => {
    auth.current = { isAuthenticated: false, isLoading: false, user: null }
  })

  it("version courte, sans séance du jour, pour un visiteur qui a déclaré son examen", async () => {
    memoriserCursusPrepareEnAttente(4)
    monter()
    expect(await screen.findByText("Bienvenue sur EduKora")).toBeInTheDocument()
    expect(screen.getByText("Étape 1 sur 2")).toBeInTheDocument()
    fireEvent.click(screen.getByRole("button", { name: "Suivant" }))
    expect(screen.getByText("Ta séance du jour t'attend")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Me connecter" })).toHaveAttribute("href", "/connexion")
    expect(screen.queryByText("Trois étapes, dans l'ordre")).toBeNull()
  })

  it("rien pour un visiteur qui n'a pas encore choisi son examen", async () => {
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("anonyme"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
  })

  it("ce que le visiteur a fermé n'est pas remontré une fois connecté", async () => {
    memoriserCursusPrepareEnAttente(4)
    const { unmount } = monter()
    await screen.findByText("Bienvenue sur EduKora")
    fireEvent.click(screen.getByRole("button", { name: "Passer" }))
    expect(lireDonnees("anonyme").guides["bienvenue-visiteur"]).toBeDefined()

    unmount()
    reinitialiserEtat()
    auth.current = { isAuthenticated: true, isLoading: false, user: ELEVE }
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    // Reporté sur le compte...
    expect(lireDonnees("7:3").guides["bienvenue-visiteur"]).toMatchObject({ statut: "ignore" })
  })
})

describe("mémoire par compte et par profil", () => {
  it("le tutoriel déjà vu par un enfant se montre encore au profil d'un autre", async () => {
    memoriser("7:3", "bienvenue", 1, "termine")
    const { unmount } = monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()

    unmount()
    reinitialiserEtat()
    auth.current = { ...auth.current, user: { ...ELEVE, profil_actif: { id: 4 } } }
    monter()
    expect(await screen.findByText("Bienvenue sur EduKora")).toBeInTheDocument()
  })

  it("rien ne se montre ni ne s'écrit tant que la session n'est pas lue", async () => {
    auth.current = { isAuthenticated: false, isLoading: true, user: null }
    memoriserCursusPrepareEnAttente(4)
    monter()
    await act(async () => {})
    expect(lireEtat().identite).toBeNull()
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
  })
})

describe("non-interférence", () => {
  it.each([
    "/quiz/session/12",
    "/quiz/essai",
    "/abonnement",
    "/mes-paiements",
    "/connexion",
    "/inedit/tentative/3",
    "/simulation/2",
  ])("aucune aide automatique sur %s", async (chemin) => {
    monter(chemin)
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    await act(async () => {})
    expect(carte()).toBeNull()
    expect(lireEtat().ouvert).toBeNull()
  })

  it("rien par-dessus l'écran de choix de l'examen, puis le tutoriel arrive quand il se ferme", async () => {
    act(() => signalerOnboarding(true))
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
    act(() => signalerOnboarding(false))
    expect(await screen.findByText("Bienvenue sur EduKora")).toBeInTheDocument()
  })

  it("rien en salle d'examen", async () => {
    definirModeExamen(true)
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
  })

  it("rien par-dessus une fenêtre déjà ouverte (code PIN, menu...)", async () => {
    const fenetre = document.createElement("div")
    fenetre.setAttribute("role", "dialog")
    fenetre.setAttribute("data-state", "open")
    document.body.appendChild(fenetre)
    try {
      monter()
      await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
      expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
    } finally {
      fenetre.remove()
    }
  })

  it("respecte le choix de ne plus recevoir de conseils", async () => {
    localStorage.setItem(
      cleDeLIdentite("7:3"),
      JSON.stringify({ v: 1, guides: {}, prefs: { aidesAuto: false } }),
    )
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByText("Bienvenue sur EduKora")).toBeNull()
  })

  it("une erreur de stockage ne casse ni l'affichage ni la fermeture", async () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("quota", "QuotaExceededError")
    })
    monter()
    await screen.findByText("Bienvenue sur EduKora")
    expect(() => fireEvent.click(screen.getByRole("button", { name: "Passer" }))).not.toThrow()
    expect(carte()).toBeNull()
  })
})

describe("changement de page", () => {
  it("quitter l'accueil ferme le tutoriel et l'écarte, sans le répéter à chaque navigation", async () => {
    const utilisateur = userEvent.setup()
    monter()
    await screen.findByText("Bienvenue sur EduKora")
    await utilisateur.click(screen.getByRole("link", { name: "Aller aux cours" }))
    await waitFor(() => expect(screen.getByTestId("chemin")).toHaveTextContent("/cm/cours"))
    expect(carte()).toBeNull()
    expect(lireDonnees("7:3").guides.bienvenue.statut).toBe("ignore")
  })
})

describe("relance manuelle et centre d'aide", () => {
  it("rouvre un guide déjà vu à la demande, au clavier, et rend le focus en fermant", async () => {
    memoriser("7:3", "bienvenue", 1, "termine")
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    const bouton = screen.getByRole("button", { name: "Un bouton de la page" })
    bouton.focus()
    act(() => ouvrirGuide("bienvenue", { explicite: true }))
    const dialogue = await screen.findByRole("dialog", { name: "Bienvenue sur EduKora" })
    // Une demande explicite met le focus dans la carte (clavier, lecteur d'écran).
    expect(dialogue).toHaveFocus()
    fireEvent.keyDown(document, { key: "Escape" })
    expect(carte()).toBeNull()
    expect(bouton).toHaveFocus()
    // Fermer un guide relancé à la main ne change pas ce qu'il avait déjà terminé.
    expect(lireDonnees("7:3").guides.bienvenue.statut).toBe("termine")
  })

  it("le centre d'aide liste les guides, leurs explications, et relance sans repasser par la bienvenue", async () => {
    memoriser("7:3", "bienvenue", 1, "termine")
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    act(() => ouvrirCentre())
    const panneau = await screen.findByRole("dialog", { name: /Aide/ })
    expect(panneau).toHaveTextContent("Découvrir EduKora")
    expect(panneau).toHaveTextContent("Comment marche ta séance ?")
    expect(panneau).toHaveTextContent("Déjà vu")
    // Les explications se lisent sans rien relancer.
    expect(panneau).toHaveTextContent("Comprendre le cours, t'entraîner sur un exercice")

    const relancer = screen.getAllByRole("button", { name: "Relancer le guide" })[0]
    fireEvent.click(relancer)
    expect(await screen.findByText("Étape 1 sur 3")).toBeInTheDocument()
    expect(lireEtat().centreOuvert).toBe(false)
  })

  it("relancer depuis une autre page ramène à l'accueil et y garde le guide ouvert", async () => {
    memoriser("7:3", "bienvenue", 1, "termine")
    const { unmount } = render(
      <MemoryRouter initialEntries={["/compte"]}>
        <PageAccueil />
        <Chemin />
        <GuideHost />
      </MemoryRouter>,
    )
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    act(() => ouvrirCentre())
    await screen.findByRole("dialog", { name: /Aide/ })
    fireEvent.click(screen.getAllByRole("button", { name: "Relancer le guide" })[0])
    await waitFor(() => expect(screen.getByTestId("chemin")).toHaveTextContent("/cm"))
    expect(await screen.findByText("Étape 1 sur 3")).toBeInTheDocument()
    unmount()
  })

  it("désactiver les conseils automatiques est mémorisé, localement", async () => {
    monter()
    await screen.findByText("Bienvenue sur EduKora")
    fireEvent.click(screen.getByRole("button", { name: "Passer" }))
    act(() => ouvrirCentre())
    const case_ = await screen.findByRole("checkbox", { name: /Afficher les conseils automatiquement/ })
    expect(case_).toBeChecked()
    fireEvent.click(case_)
    expect(lireDonnees("7:3").prefs.aidesAuto).toBe(false)
    expect(screen.getByText("Ces réglages restent sur cet appareil.")).toBeInTheDocument()
  })

  it("un visiteur n'a pas l'aide de la séance du jour dans son centre d'aide", async () => {
    auth.current = { isAuthenticated: false, isLoading: false, user: null }
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("anonyme"))
    act(() => ouvrirCentre())
    const panneau = await screen.findByRole("dialog", { name: /Aide/ })
    expect(panneau).toHaveTextContent("Découvrir EduKora")
    expect(panneau).not.toHaveTextContent("Comment marche ta séance ?")
  })

  it("parle anglais quand l'interface est en anglais", async () => {
    await definirLangue("en", { persister: false })
    monter()
    expect(await screen.findByText("Welcome to EduKora")).toBeInTheDocument()
    expect(screen.getByText("Step 1 of 3")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Skip" })).toBeInTheDocument()
  })
})

describe("aide contextuelle de la séance", () => {
  beforeEach(() => {
    memoriser("7:3", "bienvenue", 1, "termine")
  })

  it("se montre seule la première fois, se ferme, et se rouvre par son « ? »", async () => {
    monter()
    const titre = await screen.findByRole("heading", { name: "Comment marche ta séance ?" })
    expect(titre).toBeInTheDocument()
    expect(screen.queryByRole("button", { name: "Revoir cette aide" })).toBeNull()

    fireEvent.click(screen.getByRole("button", { name: "J'ai compris" }))
    expect(screen.queryByRole("heading", { name: "Comment marche ta séance ?" })).toBeNull()
    expect(lireDonnees("7:3").guides["seance-du-jour"].statut).toBe("termine")

    fireEvent.click(screen.getByRole("button", { name: "Revoir cette aide" }))
    expect(await screen.findByRole("heading", { name: "Comment marche ta séance ?" })).toBeInTheDocument()
  })

  it("cède la place au tutoriel de bienvenue : jamais deux aides en même temps", async () => {
    localStorage.clear()
    reinitialiserStockage()
    reinitialiserEtat()
    monter()
    await screen.findByText("Bienvenue sur EduKora")
    expect(screen.queryByRole("heading", { name: "Comment marche ta séance ?" })).toBeNull()
    // ...et pas non plus juste après : une seule aide automatique par visite.
    fireEvent.click(screen.getByRole("button", { name: "Passer" }))
    await act(async () => {})
    expect(screen.queryByRole("heading", { name: "Comment marche ta séance ?" })).toBeNull()
  })

  it("ne revient pas à la visite suivante une fois comprise", async () => {
    const { unmount } = monter()
    await screen.findByRole("heading", { name: "Comment marche ta séance ?" })
    fireEvent.click(screen.getByRole("button", { name: "J'ai compris" }))
    unmount()
    reinitialiserEtat()
    monter()
    await waitFor(() => expect(lireEtat().identite).toBe("7:3"))
    expect(screen.queryByRole("heading", { name: "Comment marche ta séance ?" })).toBeNull()
  })
})
