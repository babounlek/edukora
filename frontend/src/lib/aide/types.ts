/** Les rubriques du centre d'aide : miroir de `aide.models.CategorieAide` (backend). Les libellés sont les clés `aide.cat.*`. */
export const CATEGORIES_AIDE = ["demarrer", "connexion", "paiement", "utiliser", "parents", "autres"] as const
export type CategorieAide = (typeof CATEGORIES_AIDE)[number]

export interface ArticleAideResume {
  slug: string
  categorie: CategorieAide
  titre: string
  resume: string
  mots_cles: string
  populaire: boolean
  /** Chemins internes (français) où l'article est proposé en tête du panneau d'aide. */
  pages: string[]
  /** Faux : l'article n'existe qu'en français et s'affiche donc en français même dans l'interface anglaise. */
  traduit: boolean
}

export interface ArticleAideDetail extends ArticleAideResume {
  corps: string
  maj_le: string
  voisins: ArticleAideResume[]
}
