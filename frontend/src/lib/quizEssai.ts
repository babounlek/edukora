import type { QuizQuestion, QuizSession } from "@/api/types"

// L'essai gratuit n'a pas de session côté serveur (voir quiz.essai) : le quiz en cours vit ici, dans
// sessionStorage - il survit à un rechargement de la page, pas à la fermeture de l'onglet, ce qui
// suffit pour un essai de quelques minutes. Chaque réponse y est réécrite telle que le serveur l'a
// corrigée, donc le score se recalcule toujours depuis ce seul objet.
const CLE = "edukora:quiz-essai"

export function memoriserEssai(session: QuizSession) {
  try {
    sessionStorage.setItem(CLE, JSON.stringify(session))
  } catch {
    // Stockage indisponible (navigation privée...) : l'essai marche, seul le rechargement le perd.
  }
}

export function lireEssai(): QuizSession | null {
  try {
    const brut = sessionStorage.getItem(CLE)
    if (!brut) return null
    const session = JSON.parse(brut) as Partial<QuizSession>
    // Un contenu stocké qui n'a plus la forme attendue (ancienne version du site) vaut « pas d'essai ».
    if (!session || !session.essai || !Array.isArray(session.questions) || session.questions.length === 0) return null
    return session as QuizSession
  } catch {
    return null
  }
}

export function oublierEssai() {
  try {
    sessionStorage.removeItem(CLE)
  } catch {
    // rien à faire
  }
}

/** Remplace une question par sa version corrigée et renvoie la session mise à jour. */
export function avecQuestionCorrigee(session: QuizSession, corrigee: QuizQuestion): QuizSession {
  return { ...session, questions: session.questions.map((q) => (q.id === corrigee.id ? { ...q, ...corrigee } : q)) }
}

export interface ScoreEssaiTheme {
  theme: string
  total: number
  reussies: number
}

/** Score de l'essai, calculé depuis les réponses stockées : bonnes réponses, répondues, par thème. */
export function scoreEssai(session: QuizSession) {
  const repondues = session.questions.filter((q) => q.reponse)
  const reussies = repondues.filter((q) => q.reponse?.est_correcte).length
  const parTheme = new Map<string, ScoreEssaiTheme>()
  for (const q of repondues) {
    const nom = q.theme ?? q.subject_label
    const ligne = parTheme.get(nom) ?? { theme: nom, total: 0, reussies: 0 }
    ligne.total += 1
    if (q.reponse?.est_correcte) ligne.reussies += 1
    parTheme.set(nom, ligne)
  }
  return { total: session.questions.length, repondues: repondues.length, reussies, parTheme: [...parTheme.values()] }
}
