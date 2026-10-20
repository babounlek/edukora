import { describe, expect, it } from "vitest"

import { agrandirFractionsEnLigne, extractCallouts, extractSolutionToggles, groupBareCoursLinks, italicizeQuotes, nomAccessibleDuChoix, normalizeMathBlocks } from "./markdown"

describe("agrandirFractionsEnLigne", () => {
  it("passe en \\dfrac une chaîne d'égalités en ligne (test élève P1)", () => {
    const source = "Donc $\\frac{x^2-25}{x^2+10x+25} = \\frac{(x-5)(x+5)}{(x+5)^2} = \\frac{x-5}{x+5}$."
    expect(agrandirFractionsEnLigne(source)).toBe(
      "Donc $\\dfrac{x^2-25}{x^2+10x+25} = \\dfrac{(x-5)(x+5)}{(x+5)^2} = \\dfrac{x-5}{x+5}$.",
    )
  })

  it("agrandit aussi une seule fraction quand la formule contient une égalité", () => {
    expect(agrandirFractionsEnLigne("On a $f(x) = \\frac{1}{x}$.")).toBe("On a $f(x) = \\dfrac{1}{x}$.")
  })

  it("agrandit deux fractions sans égalité", () => {
    expect(agrandirFractionsEnLigne("$\\frac{a}{b} + \\frac{c}{d}$")).toBe("$\\dfrac{a}{b} + \\dfrac{c}{d}$")
  })

  it("laisse une fraction isolée dans une phrase à sa taille de texte", () => {
    const source = "Un demi s'écrit $\\frac{1}{2}$ dans le texte."
    expect(agrandirFractionsEnLigne(source)).toBe(source)
  })

  it("ne touche ni les formules display, ni \\dfrac, ni \\tfrac, ni le code", () => {
    const display = "$$\\frac{a}{b} = \\frac{c}{d}$$"
    expect(agrandirFractionsEnLigne(display)).toBe(display)
    const deja = "$\\dfrac{a}{b} = \\tfrac{c}{d}$"
    expect(agrandirFractionsEnLigne(deja)).toBe(deja)
    const code = "`$\\frac{a}{b} = \\frac{c}{d}$`"
    expect(agrandirFractionsEnLigne(code)).toBe(code)
  })

  it("ne confond pas une commande qui commence par frac", () => {
    const source = "$\\fracture = \\frac{1}{2}$"
    expect(agrandirFractionsEnLigne(source)).toBe("$\\fracture = \\dfrac{1}{2}$")
  })
})

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

  it("n'engloutit pas une sous-question déjà numérotée sous une forme sans point final (ex. \"b)\")", () => {
    // Repère hérité de la numérotation d'origine du sujet plutôt qu'injecté par
    // _render_question_enonce ("**b)**", sans point avant sa fermeture "**",
    // contrairement au préfixe que _render_question_enonce injecte lui-même,
    // "**3b.**" - voir le test suivant) - peu importe sa forme exacte, la première
    // ligne vide suffit à elle seule à arrêter la capture (voir extractCallouts) : régression
    // constatée en prod sur mathematiques-probatoire-a-2024 (scan corpus du
    // 2026-09-02 : 292 occurrences sur tout le corpus, toutes matières confondues).
    const markdown = [
      "### Conseil",
      "Pense à vérifier que le total annoncé est correct avant de te lancer dans le calcul.",
      "",
      "**b)** Combien y a-t-il de tirages comportant des questions de la même discipline ?",
      "",
      "### Rappel de méthode",
      "Contenu de la question suivante.",
    ].join("\n")

    const result = extractCallouts(markdown)

    expect(result).toContain("\n**b)** Combien y a-t-il de tirages comportant des questions de la même discipline ?\n")
    expect(result).not.toContain("> **b)**")
  })

  it("n'étend pas l'encadré au-delà du premier paragraphe (rappel/correction séparés)", () => {
    // SKILL.md impose un "### Rappel de méthode" strictement mono-paragraphe : le
    // principe général reste seul dans l'encadré coloré, la résolution chiffrée qui
    // suit (démonstration, formules, réponse finale) redevient un texte de corrigé
    // normal, visuellement distinct - c'est la séparation attendue entre rappel et
    // correction (signalé en prod : mathematiques-probatoire-c-et-e-2008,
    // mathematiques-probatoire-a-2023-blanc, scan corpus du 2026-09-02 - ~3600 blocs
    // sur ~2000 exercices absorbaient toute la résolution avant ce correctif).
    const markdown = [
      "### Rappel de méthode",
      "Principe général.",
      "",
      "Application chiffrée au cas précis.",
      "",
      "$$",
      "x = 42",
      "$$",
      "",
      "**La réponse est 42.**",
      "",
      "### Piège à éviter",
      "Contenu piège.",
    ].join("\n")

    const result = extractCallouts(markdown)
    const blockquoteLines = result.split("\n").filter((line) => line.startsWith(">")).join("\n")

    expect(blockquoteLines).toContain("Principe général.")
    expect(blockquoteLines).not.toContain("Application chiffrée au cas précis.")
    expect(result).toContain("\nApplication chiffrée au cas précis.\n")
    expect(result).toContain("\n**La réponse est 42.**\n")
  })

  it("arrête un Rappel de méthode à la sous-question suivante déjà numérotée, même sans second paragraphe", () => {
    const markdown = [
      "### Rappel de méthode",
      "Principe général.",
      "",
      "**3b.** Sommons l'encadrement de la question précédente.",
    ].join("\n")

    const result = extractCallouts(markdown)
    const blockquoteLines = result.split("\n").filter((line) => line.startsWith(">")).join("\n")

    expect(blockquoteLines).toContain("Principe général.")
    expect(result).toContain("\n**3b.** Sommons l'encadrement de la question précédente.")
    expect(result).not.toContain("> **3b.**")
  })
})

