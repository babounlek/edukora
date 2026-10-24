import { usePublierContextePage, type ContextePage } from "@/lib/guides/contextePage"

/**
 * Publie pour les guides ce que la page affiche (voir lib/guides/contextePage.ts), depuis un endroit du
 * JSX : pour les pages dont le corps a des retours anticipés, où un hook ne peut pas être appelé.
 * Ne rend rien.
 */
export function PublierContexte({ cle, contexte }: { cle: string; contexte: ContextePage }) {
  usePublierContextePage(cle, contexte)
  return null
}
