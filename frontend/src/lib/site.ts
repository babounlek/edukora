/**
 * Nom et domaine de la plateforme - provisoires tant que le produit est en
 * conception. Toujours passer par ces constantes plutôt que d'écrire "EduKamer"
 * ou le domaine en dur : un rebuild suffit alors à tout changer d'un coup.
 */
export const SITE_NAME = import.meta.env.VITE_SITE_NAME ?? "EduKamer"
export const SITE_URL = (import.meta.env.VITE_SITE_URL ?? "https://edukamer.cm").replace(/\/$/, "")
export const SITE_DOMAIN = SITE_URL.replace(/^https?:\/\//, "")
