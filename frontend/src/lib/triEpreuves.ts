/**
 * Le tri de la liste des épreuves. « Aléatoire » est le tri PAR DÉFAUT : il n'a donc pas de valeur dans
 * l'URL, et chaque visite montre un mélange différent (la page y ajoute un germe, voir
 * `nouveauGermeAleatoire`, pour que le défilement infini garde un ordre cohérent d'une page à l'autre).
 * « Ajoutées récemment » se choisit avec `?ordering=recent`. « Plus récentes (année) » se choisit avec
 * `?ordering=annee` ; il n'envoie aucun tri à l'API, ce qui donne le tri par défaut du backend (année
 * décroissante, niveau par niveau).
 *
 * `?ordering=aleatoire` reste valide (c'est le défaut) ; `?ordering=year` (qui triait par année CROISSANTE)
 * et `?ordering=popular` (vide tant qu'aucune épreuve n'a 3 lecteurs) retombent sur le défaut.
 */
export type TriEpreuves = "aleatoire" | "recent" | "annee"

export const TRI_PAR_DEFAUT: TriEpreuves = "aleatoire"

/** Le tri d'après le paramètre `ordering` de l'URL. */
export function triDepuisUrl(valeur: string | null): TriEpreuves {
  if (valeur === "annee") return "annee"
  if (valeur === "recent") return "recent"
  return TRI_PAR_DEFAUT
}

/** La valeur à écrire dans l'URL : vide pour le tri par défaut, qui n'y figure pas. */
export function valeurUrlDuTri(tri: string): string {
  if (tri === "annee") return "annee"
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
