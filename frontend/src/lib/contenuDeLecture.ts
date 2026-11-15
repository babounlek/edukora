/**
 * Chemins d'API qui portent le contenu LU par l'élève (épreuve, cours) : ceux qu'on garde
 * pour la lecture hors connexion. Volontairement une liste fermée - un cache large
 * mettrait en mémoire des réponses personnelles (compte, paiements, séances) qui n'ont
 * rien à y faire. Partagé entre la config du service worker (vite.config.ts) et ses tests.
 */
export const CONTENU_DE_LECTURE = new RegExp(
  [
    "\\/(catalog\\/(lessons|cours)|access\\/(read|cours\\/read))\\/[^/]+\\/$",
    // R21 : un exercice lu seul depuis un thème, et la liste des exercices du thème.
    "\\/catalog\\/themes\\/\\d+\\/exercices\\/\\d+\\/lecture\\/$",
    "\\/catalog\\/cursus\\/\\d+\\/themes-frequents\\/\\d+\\/exercices\\/$",
  ].join("|"),
)
