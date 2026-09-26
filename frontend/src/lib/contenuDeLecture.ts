/**
 * Chemins d'API qui portent le contenu LU par l'élève (épreuve, cours) : ceux qu'on garde
 * pour la lecture hors connexion. Volontairement une liste fermée - un cache large
 * mettrait en mémoire des réponses personnelles (compte, paiements, séances) qui n'ont
 * rien à y faire. Partagé entre la config du service worker (vite.config.ts) et ses tests.
 */
export const CONTENU_DE_LECTURE = /\/(catalog\/(lessons|cours)|access\/(read|cours\/read))\/[^/]+\/$/
