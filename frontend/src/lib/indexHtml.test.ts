import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"

/**
 * Le titre statique d'index.html est celui de la version française : sur un lien profond /en/..., un script en tête de
 * page le remplace avant tout JavaScript (test élève Gogo : onglet « Corrigés BEPC, Probatoire et BAC » pour un élève GCE).
 */
const html = readFileSync(resolve(__dirname, "../../index.html"), "utf-8")
const script = html.match(/\(function \(\) \{\s*var p = location\.pathname;[\s\S]*?\}\)\(\);/)?.[0] ?? ""

function executer(pathname: string) {
  const description = { content: "FR", setAttribute(_n: string, v: string) { this.content = v } }
  const doc = {
    title: "FR",
    documentElement: { lang: "fr" },
    querySelector: () => description,
  }
  new Function("location", "document", script.replace("%VITE_SITE_NAME%", "EduKora"))({ pathname }, doc)
  return { doc, description }
}

describe("index.html : titre des liens /en", () => {
  it("contient le script", () => {
    expect(script).not.toBe("")
  })

  it("passe le titre, la langue et la description en anglais sur /en et /en/...", () => {
    for (const chemin of ["/en", "/en/cm", "/en/cm/past-papers/maths/read"]) {
      const { doc, description } = executer(chemin)
      expect(doc.title).toMatch(/^EduKora - Past papers and solutions for the GCE/)
      expect(doc.documentElement.lang).toBe("en")
      expect(description.content).toMatch(/^Every day, we tell you what to revise/)
    }
  })

  it("ne touche à rien hors de /en (y compris /enfant ou /entree)", () => {
    for (const chemin of ["/", "/cm", "/enfant", "/entree/x", "/cm/en"]) {
      const { doc, description } = executer(chemin)
      expect(doc.title).toBe("FR")
      expect(doc.documentElement.lang).toBe("fr")
      expect(description.content).toBe("FR")
    }
  })
})
