import { render, screen, within } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import type { EpreuveExercise } from "@/api/types"
import { apercuQuestion, libelleDansSection, sectionsDEpreuve } from "@/components/EpreuveSommaire"

import { BarreExercices } from "./BarreExercices"

function exercice(numero: string, groupes: string[]): EpreuveExercise {
  return {
    numero_exercice: numero,
    titre: "",
    points: "25",
    groupes,
    enonce_intro_markdown: "",
    enonce_markdown: "",
    corrige_markdown: "",
  }
}

/** Épreuve du GCE : `parSection` questions numérotées de suite dans chacune des sections. */
function epreuve(sections: string[], parSection: number): EpreuveExercise[] {
  const sortie: EpreuveExercise[] = []
  sections.forEach((section) => {
    for (let i = 0; i < parSection; i += 1) sortie.push(exercice(String(sortie.length + 1), [section]))
  })
  return sortie
}

beforeEach(() => {
  // jsdom n'a pas IntersectionObserver ni scrollTo sur les éléments.
  vi.stubGlobal(
    "IntersectionObserver",
    class {
      observe() {}
      disconnect() {}
      unobserve() {}
    },
  )
  Element.prototype.scrollTo = vi.fn() as unknown as typeof Element.prototype.scrollTo
})

describe("sectionsDEpreuve", () => {
  it("découpe une longue épreuve groupée, dans l'ordre, avec le rang global des exercices", () => {
    const sections = sectionsDEpreuve(epreuve(["SECTION 1.1", "SECTION 5.3", "SECTION 5.5"], 6))
    expect(sections?.map((s) => s.label)).toEqual(["SECTION 1.1", "SECTION 5.3", "SECTION 5.5"])
    expect(sections?.[1].items.map((i) => i.index)).toEqual([6, 7, 8, 9, 10, 11])
    expect(sections?.[1].items[0].exercise.numero_exercice).toBe("7")
  })

  it("laisse une épreuve courte au sommaire plat", () => {
    expect(sectionsDEpreuve(epreuve(["SECTION A", "SECTION B"], 4))).toBeNull()
  })

  it("laisse une épreuve au sommaire plat quand un exercice n'a aucun groupe", () => {
    const exercices = epreuve(["SECTION A", "SECTION B"], 5)
    exercices[3] = exercice("4", [])
    expect(sectionsDEpreuve(exercices)).toBeNull()
  })

  it("ne fait pas de section d'un groupe unique", () => {
    expect(sectionsDEpreuve(epreuve(["SECTION A"], 12))).toBeNull()
  })

  it("distingue deux sections qui ne diffèrent que par leur groupe parent", () => {
    const exercices = [
      ...Array.from({ length: 5 }, (_, i) => exercice(String(i + 1), ["Partie A", "I."])),
      ...Array.from({ length: 5 }, (_, i) => exercice(String(i + 6), ["Partie B", "I."])),
    ]
    expect(sectionsDEpreuve(exercices)?.map((s) => s.label)).toEqual(["Partie A · I.", "Partie B · I."])
  })
})

describe("sections des sujets à en-tête de section", () => {
  /** Au GCE, le titre extrait de chaque exercice est celui de sa section, identique pour toutes ses questions. */
  function avecTitres(titres: Record<string, string>) {
    return epreuve(Object.keys(titres), 5).map((e) => ({ ...e, titre: titres[e.groupes[0]] }))
  }

  it("prend le titre commun des exercices comme intitulé de la section", () => {
    const sections = sectionsDEpreuve(
      avecTitres({ "SECTION 2.1": "Section 2.1 The Gospel According to Luke", "SECTION 2.2": "Section 2.2 The Fourth Gospel" }),
    )
    expect(sections?.map((s) => s.intitule)).toEqual([
      "Section 2.1 The Gospel According to Luke",
      "Section 2.2 The Fourth Gospel",
    ])
    // Le repère court sert aux pastilles de la barre.
    expect(sections?.map((s) => s.label)).toEqual(["SECTION 2.1", "SECTION 2.2"])
  })

  it("garde un titre de section qui contient « - » en entier", () => {
    const sections = sectionsDEpreuve(
      avecTitres({
        "SECTION 4.2": "Section 4.2 Ethics and Morality",
        "SECTION 6.0": "Section 6.0 The Historical Development of Islam (570CE - 661CE)",
      }),
    )
    expect(sections?.[1].intitule).toBe("Section 6.0 The Historical Development of Islam (570CE - 661CE)")
  })

  it("retombe sur le repère de groupe quand les titres diffèrent ou manquent", () => {
    const exercices = avecTitres({ "SECTION A": "", "SECTION B": "" })
    exercices[1] = { ...exercices[1], titre: "Une question à part" }
    expect(sectionsDEpreuve(exercices)?.map((s) => s.intitule)).toEqual(["SECTION A", "SECTION B"])
  })

  it("nomme un exercice par son numéro imprimé, pas par le titre de sa section", () => {
    expect(libelleDansSection(exercice("19", ["SECTION 4.1"]))).toBe("Exercice 19")
    expect(libelleDansSection(exercice("I-2", ["SECTION I"]))).toBe("I-2")
  })

  it("donne le début de la question, sans l'en-tête de section ni le barème", () => {
    const enonce = "**Section 2.2 The Fourth Gospel**\n\nExamine the raising of Lazarus to life by Jesus.\n\n(25 marks)"
    expect(apercuQuestion(enonce, "Section 2.2 The Fourth Gospel")).toBe("Examine the raising of Lazarus to life by Jesus.")
  })

  it("tronque une longue question et retire le balisage", () => {
    const apercu = apercuQuestion(`"While *I am in the world*, I am the light of the world" (John 9;5). ${"Discuss this statement ".repeat(8)}`)
    expect(apercu.length).toBeLessThanOrEqual(90)
    expect(apercu.endsWith("…")).toBe(true)
    expect(apercu).not.toContain("*")
  })
})

describe("BarreExercices", () => {
  it("garde une seule rangée de pastilles pour une épreuve courte", () => {
    render(<BarreExercices exercises={epreuve(["SECTION A", "SECTION B"], 3)} />)
    expect(screen.getAllByRole("list")).toHaveLength(1)
    expect(screen.getAllByRole("link")).toHaveLength(6)
  })

  it("sépare sections et questions pour une longue épreuve : seules les questions de la section en cours sont listées", () => {
    render(<BarreExercices exercises={epreuve(["SECTION 2.1", "SECTION 2.2", "SECTION 4.1"], 6)} />)
    const [rangeeSections, rangeeQuestions] = screen.getAllByRole("list")

    const sections = within(rangeeSections).getAllByRole("link")
    expect(sections.map((a) => a.textContent)).toEqual(["SECTION 2.1", "SECTION 2.2", "SECTION 4.1"])
    // Cliquer une section mène à sa première question, au numéro imprimé du sujet.
    expect(sections[1].getAttribute("href")).toBe("#exercice-7")
    expect(sections[0].getAttribute("aria-current")).toBe("location")

    const questions = within(rangeeQuestions).getAllByRole("link")
    expect(questions).toHaveLength(6)
    expect(questions.map((a) => a.getAttribute("href"))).toEqual([
      "#exercice-1",
      "#exercice-2",
      "#exercice-3",
      "#exercice-4",
      "#exercice-5",
      "#exercice-6",
    ])
  })

  it("n'affiche rien pour un seul exercice", () => {
    const { container } = render(<BarreExercices exercises={[exercice("1", [])]} />)
    expect(container).toBeEmptyDOMElement()
  })
})
