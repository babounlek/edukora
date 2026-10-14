import { describe, expect, it } from "vitest"

import type { EpreuveContent, EpreuveExercise } from "@/api/types"
import { EXEMPLES_CORRIGE, extraireExempleCorrige } from "./exempleCorrige"

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
