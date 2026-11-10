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
  it("sans exemple (cursus sans épreuve gratuite) : null", () => {
    expect(extraireExempleCorrige(epreuve(exercice("1", "x", "y")), null)).toBeNull()
  })

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
  const probatoire = (code: string) => ({ examen: "PROBATOIRE", series: { code } })
  const slug = (langue: "fr" | "en", cursus: Parameters<typeof exempleDuCursus>[1]) => exempleDuCursus(langue, cursus)?.slug

  // Rattachement vérifié en base le 2026-11-08 (Lesson.est_vitrine, Lesson.cursus) : chaque épreuve est gratuite, validée, et
  // rattachée au cursus pour lequel elle est montrée. Un changement ici doit être recontrôlé de même.
  it("chaque cursus francophone a SA propre épreuve gratuite", () => {
    expect(slug("fr", { examen: "BEPC", series: null })).toBe("mathematiques-bepc-2026")
    expect(slug("fr", bac("C"))).toBe("mathematiques-bac-c-2026")
    expect(slug("fr", bac("D"))).toBe("mathematiques-bac-d-2026")
    expect(slug("fr", bac("A"))).toBe("mathematiques-bac-a-2026-blanc-2")
    expect(slug("fr", bac("A1"))).toBe("mathematiques-bac-a1-2015")
    expect(slug("fr", probatoire("D"))).toBe("mathematiques-probatoire-d-2025")
    expect(slug("fr", probatoire("A"))).toBe("mathematiques-probatoire-a")
    expect(slug("fr", probatoire("TI"))).toBe("systemes-dinformation-probatoire-ti-2023")
  })

  it("BAC E : l'épreuve commune C et E (celle de la série C n'est pas rattachée à E)", () => {
    expect(slug("fr", bac("E"))).toBe("mathematiques-bac-c-et-e-2026-2")
    expect(exempleDuCursus("fr", bac("E"))).not.toBe(exempleDuCursus("fr", bac("C")))
  })

  it("BAC TI : sa propre mathématique gratuite, jamais le corrigé de BEPC", () => {
    expect(slug("fr", bac("TI"))).toBe("mathematiques-bac-d-et-ti-2025")
    expect(exempleDuCursus("fr", bac("TI"))).not.toBe(EXEMPLES_CORRIGE.fr)
  })

  it("Probatoire C et E passent la même épreuve", () => {
    expect(slug("fr", probatoire("C"))).toBe("mathematiques-probatoire-c-et-e-2025")
    expect(exempleDuCursus("fr", probatoire("E"))).toBe(exempleDuCursus("fr", probatoire("C")))
  })

  it("un cursus sans épreuve gratuite n'a AUCUN exemple (jamais celui d'un autre examen)", () => {
    expect(exempleDuCursus("fr", bac("A2"))).toBeNull()
    expect(exempleDuCursus("fr", bac("G"))).toBeNull()
    expect(exempleDuCursus("fr", bac("ELECTRICITE"))).toBeNull()
    expect(exempleDuCursus("fr", { examen: "CAP", series: { code: "COMMERCE" } })).toBeNull()
    expect(exempleDuCursus("fr", probatoire("COMMERCE"))).toBeNull()
  })

  it("sans examen déclaré : l'exemple par défaut de la langue", () => {
    expect(exempleDuCursus("fr", null)).toBe(EXEMPLES_CORRIGE.fr)
    expect(exempleDuCursus("fr", undefined)).toBe(EXEMPLES_CORRIGE.fr)
    expect(exempleDuCursus("en", null)).toBe(EXEMPLES_CORRIGE.en)
  })

  it("en anglais, jamais un exemple français, quel que soit l'examen déclaré", () => {
    expect(exempleDuCursus("en", bac("C"))).toBeNull()
  })

  it("GCE A Level : une mathématique gratuite de l'A Level, branches générale et technique", () => {
    const general = exempleDuCursus("en", { examen: "GCE_AL", series: null })
    expect(general?.slug).toBe("pure-mathematics-with-mechanics-gce-a-level-2023-paper-2")
    expect(general?.slug).toMatch(/a-level/)
    expect(exempleDuCursus("en", { examen: "GCE_AL", series: { code: "GCE_TECHNICAL" } })).toBe(general)
  })

  it("GCE O Level (générale ou technique) : l'exemple par défaut de l'anglais", () => {
    expect(exempleDuCursus("en", { examen: "GCE_OL", series: null })).toBe(EXEMPLES_CORRIGE.en)
    expect(exempleDuCursus("en", { examen: "GCE_OL", series: { code: "GCE_TECHNICAL" } })).toBe(EXEMPLES_CORRIGE.en)
  })

  it("l'exemple A Level retient l'exercice entier : l'exercice 4, avec ses deux questions", () => {
    const AL = exempleDuCursus("en", { examen: "GCE_AL", series: null })
    const Q_I = "**i.** A"
    const Q_II = "**ii.** B"
    const quatre = exercice("4", `${Q_I}

${Q_II}`, `${Q_I}

Réponse 1

${Q_II}

Réponse 2`)
    const extrait = extraireExempleCorrige(epreuve(exercice("1", "x", "y"), quatre), AL)
    expect(extrait?.exercice).toBe(quatre)
    expect(extrait?.corrigeMarkdown).toBe(quatre.corrige_markdown)
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

  it("repères avec lettre (« **1.a.** », BAC TI) : coupe avant la 1.b", () => {
    const TI = exempleDuCursus("fr", { examen: "BAC", series: { code: "TI" } })
    const exo = exercice("1", "intro", "**1.a.** A\n\nRéponse\n\n**1.b.** B\n\nRéponse")
    expect(extraireExempleCorrige(epreuve(exo), TI)?.corrigeMarkdown).toBe("**1.a.** A\n\nRéponse")
  })

  it("repère « 1) » non gras en début de ligne (BAC C et E)", () => {
    const E = exempleDuCursus("fr", { examen: "BAC", series: { code: "E" } })
    const exo = exercice("3", "intro", "1) Étudier g\n\nRéponse\n\n2) Calculer les limites\n\nRéponse")
    expect(extraireExempleCorrige(epreuve(exo), E)?.corrigeMarkdown).toBe("1) Étudier g\n\nRéponse")
  })

  it("un seul repère : corrigé entier", () => {
    const exo = exercice("3", "intro", "**1.** A\n\nRéponse")
    expect(extraireExempleCorrige(epreuve(exo), BAC_C)?.corrigeMarkdown).toBe("**1.** A\n\nRéponse")
  })
})
