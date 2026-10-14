import { afterEach, describe, expect, it } from "vitest"

import { formatCompteARebours } from "@/components/CompteAReboursBadge"
import type { CompteARebours } from "@/api/types"
import { en } from "./en"
import { fr } from "./fr"
import {
  cheminDansLangue,
  definirLangue,
  initialiserLangue,
  langueCourante,
  langueDuChemin,
  langueStockee,
  LANGUE_STORAGE_KEY,
  retirerPrefixeLangue,
  t,
  tn,
  urlDansLangue,
} from "./index"

const compte = (surcharges: Partial<CompteARebours>): CompteARebours => ({
  date_examen: "2027-05-24",
  jours_restants: 100,
  session_label: "BAC 2027",
  estimee: false,
  ...surcharges,
})

afterEach(async () => {
  localStorage.clear()
  window.history.replaceState(null, "", "/")
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
  it("garde le choix et, sans préfixe, renvoie vers la version anglaise de la même page", async () => {
    await definirLangue("en")
    expect(localStorage.getItem(LANGUE_STORAGE_KEY)).toBe("en")
    expect(langueStockee()).toBe("en")
    await definirLangue("fr", { persister: false })
    window.history.replaceState(null, "", "/cm/epreuves?cursus=3#haut")
    expect(await initialiserLangue()).toBe("/en")
    expect(langueCourante()).toBe("en")
    expect(window.location.pathname + window.location.search + window.location.hash).toBe("/en/cm/epreuves?cursus=3#haut")
  })

  it("sans choix mémorisé ou avec une valeur invalide, reste en français", async () => {
    expect(await initialiserLangue()).toBe("")
    expect(langueCourante()).toBe("fr")
    localStorage.setItem(LANGUE_STORAGE_KEY, "klingon")
    expect(langueStockee()).toBeNull()
    expect(await initialiserLangue()).toBe("")
    expect(langueCourante()).toBe("fr")
    expect(window.location.pathname).toBe("/")
  })
})

describe("langue dans l'URL", () => {
  it("un préfixe /en donne l'anglais, même si le navigateur a choisi le français, sans toucher au choix", async () => {
    localStorage.setItem(LANGUE_STORAGE_KEY, "fr")
    window.history.replaceState(null, "", "/en/cm/cours")
    expect(await initialiserLangue()).toBe("/en")
    expect(langueCourante()).toBe("en")
    expect(langueStockee()).toBe("fr")
    expect(window.location.pathname).toBe("/en/cm/cours")
  })

  it("une URL sans préfixe reste en français quand rien n'est choisi", async () => {
    window.history.replaceState(null, "", "/cm/cours")
    expect(await initialiserLangue()).toBe("")
    expect(langueCourante()).toBe("fr")
  })

  it("lit et retire le préfixe sans confondre un segment voisin", () => {
    expect(langueDuChemin("/en")).toBe("en")
    expect(langueDuChemin("/en/cm")).toBe("en")
    expect(langueDuChemin("/cm/en")).toBeNull()
    expect(langueDuChemin("/english")).toBeNull()
    expect(retirerPrefixeLangue("/en/cm/cours")).toBe("/cm/cours")
    expect(retirerPrefixeLangue("/en")).toBe("/")
    expect(retirerPrefixeLangue("/cm/cours")).toBe("/cm/cours")
  })

  it("place un chemin dans une langue, sans doubler le préfixe", () => {
    expect(cheminDansLangue("/cm/cours", "en")).toBe("/en/cm/cours")
    expect(cheminDansLangue("/en/cm/cours", "en")).toBe("/en/cm/cours")
    expect(cheminDansLangue("/", "en")).toBe("/en")
    expect(cheminDansLangue("/en/cm/cours", "fr")).toBe("/cm/cours")
    expect(cheminDansLangue("/en", "fr")).toBe("/")
    expect(cheminDansLangue("/cm/cours", "fr")).toBe("/cm/cours")
  })

  it("l'URL de l'autre langue garde la requête et l'ancre", () => {
    const ici = { pathname: "/cm/epreuves/maths", search: "?q=2", hash: "#corrige" }
    expect(urlDansLangue("en", ici)).toBe("/en/cm/epreuves/maths?q=2#corrige")
    expect(urlDansLangue("fr", { ...ici, pathname: "/en/cm/epreuves/maths" })).toBe("/cm/epreuves/maths?q=2#corrige")
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