describe("groupBareCoursLinks", () => {
  it("regroupe une pile de marqueurs orphelins consécutifs en un seul marqueur groupé", () => {
    // Reproduit la queue "append_unmatched" réelle produite par
    // catalog.rendering.annotate_cours_links quand plusieurs rappels d'un même
    // exercice n'ont pu être appariés à aucun bloc précis (ex. un "Problème" à
    // plusieurs parties) - constaté en prod sur mathematiques-probatoire-c-2004.
    const markdown = [
      "### Piège à éviter",
      "Contenu piège.",
      "",
      "[COURS_LINK:premier-cours]",
      "",
      "[COURS_LINK:second-cours]",
      "",
      "[COURS_LINK:troisieme-cours]",
    ].join("\n")

    const result = groupBareCoursLinks(markdown)

    expect(result).toContain("[COURS_LINK_GROUP:premier-cours,second-cours,troisieme-cours]")
    expect(result).not.toContain("[COURS_LINK:premier-cours]")
  })

  it("laisse un marqueur orphelin isolé inchangé", () => {
    const markdown = ["### Piège à éviter", "Contenu piège.", "", "[COURS_LINK:seul-cours]"].join("\n")

    const result = groupBareCoursLinks(markdown)

    expect(result).toBe(markdown)
  })

  it("ne touche pas des marqueurs [COURS_LINK:...] déjà à l'intérieur d'un blockquote", () => {
    // Après extractCallouts, un marqueur apparié reste dans le corps du blockquote
    // (préfixé "> ") - jamais confondu avec la queue orpheline en tête de ligne.
    const markdown = [
      "> [CALLOUT:rappel]",
      ">",
      "> Contenu du rappel.",
      ">",
      "> [COURS_LINK:premier-cours]",
      ">",
      "> [COURS_LINK:second-cours]",
    ].join("\n")

    const result = groupBareCoursLinks(markdown)

    expect(result).toBe(markdown)
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

describe("normalizeMathBlocks : formule `$$...$$` d'une ligne", () => {
  it("passe en bloc display une chaîne de fractions seule sur sa ligne (test élève P1)", () => {
    const markdown = "Donc :\n\n$$\\frac{a}{b} = \\frac{c}{d}$$\n\nVérification."
    expect(normalizeMathBlocks(markdown)).toBe("Donc :\n\n$$\n\\frac{a}{b} = \\frac{c}{d}\n$$\n\nVérification.")
  })

  it("couvre aussi les sommes, intégrales et limites", () => {
    expect(normalizeMathBlocks("$$\\int_0^1 f(x)\\,dx$$")).toBe("$$\n\\int_0^1 f(x)\\,dx\n$$")
    expect(normalizeMathBlocks("$$\\lim_{x\\to 0} \\sin x$$")).toBe("$$\n\\lim_{x\\to 0} \\sin x\n$$")
  })

  it("laisse une formule d'une ligne sans fraction, somme ni intégrale telle quelle", () => {
    const markdown = "$$x^2 = 4$$"
    expect(normalizeMathBlocks(markdown)).toBe(markdown)
  })

  it("laisse une formule $$...$$ prise dans une phrase", () => {
    const markdown = "On pose $$\\frac{a}{b} = 2$$ puis on continue."
    expect(normalizeMathBlocks(markdown)).toBe(markdown)
  })

  it("laisse une formule d'une ligne dans une citation", () => {
    const markdown = "> $$\\frac{a}{b} = 2$$"
    expect(normalizeMathBlocks(markdown)).toBe(markdown)
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

describe("nomAccessibleDuChoix", () => {
  it("nomme un choix en texte simple avec sa lettre", () => {
    expect(nomAccessibleDuChoix("a", "35")).toBe("A. 35")
    expect(nomAccessibleDuChoix("b", "$128$ m")).toBe("B. 128 m")
  })

  it("ne pose rien sur un choix qui porte une formule : le contenu du bouton la dit mieux", () => {
    expect(nomAccessibleDuChoix("c", "$\dfrac{1}{2}$")).toBeUndefined()
    expect(nomAccessibleDuChoix("d", "$x^2$")).toBeUndefined()
  })

  it("ne pose rien sur un choix vide", () => {
    expect(nomAccessibleDuChoix("a", "  ")).toBeUndefined()
  })
})
