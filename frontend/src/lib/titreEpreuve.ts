import type { Epreuve } from "@/api/types"

const SUFFIXES = { fr: " - corrigé", en: " - solutions" } as const

/**
 * Le titre d'une annale corrigée avec le mot que cherche l'élève : « Mathématiques BEPC 2026 - corrigé ». Même règle que
 * backend/catalog/apercu_partage.titre_epreuve, pour que le moteur de recherche et le visiteur lisent le même titre :
 * seules les annales corrigées (CORR) sont concernées, et un titre qui le dit déjà reste tel quel.
 */
export function titreEpreuve(titre: string, type: Epreuve["lesson_type"], langue: "fr" | "en"): string {
  if (type !== "CORR") return titre
  const bas = titre.toLowerCase()
  if (bas.includes("corrig") || bas.includes("solution")) return titre
  return titre + SUFFIXES[langue]
}
