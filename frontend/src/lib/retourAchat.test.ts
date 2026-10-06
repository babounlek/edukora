import { describe, expect, it } from "vitest"

import type { Cursus } from "@/api/types"

import { cheminRetourSur, choisirCursusPourAchat, lienAbonnement } from "./retourAchat"

const cursus = (id: number) => ({ id }) as Cursus

describe("cheminRetourSur", () => {
  it("accepte un chemin interne, query string comprise", () => {
    expect(cheminRetourSur("/cm/epreuves-inedites/maths-bac-d?ref=pdf")).toBe("/cm/epreuves-inedites/maths-bac-d?ref=pdf")
  })

  it.each([null, undefined, "", "cm/epreuves", "https://evil.example/x", "//evil.example/x", "/\\evil.example", "/a://b"])(
    "refuse %s (jamais une redirection hors du site)",
    (valeur) => {
      expect(cheminRetourSur(valeur)).toBeNull()
    },
  )
})

describe("choisirCursusPourAchat", () => {
  it("prend le cursus déclaré quand l'épreuve le couvre", () => {
    expect(choisirCursusPourAchat([cursus(1), cursus(2)], 2)?.id).toBe(2)
  })

  it("retombe sur le premier quand le cursus déclaré n'est pas couvert ou absent", () => {
    expect(choisirCursusPourAchat([cursus(1), cursus(2)], 9)?.id).toBe(1)
    expect(choisirCursusPourAchat([cursus(1), cursus(2)], null)?.id).toBe(1)
  })

  it("renvoie undefined sans cursus", () => {
    expect(choisirCursusPourAchat([], 1)).toBeUndefined()
  })
})

describe("lienAbonnement", () => {
  it("encode le chemin de retour", () => {
    const lien = lienAbonnement(14, "/cm/epreuves-inedites/a?x=1&y=2")
    const params = new URL(lien, "http://x").searchParams
    expect(params.get("cursus")).toBe("14")
    expect(params.get("duree")).toBe("examen")
    expect(params.get("retour")).toBe("/cm/epreuves-inedites/a?x=1&y=2")
  })
})
