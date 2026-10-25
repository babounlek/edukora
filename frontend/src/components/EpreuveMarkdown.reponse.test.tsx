import { render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { afterAll, beforeAll, describe, expect, it } from "vitest"

import { definirLangue } from "@/lib/i18n"
import { extractAnswerHighlights } from "@/lib/markdown"

import { EpreuveMarkdown } from "./EpreuveMarkdown"

function afficher(markdown: string) {
  return render(
    <MemoryRouter>
      <EpreuveMarkdown markdown={markdown} directCoursLinks />
    </MemoryRouter>,
  )
}

describe("extractAnswerHighlights", () => {
  it("isole la réponse d'un QCM en fin de paragraphe, l'explication restant un paragraphe normal", () => {
    const sortie = extractAnswerHighlights("The shoot apex makes auxin. This is apical dominance. **Answer: C.**")
    expect(sortie).toBe(
      "The shoot apex makes auxin. This is apical dominance.\n\n> [ANSWER]\n>\n> **Answer: C.**\n",
    )
  })

  it("encadre une réponse seule sur sa ligne et garde le texte qui la suit", () => {
    expect(extractAnswerHighlights("**Answer: $1 : 20\\,000$** (so $n = 20\\,000$).")).toContain(
      "> [ANSWER]\n>\n> **Answer: $1 : 20\\,000$** (so $n = 20\\,000$).",
    )
    expect(extractAnswerHighlights("**Intended answer: D ($4$).**")).toContain("> [ANSWER]")
    expect(extractAnswerHighlights("**Réponse : b) en solution neutre.**")).toContain("> [ANSWER]")
  })

  it("encadre la conclusion chiffrée d'un calcul, pas un intitulé", () => {
    expect(extractAnswerHighlights("**The tension in the string is $8$ N.**")).toContain("> [ANSWER]")
    expect(extractAnswerHighlights("**Exercice 2 ($4$ points)**")).not.toContain("[ANSWER]")
    expect(extractAnswerHighlights("**(ii) Find $x$**")).not.toContain("[ANSWER]")
    expect(extractAnswerHighlights("**Introduction.** Define a film industry.")).not.toContain("[ANSWER]")
    expect(extractAnswerHighlights("**Variation table of $g$:**")).not.toContain("[ANSWER]")
  })

  it("sans les conclusions chiffrées (corrigés français), seules les réponses étiquetées sont encadrées", () => {
    const options = { conclusionsChiffrees: false }
    expect(extractAnswerHighlights("**Limite en $-\\infty$.**", options)).not.toContain("[ANSWER]")
    expect(extractAnswerHighlights("**Réponse : b) en solution neutre.**", options)).toContain("[ANSWER]")
  })

  it("ne touche ni le code, ni les formules display, ni les citations, ni les tableaux, ni les listes", () => {
    const intacts = [
      "```\n**Answer: B.**\n```",
      "$$\n**Answer: B.**\n$$",
      "> **Answer: B.**",
      "| **Answer: B.** | x |",
      "- **Answer: B.**",
      "Use `x` then **Answer: B.**",
      "Not a sentence end **Answer: B.**",
    ]
    for (const texte of intacts) expect(extractAnswerHighlights(texte)).toBe(texte)
  })
})

describe("EpreuveMarkdown : la réponse du corrigé est mise en exergue", () => {
  beforeAll(() => definirLangue("en", { persister: false }))
  afterAll(() => definirLangue("fr", { persister: false }))

  it("affiche la réponse d'un QCM dans un encadré nommé, séparé de l'explication", () => {
    afficher("**1.** Which function?\n\nSupport only. **Answer: B.**")
    const encadre = screen.getByRole("note")
    expect(encadre).toHaveTextContent("Answer: B.")
    expect(encadre).not.toHaveTextContent("Support only")
    expect(screen.getByText("Support only.")).toBeInTheDocument()
  })

  it("garde une conclusion chiffrée (formule) dans l'encadré", () => {
    afficher("Power in equals power out.\n\n**The current is $0.125\\,\\mathrm{A}$.**")
    expect(screen.getByRole("note")).toHaveTextContent("The current is")
  })
})
