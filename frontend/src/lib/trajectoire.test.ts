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

  it("quand la cible est hors de portée, dit le pas suivant plutôt qu'un verdict", () => {
    const plan = {
      jour_j: "2027-05-31", themes_a_consolider: 90, par_semaine: 4,
      cette_semaine: { debut: "2026-11-16", fin: "2026-11-22", cible: 4, faits: 1 },
      etapes: [],
      une_seance_de_plus: { couverture_projetee: 0.24 },
    }
    const t = trajectoire({
      couverture_projetee: 0.17, suffisant: false, seances_de_plus_par_semaine: null, atteignable: false,
      seances_par_semaine: 2.3, plan,
    })
    expect(phraseTrajectoire(t, "normal")).toBe(
      "À ce rythme (2,3 séances par semaine), tu couvres 17 % de l'essentiel le jour J. "
        + "Avec une séance de plus par semaine, tu passes à 24 %.",
    )
    // Une séance de plus qui ne change pas le chiffre arrondi : l'ancien texte, pas « tu passes à 17 % ».
    const sansGain = { ...t, plan: { ...plan, une_seance_de_plus: { couverture_projetee: 0.171 } } }
    expect(phraseTrajectoire(sansGain, "normal")).toMatch(/vise ce qui tombe le plus/)
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

  it("ne projette pas un pourcentage minuscule : sous 10 %, une phrase de début", () => {
    const t = trajectoire({ couverture_projetee: 0.01, suffisant: false, seances_de_plus_par_semaine: null, seances_par_semaine: 1 })
    expect(phraseTrajectoire(t, "normal")).toBe("Tu viens de te lancer : chaque séance compte. Vise d'abord ce qui tombe le plus.")
  })
})
