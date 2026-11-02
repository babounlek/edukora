/**
 * Le tri de la liste des épreuves. « Plus récentes (année) » est le tri PAR DÉFAUT : il n'a donc pas de
 * valeur dans l'URL et n'envoie aucun tri à l'API, ce qui donne le tri par défaut du backend (année
 * décroissante, niveau par niveau).
 * « Ajoutées récemment » se choisit avec `?ordering=recent`. « Aléatoire » se choisit avec
 * `?ordering=aleatoire` (la page y ajoute un germe, voir `nouveauGermeAleatoire`, pour que le défilement
 * infini garde un ordre cohérent d'une page à l'autre).
 *
 * `?ordering=year` (qui triait par année CROISSANTE) et `?ordering=popular` (vide tant qu'aucune épreuve
 * n'a 3 lecteurs) retombent sur le défaut.
 */
export type TriEpreuves = "aleatoire" | "recent" | "annee"

export const TRI_PAR_DEFAUT: TriEpreuves = "annee"

/** Le tri d'après le paramètre `ordering` de l'URL. */
export function triDepuisUrl(valeur: string | null): TriEpreuves {
  if (valeur === "aleatoire") return "aleatoire"
  if (valeur === "recent") return "recent"
  return TRI_PAR_DEFAUT
}

/** La valeur à écrire dans l'URL : vide pour le tri par défaut, qui n'y figure pas. */
export function valeurUrlDuTri(tri: string): string {
  if (tri === "aleatoire") return "aleatoire"
  if (tri === "recent") return "recent"
  return ""
}

/** Le paramètre `ordering` à envoyer à l'API : rien pour l'année (tri par défaut du backend). */
export function triPourApi(tri: TriEpreuves): "random" | "recent" | undefined {
  if (tri === "aleatoire") return "random"
  return tri === "recent" ? "recent" : undefined
}

/** Un germe entier positif pour le tri aléatoire : le même germe redonne le même ordre côté API. */
export function nouveauGermeAleatoire(): number {
  return Math.floor(Math.random() * 2 ** 31)
}
