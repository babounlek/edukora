import { beforeEach, describe, expect, it } from "vitest"

import type { ResultatRecherche } from "@/api/types"
import {
  actionsTheme,
  cibleResultat,
  decouperSurbrillance,
  jetonsDeSurbrillance,
  lireRecentes,
  memoriserRecente,
  oublierRecentes,
  plier,
} from "./recherche"

function resultat(surcharge: Partial<ResultatRecherche>): ResultatRecherche {
  return {
    id: 1,
    type: "COURS",
    titre: "Un titre",
    apercu: "",
    annee: null,
    matiere: { code: "MATHS", label: "Mathématiques" },
    cursus: [],
    cursus_total: 0,
    tous_cursus: false,
    cursus_cible: null,
    acces: "verrouille",
    nb: null,
    details: {},
    ...surcharge,
  }
}

describe("plier", () => {
  it("retire accents et casse sans changer la longueur", () => {
    expect(plier("Théorème de Thalès")).toBe("theoreme de thales")
    for (const texte of ["Théorème", "œuvre", "x² + ℂ", "Ça va ?"]) {
      expect(plier(texte)).toHaveLength([...texte].length)
    }
  })
})

describe("jetonsDeSurbrillance", () => {
  it("normalise, singularise et écarte mots vides et jetons courts", () => {
    // « thales » -> « thale » : la racine sert de DÉBUT de mot (« thale » surligne « Thalès »), exactement
    // comme côté serveur (recherche.texte.racine) - c'est ce qui fait trouver le singulier comme le pluriel.
    expect(jetonsDeSurbrillance("théorème de Thalès")).toEqual(["theoreme", "thale"])
    expect(jetonsDeSurbrillance("les équations du second degré")).toEqual(["equation", "second", "degre"])
    expect(jetonsDeSurbrillance("d")).toEqual([])
    expect(jetonsDeSurbrillance("l'équation d'une droite")).toEqual(["equation", "droite"])
  })

  it("laisse « maths » tel quel et ne singularise pas un nombre", () => {
    expect(jetonsDeSurbrillance("maths 2019")).toEqual(["maths", "2019"])
  })

  it("ne garde aucun doublon", () => {
    expect(jetonsDeSurbrillance("limite limites")).toEqual(["limite"])
  })
})

describe("decouperSurbrillance", () => {
  const recoller = (morceaux: { texte: string }[]) => morceaux.map((m) => m.texte).join("")

  it("surligne les mots sans tenir compte des accents ni de la casse", () => {
    const morceaux = decouperSurbrillance("Le théorème de Thalès relie les longueurs", ["theoreme", "thales"])
    expect(morceaux.filter((m) => m.surligne).map((m) => m.texte)).toEqual(["théorème", "Thalès"])
  })

  it("surligne le mot entier quand le mot cherché n'en est que le début", () => {
    const morceaux = decouperSurbrillance("Thalès et Pythagore", ["thal"])
    expect(morceaux.filter((m) => m.surligne).map((m) => m.texte)).toEqual(["Thalès"])
  })

  it("ne surligne pas un jeton trouvé au milieu d'un mot", () => {
    const morceaux = decouperSurbrillance("Pythagore", ["thag"])
    expect(morceaux.some((m) => m.surligne)).toBe(false)
  })

  it("ne perd ni n'ajoute aucun caractère", () => {
    const texte = "Soit f(x) = ln x ; calculer la limite en +∞ de « f » — Thalès !"
    expect(recoller(decouperSurbrillance(texte, ["limite", "thales", "calculer"]))).toBe(texte)
  })

  it("sans jeton, renvoie le texte tel quel", () => {
    expect(decouperSurbrillance("rien", [])).toEqual([{ texte: "rien", surligne: false }])
    expect(decouperSurbrillance("", ["x"])).toEqual([{ texte: "", surligne: false }])
  })
})

