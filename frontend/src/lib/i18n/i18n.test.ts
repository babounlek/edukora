import { afterEach, describe, expect, it } from "vitest"

import { formatCompteARebours } from "@/components/CompteAReboursBadge"
import type { CompteARebours } from "@/api/types"
import { en } from "./en"
import { fr } from "./fr"
import { definirLangue, initialiserLangue, langueCourante, langueStockee, LANGUE_STORAGE_KEY, t, tn } from "./index"

const compte = (surcharges: Partial<CompteARebours>): CompteARebours => ({
  date_examen: "2027-05-24",
  jours_restants: 100,
  session_label: "BAC 2027",
  estimee: false,
  ...surcharges,
})

afterEach(async () => {
  localStorage.clear()
  await definirLangue("fr", { persister: false })
})

function variables(texte: string): string[] {
  return [...texte.matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort()
}

describe("dictionnaires", () => {
  it("l'anglais ne traduit que des clés qui existent en français", () => {
    const inconnues = Object.keys(en).filter((cle) => !(cle in fr))
    expect(inconnues).toEqual([])
  })

  it("chaque traduction garde exactement les variables du français", () => {
    for (const [cle, anglais] of Object.entries(en)) {
      expect(variables(anglais as string), cle).toEqual(variables(fr[cle as keyof typeof fr]))
    }
  })

  it("toute la tranche française est traduite en anglais", () => {
    const manquantes = Object.keys(fr).filter((cle) => !(cle in en))
    expect(manquantes).toEqual([])
  })
})

describe("t / tn", () => {
  it("français par défaut, variables interpolées", () => {
    expect(langueCourante()).toBe("fr")
    expect(t("nav.reviser")).toBe("Réviser")
    expect(t("nav.menu_description", { site: "Edukamer" })).toBe("Navigation principale d'Edukamer")
  })

  it("une variable absente reste visible plutôt que de disparaître", () => {
    expect(t("nav.menu_description")).toBe("Navigation principale d'{site}")
  })

  it("bascule en anglais puis revient", async () => {
    await definirLangue("en")
    expect(langueCourante()).toBe("en")
    expect(t("nav.reviser")).toBe("Revise")
    expect(document.documentElement.lang).toBe("en")
    await definirLangue("fr")
    expect(t("nav.reviser")).toBe("Réviser")
    expect(document.documentElement.lang).toBe("fr")
  })

  it("une clé sans traduction retombe sur le français", async () => {
    await definirLangue("en")
    const cle = "nav.reviser" as const
    const sauvegarde = en[cle]
    delete en[cle]
    try {
      expect(t(cle)).toBe("Réviser")
    } finally {
      en[cle] = sauvegarde
    }
  })

  it("tn choisit la forme du pluriel (clés _one / _other)", () => {
    // Aucune clé de pluriel n'existe encore dans la tranche traduite : on vérifie le mécanisme
    // sur le dictionnaire source en y ajoutant temporairement deux clés.
    const source = fr as unknown as Record<string, string>
    source["test.copie_one"] = "{n} copie"
    source["test.copie_other"] = "{n} copies"
    try {
      expect(tn("test.copie" as never, 1)).toBe("1 copie")
      expect(tn("test.copie" as never, 3)).toBe("3 copies")
    } finally {
      delete source["test.copie_one"]
      delete source["test.copie_other"]
    }
  })
})

describe("persistance", () => {
  it("garde le choix et le retrouve au démarrage", async () => {
    await definirLangue("en")
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("en")
    expect(langueStockee()).toBe("en")
    await definirLangue("fr", { persister: false })
    await initialiserLangue()
    expect(langueCourante()).toBe("en")
  })

  it("sans choix mémorisé ou avec une valeur invalide, reste en français", async () => {
    await initialiserLangue()
    expect(langueCourante()).toBe("fr")
    localStorage.setItem(LANGUE_STORAGE_KEY, "klingon")
    expect(langueStockee()).toBeNull()
    await initialiserLangue()
    expect(langueCourante()).toBe("fr")
  })
})

describe("compte à rebours traduit", () => {
  it("français inchangé", () => {
    expect(formatCompteARebours(compte({ jours_restants: 244 }))).toBe("J-244")
    expect(formatCompteARebours(compte({ jours_restants: 1 }))).toBe("demain")
    expect(formatCompteARebours(compte({ jours_restants: 0 }))).toBe("c'est aujourd'hui")
    expect(formatCompteARebours(compte({ estimee: true, date_examen: "2028-05-24" }))).toBe("vers mai 2028")
    expect(formatCompteARebours(compte({ jours_restants: -3 }))).toBe("")
  })

  it("anglais : jours, demain et mois estimé", async () => {
    await definirLangue("en")
    expect(formatCompteARebours(compte({ jours_restants: 244 }))).toBe("D-244")
    expect(formatCompteARebours(compte({ jours_restants: 1 }))).toBe("tomorrow")
    expect(formatCompteARebours(compte({ estimee: true, date_examen: "2028-05-24" }))).toBe("around May 2028")
  })
})
