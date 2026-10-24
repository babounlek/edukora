import { describe, expect, it, vi } from "vitest"

import type { QuotaPdf } from "@/api/types"

import { EVENEMENT_QUOTA_PDF, heureDeReinitialisation, messageLimiteAtteinte, messageRestants, signalerChangementQuota } from "./quotaPdf"

function quota(surcharge: Partial<QuotaPdf> = {}): QuotaPdf {
  return {
    actif: true, profil: "visiteur", limite: 3, utilise: 3, restant: 0, motif: "quota_depasse",
    reinitialisation: "2026-10-25T00:00:00+01:00", fuseau: "Africa/Douala", gratuits: [], ...surcharge,
  }
}

describe("quotaPdf", () => {
  it("dit combien il reste, au singulier et au pluriel", () => {
    expect(messageRestants(1)).toBe("Il te reste 1 téléchargement PDF aujourd'hui.")
    expect(messageRestants(2)).toBe("Il te reste 2 téléchargements PDF aujourd'hui.")
  })

  it("donne l'heure de remise à zéro dans le fuseau du serveur, pas celui de l'appareil", () => {
    const heure = heureDeReinitialisation(quota())

    expect(heure).toMatch(/^00[:h]00 \(heure de Douala\)$/)
  })

  it("annonce un quota épuisé avec l'heure de remise à zéro", () => {
    const message = messageLimiteAtteinte(quota())

    expect(message).toContain("limite quotidienne")
    expect(message).toContain("Douala")
  })

  it("distingue le plafond du réseau et le budget des visiteurs du quota personnel", () => {
    expect(messageLimiteAtteinte(quota({ motif: "plafond_reseau" }))).toContain("depuis ta connexion")
    expect(messageLimiteAtteinte(quota({ motif: "budget_global" }))).toContain("sans compte")
  })

  it("prévient les compteurs affichés quand un téléchargement a eu lieu", () => {
    const ecoute = vi.fn()
    window.addEventListener(EVENEMENT_QUOTA_PDF, ecoute)

    signalerChangementQuota()

    expect(ecoute).toHaveBeenCalledTimes(1)
    window.removeEventListener(EVENEMENT_QUOTA_PDF, ecoute)
  })
})
