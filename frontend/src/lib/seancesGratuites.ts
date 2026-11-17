/**
 * Les quiz GRATUITS déjà joués jusqu'au bout sur CET appareil, par examen, avec le meilleur score. Deux usages :
 *
 * - la carte du hero de l'accueil (voir components/PremiereSeance) : une fois la séance gratuite de mathématiques faite,
 *   elle propose la matière gratuite suivante au lieu de répéter « Ta première séance » ;
 * - « Déjà joué » : la liste des quiz gratuits (components/EssaisGratuitsQuiz) et l'écran du quiz (QuizSessionPage)
 *   disent qu'on rejoue un quiz déjà fait, et le score à battre. Un thème gratuit ne compte que 5 à 9 questions : le
 *   relancer redonne les mêmes, et rien ne le disait.
 *
 * Dans localStorage, comme les records de l'essai (lib/quizEssai) : le visiteur n'a pas de compte, donc rien d'autre ne
 * sait ce qu'il a fait. Conséquence assumée : sur un autre appareil, ou stockage vidé, tout repart de zéro - aucun
 * écran ne promet quoi que ce soit qui dépende de cette mémoire.
 */

const CLE = "edukora:seances-jouees"
// Un examen offre une dizaine de quiz gratuits : la borne ne sert qu'à ne jamais grossir sans fin.
const MAX = 400

export interface ScoreSeance {
  reussies: number
  total: number
}

/** `null` : jouée, score inconnu (ancien format du stockage, ou quiz marqué sans score). */
type Entree = [number, number] | null

export function cleSeance(cursus: number, theme: number): string {
  return `${cursus}:${theme}`
}

function lire(): Record<string, Entree> {
  try {
    const brut = localStorage.getItem(CLE)
    const stocke: unknown = brut ? JSON.parse(brut) : null
    // Premier format : une simple liste de clés, sans score.
    if (Array.isArray(stocke)) {
      return Object.fromEntries(stocke.filter((x): x is string => typeof x === "string").map((cle) => [cle, null]))
    }
    if (!stocke || typeof stocke !== "object") return {}
    const entrees: Record<string, Entree> = {}
    for (const [cle, v] of Object.entries(stocke)) {
      const valide = Array.isArray(v) && v.length === 2 && v.every((n) => Number.isFinite(n)) && v[1] > 0
      entrees[cle] = valide ? [v[0], v[1]] : null
    }
    return entrees
  } catch {
    return {}
  }
}

/** Les clés `cursus:theme` des quiz gratuits joués sur cet appareil. */
export function seancesJouees(): Set<string> {
  return new Set(Object.keys(lire()))
}

/** Les mêmes, avec le meilleur score de chacun (null quand il n'est pas connu). */
export function scoresDesSeances(): Map<string, ScoreSeance | null> {
  return new Map(Object.entries(lire()).map(([cle, v]) => [cle, v ? { reussies: v[0], total: v[1] } : null]))
}

/** Ce quiz a-t-il déjà été joué ici, et avec quel meilleur score ? */
export function seanceJouee(cursus: number, theme: number): { jouee: boolean; record: ScoreSeance | null } {
  const scores = scoresDesSeances()
  const cle = cleSeance(cursus, theme)
  return { jouee: scores.has(cle), record: scores.get(cle) ?? null }
}

/**
 * Note ces thèmes comme joués pour cet examen. `score` : le résultat de la séance ; on ne garde que le meilleur taux de
 * réussite (comme lib/quizEssai.bat), jamais le dernier. Idempotent.
 */
export function marquerSeancesJouees(cursus: number, themes: Array<number | null | undefined>, score?: ScoreSeance): void {
  const cles = [...new Set(themes.filter((t): t is number => typeof t === "number").map((t) => cleSeance(cursus, t)))]
  if (cles.length === 0) return
  const entrees = lire()
  const nouveau: Entree = score && score.total > 0 ? [score.reussies, score.total] : null
  let change = false
  for (const cle of cles) {
    const avant = entrees[cle]
    const meilleur = nouveau !== null && (avant == null || nouveau[0] * avant[1] > avant[0] * nouveau[1])
    if (cle in entrees && !meilleur) continue
    entrees[cle] = meilleur ? nouveau : null
    change = true
  }
  if (!change) return
  try {
    localStorage.setItem(CLE, JSON.stringify(Object.fromEntries(Object.entries(entrees).slice(-MAX))))
  } catch {
    // Stockage indisponible (navigation privée stricte) : rien n'est gardé, les écrans se comportent comme à la première visite.
  }
}
