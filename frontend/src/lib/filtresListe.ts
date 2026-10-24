/**
 * Ce qui, dans l'URL et le navigateur, appartient à UNE langue : l'examen (BEPC, GCE…) et la matière d'un filtre de
 * liste. Un changement de langue voulu par l'élève (voir ouvrirDansLangue) les abandonne, sinon la page rechargée en
 * anglais gardait `?cursus=14` (un BEPC) et affichait BEPC et GCE ensemble. Module sans dépendance : il est lu par
 * l'i18n comme par les pages.
 */

/** Dernière recherche filtrée de la liste des épreuves (sessionStorage), restaurée sur un lien nu. */
export const FILTERS_SESSION_KEY = "edukamer_epreuves_derniers_filtres"

const PARAMS_LIES_A_LA_LANGUE = ["cursus", "subject", "tout"]

/** La requête d'URL (`?a=1&b=2` ou vide) sans les filtres propres à une langue ; les autres paramètres sont conservés. */
export function requeteSansFiltresDeLangue(search: string): string {
  const params = new URLSearchParams(search)
  for (const cle of PARAMS_LIES_A_LA_LANGUE) params.delete(cle)
  const texte = params.toString()
  return texte ? `?${texte}` : ""
}

/** Oublie les filtres mémorisés par le navigateur pour la session. Sans effet si le stockage est indisponible. */
export function oublierFiltresMemorises(): void {
  try {
    sessionStorage.removeItem(FILTERS_SESSION_KEY)
  } catch {
    /* navigation privée : rien n'était mémorisé */
  }
}
