import { useSyncExternalStore } from "react"

/**
 * Cursus déclaré par un visiteur PAS ENCORE connecté (voir OnboardingModal) : il n'a
 * pas de compte où l'écrire, mais il ne doit pas non plus avoir à le redire après sa
 * première connexion - AuthContext reprend cette valeur et la pousse sur le compte.
 *
 * Module à part plutôt que dans OnboardingModal : AuthContext a besoin de ces
 * fonctions, et OnboardingModal a besoin de useAuth - les faire s'importer l'un
 * l'autre créerait un cycle pour trois lignes de localStorage.
 *
 * useCursusAccueil (accueil, catalogue) lit cette déclaration pour personnaliser ce
 * qu'il montre à un visiteur non connecté. Un simple accès à localStorage ne suffit
 * pas : écrire dedans ne fait re-rendre ni BandeauCursus (qui vient d'écrire) ni les
 * composants voisins déjà montés sur la même page - le choix semblait n'avoir aucun
 * effet tant qu'on ne rechargeait pas la page. D'où le petit magasin externe
 * (useSyncExternalStore, même mécanique que modeExamen.ts) : toute écriture prévient
 * immédiatement tous les abonnés, sur la page en cours.
 */
const CURSUS_PREPARE_EN_ATTENTE_KEY = "edukamer_cursus_prepare_en_attente"

function lire(): number | null {
  try {
    const brut = localStorage.getItem(CURSUS_PREPARE_EN_ATTENTE_KEY)
    const id = brut ? Number(brut) : NaN
    // Valeur écrite par nous, mais relue depuis un stockage que l'utilisateur peut
    // éditer : un id non entier partirait tel quel dans un PATCH que le serveur
    // rejetterait, autant ne jamais l'envoyer.
    return Number.isInteger(id) && id > 0 ? id : null
  } catch {
    return null
  }
}

let valeur = lire()
const abonnes = new Set<() => void>()

function notifier() {
  valeur = lire()
  abonnes.forEach((rappel) => rappel())
}

function abonner(rappel: () => void) {
  abonnes.add(rappel)
  return () => {
    abonnes.delete(rappel)
  }
}

export function memoriserCursusPrepareEnAttente(cursusId: number) {
  try {
    localStorage.setItem(CURSUS_PREPARE_EN_ATTENTE_KEY, String(cursusId))
  } catch {
    // stockage indisponible (navigation privée) - le visiteur redira son examen à la
    // connexion, ce n'est jamais une raison d'interrompre son parcours.
  }
  notifier()
}

export function lireCursusPrepareEnAttente(): number | null {
  return lire()
}

export function oublierCursusPrepareEnAttente() {
  try {
    localStorage.removeItem(CURSUS_PREPARE_EN_ATTENTE_KEY)
  } catch {
    // idem : rien à nettoyer si le stockage est indisponible
  }
  notifier()
}

/** Version réactive de lireCursusPrepareEnAttente() : se re-rend dès qu'un composant
 * (typiquement BandeauCursus) écrit une nouvelle valeur, sans attendre un rechargement. */
export function useCursusPrepareEnAttente(): number | null {
  return useSyncExternalStore(abonner, () => valeur, () => null)
}
