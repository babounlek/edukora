/**
 * Saisie du code PIN d'un profil, demandée depuis du code non-React (voir
 * changerProfilActif.ts) : un composant monté une fois pour toutes (PinDialogs) enregistre
 * son gestionnaire ici, et l'appelant attend simplement le code saisi.
 */

export interface DemandePinProfil {
  prenom: string
  /** Message d'erreur de la tentative précédente (code incorrect, trop d'essais...). */
  erreur?: string
}

type GestionnairePin = (demande: DemandePinProfil) => Promise<string | null>

let gestionnaire: GestionnairePin | null = null

export function setGestionnairePinProfil(g: GestionnairePin | null) {
  gestionnaire = g
}

/** Le code saisi, ou null si l'utilisateur annule (ou qu'aucune interface n'est montée). */
export function demanderPinProfil(demande: DemandePinProfil): Promise<string | null> {
  return gestionnaire ? gestionnaire(demande) : Promise.resolve(null)
}

/** Levée quand l'utilisateur renonce à saisir le code : à ignorer silencieusement. */
export class PinAnnule extends Error {
  constructor() {
    super("Saisie du code annulée.")
  }
}
