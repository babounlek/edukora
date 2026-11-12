import { describe, expect, it } from "vitest"

import type { CampagneEnCours } from "@/api/types"
import { messageParents } from "@/lib/messageParents"
import { PRIX_MOIS_FCFA } from "@/lib/tarifs"

const campagne = { prix: 13500, prix_reference: 15000, fin: "2026-11-11T22:59:59Z" } as CampagneEnCours

describe("messageParents", () => {
  it("dit ce que l'élève veut, le prix, le moyen de payer et l'absence de prélèvement", () => {
    const message = messageParents({ examen: "BEPC", contenu: "lire le corrigé de « SVT BEPC 2025 »" })
    expect(message).toContain("le BEPC")
    expect(message).toContain("lire le corrigé de « SVT BEPC 2025 »")
    expect(message).toContain("2 000 FCFA par mois")
    expect(message).toContain("Mobile Money")
    expect(message).toContain("sans prélèvement automatique")
    expect(message.endsWith("Tous les détails ici :")).toBe(true)
  })

  it("prend le prix de la campagne, avec la date limite et le prix de référence", () => {
    const message = messageParents({ campagne })
    expect(message).toContain("13 500 FCFA")
    expect(message).toContain("au lieu de 15 000 FCFA jusqu'au 11 novembre")
  })

  it("sans campagne, le prix vient de la constante partagée (jamais un nombre recopié)", () => {
    expect(messageParents({})).toContain(`${PRIX_MOIS_FCFA.toLocaleString("fr-FR").replace(/\s/g, " ")} FCFA`.replace(/ | /g, " "))
  })

  it("reste lisible sans examen ni contenu", () => {
    const message = messageParents({})
    expect(message).toContain("mon examen")
    expect(message).toContain("corrigés complets")
  })
})
