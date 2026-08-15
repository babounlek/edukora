import { describe, expect, it } from "vitest"

import { extractCallouts } from "./markdown"

describe("extractCallouts", () => {
  it("garde un marqueur [COURS_LINK:...] injecté après un Rappel de méthode dans le même blockquote", () => {
    // Reproduit le corrigé réel injecté par _annotate_cours_links côté backend :
    // le marqueur est un paragraphe séparé, juste après le contenu du rappel.
    const markdown = [
      "### Rappel de méthode",
      "Une définition rigoureuse en chimie doit être concise.",
      "",
      "[COURS_LINK:definir-une-base-selon-bronsted]",
      "",
      "### Corrigé",
      "La suite du corrigé.",
    ].join("\n")

    const result = extractCallouts(markdown)
    const blockquoteLines = result.split("\n").filter((line) => line.startsWith(">"))

    expect(blockquoteLines.join("\n")).toContain("[COURS_LINK:definir-une-base-selon-bronsted]")
    // La suite (### Corrigé) ne doit pas avoir été engloutie dans le blockquote.
    expect(result).toContain("\n### Corrigé\nLa suite du corrigé.")
  })

  it("inclut plusieurs marqueurs [COURS_LINK:...] consécutifs dans le même blockquote", () => {
    const markdown = [
      "### Rappel de méthode",
      "Contenu fusionné pour deux sous-questions.",
      "",
      "[COURS_LINK:premier-cours]",
      "",
      "[COURS_LINK:second-cours]",
      "",
      "### Corrigé",
      "La suite.",
    ].join("\n")

    const result = extractCallouts(markdown)
    const blockquoteLines = result.split("\n").filter((line) => line.startsWith(">")).join("\n")

    expect(blockquoteLines).toContain("[COURS_LINK:premier-cours]")
    expect(blockquoteLines).toContain("[COURS_LINK:second-cours]")
  })

  it("n'engloutit pas l'énoncé de la question suivante dans un Conseil/Piège sans marqueur", () => {
    // Un "### Conseil" à un seul paragraphe est immédiatement suivi, sans titre "###"
    // intermédiaire, par l'énoncé de la question suivante (voir _render_question_corrige) -
    // ce texte ne doit jamais finir cité (">") à l'intérieur du blockquote du Conseil.
    const markdown = [
      "### Conseil",
      "Retiens cette définition par cœur.",
      "",
      "2. Choisir la réponse juste",
      "",
      "### Rappel de méthode",
      "Contenu de la question suivante.",
    ].join("\n")

    const result = extractCallouts(markdown)

    expect(result).toContain("\n2. Choisir la réponse juste\n")
    expect(result).not.toContain("> 2. Choisir la réponse juste")
  })
})
