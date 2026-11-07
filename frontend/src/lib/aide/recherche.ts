import { remplirGabarits } from "@/lib/aide/texte"
import type { ArticleAideResume } from "@/lib/aide/types"

/** Minuscules, sans accents ni ponctuation : « Reçois-tu ton CODE ? » -> « recois tu ton code ». */
export function normaliser(texte: string): string {
  return texte
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/œ/g, "oe")
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
}

/** Mots vides trop courants pour départager deux articles. */
const MOTS_VIDES = new Set([
  "le", "la", "les", "un", "une", "des", "de", "du", "d", "l", "et", "ou", "a", "au", "aux", "en", "mon", "ma", "mes", "ton", "ta",
  "tes", "je", "j", "tu", "il", "on", "ce", "ca", "que", "qui", "pour", "pas", "ne", "n", "est", "sur", "the", "of", "to", "my", "is", "i",
])

function distanceAuPlus1(a: string, b: string): boolean {
  if (a === b) return true
  if (Math.abs(a.length - b.length) > 1) return false
  let i = 0
  let j = 0
  let ecarts = 0
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) {
      i++
      j++
      continue
    }
    if (++ecarts > 1) return false
    if (a.length > b.length) i++
    else if (a.length < b.length) j++
    else {
      i++
      j++
    }
  }
  return ecarts + (a.length - i) + (b.length - j) <= 1
}

/** Le jeton figure-t-il dans la liste de mots : tel quel, comme début de mot, ou à une faute près (mots de 5 lettres et plus). */
function correspond(jeton: string, mots: string[]): number {
  let meilleur = 0
  for (const mot of mots) {
    if (mot === jeton) return 3
    if (jeton.length >= 3 && mot.startsWith(jeton)) meilleur = Math.max(meilleur, 2)
    else if (jeton.length >= 5 && mot.length >= 5 && distanceAuPlus1(jeton, mot)) meilleur = Math.max(meilleur, 1)
  }
  return meilleur
}

/**
 * Cherche dans les titres, résumés et mots-clés (les articles complets ne sont pas chargés pour chercher).
 * Tous les mots utiles de la requête doivent se retrouver quelque part ; un mot du titre pèse plus qu'un mot-clé,
 * qui pèse plus qu'un mot du résumé. Sans accent, avec une faute de frappe tolérée. Triés du plus au moins pertinent.
 */
export function rechercherArticles(articles: ArticleAideResume[], requete: string): ArticleAideResume[] {
  const jetons = normaliser(requete)
    .split(" ")
    .filter((j) => j && !MOTS_VIDES.has(j))
  if (jetons.length === 0) return []
  const resultats: { article: ArticleAideResume; score: number }[] = []
  for (const article of articles) {
    const titre = normaliser(remplirGabarits(article.titre)).split(" ")
    const motsCles = normaliser(article.mots_cles).split(" ")
    const resume = normaliser(remplirGabarits(article.resume)).split(" ")
    let score = 0
    let tous = true
    for (const jeton of jetons) {
      const dansTitre = correspond(jeton, titre)
      const dansMotsCles = correspond(jeton, motsCles)
      const dansResume = correspond(jeton, resume)
      if (!dansTitre && !dansMotsCles && !dansResume) {
        tous = false
        break
      }
      score += dansTitre * 4 + dansMotsCles * 3 + dansResume
    }
    if (tous) resultats.push({ article, score })
  }
  return resultats.sort((a, b) => b.score - a.score).map((r) => r.article)
}

/**
 * Ramène un chemin du routeur à la forme des `pages` d'un article : le préfixe pays à deux lettres (« /cm/epreuves »)
 * n'en fait pas partie, et la barre finale non plus.
 */
function cheminDePage(chemin: string): string {
  const segments = chemin.split("/").filter(Boolean)
  if (segments.length > 0 && /^[a-z]{2}$/i.test(segments[0])) segments.shift()
  return "/" + segments.join("/")
}

/** Les articles proposés en tête du panneau d'aide sur cette page : ceux dont `pages` contient son chemin ou un de ses parents. */
export function articlesPourPage(articles: ArticleAideResume[], chemin: string): ArticleAideResume[] {
  const page = cheminDePage(chemin)
  return articles.filter((article) =>
    article.pages.some((p) => (p === "/" ? page === "/" : page === p || page.startsWith(`${p}/`))),
  )
}
