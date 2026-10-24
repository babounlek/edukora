import type { ContextePage } from "./contextePage"
import { t } from "@/lib/i18n"
import type { CleI18n } from "@/lib/i18n"
import type { TexteDynamique } from "./types"

/** Le texte d'un titre ou d'une étape, qu'il soit une clé i18n ou composé d'après la page. */
export function resoudreTexte(texte: CleI18n | TexteDynamique, page: ContextePage | undefined): string {
  return typeof texte === "function" ? texte(page) : t(texte)
}
