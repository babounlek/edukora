import type { ResultatRecherche, TypeResultatRecherche } from "@/api/types"
import { trackEvent } from "@/lib/analytics"
import {
  coursDetailPath,
  coursListPath,
  epreuveDetailPath,
  epreuveInediteDetailPath,
  epreuveReaderPath,
  themeExercicesPath,
} from "@/lib/countryPath"

/** Ordre d'affichage des groupes : le thème d'abord (la meilleure porte d'entrée), la question de
 * quiz en dernier. Le même que celui du serveur (recherche.moteur.ORDRE_GROUPES). */
export const TYPES_RECHERCHE: TypeResultatRecherche[] = ["THEME", "COURS", "EPREUVE", "INEDITE", "EXERCICE", "QUIZ"]

export const LIBELLES_TYPE: Record<TypeResultatRecherche, { singulier: string; pluriel: string }> = {
  THEME: { singulier: "Thème", pluriel: "Thèmes" },
  COURS: { singulier: "Cours", pluriel: "Cours" },
  EPREUVE: { singulier: "Épreuve", pluriel: "Épreuves" },
  INEDITE: { singulier: "Épreuve inédite", pluriel: "Épreuves inédites" },
  EXERCICE: { singulier: "Exercice", pluriel: "Exercices" },
  QUIZ: { singulier: "Quiz", pluriel: "Questions de quiz" },
}

/** En dessous, la saisie n'est pas envoyée : un ou deux caractères ne désignent rien. */
export const LONGUEUR_MIN_RECHERCHE = 2

// --- Surbrillance --------------------------------------------------------------------

/**
 * Version de `texte` sans accents et en minuscules, de MÊME LONGUEUR (un caractère pour un
 * caractère) : une position trouvée dans l'une vaut pour l'autre. Même principe que
 * recherche.texte._plier côté serveur - c'est ce qui permet de surligner « théorème » quand
 * l'élève a tapé « theoreme », sans décaler le surlignage dans la chaîne d'origine.
 */
export function plier(texte: string): string {
  let sortie = ""
  for (const caractere of texte) {
    const decompose = caractere.toLowerCase().normalize("NFKD").replace(/\p{Diacritic}/gu, "")
    // Un caractère d'origine compte pour UN caractère plié, même si sa décomposition en donne plusieurs
    // (ligature, exposant) : sinon les positions des deux chaînes divergeraient.
    sortie += decompose.length > 0 ? decompose[0] : " "
  }
  return sortie
}

const MOTS_VIDES = new Set([
  "de", "du", "des", "la", "le", "les", "un", "une", "et", "ou", "en", "au", "aux", "sur", "dans", "par",
  "pour", "avec", "sans", "est", "que", "qui", "quoi", "ce", "se", "sa", "son", "ses", "ma", "mon", "mes",
  "ta", "ton", "tes", "il", "elle", "on", "ne", "pas",
])

/** Mots de la requête à surligner : sans accents, sans mots vides, au singulier approximatif
 * (« équations » -> « equation »), trois caractères au moins - un « d » isolé surlignerait la moitié du texte. */
