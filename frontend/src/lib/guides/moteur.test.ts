import { describe, expect, it } from "vitest"

import { GUIDES, trouverGuide } from "./contenu"
import { etapesEffectives, guideAutomatique, peutDeclencherAuto, routeAutoPermise, type SituationAuto } from "./moteur"
import type { ContexteGuide, DonneesGuides } from "./types"

const memoireVide = (): DonneesGuides => ({ v: 1, guides: {}, prefs: { aidesAuto: true } })

const contexteEleve = (surcharges: Partial<ContexteGuide> = {}): ContexteGuide => ({
  pathname: "/cm",
  public: "eleve",
  onboardingOuvert: false,
  enExamen: false,
  dialogueOuvert: false,
  ciblePresente: () => true,
  ...surcharges,
})

const situation = (surcharges: Partial<SituationAuto> = {}): SituationAuto => ({
  memoire: memoireVide(),
  guideOuvert: false,
  autoDejaMontre: false,
  ...surcharges,
})

const bienvenue = trouverGuide("bienvenue")!
const bienvenueVisiteur = trouverGuide("bienvenue-visiteur")!
const aideSeance = trouverGuide("seance-du-jour")!

describe("définitions des guides", () => {
  it("chaque guide a un identifiant stable et unique, une version et au moins une étape", () => {
    const ids = GUIDES.map((guide) => guide.id)
    expect(new Set(ids).size).toBe(ids.length)
    for (const guide of GUIDES) {
      expect(guide.version).toBeGreaterThanOrEqual(1)
      expect(guide.etapes.length).toBeGreaterThan(0)
    }
  })

  it("le tutoriel de bienvenue tient en trois étapes au plus, pour l'élève comme pour le visiteur", () => {
    expect(bienvenue.etapes.length).toBeLessThanOrEqual(3)
    expect(bienvenueVisiteur.etapes.length).toBeLessThanOrEqual(3)
  })

  it("le visiteur n'a aucune étape sur la séance du jour, qu'il ne voit pas", () => {
    for (const etape of bienvenueVisiteur.etapes) {
      expect(etape.cible).toBeUndefined()
    }
  })
})

describe("routeAutoPermise", () => {
  it.each([
    "/quiz/session/12",
    "/quiz/essai",
    "/quiz/essai/resultat",
    "/historique/quiz/4",
    "/inedit/tentative/3",
    "/simulation/9",
    "/abonnement",
    "/mes-paiements",
    "/connexion",
  ])("%s : aucune aide ne s'impose", (chemin) => {
    expect(routeAutoPermise(chemin)).toBe(false)
  })

  it.each(["/quiz", "/cm", "/cm/cours", "/parcours", "/compte", "/tarifs"])("%s : permise", (chemin) => {
    expect(routeAutoPermise(chemin)).toBe(true)
  })
})

describe("etapesEffectives", () => {
  it("saute une étape dont la cible obligatoire manque", () => {
    const sansSeance = etapesEffectives(bienvenue, (cible) => cible !== "seance-commencer")
    expect(sansSeance.map((e) => e.id)).toEqual(["interet", "etapes"])
  })

  it("garde sans mise en évidence une étape dont la cible n'est pas obligatoire", () => {
    const sansCible = etapesEffectives(aideSeance, () => false)
    expect(sansCible.map((e) => e.id)).toEqual(["fonctionnement"])
  })

  it("tout est présent : toutes les étapes", () => {
    expect(etapesEffectives(bienvenue, () => true)).toHaveLength(3)
  })
})