describe("cibleResultat", () => {
  it("mène chaque type vers sa page", () => {
    expect(cibleResultat("cm", resultat({ type: "COURS", details: { slug: "thales" } }))).toBe("/cours/thales")
    expect(cibleResultat("cm", resultat({ type: "EPREUVE", details: { slug: "maths-bac-c-2019" } }))).toBe(
      "/cm/epreuves/maths-bac-c-2019",
    )
    expect(cibleResultat("cm", resultat({ type: "INEDITE", details: { slug: "maths-inedite-1", id: 4 } }))).toBe(
      "/cm/epreuves-inedites/maths-inedite-1",
    )
  })

  it("replie une inédite sans slug sur son id", () => {
    expect(cibleResultat("cm", resultat({ type: "INEDITE", details: { id: 4 } }))).toBe("/cm/epreuves-inedites/4")
  })

  it("pose un exercice sur son ancre, dans le lecteur seulement si l'accès est ouvert", () => {
    const exercice = (acces: ResultatRecherche["acces"]) =>
      resultat({ type: "EXERCICE", acces, details: { slug: "maths-2019", ancre: "exercice-3" } })
    expect(cibleResultat("cm", exercice("verrouille"))).toBe("/cm/epreuves/maths-2019#exercice-3")
    expect(cibleResultat("cm", exercice("ouvert"))).toBe("/cm/epreuves/maths-2019/lire#exercice-3")
    expect(cibleResultat("cm", exercice("libre"))).toBe("/cm/epreuves/maths-2019/lire#exercice-3")
  })

  it("mène une question de quiz au quiz du thème, dans le cursus de l'élève", () => {
    const quiz = resultat({ type: "QUIZ", cursus_cible: 5, details: { tag_id: 9 } })
    expect(cibleResultat("cm", quiz)).toBe("/quiz?cursus=5&theme=9")
    expect(cibleResultat("cm", resultat({ type: "QUIZ", details: { tag_id: 9 } }))).toBe("/quiz?theme=9")
  })
})

describe("actionsTheme", () => {
  const theme = (details: ResultatRecherche["details"], cursus_cible: number | null = 5) =>
    resultat({ type: "THEME", cursus_cible, details: { tag_id: 7, subject_code: "MATHS", ...details } })

  it("propose cours, exercices et quiz selon ce que le thème contient", () => {
    const actions = actionsTheme("cm", theme({ nb_cours: 2, nb_exercices: 1, nb_quiz: 12 }))
    expect(actions.map((a) => [a.cle, a.libelle])).toEqual([
      ["cours", "2 cours"],
      ["exercices", "1 exercice"],
      ["quiz", "Quiz · 12 questions"],
    ])
    expect(actions[0].to).toBe("/cm/cours?theme=7&subject=MATHS&cursus=5")
    expect(actions[1].to).toBe("/cm/themes-frequents/7/exercices?subject=MATHS&cursus=5")
    expect(actions[2].to).toBe("/quiz?cursus=5&theme=7")
  })

  it("n'invente pas la page des exercices sans cursus connu", () => {
    const actions = actionsTheme("cm", theme({ nb_cours: 1, nb_exercices: 3 }, null))
    expect(actions.map((a) => a.cle)).toEqual(["cours"])
    expect(actions[0].to).toBe("/cm/cours?theme=7&subject=MATHS")
  })

  it("un thème sans identifiant n'a aucune action", () => {
    expect(actionsTheme("cm", resultat({ type: "THEME", details: {} }))).toEqual([])
  })

  it("mène un thème à sa première ressource", () => {
    expect(cibleResultat("cm", theme({ nb_quiz: 3 }))).toBe("/quiz?cursus=5&theme=7")
    expect(cibleResultat("cm", theme({ nb_cours: 1, nb_quiz: 3 }))).toBe("/cm/cours?theme=7&subject=MATHS&cursus=5")
  })
})

describe("recherches récentes", () => {
  beforeEach(() => localStorage.clear())

  it("garde les cinq dernières, la plus récente d'abord, sans doublon", () => {
    for (const requete of ["a1", "thales", "discriminant", "mendel", "limites", "suites", "Thalès"]) {
      memoriserRecente(requete)
    }
    expect(lireRecentes()).toEqual(["Thalès", "suites", "limites", "mendel", "discriminant"])
  })

  it("ignore une saisie trop courte", () => {
    memoriserRecente(" a ")
    expect(lireRecentes()).toEqual([])
  })

  it("oublie tout, et supporte un stockage corrompu", () => {
    memoriserRecente("thales")
    oublierRecentes()
    expect(lireRecentes()).toEqual([])
    localStorage.setItem("edukamer_recherches_recentes", "pas du json")
    expect(lireRecentes()).toEqual([])
  })
})
