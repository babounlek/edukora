import { describe, expect, it } from "vitest"

import { extractCallouts, extractSolutionToggles, italicizeQuotes, normalizeMathBlocks } from "./markdown"

describe("extractSolutionToggles", () => {
  it("garde une solution multi-ligne entière dans le toggle, fence de code compris", () => {
    const markdown = [
      "### Solution",
      "",
      "```php",
      "$i = 0;",
      "while ($i < 3) {",
      "    $i++;",
      "}",
      "```",
      "",
      "### Exercice 2",
      "",
      "Suite.",
    ].join("\n")

    const result = extractSolutionToggles(markdown)
    const quoted = result.split("\n").filter((line) => line.startsWith(">"))

    expect(quoted).toContain("> $i = 0;")
    expect(quoted).toContain("> ```")
    expect(result).toContain("\n### Exercice 2\n\nSuite.")
  })

  it("garde une solution en plusieurs paragraphes jusqu'à la fin du texte", () => {
    const result = extractSolutionToggles("### Solution\n\nPremier paragraphe.\n\nSecond paragraphe.")
    const unquoted = result.split("\n").filter((line) => line && !line.startsWith(">"))

    expect(unquoted).toEqual([])
    expect(result).toContain("> Second paragraphe.")
  })
})

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

describe("code protégé des transformations de rendu", () => {
  it("normalizeMathBlocks ne prend pas `$$a` ... `$$a` pour une formule display", () => {
    const markdown = "Écrire `$c=$$a;` puis\n\nla valeur `$$a` équivaut à `$b`."

    expect(normalizeMathBlocks(markdown)).toBe(markdown)
  })

  it("italicizeQuotes laisse intacts les guillemets d'un fence et d'un span de code", () => {
    const markdown = 'Afficher `echo " ";` :\n\n```php\necho "a";\n```\n\nPuis « texte » normal.'
    const result = italicizeQuotes(markdown)

    expect(result).toContain('`echo " ";`')
    expect(result).toContain('echo "a";')
    expect(result).toContain("*«texte»*".replace("«texte»", "« texte »"))
  })
})

describe("normalizeMathBlocks dans une citation", () => {
  it("garde chaque ligne d'un bloc display multi-lignes préfixée par > (solution masquée)", () => {
    const markdown = [
      "> [SOLUTION_TOGGLE]",
      ">",
      "> $$",
      "> \begin{array}{c|c}",
      "> \hline",
      "> x & 1 \\\\",
      "> \end{array}",
      "> $$",
    ].join("\n")

    const result = normalizeMathBlocks(markdown)
    const lignes = result.split("\n").filter((l) => l.trim())

    expect(lignes.every((l) => l.startsWith(">"))).toBe(true)
    expect(result).toContain("> \hline")
    expect(result.match(/> \$\$/g)).toHaveLength(2)
  })
})
