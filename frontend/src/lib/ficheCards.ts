export interface FicheCard {
  question: string
  reponse: string
}

/**
 * Découpe le Markdown d'une fiche (Lesson.lesson_type=FICHE) en cartes recto/verso,
 * une par titre de niveau 2 ("## ...") - convention déjà utilisée pour les sections
 * d'un contenu long-format dans ce projet. Si la fiche n'a aucun titre de niveau 2
 * (contenu très court, ou rédigée sans cette convention), retombe sur une carte
 * unique portant tout le contenu plutôt que de n'afficher qu'une liste vide.
 */
export function parseFicheCards(markdown: string): FicheCard[] {
  const lines = markdown.split("\n")
  const cards: FicheCard[] = []
  let question: string | null = null
  let body: string[] = []

  function pushCurrent() {
    if (question !== null) cards.push({ question, reponse: body.join("\n").trim() })
  }

  for (const line of lines) {
    const match = /^##\s+(.*)/.exec(line)
    if (match) {
      pushCurrent()
      question = match[1].trim()
      body = []
    } else if (question !== null) {
      body.push(line)
    }
  }
  pushCurrent()

  if (cards.length === 0) {
    const trimmed = markdown.trim()
    if (trimmed) cards.push({ question: "Fiche", reponse: trimmed })
  }

  return cards
}
