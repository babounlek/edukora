import { describe, expect, it } from "vitest"

import appSource from "../../App.tsx?raw"
import { cheminAnglais, cheminInterne, PATRONS_INTERNES, SEGMENTS_EN } from "./segments"

// Segments volontairement identiques dans les deux langues : ni à traduire, ni à mettre dans la table.
const IDENTIQUES = ["quiz", "session", "simulation", "revision"]

/** Un chemin d'exemple pour un patron : « :slug » devient une valeur qui ne ressemble à aucun segment. */
function exemple(patron: string): string {
  return patron.replace(/:(\w+)/g, (_, nom: string) => `valeur-${nom}`)
}

describe("traduction des segments d'URL", () => {
  it("traduit les chemins publics dans les deux sens", () => {
    expect(cheminAnglais("/cm/epreuves/physics-gce-ordinary-level-2023-paper-1/lire")).toBe(
      "/cm/past-papers/physics-gce-ordinary-level-2023-paper-1/read",
    )
    expect(cheminInterne("/cm/past-papers/physics-gce-ordinary-level-2023-paper-1/read")).toBe(
      "/cm/epreuves/physics-gce-ordinary-level-2023-paper-1/lire",
    )
    expect(cheminAnglais("/cm/cours")).toBe("/cm/lessons")
    expect(cheminAnglais("/cm/themes-frequents/12/exercices/7")).toBe("/cm/frequent-topics/12/exercises/7")
    expect(cheminAnglais("/tarifs")).toBe("/pricing")
    expect(cheminAnglais("/quiz/essai/resultat")).toBe("/quiz/trial/result")
    expect(cheminAnglais("/inedit/tentative/5/resultat")).toBe("/mock/attempt/5/result")
  })

  it("ne traduit jamais un segment dynamique (slug, id, pays)", () => {
    // Un slug qui s'appellerait comme un segment fixe reste intact.
    expect(cheminAnglais("/cm/epreuves/cours")).toBe("/cm/past-papers/cours")
    expect(cheminAnglais("/cours/epreuves")).toBe("/lessons/epreuves")
    expect(cheminInterne("/cm/past-papers/lessons")).toBe("/cm/epreuves/lessons")
  })

  it("rend tel quel un chemin qu'aucune route ne connaît, et garde le slash final", () => {
    expect(cheminAnglais("/n-importe/quoi/du-tout")).toBe("/n-importe/quoi/du-tout")
    expect(cheminAnglais("/")).toBe("/")
    expect(cheminAnglais("/cm/cours/")).toBe("/cm/lessons/")
    expect(cheminInterne("/cm/lessons/")).toBe("/cm/cours/")
    // Une ancienne forme française sous /en n'est pas une route anglaise : rendue telle quelle.
    expect(cheminInterne("/cm/epreuves/x")).toBe("/cm/epreuves/x")
  })

  it("chaque patron fait l'aller-retour sans perte", () => {
    for (const patron of PATRONS_INTERNES) {
      const interne = exemple(patron)
      const anglais = cheminAnglais(interne)
      expect(cheminInterne(anglais), patron).toBe(interne)
      // Et le chemin anglais ne contient plus aucun segment fixe français.
      for (const [fr, en] of Object.entries(SEGMENTS_EN)) {
        if (patron.split("/").includes(fr)) {
          expect(anglais.split("/"), `${patron} -> ${anglais}`).not.toContain(fr)
          expect(anglais.split("/"), `${patron} -> ${anglais}`).toContain(en)
        }
      }
    }
  })

  it("la table est cohérente : pas de doublon, pas de segment orphelin", () => {
    const valeurs = Object.values(SEGMENTS_EN)
    expect(new Set(valeurs).size).toBe(valeurs.length)
    // Un segment anglais ne peut pas être aussi un segment français à traduire.
    for (const en of valeurs) expect(Object.keys(SEGMENTS_EN)).not.toContain(en)
    const fixes = new Set(PATRONS_INTERNES.flatMap((p) => p.split("/")).filter((s) => s && !s.startsWith(":")))
    for (const fr of Object.keys(SEGMENTS_EN)) expect(fixes.has(fr), `« ${fr} » n'est dans aucune route`).toBe(true)
  })

  // Le garde-fou : ajouter une route sans traduire ses segments fait échouer ce test, au lieu de laisser
  // un segment français dans les URL anglaises.
  it("tout segment fixe d'une route est traduit (ou déclaré identique)", () => {
    const fixes = new Set(PATRONS_INTERNES.flatMap((p) => p.split("/")).filter((s) => s && !s.startsWith(":")))
    for (const segment of fixes) {
      expect(
        segment in SEGMENTS_EN || IDENTIQUES.includes(segment),
        `segment « ${segment} » : ajouter sa traduction dans segments-url.json, ou le déclarer identique ici`,
      ).toBe(true)
    }
  })

  it("couvre exactement les routes déclarées dans App.tsx", () => {
    const pays = appSource.slice(
      appSource.indexOf('<Route path="/:country"'),
      appSource.indexOf("</Route>", appSource.indexOf('<Route path="/:country"')),
    )
    const sousPays = [...pays.matchAll(/path="([^"]+)"/g)].map((m) => m[1]).filter((p) => !p.startsWith("/"))
    const reste = appSource.slice(appSource.indexOf("</Route>", appSource.indexOf('<Route path="/:country"')))
    const racines = [...reste.matchAll(/path="([^"]+)"/g)].map((m) => m[1]).filter((p) => p !== "*")
    const declarees = [...sousPays.map((p) => `/:country/${p}`), ...racines].sort()
    expect(declarees).toEqual([...PATRONS_INTERNES].sort())
  })
})