describe("peutDeclencherAuto", () => {
  it("le tutoriel de l'élève se lance sur l'accueil, la première fois", () => {
    expect(peutDeclencherAuto(bienvenue, contexteEleve(), situation())).toBe(true)
  })

  it("le tutoriel du visiteur se lance pour un visiteur, pas pour un élève", () => {
    expect(peutDeclencherAuto(bienvenueVisiteur, contexteEleve({ public: "visiteur" }), situation())).toBe(true)
    expect(peutDeclencherAuto(bienvenueVisiteur, contexteEleve({ public: "eleve" }), situation())).toBe(false)
    expect(peutDeclencherAuto(bienvenue, contexteEleve({ public: "visiteur" }), situation())).toBe(false)
  })

  it("rien tant qu'on ne sait pas qui regarde", () => {
    expect(peutDeclencherAuto(bienvenue, contexteEleve({ public: null }), situation())).toBe(false)
  })

  it("rien hors de la page du guide", () => {
    expect(peutDeclencherAuto(bienvenue, contexteEleve({ pathname: "/cm/cours" }), situation())).toBe(false)
  })

  it.each(["/quiz/session/3", "/abonnement", "/mes-paiements", "/connexion", "/inedit/tentative/5"])(
    "jamais sur %s",
    (chemin) => {
      const ailleurs = contexteEleve({ pathname: chemin })
      for (const guide of GUIDES) expect(peutDeclencherAuto(guide, ailleurs, situation())).toBe(false)
    },
  )

  it("rien pendant l'écran de choix de l'examen, la salle d'examen ou une fenêtre ouverte", () => {
    expect(peutDeclencherAuto(bienvenue, contexteEleve({ onboardingOuvert: true }), situation())).toBe(false)
    expect(peutDeclencherAuto(bienvenue, contexteEleve({ enExamen: true }), situation())).toBe(false)
    expect(peutDeclencherAuto(bienvenue, contexteEleve({ dialogueOuvert: true }), situation())).toBe(false)
  })

  it("jamais par-dessus un guide déjà ouvert", () => {
    expect(peutDeclencherAuto(bienvenue, contexteEleve(), situation({ guideOuvert: true }))).toBe(false)
  })

  it("une seule aide automatique par visite", () => {
    expect(peutDeclencherAuto(bienvenue, contexteEleve(), situation({ autoDejaMontre: true }))).toBe(false)
  })

  it("pas de répétition une fois terminé ou écarté", () => {
    for (const statut of ["termine", "ignore"] as const) {
      const memoire = memoireVide()
      memoire.guides.bienvenue = { version: bienvenue.version, statut, date: 1 }
      expect(peutDeclencherAuto(bienvenue, contexteEleve(), situation({ memoire }))).toBe(false)
    }
  })

  it("une version plus récente que celle vue est reproposée", () => {
    const memoire = memoireVide()
    memoire.guides.bienvenue = { version: bienvenue.version - 1, statut: "termine", date: 1 }
    expect(peutDeclencherAuto(bienvenue, contexteEleve(), situation({ memoire }))).toBe(true)
  })

  it("respecte le choix de ne plus recevoir de conseils", () => {
    const memoire = memoireVide()
    memoire.prefs.aidesAuto = false
    expect(peutDeclencherAuto(bienvenue, contexteEleve(), situation({ memoire }))).toBe(false)
  })

  it("le tutoriel de l'élève attend que le bouton de séance soit à l'écran", () => {
    expect(peutDeclencherAuto(bienvenue, contexteEleve({ ciblePresente: () => false }), situation())).toBe(false)
  })

  it("l'aide de la séance cède la place au tutoriel de bienvenue encore à faire", () => {
    expect(peutDeclencherAuto(aideSeance, contexteEleve(), situation())).toBe(false)
  })

  it("l'aide de la séance se montre une fois la bienvenue vue", () => {
    const memoire = memoireVide()
    memoire.guides.bienvenue = { version: bienvenue.version, statut: "ignore", date: 1 }
    expect(peutDeclencherAuto(aideSeance, contexteEleve(), situation({ memoire }))).toBe(true)
  })
})

describe("aides de page (cours, exercice, quiz)", () => {
  const vu = (...ids: string[]) => {
    const memoire = memoireVide()
    for (const id of ids) memoire.guides[id] = { version: 1, statut: "termine", date: 1 }
    return memoire
  }
  const bienvenueVue = vu("bienvenue")

  it.each([
    ["cours", "/cours/limites-de-fonctions/lire", true],
    ["cours", "/cours/limites-de-fonctions", false],
    ["exercice", "/cm/themes-frequents/12/exercices/40", true],
    ["exercice", "/cm/themes-frequents/12/exercices", false],
    ["quiz-depart", "/quiz", true],
    ["quiz-depart", "/quiz/session/3", false],
    ["examen-matieres", "/mes-acces", true],
    ["examen-matieres", "/compte", false],
    ["annales", "/cm/epreuves", true],
    ["annales", "/cm/epreuves/bac-2020", false],
    ["inedites", "/cm/epreuves-inedites/12", true],
    ["inedites", "/cm/epreuves-inedites", false],
    ["progression", "/parcours", true],
    ["progression", "/parcours/4", false],
  ])("%s sur %s : route reconnue = %s", (id, chemin, attendu) => {
    expect(trouverGuide(id)!.route(chemin)).toBe(attendu)
  })

  it("chaque aide se lance seule sur sa page une fois la bienvenue vue", () => {
    const pages: Record<string, string> = {
      cours: "/cours/limites/lire",
      exercice: "/cm/themes-frequents/1/exercices/2",
      "quiz-depart": "/quiz",
      "examen-matieres": "/mes-acces",
      annales: "/cm/epreuves",
      inedites: "/cm/epreuves-inedites/3",
      progression: "/parcours",
    }
    for (const [id, pathname] of Object.entries(pages)) {
      expect(peutDeclencherAuto(trouverGuide(id)!, contexteEleve({ pathname }), situation({ memoire: bienvenueVue }))).toBe(true)
    }
  })

  it("l'aide du quiz attend la carte de réglage (réservée aux abonnés)", () => {
    const sansCarte = contexteEleve({ pathname: "/quiz", ciblePresente: () => false })
    expect(peutDeclencherAuto(trouverGuide("quiz-depart")!, sansCarte, situation({ memoire: bienvenueVue }))).toBe(false)
  })

  it("jamais deux aides dans la même visite", () => {
    const cours = trouverGuide("cours")!
    expect(
      peutDeclencherAuto(cours, contexteEleve({ pathname: "/cours/x/lire" }), situation({ memoire: bienvenueVue, autoDejaMontre: true })),
    ).toBe(false)
  })

  it("seules les aides liées à un contenu n'ont pas de chemin de relance", () => {
    expect(trouverGuide("cours")!.cheminRelance).toBeUndefined()
    expect(trouverGuide("exercice")!.cheminRelance).toBeUndefined()
    expect(trouverGuide("quiz-depart")!.cheminRelance).toBe("/quiz")
  })
})

describe("guideAutomatique", () => {
  it("choisit le tutoriel qui correspond à qui regarde", () => {
    expect(guideAutomatique(contexteEleve(), situation())?.id).toBe("bienvenue")
    expect(guideAutomatique(contexteEleve({ public: "visiteur" }), situation())?.id).toBe("bienvenue-visiteur")
  })

  it("aucun quand rien n'est permis", () => {
    expect(guideAutomatique(contexteEleve({ pathname: "/quiz/session/1" }), situation())).toBeNull()
  })
})
