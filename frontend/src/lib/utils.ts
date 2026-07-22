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
