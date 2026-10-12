/**
 * Prix affichés en dur là où aucun `Plan` n'est chargé (hero de /tarifs, paywall...).
 * À aligner avec la table Plan côté serveur (abonnement Jusqu'à l'Examen, tarif unique
 * du 2026-10-02) : là où un plan est disponible, on lit `plan.price` plutôt que cette
 * constante - elle ne sert qu'à ne pas dupliquer le nombre d'un fichier à l'autre.
 */
export const PRIX_ABONNEMENT_FCFA = 15000
/** Enfant supplémentaire de la même famille (−20 %, voir Plan.prix_enfant_supplementaire). */
export const PRIX_ENFANT_SUPPLEMENTAIRE_FCFA = 12000
