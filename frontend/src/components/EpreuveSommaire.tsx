import { SommaireNav, type SommaireEntry } from "@/components/SommaireNav"

/**
 * Le strict nécessaire pour étiqueter un exercice - satisfait aussi bien par
 * EpreuveExercise (corrigé, lecture abonnée) que par EpreuvePreviewExercise (sujet
 * public, sans corrigé) : la fiche et le lecteur affichent le même sommaire et les
 * mêmes libellés sur les mêmes exercices, seul le contenu autour diffère.
 */
export interface ExerciceLabelSource {
  numero_exercice: string
  titre: string
}

/**
 * Ancre d'un exercice dans la page de lecture - partagée entre le sommaire et les blocs
 * qu'il vise (voir EpreuveReaderPage). `numero_exercice` n'est pas toujours un nombre
 * (voir Exercise.numero_exercice côté backend : "3a", "Probleme-IIA", "Section III"),
 * d'où le passage par un slug plutôt qu'une interpolation directe dans une URL.
 */
export function exerciceAnchorId(numeroExercice: string) {
  const slug = numeroExercice
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
  return `exercice-${slug || "sans-numero"}`
}

const NUMERIQUE_RE = /^\d+$/

// Au-delà, le libellé déborde la sidebar (220px) et se fait couper en plein milieu du
// fil d'Ariane, là où l'information utile se trouve justement à la fin.
const LONGUEUR_MAX_SIDEBAR = 48

/** "Ex. 3" pour un repère numérique, le repère tel quel sinon ("Problème", "Section III"). */
export function libelleCourtExercice(exercise: ExerciceLabelSource) {
  return NUMERIQUE_RE.test(exercise.numero_exercice.trim())
    ? `Ex. ${exercise.numero_exercice.trim()}`
    : exercise.numero_exercice.trim()
}

/**
 * Les épreuves de SVT titrent leurs exercices par un fil d'Ariane complet ("Partie A :
 * Évaluation des ressources - I. Évaluation des savoirs - Exercice 1 : QCM", 24 titres
 * du corpus dépassent 70 caractères) : on n'en garde que le dernier segment, le seul
 * qui distingue un exercice de son voisin - les précédents sont communs à toute une
 * partie de l'épreuve. Le titre entier reste accessible en infobulle (voir SommaireNav).
 */
function libelleLong(exercise: ExerciceLabelSource) {
  const titre = exercise.titre.trim() || `Exercice ${exercise.numero_exercice.trim()}`
  if (titre.length <= LONGUEUR_MAX_SIDEBAR) return titre
  const segments = titre.split(" - ")
  return segments[segments.length - 1].trim()
}

/**
 * Sommaire de navigation entre les exercices d'une épreuve. Les libellés viennent du
 * backend (voir catalog.rendering._exercise_titre_et_points) : le titre d'un exercice
 * n'a pas de champ dédié en base, il est extrait de son en-tête d'énoncé - d'où le repli
 * sur "Exercice {numero}" quand l'épreuve source n'en portait aucun.
 */
export function EpreuveSommaire({ exercises }: { exercises: ExerciceLabelSource[] }) {
  const entries: SommaireEntry[] = exercises.map((exercise) => ({
    id: exerciceAnchorId(exercise.numero_exercice),
    short: libelleCourtExercice(exercise),
    long: libelleLong(exercise),
    title: exercise.titre.trim() || undefined,
  }))

  return <SommaireNav entries={entries} ariaLabel="Sommaire des exercices" />
}
