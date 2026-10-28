import { render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it } from "vitest"

import type { Campagne } from "@/api/types"
import { definirLangue } from "@/lib/i18n"
import { nomCampagne, urgenceCampagne } from "@/lib/campagne"
import { BandeauCampagne } from "./BandeauCampagne"

const JOUR = 86_400_000

function campagne(finDansMs: number): Campagne {
  return {
    id: 1,
    nom: "Offre fondateurs",
    nom_en: "Founders offer",
    pourcentage: 20,
    debut: new Date(Date.now() - JOUR).toISOString(),
    fin: new Date(Date.now() + finDansMs).toISOString(),
  }
}

describe("urgenceCampagne", () => {
  it("ne dit rien tant que la date limite est loin", () => {
    expect(urgenceCampagne(campagne(10 * JOUR).fin)).toBeNull()
  })

  it("annonce les jours restants dans la dernière semaine", () => {
    expect(urgenceCampagne(campagne(3 * JOUR - 1000).fin)).toBe("Plus que 3 jours")
  })

  it("annonce le dernier jour", () => {
    expect(urgenceCampagne(campagne(5 * 3_600_000).fin)).toBe("Dernier jour")
  })

  it("ne dit rien une fois la campagne finie", () => {
    expect(urgenceCampagne(campagne(-1000).fin)).toBeNull()
  })
})

describe("BandeauCampagne", () => {
  it("annonce la remise, le prix avant/après et la date limite", () => {
    render(<BandeauCampagne campagne={campagne(10 * JOUR)} prix={12000} prixReference={15000} />)

    expect(screen.getByText("Offre fondateurs : −20 % sur l'abonnement")).toBeInTheDocument()
    expect(screen.getByText(/Prix promotionnel : 12 000 FCFA au lieu de 15 000 FCFA, jusqu'au/)).toBeInTheDocument()
    expect(screen.queryByText(/Plus que|Dernier jour/)).not.toBeInTheDocument()
  })

  it("ajoute l'urgence dans les derniers jours", () => {
    render(<BandeauCampagne campagne={campagne(2 * JOUR - 1000)} prix={12000} prixReference={15000} />)

    expect(screen.getByText("Plus que 2 jours")).toBeInTheDocument()
  })
})

describe("nomCampagne", () => {
  afterEach(async () => {
    localStorage.clear()
    await definirLangue("fr")
  })

  it("donne le nom français en français", () => {
    expect(nomCampagne({ nom: "Offre de la rentrée", nom_en: "Back-to-school offer" })).toBe("Offre de la rentrée")
  })

  it("donne le nom anglais en anglais, et le français à défaut", async () => {
    await definirLangue("en")
    expect(nomCampagne({ nom: "Offre de la rentrée", nom_en: "Back-to-school offer" })).toBe("Back-to-school offer")
    expect(nomCampagne({ nom: "Offre de la rentrée", nom_en: "" })).toBe("Offre de la rentrée")
  })
})
