/**
 * Le jeton d'« invité » : essayer une épreuve inédite gratuite SANS s'inscrire (voir users.invites côté backend).
 *
 * Gardé dans localStorage, contrairement au vrai jeton d'accès (mémoire seulement, voir api/client.ts) : il doit survivre
 * à un rechargement, sans cookie de refresh pour le reconstituer, et il ne vaut presque rien (aucune identité, aucun
 * accès hors /inedit/, copie d'une épreuve offerte). Le client ne le joint qu'aux appels `/inedit/` : pour tout le
 * reste du site, ce visiteur reste anonyme.
 *
 * Pas de React ici : le client API le lit directement.
 */

const CLE = "edukora-invite"

// Repli quand localStorage refuse d'écrire : sans lui, l'invité créé serait perdu à la première requête.
let memoire: string | null = null

export const EVENEMENT_INVITE = "edukora:invite"

export function getJetonInvite(): string | null {
  try {
    return localStorage.getItem(CLE) || null
  } catch {
    return null
  }
}

export function setJetonInvite(jeton: string): void {
  try {
    localStorage.setItem(CLE, jeton)
  } catch {
    // stockage indisponible (navigation privée stricte) : l'essai tiendra le temps de la page, jamais au-delà
    memoire = jeton
  }
  window.dispatchEvent(new Event(EVENEMENT_INVITE))
}

export function clearJetonInvite(): void {
  memoire = null
  try {
    localStorage.removeItem(CLE)
  } catch {
    // rien à effacer
  }
  window.dispatchEvent(new Event(EVENEMENT_INVITE))
}

/** Le jeton à joindre, repli mémoire compris. */
export function jetonInviteCourant(): string | null {
  return getJetonInvite() ?? memoire
}

/** Vrai tant que ce navigateur porte un essai sans compte. */
export function aUnEssaiSansCompte(): boolean {
  return jetonInviteCourant() !== null
}
