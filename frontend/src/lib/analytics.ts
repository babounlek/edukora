import { apiRequest } from "@/api/client"

// Même vocabulaire fermé que analytics.models.EventName côté backend - voir sa
// docstring pour la raison (jamais un nom d'évènement libre).
export type AnalyticsEventName =
  | "search_no_results"
  | "payment_initiated"
  | "payment_succeeded"
  | "payment_failed"
  | "payment_timeout"
  | "quiz_started"
  | "quiz_completed"
  | "inedit_tentative_started"
  | "inedit_tentative_completed"
  | "pdf_sujet_landing"
  | "pdf_sujet_inedit_landing"
  | "pdf_fiche_sujet_landing"
  | "pdf_fiche_corrige_landing"

/**
 * Fire-and-forget : voir l'audit UX, reco 5.3. Ne doit jamais faire échouer ni
 * ralentir le parcours qu'il observe - une erreur réseau ou un rejet serveur est
 * juste avalé, jamais remonté à l'appelant. `auth: "optional"` : associe
 * l'utilisateur connecté quand il y en a un, sans jamais l'exiger (la majorité des
 * évènements utiles - recherche sans résultat, abandon de paiement avant connexion -
 * viennent justement d'un visiteur pas encore authentifié).
 */
export function trackEvent(name: AnalyticsEventName, properties?: Record<string, unknown>) {
  apiRequest("/analytics/events/", { method: "POST", body: { name, properties }, auth: "optional" }).catch(() => {})
}
