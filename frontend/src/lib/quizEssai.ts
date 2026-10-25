import type { QuizQuestion, QuizSession } from "@/api/types"
import { t } from "@/lib/i18n"

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

// Les mêmes barèmes que quiz.xp côté serveur (XP_QCM_JUSTE, XP_OUVERTE) : le visiteur voit ce que le même quiz
// lui aurait rapporté avec un compte. Un montant AFFICHÉ, jamais crédité - l'essai n'écrit rien côté serveur.
const POINTS_QCM_JUSTE = 10
const POINTS_OUVERTE: Record<string, number> = { REUSSI: 5, PARTIEL: 2 }

/** Points que cet essai aurait rapportés à un élève connecté. */
export function pointsEssai(session: QuizSession): number {
  return session.questions.reduce((somme, q) => {
    if (!q.reponse) return somme
    if (q.type_reponse === "QCM") return somme + (q.reponse.est_correcte ? POINTS_QCM_JUSTE : 0)
    return somme + (POINTS_OUVERTE[q.reponse.resultat_declare] ?? 0)
  }, 0)
}

// Le record, lui, reste sur l'appareil (localStorage) : le détail de l'essai disparaît à la fermeture de
// l'onglet, mais « bats ton record » est ce qui donne envie de refaire un quiz tout de suite. Une entrée par
// thème de quiz ; une seule par thème et on ne garde que le meilleur taux de réussite.
const CLE_RECORDS = "edukora:records-essai"

export interface RecordEssai {
  reussies: number
  total: number
}

function lireRecords(): Record<string, RecordEssai> {
  try {
    const brut = localStorage.getItem(CLE_RECORDS)
    const records = brut ? JSON.parse(brut) : null
    return records && typeof records === "object" ? records : {}
  } catch {
    return {}
  }
}

function cleRecord(session: QuizSession): string | null {
  const theme = session.questions[0]?.theme_id
  return theme == null ? null : `${session.cursus}:${theme}`
}

/** Le meilleur essai déjà fait sur ce thème, ou null. */
export function lireRecord(session: QuizSession): RecordEssai | null {
  const cle = cleRecord(session)
  const record = cle ? lireRecords()[cle] : null
  return record && record.total > 0 ? record : null
}

/** Vrai quand `reussies / total` dépasse strictement le record : un premier essai (pas de record) n'est pas un exploit. */
export function bat(record: RecordEssai | null, reussies: number, total: number): boolean {
  return record !== null && total > 0 && reussies * record.total > record.reussies * total
}

/** Garde ce résultat s'il est le premier du thème ou s'il bat le record. Idempotent : l'appeler deux fois ne change rien. */
export function memoriserRecord(session: QuizSession, reussies: number, total: number) {
  const cle = cleRecord(session)
  const precedent = lireRecord(session)
  if (!cle || total <= 0 || (precedent !== null && !bat(precedent, reussies, total))) return
  try {
    localStorage.setItem(CLE_RECORDS, JSON.stringify({ ...lireRecords(), [cle]: { reussies, total } }))
  } catch {
    // Stockage indisponible : l'essai marche, seul le record n'est pas gardé.
  }
}

/** Page qui relance cet essai précis : le lien qu'on partage (voir QuizEssaiLancementPage). */
export function cheminEssai(session: QuizSession): string | null {
  const theme = session.questions[0]?.theme_id
  if (!session.essai || session.subject == null || theme == null) return null
  return `/quiz/essai/${session.cursus}/${session.subject}/${theme}`
}

/** L'accroche du message de partage, sans le lien. */
export function texteDePartageEssai(session: QuizSession): string {
  const q = session.questions[0]
  const theme = q?.theme ? t("essai.partage_theme", { theme: q.theme }) : ""
  return t("essai.partage", { theme, matiere: q?.subject_label ?? t("essai.partage_quiz"), cursus: session.cursus_display })
}

/** L'accroche d'un DÉFI : le score qu'on vient de faire et de quoi donner envie de faire mieux, sans le lien. */
export function texteDeDefiEssai(session: QuizSession, reussies: number, total: number): string {
  const q = session.questions[0]
  const theme = q?.theme ? t("essai.partage_theme", { theme: q.theme }) : ""
  return t("essai.partage_defi", { a: reussies, b: total, theme, matiere: q?.subject_label ?? t("essai.partage_quiz"), cursus: session.cursus_display })
}
