import { describe, expect, it } from "vitest"

import type { EpreuveContent, EpreuveExercise } from "@/api/types"
import { EXEMPLES_CORRIGE, exempleDuCursus, extraireExempleCorrige } from "./exempleCorrige"

const exercice = (numero: string, enonce: string, corrige: string): EpreuveExercise => ({
  numero_exercice: numero, titre: "", points: "", groupes: [], enonce_intro_markdown: `**Exercice ${numero}**`,
  enonce_markdown: enonce, corrige_markdown: corrige,
})
const epreuve = (...exercises: EpreuveExercise[]): Pick<EpreuveContent, "exercises"> => ({ exercises })

describe("EXEMPLES_CORRIGE", () => {
  it("chaque langue a sa propre épreuve gratuite", () => {
    expect(EXEMPLES_CORRIGE.fr.slug).toBe("mathematiques-bepc-2026")
    expect(EXEMPLES_CORRIGE.en.slug).toMatch(/gce/)
    expect(EXEMPLES_CORRIGE.en.slug).not.toBe(EXEMPLES_CORRIGE.fr.slug)
  })
})

describe("extraireExempleCorrige", () => {
  const Q2 = "**2.** Seconde question"
  const Q1 = "**1.** Première question"
  const exo = exercice("1", `${Q1}\n\n${Q2}`, `${Q1}\n\nRéponse 1\n\n${Q2}\n\nRéponse 2`)

  it("question 1 seule : coupe le corrigé juste avant l'énoncé de la question 2", () => {
    const extrait = extraireExempleCorrige(epreuve(exo), EXEMPLES_CORRIGE.fr)
    expect(extrait?.exercice).toBe(exo)
    expect(extrait?.corrigeMarkdown).toBe(`${Q1}\n\nRéponse 1`)
  })

  it("question 1 seule : un exercice à une seule question garde son corrigé entier", () => {
    const seul = exercice("1", Q1, `${Q1}\n\nRéponse`)
    expect(extraireExempleCorrige(epreuve(seul), EXEMPLES_CORRIGE.fr)?.corrigeMarkdown).toBe(`${Q1}\n\nRéponse`)
  })

  it("question 1 seule : si l'énoncé 2 ne se retrouve pas dans le corrigé, corrigé entier", () => {
    const decale = exercice("1", `${Q1}\n\n${Q2}`, "Corrigé sans reprise des énoncés")
    expect(extraireExempleCorrige(epreuve(decale), EXEMPLES_CORRIGE.fr)?.corrigeMarkdown).toBe("Corrigé sans reprise des énoncés")
  })

  it("exercice entier : retrouve l'exercice par son numéro et garde tout le corrigé", () => {
    const premier = exercice("1", "x", "corrigé 1")
    const deuxieme = exercice("2", `${Q1}\n\n${Q2}`, `${Q1}\n\nA\n\n${Q2}\n\nB`)
    const extrait = extraireExempleCorrige(epreuve(premier, deuxieme), EXEMPLES_CORRIGE.en)
    expect(extrait?.exercice).toBe(deuxieme)
    expect(extrait?.corrigeMarkdown).toBe(deuxieme.corrige_markdown)
  })

  it("l'exercice demandé est absent, ou l'épreuve n'est pas chargée : null (la section disparaît)", () => {
    expect(extraireExempleCorrige(epreuve(exercice("1", "x", "y")), EXEMPLES_CORRIGE.en)).toBeNull()
    expect(extraireExempleCorrige(undefined, EXEMPLES_CORRIGE.fr)).toBeNull()
    expect(extraireExempleCorrige(epreuve(), EXEMPLES_CORRIGE.fr)).toBeNull()
  })
})

describe("exempleDuCursus", () => {
  const bac = (code: string) => ({ examen: "BAC", series: { code } })

  it("BAC C et D : la mathématique gratuite de leur examen", () => {
    expect(exempleDuCursus("fr", bac("C")).slug).toBe("mathematiques-bac-c-2026")
    expect(exempleDuCursus("fr", bac("D")).slug).toBe("mathematiques-bac-d-2026")
  })

  it("BAC E : la même épreuve que la série C", () => {
    expect(exempleDuCursus("fr", bac("E"))).toBe(exempleDuCursus("fr", bac("C")))
  })

  it("sans épreuve gratuite adaptée (BAC A, Probatoire, BAC TI) ou sans examen déclaré : l'exemple par défaut", () => {
    expect(exempleDuCursus("fr", bac("A"))).toBe(EXEMPLES_CORRIGE.fr)
    expect(exempleDuCursus("fr", { examen: "PROBATOIRE", series: { code: "C" } })).toBe(EXEMPLES_CORRIGE.fr)
    expect(exempleDuCursus("fr", { examen: "BEPC", series: null })).toBe(EXEMPLES_CORRIGE.fr)
    expect(exempleDuCursus("fr", null)).toBe(EXEMPLES_CORRIGE.fr)
    expect(exempleDuCursus("fr", undefined)).toBe(EXEMPLES_CORRIGE.fr)
  })

  it("en anglais, jamais un exemple français, quel que soit l'examen déclaré", () => {
    expect(exempleDuCursus("en", bac("C"))).toBe(EXEMPLES_CORRIGE.en)
  })
})

describe("extraireExempleCorrige : coupe par repère de sous-question", () => {
  const BAC_C = exempleDuCursus("fr", { examen: "BAC", series: { code: "C" } })
  const corrige = "**1.** Première\n\n### Rappel de méthode\nTexte\n\nCalcul 1\n\n**2.** Seconde\n\nCalcul 2\n\n**3.** Troisième"

  it("garde la première sous-question et coupe avant le deuxième repère", () => {
    const exo = exercice("3", "intro\n\nsuite", corrige)
    const extrait = extraireExempleCorrige(epreuve(exo), BAC_C)
    expect(extrait?.corrigeMarkdown).toBe("**1.** Première\n\n### Rappel de méthode\nTexte\n\nCalcul 1")
  })

  it("repères en chiffres romains (« **I.1.** »)", () => {
    const exo = exercice("3", "intro", "**I.1.** A\n\nRéponse\n\n**I.2.** B\n\nRéponse")
    expect(extraireExempleCorrige(epreuve(exo), BAC_C)?.corrigeMarkdown).toBe("**I.1.** A\n\nRéponse")
  })

  it("un seul repère : corrigé entier", () => {
    const exo = exercice("3", "intro", "**1.** A\n\nRéponse")
    expect(extraireExempleCorrige(epreuve(exo), BAC_C)?.corrigeMarkdown).toBe("**1.** A\n\nRéponse")
  })
})
