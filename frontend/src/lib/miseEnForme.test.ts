import { describe, expect, it } from "vitest"

import { appliquerFormat } from "./miseEnForme"

describe("appliquerFormat", () => {
  it("entoure la sélection de signes de gras, et les retire au second appui", () => {
    const a = appliquerFormat("une règle clé", 4, 9, "gras")
    expect(a.texte).toBe("une **règle** clé")
    expect(a.texte.slice(a.debut, a.fin)).toBe("règle")
    const b = appliquerFormat(a.texte, 4, 13, "gras")
    expect(b.texte).toBe("une règle clé")
  })

  it("sans sélection, pose les signes avec le curseur entre les deux", () => {
    const r = appliquerFormat("a b", 1, 1, "formule")
    expect(r.texte).toBe("a$$ b")
    expect([r.debut, r.fin]).toEqual([2, 2])
  })

  it("met un tiret en tête de chaque ligne touchée, et le retire au second appui", () => {
    const a = appliquerFormat("un\ndeux\ntrois", 0, 6, "liste")
    expect(a.texte).toBe("- un\n- deux\ntrois")
    const b = appliquerFormat(a.texte, 0, 11, "liste")
    expect(b.texte).toBe("un\ndeux\ntrois")
  })

  it("ne prend pas un gras pour un italique à retirer", () => {
    const r = appliquerFormat("**fort**", 0, 8, "italique")
    expect(r.texte).toBe("***fort***")
  })
})
