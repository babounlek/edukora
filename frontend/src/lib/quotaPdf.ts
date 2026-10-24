import type { QuotaPdf } from "@/api/types"
import { localeCourante, t, tn } from "@/lib/i18n"

/**
 * Quota quotidien de téléchargements PDF - la partie sans réseau (le hook est dans useQuotaPdf.ts) : l'événement qui
 * dit « le compteur a changé » et les phrases affichées. Le serveur décide de tout (access.quota) ; ici on ne fait que
 * le dire à l'élève, dans sa langue.
 */

export const EVENEMENT_QUOTA_PDF = "edukora:quota-pdf"

/** À appeler quand un PDF vient d'être livré (ou refusé) : tout compteur affiché se met à jour depuis le serveur. */
export function signalerChangementQuota() {
  window.dispatchEvent(new Event(EVENEMENT_QUOTA_PDF))
}

/** L'heure de remise à zéro, dans le fuseau décidé par le serveur (Douala), pas celui de l'appareil. */
export function heureDeReinitialisation(quota: Pick<QuotaPdf, "reinitialisation" | "fuseau">): string {
  const date = new Date(quota.reinitialisation)
  if (Number.isNaN(date.getTime())) return ""
  let heure: string
  try {
    heure = new Intl.DateTimeFormat(localeCourante(), { hour: "2-digit", minute: "2-digit", timeZone: quota.fuseau }).format(date)
  } catch {
    heure = new Intl.DateTimeFormat(localeCourante(), { hour: "2-digit", minute: "2-digit" }).format(date)
  }
  const ville = (quota.fuseau.split("/").pop() ?? quota.fuseau).replace(/_/g, " ")
  return t("qpdf.heure", { heure, ville })
}

/** La phrase d'un quota épuisé, selon ce qui limite (le quota du demandeur, son réseau, le budget des anonymes). */
export function messageLimiteAtteinte(quota: QuotaPdf): string {
  if (quota.motif === "plafond_reseau") return t("qpdf.plafond_reseau")
  if (quota.motif === "budget_global") return t("qpdf.budget_global")
  return t("qpdf.epuise", { heure: heureDeReinitialisation(quota) })
}

export function messageRestants(restant: number): string {
  return tn("qpdf.restants", restant)
}
