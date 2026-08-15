import { describe, expect, it } from "vitest"

import { parseFicheCards } from "./ficheCards"

describe("parseFicheCards", () => {
  it("découpe un titre de niveau 2 par carte", () => {
    const markdown = [
      "## Dérivée d'un produit ?",
      "$(uv)' = u'v + uv'$",
      "",
      "## Dérivée d'un quotient ?",
      "$(u/v)' = (u'v - uv') / v^2$",
    ].join("\n")

    const cards = parseFicheCards(markdown)

    expect(cards).toEqual([
      { question: "Dérivée d'un produit ?", reponse: "$(uv)' = u'v + uv'$" },
      { question: "Dérivée d'un quotient ?", reponse: "$(u/v)' = (u'v - uv') / v^2$" },
    ])
  })

  it("ignore les titres de niveau 3 à l'intérieur d'une carte - pas une nouvelle carte", () => {
    const markdown = ["## Formule", "### Cas particulier", "détail"].join("\n")

    const cards = parseFicheCards(markdown)

    expect(cards).toHaveLength(1)
    expect(cards[0].reponse).toContain("### Cas particulier")
  })

  it("retombe sur une carte unique quand aucun titre de niveau 2 n'est présent", () => {
    const cards = parseFicheCards("Juste un paragraphe, sans titre.")

    expect(cards).toEqual([{ question: "Fiche", reponse: "Juste un paragraphe, sans titre." }])
  })

  it("renvoie une liste vide pour un contenu vide", () => {
    expect(parseFicheCards("")).toEqual([])
    expect(parseFicheCards("   \n  ")).toEqual([])
  })

  it("garde le contenu avant le premier titre de niveau 2 hors de toute carte", () => {
    // Contenu orphelin (avant tout titre) : jamais montré, plutôt que de l'attribuer
    // à tort à la première vraie carte - voir la docstring de parseFicheCards.
    const markdown = ["Une intro qui ne devrait pas être une carte.", "", "## Vraie carte", "réponse"].join("\n")

    const cards = parseFicheCards(markdown)

    expect(cards).toEqual([{ question: "Vraie carte", reponse: "réponse" }])
  })
})
