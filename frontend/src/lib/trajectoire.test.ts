import { describe, expect, it } from "vitest"

import type { Trajectoire } from "@/api/types"
import { formatDepuis } from "@/lib/formatDepuis"
import { phraseTrajectoire } from "@/lib/trajectoire"

function trajectoire(surcharge: Partial<Trajectoire> = {}): Trajectoire {
  return {
    jours_restants: 60,
    fenetre_jours: 21,
    seances_fenetre: 6,
    seances_par_semaine: 2,
    couverture_actuelle: 0.4,
    couverture_projetee: 0.85,
    cible: 0.8,
    suffisant: true,
    seances_de_plus_par_semaine: null,
    atteignable: true,
    ...surcharge,
  }
}

describe("phraseTrajectoire", () => {
  it("ne projette rien sans rythme mesurable, et dit ce qui manque pour en avoir un", () => {
    expect(phraseTrajectoire(trajectoire({ seances_fenetre: 1, couverture_projetee: null, suffisant: null }), "normal"))
      .toBe("Pas encore de rythme mesurable : 2 séances de plus et on te dit où tu vas.")
  })

  it("dit continue quand le rythme suffit", () => {
    expect(phraseTrajectoire(trajectoire(), "normal"))
      .toBe("À ce rythme (2 séances par semaine), tu couvres 85 % de l'essentiel le jour J. Continue comme ça.")
  })

  it("dit calmement combien de séances de plus quand ça ne suffit pas", () => {
    const t = trajectoire({ couverture_projetee: 0.62, suffisant: false, seances_de_plus_par_semaine: 1, seances_par_semaine: 1.5 })
    expect(phraseTrajectoire(t, "normal"))
      .toBe("À ce rythme (1,5 séance par semaine), tu couvres 62 % de l'essentiel le jour J. Une séance de plus par semaine et tu y es.")
  })

  it("quand la cible est hors de portée, oriente vers l'essentiel sans reproche", () => {
    const t = trajectoire({ couverture_projetee: 0.45, suffisant: false, seances_de_plus_par_semaine: null, atteignable: false })
    expect(phraseTrajectoire(t, "normal")).toMatch(/vise ce qui tombe le plus/)
    expect(phraseTrajectoire(t, "normal")).not.toMatch(/retard/)
  })
})

describe("formatDepuis", () => {
  const aujourdhui = new Date(2026, 8, 29) // mardi 29 septembre 2026

  it("nomme le jour à moins d'une semaine, la date au-delà", () => {
    expect(formatDepuis("2026-09-29", aujourdhui)).toBe("ce matin")
    expect(formatDepuis("2026-09-28", aujourdhui)).toBe("hier")
    expect(formatDepuis("2026-09-25", aujourdhui)).toBe("vendredi")
    expect(formatDepuis("2026-09-12", aujourdhui)).toBe("le 12 septembre")
  })
})
