/**
 * Les thèmes de quiz déjà joués jusqu'au bout sur CET appareil, par examen. Sert la carte du hero de l'accueil (voir
 * components/PremiereSeance) : une fois la séance gratuite de mathématiques faite, la carte propose la matière gratuite
 * suivante au lieu de répéter « Ta première séance ».
 *
 * Dans localStorage, comme les records de l'essai (lib/quizEssai) : le visiteur n'a pas de compte, donc rien d'autre ne
 * sait ce qu'il a fait. Conséquence assumée : sur un autre appareil, ou stockage vidé, la carte repart de la première
 * séance - elle ne promet jamais rien qui dépende de cette mémoire.
 */

const CLE = "edukora:seances-jouees"
// Un visiteur ne joue que quelques thèmes ; un abonné, des centaines. On borne pour ne pas grossir sans fin.
const MAX = 400

export function cleSeance(cursus: number, theme: number): string {
  return `${cursus}:${theme}`
}

function lire(): string[] {
  try {
    const brut = localStorage.getItem(CLE)
    const liste = brut ? JSON.parse(brut) : null
    return Array.isArray(liste) ? liste.filter((x): x is string => typeof x === "string") : []
  } catch {
    return []
  }
}

/** Les clés `cursus:theme` des séances jouées sur cet appareil. */
export function seancesJouees(): Set<string> {
  return new Set(lire())
}

/** Note ces thèmes comme joués pour cet examen. Idempotent. */
export function marquerSeancesJouees(cursus: number, themes: Array<number | null | undefined>): void {
  const nouvelles = themes.filter((t): t is number => typeof t === "number").map((t) => cleSeance(cursus, t))
  if (nouvelles.length === 0) return
  const liste = lire()
  const ajout = [...new Set(nouvelles)].filter((cle) => !liste.includes(cle))
  if (ajout.length === 0) return
  try {
    localStorage.setItem(CLE, JSON.stringify([...liste, ...ajout].slice(-MAX)))
  } catch {
    // Stockage indisponible (navigation privée stricte) : la carte de l'accueil reste sur la première séance.
  }
}
