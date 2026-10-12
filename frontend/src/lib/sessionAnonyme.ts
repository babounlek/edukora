// Un visiteur qui n'a jamais ouvert de session paie deux allers-retours en erreur 401 à CHAQUE
// chargement de page (/auth/me, puis le rafraîchissement du jeton), avant que l'en-tête ne sache
// s'il doit afficher « Connexion ». Le cookie de session étant httpOnly, le navigateur ne peut pas
// savoir lui-même s'il en a un : on retient donc seulement « on a constaté que ce navigateur est
// anonyme », jamais l'inverse. Ainsi un compte déjà connecté (qui n'a pas ce marqueur) retrouve sa
// session exactement comme avant.
const CLE = "edukora:visiteur-anonyme"
// Rechecké de temps en temps : une session ouverte autrement (autre appareil partageant un
// cookie, nettoyage du stockage) ne doit pas rester ignorée indéfiniment.
const VALIDITE_MS = 7 * 24 * 60 * 60 * 1000

export function marquerVisiteurAnonyme() {
  try {
    localStorage.setItem(CLE, String(Date.now()))
  } catch {
    // Stockage indisponible : on retombe sur le comportement d'avant (un test à chaque chargement).
  }
}

/** À appeler dès qu'un jeton d'accès est obtenu, par n'importe quel chemin (connexion, rafraîchissement). */
export function effacerMarqueAnonyme() {
  try {
    localStorage.removeItem(CLE)
  } catch {
    // rien à faire
  }
}

export function estVisiteurAnonymeConnu(): boolean {
  try {
    const depuis = Number(localStorage.getItem(CLE))
    return depuis > 0 && Date.now() - depuis < VALIDITE_MS
  } catch {
    return false
  }
}
