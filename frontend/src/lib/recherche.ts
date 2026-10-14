import type { ResultatRecherche, TypeResultatRecherche } from "@/api/types"
import { trackEvent } from "@/lib/analytics"
import { langueCourante, t, tn, type CleI18n } from "@/lib/i18n"
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

// Accesseurs : le libellé se lit au moment de l'affichage, dans la langue courante.
const libellesDuType = (singulier: CleI18n, pluriel: CleI18n) => ({
  get singulier() { return t(singulier) },
  get pluriel() { return t(pluriel) },
})

export const LIBELLES_TYPE: Record<TypeResultatRecherche, { singulier: string; pluriel: string }> = {
  THEME: libellesDuType("rc.theme_s", "rc.theme_p"),
  COURS: libellesDuType("rc.cours_s", "rc.cours_p"),
  EPREUVE: libellesDuType("rc.epreuve_s", "rc.epreuve_p"),
  INEDITE: libellesDuType("rc.inedite_s", "rc.inedite_p"),
  EXERCICE: libellesDuType("rc.exercice_s", "rc.exercice_p"),
  QUIZ: libellesDuType("rc.quiz_s", "rc.quiz_p"),
}

/** Titre d'un groupe de résultats : en français celui du serveur (source de vérité), sinon le libellé du type. */
export function libelleGroupe(type: TypeResultatRecherche, libelleServeur: string): string {
  return langueCourante() === "fr" ? libelleServeur : LIBELLES_TYPE[type].pluriel
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
      libelle: tn("rc.n_cours", nb_cours),
      nb: nb_cours,
      to: `${coursListPath(country)}${parametres({ theme: tag_id, subject: subject_code, cursus })}`,
    })
  }
  // La page des exercices d'un thème est propre à un (cursus, matière) : sans cursus connu, elle n'existe pas.
  if (nb_exercices > 0 && cursus !== null) {
    actions.push({
      cle: "exercices",
      libelle: tn("rc.n_exercices", nb_exercices),
      nb: nb_exercices,
      to: `${themeExercicesPath(country, tag_id)}${parametres({ subject: subject_code, cursus })}`,
    })
  }
  if (nb_quiz > 0) {
    actions.push({
      cle: "quiz",
      libelle: tn("rc.act_quiz", nb_quiz),
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

/** Une recherche validée (Entrée, bouton, suggestion, thème proposé). Jamais le texte : seulement d'où elle part
 * et, quand c'est une suggestion, comment (`via` : "completion" = une complétion pendant la frappe). */
export function tracerRechercheLancee(source: SourceRecherche, via?: "completion") {
  trackEvent("recherche_lancee", via ? { source, via } : { source })
}

/** Les mots d'intention retirés de la requête (« corrigés », « sujets »...), tels qu'on les montre dans la
 * pastille « Compris ». Clés : le mot ramené au singulier, comme le fait le serveur. */
export const LIBELLES_MOT_TYPE: Record<string, string> = {
  get corrige() { return t("rc.mot_corrige") },
  get sujet() { return t("rc.mot_sujet") },
  get epreuve() { return t("rc.mot_epreuve") },
  get annale() { return t("rc.mot_annale") },
  get exercice() { return t("rc.mot_exercice") },
  get cour() { return t("rc.mot_cour") },
  get lecon() { return t("rc.mot_lecon") },
  get fiche() { return t("rc.mot_fiche") },
  get quiz() { return t("rc.mot_quiz") },
  get qcm() { return t("rc.mot_qcm") },
  get question() { return t("rc.mot_question") },
  get theme() { return t("rc.mot_theme") },
  // Mots d'une recherche en anglais (voir recherche.intention.MOTS_TYPE_EN), qui reprennent les mêmes libellés.
  get solution() { return t("rc.mot_corrige") },
  get past() { return t("rc.mot_annale") },
  get paper() { return t("rc.mot_epreuve") },
  get exam() { return t("rc.mot_epreuve") },
  get mock() { return t("rc.mot_epreuve") },
  get lesson() { return t("rc.mot_lecon") },
  get course() { return t("rc.mot_cour") },
  get exercise() { return t("rc.mot_exercice") },
  get mcq() { return t("rc.mot_qcm") },
  get topic() { return t("rc.mot_theme") },
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
  { cle: "EPREUVE", get libelle() { return t("nav.epreuves") }, types: ["EPREUVE", "INEDITE", "EXERCICE"] },
  { cle: "COURS", get libelle() { return t("nav.cours") }, types: ["COURS"] },
  { cle: "THEME", get libelle() { return t("qd.onglet_themes") }, types: ["THEME"] },
  { cle: "QUIZ", get libelle() { return t("qd.onglet_quiz") }, types: ["QUIZ"] },
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
