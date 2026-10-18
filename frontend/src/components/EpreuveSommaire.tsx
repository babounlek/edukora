import { SommaireNav, type SommaireEntry } from "@/components/SommaireNav"
import { t, useI18n } from "@/lib/i18n"

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

/** À partir de ce nombre d'exercices, une épreuve groupée se présente par sections (voir sectionsDEpreuve). */
export const MIN_EXERCICES_SECTIONS = 6

export interface SectionEpreuve<T extends ExerciceLabelSource> {
  /** Pile de groupes de la section, jointe : sert de clé et distingue deux sections de même nom. */
  cle: string
  /** Libellé court (le repère de groupe : « SECTION 2.1 ») : pastilles de la barre mobile. */
  label: string
  /**
   * Intitulé complet (« Section 2.1 The Gospel According to Luke »). Dans un sujet à sections, l'en-tête
   * d'énoncé de chaque exercice est celui de sa section, pas de la question : c'est le titre porté par la
   * majorité des exercices de la section (un exercice isolé peut en porter un autre, comme « 1.0 THE OLD
   * TESTAMENT - Section 1.1 ... » sur le premier). Le repère court quand aucun titre ne domine.
   */
  intitule: string
  /** `index` = rang de l'exercice dans l'épreuve entière (la numérotation affichée ne repart pas à 1). */
  items: { exercise: T; index: number }[]
}

/**
 * Découpe une longue épreuve en sections, dans l'ordre du sujet : un exercice par question de
 * dissertation fait des épreuves du GCE à 18 ou 36 « exercices » (Religious Studies, History...), que
 * ni une rangée de pastilles ni une grille ne rendent navigables. Renvoie null - et le sommaire plat
 * historique s'applique - dès que l'épreuve est courte (moins de MIN_EXERCICES_SECTIONS exercices),
 * qu'un exercice n'appartient à aucun groupe (les sections ne couvriraient pas tout le sujet) ou qu'il
 * n'y a qu'une section : une seule section ne fait rien gagner.
 */
export function sectionsDEpreuve<T extends ExerciceLabelSource>(exercises: T[]): SectionEpreuve<T>[] | null {
  if (exercises.length < MIN_EXERCICES_SECTIONS) return null
  if (exercises.some((exercise) => exercise.groupes.length === 0)) return null
  const sections: SectionEpreuve<T>[] = []
  exercises.forEach((exercise, index) => {
    const cle = exercise.groupes.join(" > ")
    const derniere = sections[sections.length - 1]
    if (derniere && derniere.cle === cle) derniere.items.push({ exercise, index })
    else {
      const label = exercise.groupes.join(" · ")
      sections.push({ cle, label, intitule: label, items: [{ exercise, index }] })
    }
  })
  for (const section of sections) {
    // Titre entier, pas libelleLong : celui-ci coupe sur « - » pour les fils d'Ariane de la SVT
    // et tronquerait « ... Islam (570CE - 661CE) » en « 661CE) ». Le CSS tronque, l'infobulle complète.
    const comptes = new Map<string, number>()
    for (const { exercise } of section.items) {
      const titre = exercise.titre.trim()
      if (titre) comptes.set(titre, (comptes.get(titre) ?? 0) + 1)
    }
    const [dominant, n] = [...comptes.entries()].sort((a, b) => b[1] - a[1])[0] ?? ["", 0]
    if (dominant && n * 2 > section.items.length) section.intitule = dominant
  }
  return sections.length > 1 ? sections : null
}

/** La section qui contient l'exercice de rang `index` (rang dans l'épreuve entière), null hors sections. */
export function sectionDeLExercice<T extends ExerciceLabelSource>(sections: SectionEpreuve<T>[] | null, index: number) {
  return sections?.find((section) => section.items.some((item) => item.index === index)) ?? null
}

/**
 * Libellé d'un exercice dans une épreuve présentée par sections : son titre est celui de la section
 * (voir SectionEpreuve.intitule), il ne distingue donc pas deux questions ; seul le numéro imprimé le fait.
 */
export function libelleDansSection(exercise: ExerciceLabelSource) {
  const numero = exercise.numero_exercice.trim()
  return NUMERIQUE_RE.test(numero) ? t("ed.exercice_n", { n: numero }) : numero
}

/** Vrai quand l'en-tête de l'exercice EST l'intitulé de sa section, déjà affiché au-dessus : le répéter dans chaque carte n'apprend rien. */
export function repeteLIntituleDeSection(exercise: ExerciceLabelSource, section: { intitule: string } | null) {
  const titre = exercise.titre.trim()
  return section !== null && titre !== "" && titre === section.intitule
}

