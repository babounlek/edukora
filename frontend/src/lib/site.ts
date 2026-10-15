/**
 * Nom et domaine de la plateforme - provisoires tant que le produit est en
 * conception. Toujours passer par ces constantes plutôt que d'écrire le nom
 * ou le domaine en dur : un rebuild suffit alors à tout changer d'un coup.
 */
export const SITE_NAME = import.meta.env.VITE_SITE_NAME ?? "EduKora"
export const SITE_URL = (import.meta.env.VITE_SITE_URL ?? "https://edukora.africa").replace(/\/$/, "")
export const SITE_DOMAIN = SITE_URL.replace(/^https?:\/\//, "")

// Un seul endroit pour les moyens de contact : ils figuraient en triple (pied de page, À propos,
// mentions légales), et un numéro corrigé à un endroit restait faux aux deux autres.
export const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

// L'entreprise qui édite la plateforme (mentions légales, CGU, confidentialité, pied de page). Le téléphone est celui
// de l'éditeur, distinct du numéro WhatsApp ci-dessous : deux moyens de contact, deux constantes.
export const EDITEUR_NOM = "Kora SARL"
export const CONTACT_TELEPHONE_URL = "tel:+237698192991"
export const CONTACT_TELEPHONE_AFFICHAGE = "+237 698 19 29 91"

export const CONTACT_WHATSAPP_URL = "https://wa.me/237670401393"
export const CONTACT_WHATSAPP_AFFICHAGE = "+237 670 40 13 93"
