import { describe, expect, it } from "vitest"

import { texteDeLaSelection } from "./NoterSelection"

function plageSur(html: string): Range {
  const zone = document.createElement("div")
  zone.innerHTML = html
  document.body.appendChild(zone)
  const plage = document.createRange()
  plage.selectNodeContents(zone)
  return plage
}

describe("texteDeLaSelection", () => {
  it("rend une formule KaTeX en LaTeX entre $, sans la double écriture MathML/HTML", () => {
    const plage = plageSur(
      `<p>Le théorème : <span class="katex"><span class="katex-mathml"><math><semantics><mrow><mi>a</mi></mrow>` +
        `<annotation encoding="application/x-tex">a^2+b^2=c^2</annotation></semantics></math></span>` +
        `<span class="katex-html" aria-hidden="true">a2+b2=c2</span></span> dans un triangle rectangle.</p>`,
    )
    expect(texteDeLaSelection(plage)).toBe("Le théorème : $a^2+b^2=c^2$ dans un triangle rectangle.")
  })

  it("ramène les retours à la ligne et les espaces multiples à une seule espace", () => {
    expect(texteDeLaSelection(plageSur("<p>Une   règle\n\n  à retenir</p>"))).toBe("Une règle à retenir")
  })
})
