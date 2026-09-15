import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Formate un montant avec des espaces comme séparateurs de milliers (ex: 1500 -> "1 500").
 * N'utilise pas toLocaleString("fr-FR") : selon le support ICU du navigateur, son séparateur
 * peut être une espace fine insécable quasi invisible, ou absent, plutôt qu'une vraie espace.
 */
export function formatAmount(amount: number): string {
  return Math.round(amount).toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ")
}

/**
 * Majuscule de première lettre pour l'affichage d'un nom de thème/tag - beaucoup
 * viennent de l'ingestion sans casse normalisée (voir catalog.Tag.name, ex.
 * "abscisse à l'origine", des milliers de tags en minuscules en base). Ne touche
 * jamais au reste de la chaîne, qui peut porter un sigle (ADN, ARN, QCM...) qu'un
 * toLowerCase() casserait. Purement un habillage d'affichage, jamais une correction
 * des données.
 */
export function capitaliserTheme(texte: string): string {
  return texte ? texte.charAt(0).toUpperCase() + texte.slice(1) : texte
}
