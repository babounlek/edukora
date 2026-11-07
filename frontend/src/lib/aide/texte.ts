import { delaiVerificationPaiementAffiche } from "@/lib/delaiVerificationPaiement"
import { CONTACT_EMAIL, CONTACT_WHATSAPP_AFFICHAGE, EDITEUR_NOM, SITE_NAME } from "@/lib/site"

/**
 * Les valeurs qu'un article écrit `{{whatsapp}}`, `{{email}}`, `{{delai_verification}}`, `{{site}}` ou `{{editeur}}` :
 * elles existent déjà dans le code (lib/site.ts, lib/delaiVerificationPaiement.ts), donc un numéro ou un délai corrigé
 * une fois l'est dans toute l'aide. Un gabarit inconnu est laissé tel quel (visible, donc vite repéré) plutôt que remplacé par du vide.
 */
function valeurs(): Record<string, string> {
  return {
    site: SITE_NAME,
    whatsapp: CONTACT_WHATSAPP_AFFICHAGE,
    email: CONTACT_EMAIL,
    editeur: EDITEUR_NOM,
    delai_verification: delaiVerificationPaiementAffiche(),
  }
}

export function remplirGabarits(texte: string): string {
  const table = valeurs()
  return texte.replace(/\{\{\s*(\w+)\s*\}\}/g, (brut, nom: string) => (nom in table ? table[nom] : brut))
}
