import { describe, expect, it } from "vitest"

import type { ThemeFrequent } from "@/api/types"
import { grouperParChapitre } from "./chapitres"

const theme = (id: number, chapitre: ThemeFrequent["chapitre"], niveau: "solide" | "en_cours" | "maitrise" | null = null): ThemeFrequent => ({
  id, tag: `thème ${id}`, nb_epreuves: 10 - id, frequence_pct: 50, quiz_disponible: true, chapitre,
  maitrise: niveau ? { taux: 80, nb_reponses: 5, niveau } : null,
})

const reels = { id: 601, titre: "Nombres réels", numero: "II", module: "Relations", ordre: [13, 2] as [number, number] }
const calcul = { id: 602, titre: "Calcul littéral", numero: "III", module: "Relations", ordre: [13, 3] as [number, number] }
const stats = { id: 606, titre: "Statistiques", numero: "II", module: "Organisation", ordre: [14, 2] as [number, number] }

describe("grouperParChapitre", () => {
  it("range les chapitres dans l'ordre du programme, pas dans celui de la fréquence", () => {
    const groupes = grouperParChapitre([theme(1, stats), theme(2, calcul), theme(3, reels)])
    expect(groupes.map((g) => g.titre)).toEqual(["Nombres réels", "Calcul littéral", "Statistiques"])
  })

  it("garde l'ordre de fréquence à l'intérieur d'un chapitre", () => {
    const groupes = grouperParChapitre([theme(1, reels), theme(2, calcul), theme(3, reels)])
    expect(groupes[0].themes.map((t) => t.id)).toEqual([1, 3])
  })

  it("met les thèmes sans chapitre en dernier, sous un groupe sans titre", () => {
    const groupes = grouperParChapitre([theme(1, null), theme(2, reels), theme(3, undefined)])
    expect(groupes.map((g) => g.cle)).toEqual(["c601", "autres"])
    expect(groupes[1].titre).toBe("")
    expect(groupes[1].themes.map((t) => t.id)).toEqual([1, 3])
  })

  it("compte les thèmes tentés et ceux que l'élève tient (solide ou maîtrisé)", () => {
    const [g] = grouperParChapitre([theme(1, reels, "solide"), theme(2, reels, "en_cours"), theme(3, reels, "maitrise"), theme(4, reels)])
    expect({ tentes: g.tentes, solides: g.solides }).toEqual({ tentes: 3, solides: 2 })
  })

  it("un visiteur (aucune maîtrise) n'a ni tentés ni solides", () => {
    const [g] = grouperParChapitre([theme(1, reels), theme(2, reels)])
    expect({ tentes: g.tentes, solides: g.solides }).toEqual({ tentes: 0, solides: 0 })
  })
})