const TITRE_NUMERO_RE = /^(exercice|exercise|question)\s*\d+$/i

/**
 * Vrai quand le titre de l'exercice le distingue de ses voisins (« Exercice 1 : Chimie organique », un
 * sujet de SVT ou de maths) : il reste alors son libellé, même dans une longue épreuve à sections. Faux
 * quand il est vide, réduit à un numéro, ou n'est que l'intitulé de la section répété (GCE) : l'exercice se
 * reconnaît alors à son numéro imprimé et au début de sa question (voir libelleDansSection, apercuQuestion).
 */
export function titreDistinctif(exercise: ExerciceLabelSource, section: { intitule: string } | null) {
  const titre = exercise.titre.trim()
  return titre !== "" && !TITRE_NUMERO_RE.test(titre) && !repeteLIntituleDeSection(exercise, section)
}

function enTexteBrut(texte: string) {
  return texte.replace(/[*_`#>$]/g, "").replace(/\s+/g, " ").trim()
}

/** Retire la première ligne d'un énoncé quand c'est le `titre` (en-tête de section collé devant chaque question). */
export function sansEnteteDeSection(markdown: string, titre: string) {
  const attendu = enTexteBrut(titre).toLowerCase()
  const lignes = markdown.split("\n")
  const premiere = lignes.findIndex((ligne) => ligne.trim() !== "")
  if (!attendu || premiere === -1 || enTexteBrut(lignes[premiere]).toLowerCase() !== attendu) return markdown
  return lignes.slice(premiere + 1).join("\n").replace(/^\s*\n/, "")
}

const APERCU_LONGUEUR_MAX = 90

/**
 * Début de la question, pour choisir sans ouvrir : les exercices d'une dissertation n'ont pas de titre
 * propre, la question EST l'exercice. Saute l'en-tête (« **Section 2.1 ...** », identique pour toute la
 * section), le balisage Markdown et les consignes de points.
 */
export function apercuQuestion(enonceMarkdown: string, titre = "", longueurMax = APERCU_LONGUEUR_MAX) {
  const entete = enTexteBrut(titre).toLowerCase()
  const lignes = enonceMarkdown
    .split(/\n+/)
    .map(enTexteBrut)
    .filter((ligne) => ligne && ligne.toLowerCase() !== entete && !/^\(\d+\s*marks?\)$/i.test(ligne))
  const debut = lignes[0] ?? ""
  return debut.length <= longueurMax ? debut : `${debut.slice(0, longueurMax - 1).trimEnd()}…`
}

const NUMERIQUE_RE = /^\d+$/

// Au-delà, le libellé déborde la sidebar (220px) et se fait couper en plein milieu du
// fil d'Ariane, là où l'information utile se trouve justement à la fin.
const LONGUEUR_MAX_SIDEBAR = 48

/** "Ex. 3" pour un repère numérique, le repère tel quel sinon ("Problème", "Section III"). */
export function libelleCourtExercice(exercise: ExerciceLabelSource) {
  return NUMERIQUE_RE.test(exercise.numero_exercice.trim())
    ? t("ed.ex_n", { n: exercise.numero_exercice.trim() })
    : exercise.numero_exercice.trim()
}

/**
 * Les épreuves de SVT titrent leurs exercices par un fil d'Ariane complet ("Partie A :
 * Évaluation des ressources - I. Évaluation des savoirs - Exercice 1 : QCM", 24 titres
 * du corpus dépassent 70 caractères) : on n'en garde que le dernier segment, le seul
 * qui distingue un exercice de son voisin - les précédents sont communs à toute une
 * partie de l'épreuve. Le titre entier reste accessible en infobulle (voir SommaireNav).
 */
export function libelleLong(exercise: ExerciceLabelSource) {
  const titre = exercise.titre.trim() || t("ed.exercice_n", { n: exercise.numero_exercice.trim() })
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
      long: t("ed.exercice_n", { n }),
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
  useI18n()
  const estGroupee = exercises.some((exercise) => exercise.groupes.length > 0)

  const entries: SommaireEntry[] = estGroupee
    ? entreesGroupees(exercises)
    : exercises.map((exercise) => ({
        id: exerciceAnchorId(exercise.numero_exercice),
        short: libelleCourtExercice(exercise),
        long: libelleLong(exercise),
        title: exercise.titre.trim() || undefined,
      }))

  return <SommaireNav entries={entries} ariaLabel={t("ed.sommaire_aria")} />
}
