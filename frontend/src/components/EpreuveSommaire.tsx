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
  // Pile de repères de groupe (Partie/section romaine/matière) - [] pour la grande
  // majorité des épreuves. Voir buildEntries plus bas et catalog.rendering.
  // _exercise_group_paths côté backend.
  groupes: string[]
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

const PARTIE_TOKEN_RE = /^Partie\s+(\S+)/i
const ROMAN_TOKEN_RE = /^([IVX]{1,4})\s*[.\-–—]/i

/** Jeton compact d'un repère de groupe pour la pastille mobile ("Partie A" -> "A",
 * "I. Activités Numériques" -> "I", "CHIMIE" inchangé - déjà court). */
function jetonCourtGroupe(label: string) {
  const partie = PARTIE_TOKEN_RE.exec(label)
  if (partie) return partie[1]
  const roman = ROMAN_TOKEN_RE.exec(label)
  if (roman) return roman[1].toUpperCase()
  return label
}

/**
 * Entrées de sommaire pour une épreuve organisée en groupes (Partie/section romaine/
 * matière - voir ExerciceLabelSource.groupes). La numérotation "Exercice N" affichée
 * est LOCALE à chaque groupe le plus imbriqué (repart à 1 dans "I.", repart encore à 1
 * dans "II." - voir catalog.rendering._exercise_group_paths) : le texte du titre
 * d'origine ("EXERCICE 2 : CHIMIE DES CHAMPS...") n'est plus affiché ici, seule sa
 * PRÉSENCE compte (voir le cas `!aUneReferencePropre` ci-dessous).
 *
 * Un exercice sans référence propre après son groupe (titre vide - ex. "Partie B",
 * qui n'est jamais subdivisée en sous-exercices numérotés dans la source) EST
 * lui-même le groupe le plus profond : il apparaît comme une entrée simple portant
 * ce nom, jamais comme un en-tête de groupe vide au-dessus d'un unique "Exercice 1".
 *
 * Plusieurs exercices CONSÉCUTIFS peuvent partager ce même cas (aucun des deux n'a de
 * référence propre reconnue, même groupe) - ex. bepc-blanc-littoral-2026-cameroun,
 * dont la Partie A est scindée en deux Exercise ("A1"/"A2", jamais littéralement
 * "Exercice 1"/"Exercice 2") sans qu'aucun sujet ne les distingue par un repère
 * reconnu. Ils désignent la MÊME section, jamais deux sous-parties distinctes : les
 * compter comme une seule entrée de sommaire (ancrée sur le premier) évite qu'un même
 * libellé de groupe ("Partie A") apparaisse deux fois de suite, une fois comme entrée
 * cliquable et une fois comme en-tête au-dessus d'un "Exercice 1" qui n'a pas lieu
 * d'être.
 */
function entreesGroupees(exercises: ExerciceLabelSource[]): SommaireEntry[] {
  const compteurs = new Map<string, number>()
  const entries: SommaireEntry[] = []
  let dernierGroupeFeuille: string | null = null

  for (const exercise of exercises) {
    const groupes = exercise.groupes
    const aUneReferencePropre = exercise.titre.trim().length > 0

    // Un exercice individuel peut rester hors de tout groupe dans une épreuve par
    // ailleurs groupée (ex. un exercice isolé avant la première "Partie") : sommaire
    // plat pour lui seul, comme si l'épreuve entière ne comportait aucun groupe.
    if (groupes.length === 0) {
      entries.push({
        id: exerciceAnchorId(exercise.numero_exercice),
        short: libelleCourtExercice(exercise),
        long: libelleLong(exercise),
        title: exercise.titre.trim() || undefined,
      })
      dernierGroupeFeuille = null
      continue
    }

    if (!aUneReferencePropre) {
      const cle = groupes.join(" > ")
      if (cle === dernierGroupeFeuille) continue
      dernierGroupeFeuille = cle
      const label = groupes[groupes.length - 1]
      entries.push({
        id: exerciceAnchorId(exercise.numero_exercice),
        short: jetonCourtGroupe(label),
        long: label,
        groupPath: groupes.slice(0, -1),
      })
      continue
    }

    dernierGroupeFeuille = null
    const cle = groupes.join(" > ")
    const n = (compteurs.get(cle) ?? 0) + 1
    compteurs.set(cle, n)
    entries.push({
      id: exerciceAnchorId(exercise.numero_exercice),
      short: `${jetonCourtGroupe(groupes[groupes.length - 1])} ${n}`,
      long: `Exercice ${n}`,
      title: exercise.titre.trim(),
      groupPath: groupes,
    })
  }

  return entries
}

/**
 * Sommaire de navigation entre les exercices d'une épreuve. Les libellés viennent du
 * backend (voir catalog.rendering._exercise_titre_et_points) : le titre d'un exercice
 * n'a pas de champ dédié en base, il est extrait de son en-tête d'énoncé - d'où le repli
 * sur "Exercice {numero}" quand l'épreuve source n'en portait aucun.
 *
 * Deux présentations selon que l'épreuve est organisée en groupes ou non (voir
 * ExerciceLabelSource.groupes) : la grande majorité des épreuves n'en a aucun, et
 * garde le sommaire plat historique - seule une épreuve à Parties/sections/matières
 * distinctes bascule sur entreesGroupees, qui hiérarchise ET renumérote localement.
 */
export function EpreuveSommaire({ exercises }: { exercises: ExerciceLabelSource[] }) {
  const estGroupee = exercises.some((exercise) => exercise.groupes.length > 0)

  const entries: SommaireEntry[] = estGroupee
    ? entreesGroupees(exercises)
    : exercises.map((exercise) => ({
        id: exerciceAnchorId(exercise.numero_exercice),
        short: libelleCourtExercice(exercise),
        long: libelleLong(exercise),
        title: exercise.titre.trim() || undefined,
      }))

  return <SommaireNav entries={entries} ariaLabel="Sommaire des exercices" />
}
