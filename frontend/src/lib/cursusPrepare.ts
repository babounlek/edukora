/**
 * Cursus déclaré par un visiteur PAS ENCORE connecté (voir OnboardingModal) : il n'a
 * pas de compte où l'écrire, mais il ne doit pas non plus avoir à le redire après sa
 * première connexion - AuthContext reprend cette valeur et la pousse sur le compte.
 *
 * Module à part plutôt que dans OnboardingModal : AuthContext a besoin de ces
 * fonctions, et OnboardingModal a besoin de useAuth - les faire s'importer l'un
 * l'autre créerait un cycle pour trois lignes de localStorage.
 */
const CURSUS_PREPARE_EN_ATTENTE_KEY = "edukamer_cursus_prepare_en_attente"

export function memoriserCursusPrepareEnAttente(cursusId: number) {
  try {
    localStorage.setItem(CURSUS_PREPARE_EN_ATTENTE_KEY, String(cursusId))
  } catch {
    // stockage indisponible (navigation privée) - le visiteur redira son examen à la
    // connexion, ce n'est jamais une raison d'interrompre son parcours.
  }
}

export function lireCursusPrepareEnAttente(): number | null {
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

export function oublierCursusPrepareEnAttente() {
  try {
    localStorage.removeItem(CURSUS_PREPARE_EN_ATTENTE_KEY)
  } catch {
    // idem : rien à nettoyer si le stockage est indisponible
  }
}
