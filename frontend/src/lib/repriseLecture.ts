// Où l'élève en était dans un cours, par appareil : la SECTION qu'il lisait (« La règle », « Exemple résolu »...) et la part
// du cours déjà parcourue. Un cours fait souvent plus de dix écrans ; sans cela, y revenir voulait dire tout redéfiler.
// On retient une section, pas un nombre de pixels : la mise en page change avec l'écran, la police et les formules.
// Simple confort d'affichage (comme les préférences de lecture) : tout accès au stockage est protégé.

const CLE = "edukora:reprise-cours"
// Au-delà, les plus anciens cours sont oubliés : la liste ne doit pas grossir sans fin sur un petit téléphone.
const COURS_RETENUS_MAX = 30
/** En dessous, l'élève vient d'ouvrir le cours : rien à reprendre. Au-dessus, il l'a fini. */
export const PART_MIN = 0.08
export const PART_MAX = 0.92

export interface Reprise {
  section: string
  /** Part du cours déjà parcourue, de 0 à 1. */
  part: number
  /** Horodatage de la dernière lecture (ms), pour oublier les plus anciennes. */
  le: number
}

function lireTout(): Record<string, Reprise> {
  try {
    const brut: unknown = JSON.parse(window.localStorage.getItem(CLE) ?? "{}")
    return brut && typeof brut === "object" && !Array.isArray(brut) ? (brut as Record<string, Reprise>) : {}
  } catch {
    return {}
  }
}

function ecrireTout(tout: Record<string, Reprise>) {
  try {
    window.localStorage.setItem(CLE, JSON.stringify(tout))
  } catch {
    // Stockage indisponible ou plein : la reprise ne vaudra pas pour la prochaine visite, rien d'autre.
  }
}

/** Où l'élève en était dans ce cours, ou null s'il n'y a rien d'utile à reprendre (jamais ouvert, à peine commencé, fini). */
export function lireReprise(slug: string): Reprise | null {
  const reprise = lireTout()[slug]
  if (!reprise || typeof reprise.section !== "string" || typeof reprise.part !== "number") return null
  return reprise.part >= PART_MIN && reprise.part <= PART_MAX ? reprise : null
}

/** Retient la position dans ce cours ; un cours lu jusqu'au bout est oublié (il n'y a plus rien à reprendre). */
export function retenirReprise(slug: string, section: string, part: number, maintenant = Date.now()) {
  const tout = lireTout()
  if (part > PART_MAX) {
    if (!(slug in tout)) return
    delete tout[slug]
  } else {
    tout[slug] = { section, part, le: maintenant }
    const slugs = Object.keys(tout)
    if (slugs.length > COURS_RETENUS_MAX) {
      slugs.sort((a, b) => tout[a].le - tout[b].le).slice(0, slugs.length - COURS_RETENUS_MAX).forEach((s) => delete tout[s])
    }
  }
  ecrireTout(tout)
}

export function oublierReprise(slug: string) {
  const tout = lireTout()
  if (!(slug in tout)) return
  delete tout[slug]
  ecrireTout(tout)
}