export function jetonsDeSurbrillance(requete: string): string[] {
  const jetons = plier(requete.replace(/\b(?:[ldjmtsc]|qu|jusqu|lorsqu|puisqu)['’]/gi, ""))
    .split(/[^a-z0-9]+/)
    .filter((mot) => mot.length >= 3 && !MOTS_VIDES.has(mot))
    .map((mot) => (mot.length >= 4 && /[sx]$/.test(mot) && !/^\d+$/.test(mot) && mot !== "maths" ? mot.slice(0, -1) : mot))
  return [...new Set(jetons)]
}

export interface MorceauSurligne {
  texte: string
  surligne: boolean
}

/** Découpe `texte` en morceaux, ceux qui commencent un mot cherché étant marqués `surligne`. Le
 * surlignage couvre le mot entier (« Thalès » en entier pour « thal »), pas seulement le préfixe. */
export function decouperSurbrillance(texte: string, jetons: string[]): MorceauSurligne[] {
  if (!texte || jetons.length === 0) return [{ texte, surligne: false }]
  const morceaux: MorceauSurligne[] = []
  let fin = 0
  // Mot par mot plutôt qu'une expression régulière « début de mot » : un lookbehind (?<!...) lève une
  // SyntaxError sur les iPhone antérieurs à iOS 16.4, et ferait planter l'affichage des résultats.
  for (const mot of plier(texte).matchAll(/[a-z0-9]+/g)) {
    if (!jetons.some((jeton) => mot[0].startsWith(jeton))) continue
    const debut = mot.index ?? 0
    if (debut > fin) morceaux.push({ texte: texte.slice(fin, debut), surligne: false })
    morceaux.push({ texte: texte.slice(debut, debut + mot[0].length), surligne: true })
    fin = debut + mot[0].length
  }
  if (fin < texte.length) morceaux.push({ texte: texte.slice(fin), surligne: false })
  return morceaux.length > 0 ? morceaux : [{ texte, surligne: false }]
}

// --- Destinations --------------------------------------------------------------------

/** Les trois façons de travailler un thème, chacune vers la page qui existe déjà. */
export interface ActionTheme {
  cle: "cours" | "exercices" | "quiz"
  libelle: string
  nb: number
  to: string
}

function parametres(valeurs: Record<string, string | number | null | undefined>): string {
  const params = new URLSearchParams()
  for (const [cle, valeur] of Object.entries(valeurs)) {
    if (valeur !== null && valeur !== undefined && valeur !== "") params.set(cle, String(valeur))
  }
  const texte = params.toString()
  return texte ? `?${texte}` : ""
}

export function actionsTheme(country: string, resultat: ResultatRecherche): ActionTheme[] {
  const { tag_id, subject_code, nb_cours = 0, nb_quiz = 0, nb_exercices = 0 } = resultat.details
  if (tag_id === undefined) return []
  const cursus = resultat.cursus_cible
  const actions: ActionTheme[] = []
  if (nb_cours > 0) {
    actions.push({
      cle: "cours",
      libelle: nb_cours > 1 ? `${nb_cours} cours` : "1 cours",
      nb: nb_cours,
      to: `${coursListPath(country)}${parametres({ theme: tag_id, subject: subject_code, cursus })}`,
    })
  }
  // La page des exercices d'un thème est propre à un (cursus, matière) : sans cursus connu, elle n'existe pas.
  if (nb_exercices > 0 && cursus !== null) {
    actions.push({
      cle: "exercices",
      libelle: nb_exercices > 1 ? `${nb_exercices} exercices` : "1 exercice",
      nb: nb_exercices,
      to: `${themeExercicesPath(country, tag_id)}${parametres({ subject: subject_code, cursus })}`,
    })
  }
  if (nb_quiz > 0) {
    actions.push({
      cle: "quiz",
      libelle: nb_quiz > 1 ? `Quiz · ${nb_quiz} questions` : "Quiz · 1 question",
      nb: nb_quiz,
      to: cheminQuiz(resultat),
    })
  }
  return actions
}

function cheminQuiz(resultat: ResultatRecherche): string {
  return `/quiz${parametres({ cursus: resultat.cursus_cible, theme: resultat.details.tag_id })}`
}

/** Où mène un résultat. Un thème mène à sa première ressource disponible (cours, sinon exercices,
 * sinon quiz) - la carte complète propose les trois (voir actionsTheme). */
export function cibleResultat(country: string, resultat: ResultatRecherche): string {
  const { slug, id, ancre } = resultat.details
  switch (resultat.type) {
    case "THEME": {
      const premiere = actionsTheme(country, resultat)[0]
      return premiere?.to ?? coursListPath(country)
    }
    case "COURS":
      return coursDetailPath(slug ?? "")
    case "EPREUVE":
      return epreuveDetailPath(country, slug ?? "")
    case "INEDITE":
      return epreuveInediteDetailPath(country, slug ?? id ?? "")
    case "EXERCICE": {
      // Lecteur (corrigé compris) si le visiteur y a droit, fiche publique de l'épreuve sinon - dans les
      // deux cas posé sur l'exercice trouvé.
      const peutLire = resultat.acces === "libre" || resultat.acces === "ouvert"
      const base = peutLire ? epreuveReaderPath(country, slug ?? "") : epreuveDetailPath(country, slug ?? "")
      return ancre ? `${base}#${ancre}` : base
    }
    case "QUIZ":
      return cheminQuiz(resultat)
  }
}

// --- Recherches récentes -------------------------------------------------------------

const CLE_RECENTES = "edukamer_recherches_recentes"
const MAX_RECENTES = 5

export function lireRecentes(): string[] {
  try {
    const brut = JSON.parse(localStorage.getItem(CLE_RECENTES) ?? "[]")
    return Array.isArray(brut) ? brut.filter((v): v is string => typeof v === "string").slice(0, MAX_RECENTES) : []
  } catch {
    return []
  }
}

/** Garde les dernières recherches VALIDÉES (Entrée, ou clic sur un résultat), la plus récente d'abord. */
export function memoriserRecente(requete: string) {
  const propre = requete.trim()
  if (propre.length < LONGUEUR_MIN_RECHERCHE) return
  try {
    const autres = lireRecentes().filter((r) => r.toLowerCase() !== propre.toLowerCase())
    localStorage.setItem(CLE_RECENTES, JSON.stringify([propre, ...autres].slice(0, MAX_RECENTES)))
  } catch {
    // stockage indisponible (navigation privée) : l'historique ne persistera pas, sans autre conséquence
  }
}

export function oublierRecentes() {
  try {
    localStorage.removeItem(CLE_RECENTES)
  } catch {
    // rien à nettoyer si le stockage est indisponible
  }
}

// --- Mesure --------------------------------------------------------------------------

/** D'où part une recherche : la palette de l'en-tête ou la page de résultats. */
export type SourceRecherche = "palette" | "page"

/** Une recherche validée (Entrée ou bouton). Jamais le texte : seulement d'où elle part. */
export function tracerRechercheLancee(source: SourceRecherche) {
  trackEvent("recherche_lancee", { source })
}

/** Un résultat ouvert : son type et son rang (1 = premier de son groupe) disent si le classement
 * tient ses promesses, et `acces` si l'élève tombe sur un contenu qu'il peut lire. */
export function tracerResultatClique(source: SourceRecherche, resultat: ResultatRecherche, rang: number) {
  trackEvent("recherche_resultat_clique", { source, type: resultat.type, rang, acces: resultat.acces })
}

// --- Onglets de résultats ------------------------------------------------------------

/**
 * Les onglets de la page de résultats, dans le MÊME ordre et avec les MÊMES mots que les onglets
 * « Réviser » (voir components/ReviserTabs) : Épreuves, Cours, Thèmes, Quiz. Deux rangées d'onglets
 * superposées qui ne parlent pas la même langue (« Exercices », « Questions de quiz »...) obligeaient à
 * se demander si c'était la même chose. Les exercices et les épreuves inédites rejoignent
 * « Épreuves » : un exercice est un morceau d'épreuve, une inédite en est une.
 */
export interface FamilleRecherche {
  cle: TypeResultatRecherche
  libelle: string
  types: TypeResultatRecherche[]
}

export const FAMILLES_RECHERCHE: FamilleRecherche[] = [
  { cle: "EPREUVE", libelle: "Épreuves", types: ["EPREUVE", "INEDITE", "EXERCICE"] },
  { cle: "COURS", libelle: "Cours", types: ["COURS"] },
  { cle: "THEME", libelle: "Thèmes", types: ["THEME"] },
  { cle: "QUIZ", libelle: "Quiz", types: ["QUIZ"] },
]

/** L'onglet d'un type de résultat (un lien ancien `?type=EXERCICE` mène à l'onglet Épreuves). */
export function familleDe(type: TypeResultatRecherche): FamilleRecherche {
  return FAMILLES_RECHERCHE.find((f) => f.types.includes(type)) ?? FAMILLES_RECHERCHE[0]
}

// --- Arrivée sur la page de recherche ------------------------------------------------

/** État de navigation posé par la loupe de l'en-tête, le bouton des onglets Réviser et les raccourcis
 * clavier : la page de recherche y reconnaît « l'élève vient CHERCHER » et met le champ en saisie, avec
 * le texte déjà tapé sélectionné. Un état de navigation plutôt qu'un paramètre d'URL : il ne se partage pas
 * avec le lien et ne reste pas dans l'historique d'un retour arrière. */
export const ETAT_FOCUS_RECHERCHE = { focusRecherche: true } as const

export function veutFocusRecherche(etat: unknown): boolean {
  return typeof etat === "object" && etat !== null && (etat as { focusRecherche?: unknown }).focusRecherche === true
}
