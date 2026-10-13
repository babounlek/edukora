import { tn } from "@/lib/i18n"

// Délai annoncé à l'élève pour la vérification d'un paiement manuel (Orange Money / MTN MoMo)
// par l'équipe. Une seule source pour tous les textes (abonnement, tarifs, mes paiements,
// CGU) : si le délai réellement tenu change, on ne modifie que cette ligne.
export const DELAI_VERIFICATION_PAIEMENT_MANUEL_HEURES = 3
export const DELAI_VERIFICATION_PAIEMENT_MANUEL = "3 heures"

/** Le même délai dans la langue courante ("3 heures" / "3 hours") - pour les pages traduites. */
export function delaiVerificationPaiementAffiche(): string {
  return tn("delai.heures", DELAI_VERIFICATION_PAIEMENT_MANUEL_HEURES)
}
