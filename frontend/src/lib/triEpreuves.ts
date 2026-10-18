/**
 * Le tri de la liste des épreuves. « Ajoutées récemment » est le tri PAR DÉFAUT : il n'a donc pas de valeur
 * dans l'URL. « Plus récentes (année) » se choisit avec `?ordering=annee` ; il n'envoie aucun tri à l'API, ce
 * qui donne le tri par défaut du backend (année décroissante, niveau par niveau).
 *
 * Un ancien lien `?ordering=recent` reste valide (c'est le défaut) ; `?ordering=year` (qui triait par année
 * CROISSANTE) et `?ordering=popular` (vide tant qu'aucune épreuve n'a 3 lecteurs) retombent sur le défaut.
 */
export type TriEpreuves = "recent" | "annee"

export const TRI_PAR_DEFAUT: TriEpreuves = "recent"

/** Le tri d'après le paramètre `ordering` de l'URL. */
export function triDepuisUrl(valeur: string | null): TriEpreuves {
  return valeur === "annee" ? "annee" : TRI_PAR_DEFAUT
}

/** La valeur à écrire dans l'URL : vide pour le tri par défaut, qui n'y figure pas. */
export function valeurUrlDuTri(tri: string): string {
  return tri === "annee" ? "annee" : ""
}

/** Le paramètre `ordering` à envoyer à l'API : `recent` pour « Ajoutées récemment », rien pour l'année. */
export function triPourApi(tri: TriEpreuves): "recent" | undefined {
  return tri === "recent" ? "recent" : undefined
}
