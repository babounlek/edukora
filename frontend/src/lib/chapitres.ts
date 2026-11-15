import type { ThemeFrequent } from "@/api/types"

/** Un chapitre du programme officiel et les thèmes fréquents qui s'y rattachent (audit produit 2026-11-13, R6). */
export interface GroupeChapitre {
  cle: string
  /** Vide pour le groupe « Autres thèmes » (aucun savoir du programme rattaché). */
  titre: string
  module: string
  themes: ThemeFrequent[]
  /** Thèmes que l'élève a déjà tentés, et parmi eux ceux qu'il tient (Solide ou Maîtrisé). 0 pour un visiteur. */
  tentes: number
  solides: number
}

/**
 * Regroupe les thèmes par chapitre du programme, dans l'ordre du programme ; les thèmes sans chapitre vont en dernier. Au sein d'un
 * chapitre, l'ordre reçu (le classement par fréquence) est gardé : le thème qui tombe le plus reste en haut.
 */
export function grouperParChapitre(themes: ThemeFrequent[]): GroupeChapitre[] {
  const groupes = new Map<string, GroupeChapitre & { ordre: [number, number] }>()
  for (const theme of themes) {
    const c = theme.chapitre ?? null
    const cle = c ? `c${c.id}` : "autres"
    let g = groupes.get(cle)
    if (!g) {
      g = {
        cle, titre: c?.titre ?? "", module: c?.module ?? "", themes: [], tentes: 0, solides: 0,
        ordre: c ? c.ordre : [Number.MAX_SAFE_INTEGER, 0],
      }
      groupes.set(cle, g)
    }
    g.themes.push(theme)
    if (theme.maitrise) {
      g.tentes += 1
      if (theme.maitrise.niveau === "solide" || theme.maitrise.niveau === "maitrise") g.solides += 1
    }
  }
  return [...groupes.values()]
    .sort((a, b) => a.ordre[0] - b.ordre[0] || a.ordre[1] - b.ordre[1])
    .map(({ ordre: _ordre, ...g }) => g)
}
