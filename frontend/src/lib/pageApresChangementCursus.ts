/**
 * Où atterrir quand l'élève change d'examen préparé (BEPC -> BAC, par ex.) sans changer d'enfant.
 *
 * Les pages qui listent du contenu (catalogue, épreuves, cours, quiz, progression...) restent ouvertes :
 * leurs données se rechargent pour le nouvel examen. Une page qui montre UN contenu précis (une épreuve,
 * un cours, un thème, une matière du parcours) appartient à l'ancien examen : la garder montrerait le
 * mauvais contenu, voire une erreur 403/404. On remonte alors à la liste de la même rubrique.
 *
 * Travaille sur des chemins INTERNES (français, sans préfixe de langue) - ceux de `useLocation()`.
 */

export interface CibleChangementCursus {
  /** Chemin interne où aller (query comprise) ; `null` = rester sur la page telle quelle. */
  chemin: string | null
  /** Une séance en cours serait quittée : demander confirmation avant de basculer. */
  seanceEnCours: boolean
}

// Filtres qui désignent l'ancien examen ou une matière/un savoir qui lui appartient : sur le nouvel examen ils
// ne renverraient rien. Les autres paramètres (recherche, tri, case « non lus »...) sont gardés.
const PARAMS_LIES_A_L_EXAMEN = ["cursus", "subject", "savoir", "savoir_label", "theme", "seance"]

function sansParamsLiesALExamen(search: string): string {
  const params = new URLSearchParams(search)
  PARAMS_LIES_A_L_EXAMEN.forEach((cle) => params.delete(cle))
  const reste = params.toString()
  return reste ? `?${reste}` : ""
}

export function cibleApresChangementCursus(
  pathname: string,
  search: string,
  paysDuNouvelExamen: string | null,
): CibleChangementCursus {
  const rester = (chemin: string | null, seanceEnCours = false): CibleChangementCursus => ({ chemin, seanceEnCours })

  // Séances : on ne laisse jamais une séance ouverte sous un autre examen. Les pages de RÉSULTAT et
  // l'historique sont ceux de l'élève, pas d'un examen : elles restent telles quelles.
  if (/^\/quiz\/session\/[^/]+$/.test(pathname)) return rester("/quiz", true)
  if (pathname === "/quiz/essai" || /^\/quiz\/essai\/[^/]+\/[^/]+\/[^/]+$/.test(pathname)) return rester("/quiz")
  if (/^\/(inedit\/tentative|simulation)\/[^/]+$/.test(pathname)) return rester("/quiz", true)

  // Pages de détail non préfixées par un pays.
  if (/^\/cours\/[^/]+(\/lire)?$/.test(pathname)) {
    return rester(paysDuNouvelExamen ? `/${paysDuNouvelExamen}/cours` : "/")
  }
  if (/^\/parcours\/[^/]+$/.test(pathname)) return rester("/parcours")
  if (/^\/epreuves\/[^/]+(\/lire)?$/.test(pathname)) {
    return rester(paysDuNouvelExamen ? `/${paysDuNouvelExamen}/epreuves` : "/")
  }

  // Pages préfixées par un pays (`/cm/...`).
  const m = /^\/([a-z]{2})(\/.*)?$/.exec(pathname)
  if (m) {
    const [, pays, suite = ""] = m
    // Si le nouvel examen est d'un autre pays, le préfixe suit - sinon le garde-fou du pays renverrait ailleurs.
    const paysCible = paysDuNouvelExamen ?? pays
    if (/^\/examens\/[^/]+$/.test(suite)) return rester(`/${paysCible}`)
    if (/^\/epreuves\/[^/]+(\/lire)?$/.test(suite) || /^\/epreuves-inedites\/[^/]+$/.test(suite)) {
      return rester(`/${paysCible}/epreuves`)
    }
    if (/^\/themes-frequents\/[^/]+\/exercices(\/[^/]+)?$/.test(suite)) return rester(`/${paysCible}/themes-frequents`)
    if (paysCible !== pays) return rester(`/${paysCible}${suite}${sansParamsLiesALExamen(search)}`)
  }

  // Page de liste ou d'espace personnel : on reste, avec des filtres débarrassés de l'ancien examen.
  const nettoye = sansParamsLiesALExamen(search)
  return rester(nettoye === search ? null : `${pathname}${nettoye}`)
}
