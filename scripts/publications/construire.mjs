// Prépare une semaine de publications « Fiches EduKora » à partir des fiches GRATUITES du site :
// instantané des fiches, vues HTML (sources/pages.html), brouillon des légendes, lignes du planning.
//
//   node construire.mjs <dossier de la semaine>               construit (prend l'instantané s'il manque)
//   node construire.mjs <dossier de la semaine> --actualiser  reprend l'instantané sur le site, puis construit
//   node construire.mjs <dossier de la semaine> --verifier    compare le site à l'instantané et contrôle les légendes,
//                                                             sans rien écrire (à lancer avant de publier)
//
// Le dossier contient semaine.json (voir LISEZMOI.md). Aucun texte de fiche n'est recopié à la main : tout vient du site,
// pour que l'élève qui clique trouve exactement le texte de l'image.
import { createRequire } from "node:module"
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs"
import { basename, dirname, resolve } from "node:path"
import { fileURLToPath, pathToFileURL } from "node:url"

const SITE = "https://edukora.africa"
const ici = dirname(fileURLToPath(import.meta.url))
const racine = resolve(ici, "../..")
const front = resolve(racine, "frontend")
const katex = createRequire(resolve(front, "package.json"))("katex")
const url = (p) => pathToFileURL(resolve(front, p)).href

const args = process.argv.slice(2)
const dossier = resolve(args.find((a) => !a.startsWith("--")) ?? ".")
const mode = args.includes("--verifier") ? "verifier" : args.includes("--actualiser") ? "actualiser" : "construire"
if (!existsSync(resolve(dossier, "semaine.json"))) {
  console.error("Usage : node construire.mjs <dossier qui contient semaine.json> [--actualiser | --verifier]")
  process.exit(1)
}
const S = JSON.parse(readFileSync(resolve(dossier, "semaine.json"), "utf8"))
for (const champ of ["lundi", "format", "examen", "cursus", "matiere", "bandeau", "matiere_nom", "hashtags", "fiches"])
  if (S[champ] === undefined) throw new Error(`semaine.json : champ « ${champ} » manquant`)
if (!["methode", "definition"].includes(S.format)) throw new Error(`format inconnu : ${S.format} (methode ou definition)`)
if (S.fiches.length && S.fiches.length !== 5) throw new Error(`une semaine a 5 fiches, semaine.json en liste ${S.fiches.length}`)
const nomSemaine = basename(dossier)
const publications = resolve(dossier, "../..")
const sources = resolve(dossier, "sources")
const instantane = resolve(sources, "fiches-en-ligne.json")

// Les fiches se lisent sur le site. Une semaine préparée avant la mise en ligne de ses fiches (GCE en brouillon) les lit
// sur le serveur local ("source": "http://localhost") : retirer "source", corriger les ids, puis --actualiser une fois
// les fiches en production. Les essais de quiz se lisent toujours sur le site : c'est ce que verra l'élève.
const SOURCE = S.source ?? SITE
const EN = S.langue === "en"
const SANS_PLANNING = args.includes("--sans-planning")

// ---------------------------------------------------------------- l'instantané du site
async function lire(chemin, base = SITE) {
  const r = await fetch(base + chemin)
  if (!r.ok) throw new Error(`${base}${chemin} : ${r.status}`)
  return r.json()
}
const fusionner = (a, b) =>
  [...new Map([...a, ...b].map((s) => [`${s.annee}|${s.origine}`, s])).values()].sort((x, y) => x.annee - y.annee)

async function prendreInstantane() {
  const parId = new Map()
  for (const c of S.cursus) {
    const { fiches } = await lire(`/memos/fiches/?cursus=${c}&matiere=${S.matiere}`, SOURCE)
    for (const f of fiches.filter((f) => f.gratuit)) {
      const deja = parId.get(f.id)
      if (deja) { deja.sessions = fusionner(deja.sessions, f.sessions); deja.cursus.push(c); continue }
      const { id, terme, definition, exemple, piege, exercice, reponse, rubrique, sessions } = f
      parId.set(f.id, { id, terme, definition, exemple, piege, exercice, reponse, rubrique, sessions, cursus: [c] })
    }
  }
  // Un essai de quiz sans compte dans CETTE matière, pour chaque série de la semaine ? Sinon l'invitation renvoie ailleurs.
  const essais = (await lire("/quiz/essais/"))
    .filter((e) => S.cursus.includes(e.cursus) && e.subject === S.matiere)
    .map((e) => ({ cursus: e.cursus, theme: e.theme_name, questions: e.nb_questions }))
  return { pris_le: new Date().toISOString().slice(0, 10), fiches: [...parId.values()], essais }
}

const CHAMPS = ["terme", "definition", "exemple", "piege", "exercice", "reponse"]
function ecarts(ancien, nouveau) {
  const lignes = []
  for (const { id } of S.fiches) {
    const a = ancien.fiches.find((f) => f.id === id), n = nouveau.fiches.find((f) => f.id === id)
    if (!n) { lignes.push(`fiche ${id} : n'est plus gratuite (ou plus publiée) en ligne`); continue }
    if (!a) { lignes.push(`fiche ${id} : absente de l'instantané`); continue }
    for (const c of CHAMPS) if ((a[c] ?? "") !== (n[c] ?? "")) lignes.push(`fiche ${id} « ${n.terme} » : ${c} modifié en ligne`)
    if (JSON.stringify(a.sessions) !== JSON.stringify(n.sessions)) lignes.push(`fiche ${id} « ${n.terme} » : sessions modifiées en ligne`)
  }
  const quiz = (x) => S.cursus.every((c) => x.essais.some((e) => e.cursus === c))
  if (quiz(ancien) !== quiz(nouveau)) lignes.push(`essai de quiz sans compte : ${quiz(nouveau) ? "apparu" : "disparu"} dans la matière`)
  return lignes
}

// Un passage à écrire commence par ⟦ : on compte les ouvrants, pour qu'un ⟧ effacé par erreur ne cache rien.
const PLACE = /⟦/g
if (mode === "verifier") {
  if (!existsSync(instantane)) throw new Error("pas d'instantané : lancer d'abord la construction")
  const lignes = ecarts(JSON.parse(readFileSync(instantane, "utf8")), await prendreInstantane())
  const legendes = resolve(dossier, "legendes.md")
  const restes = existsSync(legendes) ? readFileSync(legendes, "utf8").match(PLACE) ?? [] : ["legendes.md absent"]
  if (restes.length) lignes.push(`legendes.md : ${restes.length} passage(s) ⟦…⟧ encore à écrire`)
  const tiktok = resolve(dossier, "legendes-tiktok.md")
  if (!existsSync(tiktok)) lignes.push("legendes-tiktok.md absent : relancer construire.mjs une fois legendes.md écrit")
  else if (readFileSync(tiktok, "utf8").includes("⟦")) lignes.push("legendes-tiktok.md : des passages ⟦…⟧ encore à écrire")
  const manquantes = S.fiches.map((f, k) => `videos/j${k + 1}-${f.cle}.mp4`).filter((v) => !existsSync(resolve(dossier, v)))
  if (manquantes.length) lignes.push(`vidéos TikTok absentes (filmer.py) : ${manquantes.join(", ")}`)
  console.log(lignes.length ? "À reprendre avant de publier :\n- " + lignes.join("\n- ") : "Site, instantané et légendes concordent.")
  process.exit(lignes.length ? 1 : 0)
}

mkdirSync(sources, { recursive: true })
let enLigne_
if (mode === "actualiser" || !existsSync(instantane)) {
  const nouveau = await prendreInstantane()
  if (existsSync(instantane)) {
    const lignes = ecarts(JSON.parse(readFileSync(instantane, "utf8")), nouveau)
    console.log(lignes.length ? "Changé depuis l'instantané précédent :\n- " + lignes.join("\n- ") : "Instantané inchangé.")
  }
  writeFileSync(instantane, JSON.stringify(nouveau, null, 2) + "\n")
  enLigne_ = nouveau
} else enLigne_ = JSON.parse(readFileSync(instantane, "utf8"))

// Les fiches qu'une AUTRE semaine utilise déjà (une même fiche peut être gratuite à deux examens : « Tontine »).
const dejaPrises = new Map()
const dossierSemaines = resolve(publications, "semaines")
if (existsSync(dossierSemaines))
  for (const d of readdirSync(dossierSemaines, { withFileTypes: true })) {
    const autre = resolve(dossierSemaines, d.name, "semaine.json")
    if (!d.isDirectory() || d.name === nomSemaine || !existsSync(autre)) continue
    // Un id n'a de sens que sur sa source (site ou serveur local) : les deux numérotations se recoupent.
    // Un semaine.json en cours d'écriture par une autre préparation ne se lit pas encore : on le signale et on passe.
    let a
    try { a = JSON.parse(readFileSync(autre, "utf8")) } catch { console.log(`(${d.name}/semaine.json illisible pour l'instant : ignoré)`); continue }
    for (const f of a.fiches ?? []) dejaPrises.set(`${a.source ?? SITE}|${f.id}`, d.name)
  }
const prise = (id) => dejaPrises.get(`${SOURCE}|${id}`)

// "fiches": [] : on liste les gratuites en ligne pour les choisir, sans rien construire.
if (!S.fiches.length) {
  console.log(`Gratuites en ligne (instantané du ${enLigne_.pris_le}) ; quiz sans compte dans la matière : ` +
    `${S.cursus.every((c) => enLigne_.essais.some((e) => e.cursus === c)) ? "oui" : "non"}`)
  for (const f of enLigne_.fiches) {
    const off = [...new Set(f.sessions.filter((s) => s.origine === "OFFICIEL").map((s) => s.annee))]
    const manque = ["exemple", "piege", "exercice", "reponse"].filter((c) => !f[c])
    console.log(`  id ${f.id} | ${f.terme} | ${f.rubrique || "-"} | ${off.length} session(s) officielle(s) ${off.join(",")}` +
      ` | séries ${f.cursus.join(",")}${manque.length ? ` | sans ${manque.join(", ")} (format definition)` : ""}` +
      (prise(f.id) ? ` | DÉJÀ DANS ${prise(f.id)} : à écarter` : ""))
  }
  console.log("Les textes complets sont dans sources/fiches-en-ligne.json. Remplir \"fiches\" dans semaine.json, puis relancer.")
  process.exit(0)
}

const fiches = S.fiches.map((choix, i) => {
  const f = enLigne_.fiches.find((n) => n.id === choix.id)
  if (!f) throw new Error(`la fiche ${choix.id} (${choix.cle}) n'est pas parmi les gratuites en ligne : voir sources/fiches-en-ligne.json`)
  if (!/^[a-z0-9-]+$/.test(choix.cle)) throw new Error(`clé « ${choix.cle} » : minuscules, chiffres et tirets seulement`)
  if (prise(choix.id) && !S.reprise)
    throw new Error(`la fiche ${choix.id} « ${f.terme} » est déjà dans ${prise(choix.id)} : en choisir une autre ` +
      `(ou "reprise": true dans semaine.json pour une semaine reprise exprès)`)
  const annees = [...new Set(f.sessions.filter((s) => s.origine === "OFFICIEL").map((s) => s.annee))].sort((a, b) => a - b)
  return { ...f, ...choix, rang: i + 1, annees }
})
const ecartees = enLigne_.fiches.filter((f) => !S.fiches.some((c) => c.id === f.id))
if (ecartees.length) console.log("Gratuites en ligne non retenues :", ecartees.map((f) => `${f.id} « ${f.terme} »`).join(", "))
const avecQuiz = S.cursus.every((c) => enLigne_.essais.some((e) => e.cursus === c))

// ---------------------------------------------------------------- les textes fixes, en français ou en anglais (GCE)
// Les images, les vidéos et les lignes publiées des légendes suivent la langue de la semaine ; les notes de travail
// (titres « Jour 1 », LISEZMOI, planning) restent en français, pour l'utilisateur.
const T = EN ? {
  fiches: "EduKora sheets", numero: "no.", et: "and", lang: "en",
  titres: { "When?": "When to use it?" }, aRetenir: /^\*\*Remember\*\*/,
  toucheMethode: "Tap to see the method →", toucheFiche: "Tap to see the sheet →",
  ficheRetenir: "Key facts sheet", ficheMethode: "Method sheet",
  // n compte des ANNÉES : au GCE, Paper 1 et Paper 2 d'une même année ne font qu'une.
  preuveN: (n, ex, a, b) => `Asked in the ${ex} in <b>${n} different years</b>, from ${a} to ${b}`,
  preuve1: (ex, a) => `Asked in the ${ex} in <b>${a}</b>`,
  exemple: "Example", piege: "The trap", aToi: "Your turn", reponse: "The answer",
  appelPost: "Write your answer in the comments. Answer tonight.", appelStatut: "Reply to this status. Answer tonight.",
  invitation: (q) => `<div class="invitation"><p><b>Want more practice?</b> Try a ${q ? "" : "free "}quiz${q ? "" : " in another subject"} on edukora.africa, no account needed.</p>
<p class="detail">More EduKora sheets are waiting: some free, the rest with a subscription.</p></div>`,
  touchePieges: "Tap to see the traps →", semaineEn: (m) => `This week in ${m}`, pieges: (ex) => `5 traps to avoid in the ${ex}`,
  lequel: "Which one have you fallen into?", piegeN: (i) => `Trap ${i} / 5`,
  defi: (mot) => `Sunday challenge: 5 ${mot}, without looking at the sheets`, defiReponses: "Sunday challenge: the answers",
  defiMot: "questions",
  fiche: "Sheet", saisDefinir: "Can you define it?", appelDefPost: "Write your definition in the comments.",
  appelDefStatut: "Reply to this status.", ficheCeSoir: "The sheet tonight.", laDefinition: "The definition",
  devineQ: "What's the word? 5 definitions from this week", devineR: "What's the word? The answers",
  toucheDefinitions: "Tap to see the definitions →", recapTitre: "5 definitions to keep", recapPreuve: "Save them for your revision.",
  auExamen: (ex, liste) => `In the ${ex} in <b>${liste}</b>`,
  auExamenN: (ex, n, a, b) => `In the ${ex}: <b>${n} sessions</b> between ${a} and ${b}`,
  finTitre: "The full sheet is waiting on edukora.africa",
  finDetail: "More EduKora sheets: some free, the rest with a subscription.",
  finDemain: (n) => `Follow us: sheet no. ${n} comes tomorrow.`, finSuite: "Follow us for more.",
  videoAppel: "Your answer in the comments, before the reveal.", videoDef: "Say it in your own words, in the comments.",
} : {
  fiches: "Fiches EduKora", numero: "n°", et: "et", lang: "fr",
  titres: { "Quand ?": "Quand l'utiliser ?" }, aRetenir: /^\*\*À retenir\*\*/,
  toucheMethode: "Touche l'image pour voir la méthode →", toucheFiche: "Touche l'image pour voir la fiche →",
  ficheRetenir: "Fiche à retenir", ficheMethode: "Fiche de méthode",
  preuveN: (n, ex, a, b) => `Demandée dans <b>${n} sujets</b> du ${ex} entre ${a} et ${b}`,
  preuve1: (ex, a) => `Demandée au ${ex} en <b>${a}</b>`,
  exemple: "Exemple", piege: "Le piège", aToi: "À toi", reponse: "La réponse",
  appelPost: "Écris ta réponse en commentaire. Correction ce soir.", appelStatut: "Réponds à ce statut. Correction ce soir.",
  // L'invitation, après l'effort. Pas de total de fiches : il change (« certaines gratuites, les autres avec l'abonnement »).
  invitation: (q) => `<div class="invitation"><p><b>Envie de t'entraîner encore ?</b> Essaie un quiz ${q ? "" : "gratuit dans une autre matière "}sur edukora.africa, sans compte.</p>
<p class="detail">D'autres Fiches EduKora t'y attendent : certaines gratuites, les autres avec l'abonnement.</p></div>`,
  touchePieges: "Touche l'image pour voir les pièges →", semaineEn: (m) => `La semaine en ${m}`, pieges: (ex) => `5 pièges à éviter au ${ex}`,
  lequel: "Lequel as-tu déjà fait ?", piegeN: (i) => `Piège ${i} / 5`,
  defi: (mot) => `Le défi du dimanche : 5 ${mot}, sans regarder les fiches`, defiReponses: "Le défi du dimanche : les réponses",
  defiMot: "questions",
  fiche: "Fiche", saisDefinir: "Sais-tu définir ?", appelDefPost: "Écris ta définition en commentaire.",
  appelDefStatut: "Réponds à ce statut.", ficheCeSoir: "La fiche ce soir.", laDefinition: "La définition",
  devineQ: "Quel est le mot ? 5 définitions de la semaine", devineR: "Quel est le mot ? Les réponses",
  toucheDefinitions: "Touche l'image pour voir les définitions →", recapTitre: "5 définitions à garder",
  recapPreuve: "Enregistre-les pour tes révisions.",
  auExamen: (ex, liste) => `Au ${ex} en <b>${liste}</b>`,
  auExamenN: (ex, n, a, b) => `Au ${ex} : <b>${n} sessions</b> entre ${a} et ${b}`,
  finTitre: "La fiche complète t'attend sur edukora.africa",
  finDetail: "D'autres Fiches EduKora : certaines gratuites, les autres avec l'abonnement.",
  finDemain: (n) => `Abonne-toi : la fiche n° ${n} arrive demain.`, finSuite: "Abonne-toi pour la suite.",
  videoAppel: "Ta réponse en commentaire, avant la correction.", videoDef: "Dis-le avec tes mots, en commentaire.",
}

// ---------------------------------------------------------------- texte et formules
const echapper = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
const NBSP = " "
// Une formule en ligne longue peut se couper (après un signe =, +…) ; une courte reste d'un seul tenant.
// Une équation chimique écrite d'un seul tenant (« \mathrm{A + B \rightleftharpoons C + D} ») n'a aucun point de coupure :
// on sort ses « + » (entourés d'espaces) et ses flèches du \mathrm, pour qu'elle puisse passer à la ligne.
const ouvrirEquation = (tex) => {
  const m = tex.match(/^\\mathrm\{([\s\S]*)\}$/)
  if (!m) return tex
  let profondeur = 0
  for (const c of m[1]) { profondeur += c === "{" ? 1 : c === "}" ? -1 : 0; if (profondeur < 0) return tex }
  const morceaux = m[1].split(/(\s\+\s|\s*(?:\\rightleftharpoons|\\longrightarrow|\\rightarrow|\\to|=)\s*)/)
  if (morceaux.length < 3) return tex
  return morceaux.map((p, i) => (i % 2 ? ` ${p.trim()} ` : p.trim() ? `\\mathrm{${p.trim()}}` : "")).join("")
}
// Dans une formule longue, une parenthèse ne se coupe pas (« (x − 2) » reste entière) : on en fait un groupe KaTeX.
const parenthesesEntieres = (tex) => {
  let x = tex
  for (let i = 0; i < 4; i++) x = x.replace(/(?<!\\left|\\big|\\Big|\\bigl|\\Bigl)\(([^()]*)\)/g, "{\u0005$1\u0006}")
  return x.replace(/\u0005/g, "(").replace(/\u0006/g, ")")
}
const maths = (tex, bloc) => {
  const long = !bloc && tex.length > 40
  const html = katex.renderToString(long ? parenthesesEntieres(ouvrirEquation(tex.trim())) : tex.trim(), { displayMode: bloc, throwOnError: true })
  return long ? `<span class="formule-longue">${html}</span>` : html
}
const UNITES = "km\\/h|m\\/s|g\\/mol|g\\/L|mol\\/L|kWh|kcal|kJ|MJ|kPa|kW|mA|mol|mL|dm³|cm³|m³|cm²|mm²|m²|cm|km|kg|mm|Pa|cal|g|L|m|min|h|s|V|A|W|J|N|Hz|Ω|°C|δ|%"
// Après une formule, « M » (mol/L, au GCE) est aussi une unité : « $0.1$ M ».
const UNITE_APRES = new RegExp(`^ (${UNITES}|M)(?![A-Za-zà-ÿ])`)
const RELATION = /^\s*(=|<|>|\\approx|\\le|\\ge|\\neq|\\to|\\rightarrow|\\Rightarrow)/
// Espaces insécables : ponctuation double, unités, « = » et « / », milliers (« 50 000 »), flèche ; en anglais, après un
// mot d'une lettre (« A paediatrician »).
const MOIS = "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|January|February|March|April|May|June|July|August|September|October|November|December"
const insecables = (t) => {
  const x = t.replace(/« /g, `«${NBSP}`).replace(/ ([?!:;»])/g, `${NBSP}$1`)
    .replace(new RegExp(`(\\d) (${UNITES})(?![A-Za-zà-ÿ])`, "g"), `$1${NBSP}$2`)
    .replace(/ ([=\/×÷]) /g, `${NBSP}$1${NBSP}`)
    .replace(/(\d) (?=\d{3}(?!\d))/g, `$1${NBSP}`)
    .replace(/ →/g, `${NBSP}→`)
    // Dates : « 1er septembre 1939 », « après 1945 », « 2 June 1961 » ne se coupent pas ; « ce soir » non plus.
    .replace(new RegExp(`(\\d{1,2}(?:er)?) (${MOIS})`, "giu"), `$1${NBSP}$2`)
    .replace(new RegExp(`(${MOIS}) (\\d{4})`, "giu"), `$1${NBSP}$2`)
    .replace(/(\p{L}) ((?:1[0-9]|20)\d{2})(?!\d)/gu, `$1${NBSP}$2`)
    .replace(/\bce soir/g, `ce${NBSP}soir`)
    // Une étiquette de liste en ligne (« (a) walk away », « 3. no time lost ») reste avec ce qu'elle annonce.
    .replace(/(^|[\s(])(\([a-z0-9]\)|\d\.) /g, `$1$2${NBSP}`)
    // Une lettre seule qui désigne un point, un niveau, une espèce, suivie de sa valeur (« Q 500 kJ ») reste avec elle.
    .replace(/(^|[\s,;(])([A-Z]) (?=\d)/g, `$1$2${NBSP}`)
  return EN ? x.replace(/(^|[\s(])([AaI]) /g, `$1$2${NBSP}`) : x
}
// Un mot à trait d'union (« proposes-tu », « 2,4-diméthylhexane », « -oate ») ne se coupe pas à son trait d'union.
const sansCoupure = (html) => html.replace(/(^|[\s(«"“ \u0001\u0003])([\p{L}\d,'’]*-[\p{L}\d][\p{L}\d,'’-]*)/gu,
  (_, avant, mot) => `${avant}<span class="ns">${mot}</span>`)
const majuscule = (t) => t.charAt(0).toUpperCase() + t.slice(1)
const enLigne = (s) => {
  // Le gras peut entourer une formule (« **A few drops of $NaOH$** ») : on le repère avant de découper le texte.
  // L'italique (« *because* ») aussi ; « a*b » (une multiplication) ou « 2 * 3 » n'en sont pas.
  const morceaux = s.replace(/\*\*(.+?)\*\*/g, "\u0001$1\u0002")
    .replace(/(^|[^*\p{L}\d])\*([^*\s](?:[^*]*?[^*\s])?)\*(?![*\p{L}\d])/gu, "$1\u0003$2\u0004")
    .split(/(\$\$[\s\S]+?\$\$|\$[^$]+?\$|`[^`]+`)/)
  // Une formule en ligne et ce qui doit rester avec elle (le mot avant un « = », l'unité après : « $25$ cm ») forment un
  // bloc insécable : une espace insécable seule ne suffit pas, Chrome coupe quand même au bord d'une formule.
  const sortie = []
  let bloc = null, colle = false
  const vider = () => {
    if (bloc !== null) sortie.push(colle ? `<span class="ns">${bloc}</span>` : bloc)
    bloc = null
    colle = false
  }
  for (const m of morceaux) {
    if (m.startsWith("`")) { vider(); sortie.push(`<code>${echapper(m.slice(1, -1))}</code>`); continue }
    if (m.startsWith("$$")) { vider(); sortie.push(maths(m.slice(2, -2), true)); continue }
    if (m.startsWith("$")) {
      vider()
      bloc = maths(m.slice(1, -1), false)
      const avant = sortie.at(-1)
      if (RELATION.test(m.slice(1)) && typeof avant === "string" && avant.endsWith(" ")) {
        const j = avant.slice(0, -1).search(/[^\s>]+$/)
        if (j >= 0) {
          sortie[sortie.length - 1] = avant.slice(0, j)
          bloc = avant.slice(j, -1) + NBSP + bloc
          colle = true
        }
      } else if (typeof avant === "string" && /[\p{L}\d,)]$/u.test(avant)) {
        // Une formule collée à un mot, sans espace (« NADPH,H$^+$ », « H$_2$O ») ne s'en sépare pas.
        const j = avant.search(/[^\s>]+$/)
        if (j >= 0) {
          sortie[sortie.length - 1] = avant.slice(0, j)
          bloc = avant.slice(j) + bloc
          colle = true
        }
      }
      continue
    }
    let x = sansCoupure(insecables(echapper(m)))
    const u = bloc !== null && m.match(UNITE_APRES)
    if (u) {
      bloc += NBSP + u[1]
      colle = true
      x = x.slice(1 + u[1].length)
    }
    vider()
    sortie.push(x)
  }
  vider()
  return sortie.join("").replace(/\u0001/g, "<strong>").replace(/\u0002/g, "</strong>")
    .replace(/\u0003/g, "<em>").replace(/\u0004/g, "</em>")
}
function markdown(texte, { titres = false } = {}) {
  const sortie = []
  let liste = null, premiere = true, apresItem = false
  const fermer = () => { if (liste) sortie.push(`</${liste}>`); liste = null }
  // Un bloc $$ sur plusieurs lignes devient une seule ligne.
  for (const ligne of texte.replace(/\$\$\s*([\s\S]+?)\s*\$\$/g, (_, t) => `$$${t.replace(/\n/g, " ")}$$`).split("\n")) {
    const m = ligne.match(/^(\d+\.|-)\s+(.*)$/)
    if (m) {
      const type = m[1] === "-" ? "ul" : "ol"
      // Une liste numérotée coupée par un paragraphe reprend à son numéro (« 5. »), pas à 1.
      const debut = type === "ol" && parseInt(m[1], 10) > 1 ? ` start="${parseInt(m[1], 10)}"` : ""
      if (liste !== type) { fermer(); sortie.push(`<${type}${debut}>`); liste = type }
      sortie.push(`<li>${enLigne(m[2])}</li>`)
      premiere = false
      apresItem = true
      continue
    }
    if (!ligne.trim()) { fermer(); apresItem = false; continue }
    // Une ligne collée sous un élément de liste, sans ligne vide, en fait partie, comme sur le site : les formules
    // écrites sous « 2. Pick the equation: » restent dans l'étape 2.
    if (liste && apresItem) {
      sortie[sortie.length - 1] = sortie.at(-1).replace(/<\/li>$/, `<br>${enLigne(ligne.trim())}</li>`)
      continue
    }
    fermer()
    // Dans une définition, une ligne toute en gras devient un titre (« **La méthode** »). La première ligne aussi
    // quand elle commence par une étiquette en gras (« **Quand ?** … », « **À retenir** : … », « **L'idée** : … »).
    const t = titres && (ligne.match(/^\*\*([^*]+)\*\*\s*:?\s*$/) || (premiere && ligne.match(/^\*\*([^*]+)\*\*\s*[:,]?\s*(.+)$/)))
    premiere = false
    if (t) {
      const titre = T.titres[t[1].trim()] ?? t[1].trim()
      sortie.push(`<h2>${enLigne(titre)}</h2>`)
      if (t[2]) sortie.push(`<p>${enLigne(majuscule(t[2]))}</p>`)
    } else sortie.push(`<p>${enLigne(ligne)}</p>`)
  }
  fermer()
  return sortie.join("")
}
const listeFr = (a) => (a.length < 2 ? `${a[0] ?? ""}` : `${a.slice(0, -1).join(", ")} ${T.et} ${a.at(-1)}`)
const deLa = (nom) => (/^[aeiouyéèêàâîôûh]/i.test(nom) ? `d'${nom}` : `de ${nom}`)
// Une formule en texte simple, comme on l'écrit dans une légende Facebook (pas de LaTeX : il ne s'y affiche pas).
const EXPOSANTS = { 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹", "-": "⁻", "+": "⁺",
  A: "ᴬ", B: "ᴮ", D: "ᴰ", E: "ᴱ", G: "ᴳ", H: "ᴴ", I: "ᴵ", J: "ᴶ", K: "ᴷ", L: "ᴸ", M: "ᴹ", N: "ᴺ", O: "ᴼ", P: "ᴾ", R: "ᴿ",
  T: "ᵀ", U: "ᵁ", V: "ⱽ", W: "ᵂ", a: "ᵃ", b: "ᵇ", c: "ᶜ", d: "ᵈ", e: "ᵉ", f: "ᶠ", g: "ᵍ", h: "ʰ", i: "ⁱ", j: "ʲ", k: "ᵏ",
  l: "ˡ", m: "ᵐ", n: "ⁿ", o: "ᵒ", p: "ᵖ", r: "ʳ", s: "ˢ", t: "ᵗ", u: "ᵘ", v: "ᵛ", w: "ʷ", x: "ˣ", y: "ʸ", z: "ᶻ" }
const INDICES = { 0: "₀", 1: "₁", 2: "₂", 3: "₃", 4: "₄", 5: "₅", 6: "₆", 7: "₇", 8: "₈", 9: "₉", "+": "₊", "-": "₋",
  a: "ₐ", e: "ₑ", h: "ₕ", i: "ᵢ", j: "ⱼ", k: "ₖ", l: "ₗ", m: "ₘ", n: "ₙ", o: "ₒ", p: "ₚ", r: "ᵣ", s: "ₛ", t: "ₜ", u: "ᵤ",
  v: "ᵥ", x: "ₓ" }
const SYMBOLES = { times: "×", div: "÷", approx: "≈", le: "≤", leq: "≤", ge: "≥", geq: "≥", neq: "≠", pm: "±", infty: "∞",
  to: "→", rightarrow: "→", leftarrow: "←", longrightarrow: "⟶", Rightarrow: "⇒", Leftrightarrow: "⇔",
  rightleftharpoons: "⇌", mapsto: "↦", cdot: "·", cdots: "⋯", ldots: "…", dots: "…", circ: "°", degree: "°", prime: "′",
  in: "∈", cap: "∩", cup: "∪", sim: "∼", equiv: "≡", propto: "∝", parallel: "∥", perp: "⊥", angle: "∠", lt: "<", gt: ">",
  quad: " ", qquad: " ", mid: "|", vert: "|", ell: "ℓ", partial: "∂",
  alpha: "α", beta: "β", gamma: "γ", delta: "δ", epsilon: "ε", varepsilon: "ε", zeta: "ζ", eta: "η", theta: "θ",
  kappa: "κ", lambda: "λ", mu: "µ", nu: "ν", xi: "ξ", pi: "π", rho: "ρ", sigma: "σ", tau: "τ", phi: "φ", varphi: "φ",
  chi: "χ", psi: "ψ", omega: "ω", Gamma: "Γ", Delta: "Δ", Theta: "Θ", Lambda: "Λ", Sigma: "Σ", Phi: "Φ", Psi: "Ψ",
  Omega: "Ω",
  // Sans rendu en texte simple :
  mathbb: "", displaystyle: "", textstyle: "", limits: "", big: "", Big: "", bigl: "", bigr: "", Bigl: "", Bigr: "" }
const CLES_SYMBOLES = Object.keys(SYMBOLES).sort((a, b) => b.length - a.length)
// « \timesX » (une commande collée à une lettre) se lit comme « \times » suivi de « X ».
const commande = (nom) => {
  if (nom in SYMBOLES) return SYMBOLES[nom]
  const cle = CLES_SYMBOLES.find((k) => nom.startsWith(k))
  return cle ? SYMBOLES[cle] + nom.slice(cle.length) : nom
}
function texteBrut(t) {
  const petit = (table, marque) => (e) => ([...e].every((c) => c in table) ? [...e].map((c) => table[c]).join("") : `${marque}(${e})`)
  const exposant = petit(EXPOSANTS, "^"), indice = petit(INDICES, "_")
  // Un numérateur ou un dénominateur composé prend des parenthèses, sauf s'il en a déjà.
  const terme = (a) => (/^[\w,.²³]+$/.test(a) || /^\([^()]*\)[²³]?$/.test(a) ? a : `(${a})`)
  const formule = (f) => {
    let x = f.replace(/\\left(?![A-Za-z])|\\right(?![A-Za-z])/g, "").replace(/\{,\}/g, ",")
      .replace(/\\(?:overline|bar)\{([^{}]*)\}/g, (_, a) => [...a].map((c) => c + "̅").join(""))
      .replace(/\\vec\{([^{}]*)\}/g, "$1⃗")
      .replace(/\^\{([^{}]*)\}/g, (_, e) => exposant(e)).replace(/\^([0-9A-Za-z+-])/g, (_, e) => exposant(e))
      .replace(/_\{([^{}]*)\}/g, (_, e) => indice(e)).replace(/_([0-9A-Za-z])/g, (_, e) => indice(e))
      .replace(/\\[dt]?frac(\d)(\d)/g, "$1/$2")
    for (let i = 0; i < 5; i++)
      x = x.replace(/\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}/g, (_, a, b) => `${terme(a)}/${terme(b)}`)
        .replace(/\\[dt]?frac(\d)\{([^{}]*)\}/g, (_, a, b) => `${a}/${terme(b)}`)
        .replace(/\\sqrt\{([^{}]*)\}/g, "√($1)").replace(/\\(?:text|mathrm|operatorname|mathbf|textbf)\{([^{}]*)\}/g, "$1")
    return x.replace(/\\[,;:! ]|~/g, " ").replace(/\\%/g, "%").replace(/\\\|/g, "‖")
      .replace(/\\([A-Za-z]+)/g, (_, n) => commande(n)).replace(/[{}]/g, "").replace(/\s+/g, " ").trim()
  }
  return t.replace(/\$\$([\s\S]+?)\$\$/g, (_, f) => formule(f)).replace(/\$([^$]+)\$/g, (_, f) => formule(f))
    .replace(/\*\*/g, "").replace(/(^|[^*\p{L}\d])\*([^*\s](?:[^*]*?[^*\s])?)\*(?![*\p{L}\d])/gu, "$1$2")
    .replace(/\s*\n\s*/g, " ").trim()
}
const brut = texteBrut

// ---------------------------------------------------------------- les vues
const pages = []
// variante : une vue de rechange, photographiée seulement si la vue qu'elle remplace est trop chargée (photographier.py).
function page(nom, format, { sombre = false, corps, pied = "", variante = "" }) {
  const logo = url(`public/brand/logo-horizontal-minimal${sombre ? "-dark" : ""}.svg`)
  pages.push(`<section class="page ${format}${sombre ? " sombre" : ""}" data-nom="${nom}"${variante ? ` data-variante-de="${variante}"` : ""}>
<header><span class="bandeau">${BANDEAU}</span></header>
<main><div class="contenu">${corps}</div></main>
<footer><img src="${logo}" alt="EduKora"><span>${/\d \/ 5$/.test(pied) ? `edukora.africa · ${pied}` : pied || "edukora.africa"}</span></footer></section>`)
}
const BANDEAU = `<b>${T.fiches}</b> · ${echapper(S.bandeau)}`
const INVITATION = T.invitation(avecQuiz)
// sans_coupure s'écrit avec des espaces ordinaires : on le transforme comme le titre avant de le chercher.
// Un titre est traité comme le texte : insécables et mots à trait d'union (« est-elle ») d'un seul tenant.
const question = (f) =>
  (S.sans_coupure ?? []).reduce((t, bout) => {
    const cible = sansCoupure(insecables(echapper(bout)))
    if (!t.includes(cible)) return t
    return t.replace(cible, `<span class="ns">${cible}</span>`)
  }, sansCoupure(insecables(echapper(f.terme))))
for (const bout of S.sans_coupure ?? [])
  if (!fiches.some((f) => f.terme.includes(bout)))
    console.log(`sans_coupure : « ${bout} » ne figure dans aucun titre de la semaine`)
// Sur les images, « Probatoire D » ne se coupe pas en fin de ligne.
const EXAMEN = S.examen.replace(/ /g, " ")

function preuveDe(f) {
  const n = f.annees.length
  if (!n) throw new Error(`« ${f.terme} » n'a aucune session officielle : la carte ne peut rien annoncer`)
  if (n === 1) return T.preuve1(EXAMEN, f.annees[0])
  if (!S.preuve) return T.preuveN(n, EXAMEN, f.annees[0], f.annees.at(-1))
  return S.preuve.replace(S.examen, EXAMEN).replace("{n}", n).replace("{debut}", f.annees[0]).replace("{fin}", f.annees.at(-1))
}

// Les vidéos TikTok (9:16, une par fiche) : des scènes qui s'enchaînent, filmées par filmer.py. La durée d'une scène suit
// la longueur de son texte, pour qu'on ait le temps de le lire sans pause.
const videos = []
const lecture = (texte, min, max) => Math.min(max, Math.max(min, 1.6 + texteBrut(texte).length / 16))
const COMPTE = 5
const finVideo = (i) => ({ id: "fin", sombre: true, duree: 3.5, html:
  `<img class="logo-fin" src="${url("public/brand/logo-horizontal-minimal-dark.svg")}" alt="EduKora">` +
  `<h1>${T.finTitre}</h1><p class="detail">${T.finDetail}</p>` +
  `<p class="appel">${i < 4 ? T.finDemain(i + 2) : T.finSuite}</p>` })

if (S.format === "methode") {
  const aRetenir = (f) => T.aRetenir.test(f.definition)
  const typeFiche = (f, i) => `${aRetenir(f) ? T.ficheRetenir : T.ficheMethode} ${T.numero} ${i + 1}`
  const blocExemple = (f) => {
    const [titre, ...reste] = f.exemple.split("\n")
    const m = titre.match(/^\*\*(.+?)\*\*\s*[:,]?\s*(.*)$/)
    if (!m) return { titre: T.exemple, corps: f.exemple, origine: "" }
    // « **Example** (GCE 2015, Paper 2): … » : l'origine va sous le titre, comme celle de l'exercice.
    const o = m[2].match(/^\(([^)]+)\)\s*:?\s*([\s\S]*)$/)
    return o ? { titre: m[1], origine: `<p class="origine">${enLigne(majuscule(o[1]))}</p>`, corps: [majuscule(o[2]), ...reste].join("\n") }
      : { titre: m[1], origine: "", corps: [majuscule(m[2]), ...reste].join("\n") }
  }
  const sujetDe = (f) => {
    const m = f.exercice.match(/^\((.+?)\)\s*([\s\S]*)$/)
    return m ? { origine: `<p class="origine">${enLigne(majuscule(m[1]))}</p>`, enonce: m[2] } : { origine: "", enonce: f.exercice }
  }
  for (const f of fiches) for (const c of ["exemple", "piege", "exercice", "reponse"])
    if (!f[c]) throw new Error(`« ${f.terme} » n'a pas de champ ${c} : le format methode en a besoin (format definition ?)`)

  fiches.forEach((f, i) => {
    const p = `4x5/j${i + 1}-${f.cle}`
    const ex = blocExemple(f), at = sujetDe(f), suite = (n) => `${n} / 5`
    page(`${p}-1-question`, "post", { sombre: true, pied: aRetenir(f) ? T.toucheFiche : T.toucheMethode,
      corps: `<p class="surtitre">${typeFiche(f, i)}</p><h1>${question(f)}</h1><p class="preuve">${preuveDe(f)}</p>` })
    page(`${p}-2-methode`, "post", { pied: suite(2), corps: markdown(f.definition, { titres: true }) })
    page(`${p}-3-exemple`, "post", { pied: suite(3), corps: `<h2>${enLigne(ex.titre)}</h2>${ex.origine}${markdown(ex.corps)}` })
    page(`${p}-4-piege`, "post", { pied: suite(4), corps: `<div class="piege"><h2>${T.piege}</h2>${markdown(f.piege)}</div>` })
    page(`${p}-5-a-toi`, "post", { pied: suite(5),
      corps: `<h2>${T.aToi}</h2>${at.origine}${markdown(at.enonce)}<p class="appel">${T.appelPost}</p>` })
    page(`${p}-6-reponse-soir`, "post", {
      corps: `<p class="surtitre">${T.reponse}</p>${markdown(at.enonce)}<div class="reponse">${markdown(f.reponse)}</div>${INVITATION}` })

    const s = `9x16/j${i + 1}-${f.cle}`
    page(`${s}-1-a-toi`, "statut", {
      corps: `<p class="surtitre">${T.aToi}</p><h2>${question(f)}</h2>${at.origine}${markdown(at.enonce)}<p class="appel">${T.appelStatut}</p>` })
    page(`${s}-2-piege`, "statut", { corps: `<h2>${question(f)}</h2><div class="piege"><h2>${T.piege}</h2>${markdown(f.piege)}</div>` })
    page(`${s}-3-reponse-soir`, "statut", {
      corps: `<p class="surtitre">${T.reponse}</p>${markdown(at.enonce)}<div class="reponse">${markdown(f.reponse)}</div>${INVITATION}` })

    videos.push({ nom: `j${i + 1}-${f.cle}`, scenes: [
      { id: "question", sombre: true, duree: lecture(f.terme, 3.5, 6),
        html: `<p class="surtitre">${typeFiche(f, i)}</p><h1>${question(f)}</h1><p class="preuve">${preuveDe(f)}</p>` },
      // La méthode (ou « À retenir ») avant le piège et l'exercice : sans elle, la vidéo interroge sans rien apprendre,
      // et la réponse applique une formule jamais montrée. Même contenu que l'image 2 de la fiche.
      { id: "methode", duree: lecture(f.definition, 6, 14), html: markdown(f.definition, { titres: true }) },
      { id: "piege", duree: lecture(f.piege, 4, 9),
        html: `<p class="rappel">${question(f)}</p><div class="piege"><h2>${T.piege}</h2>${markdown(f.piege)}</div>` },
      { id: "a-toi", duree: lecture(at.enonce, 3, 8) + COMPTE, compte: COMPTE,
        html: `<h2>${T.aToi}</h2>${at.origine}${markdown(at.enonce)}<div class="compte"></div><p class="appel">${T.videoAppel}</p>` },
      { id: "reponse", duree: lecture(f.reponse, 3.5, 8),
        html: `<p class="surtitre">${T.reponse}</p><div class="reponse">${markdown(f.reponse)}</div>` },
      finVideo(i),
    ] })
  })

  // Samedi : les 5 pièges (couverture + les pièges titrés).
  page("4x5/j6-pieges-0-couverture", "post", { sombre: true, pied: T.touchePieges,
    corps: `<p class="surtitre">${T.semaineEn(echapper(S.matiere_nom))}</p><h1>${T.pieges(EXAMEN)}</h1><p class="preuve">${T.lequel}</p>` })
  fiches.forEach((f, i) => page(`4x5/j6-pieges-${i + 1}-${f.cle}`, "post", { pied: T.piegeN(i + 1),
    corps: `<h2>${question(f)}</h2><div class="piege">${markdown(f.piege)}</div>${i === fiches.length - 1 ? INVITATION : ""}` }))

  // Dimanche : les 5 exercices sans la méthode, puis les 5 réponses. Un intitulé court situe chaque question.
  const liste = (champ, de = 0, a = 5) => `<ol class="defi"${de ? ` start="${de + 1}"` : ""}>${fiches.slice(de, a).map((f) =>
    `<li>${f.court ? `<p class="origine">${echapper(f.court)}</p>` : ""}${markdown(champ === "exercice" ? sujetDe(f).enonce : f.reponse)}</li>`).join("")}</ol>`
  // Une page du défi trop chargée (réponses longues, comme au GCE) est remplacée par deux : fiches 1 à 3, puis 4 et 5.
  const suite = EN ? " (continued)" : " (suite)"
  for (const [format, sous] of [["post", "4x5"], ["statut", "9x16"]]) {
    for (const [nom, titre, champ, fin] of [["j7-defi-1-questions", T.defi(S.defi ?? T.defiMot), "exercice", ""],
      ["j7-defi-2-reponses-soir", T.defiReponses, "reponse", INVITATION]]) {
      page(`${sous}/${nom}`, format, { corps: `<h2>${titre}</h2>${liste(champ)}${fin}` })
      page(`${sous}/${nom}-a`, format, { variante: `${sous}/${nom}`, corps: `<h2>${titre}</h2>${liste(champ, 0, 3)}` })
      page(`${sous}/${nom}-b`, format, { variante: `${sous}/${nom}`, corps: `<h2>${titre}${suite}</h2>${liste(champ, 3, 5)}${fin}` })
    }
  }
} else {
  // Définitions seules : le mot le matin, la fiche le soir ; samedi retrouver le mot ; dimanche le récapitulatif.
  const auExamen = (f) => (f.annees.length <= 3
    ? T.auExamen(EXAMEN, listeFr(f.annees))
    : T.auExamenN(EXAMEN, f.annees.length, f.annees[0], f.annees.at(-1)))
  const definition = (f) => `<h2>${question(f)}</h2><div class="reponse">${markdown(f.definition)}</div>`
  // L'indice du samedi ne doit contenir aucun mot du terme à trouver, même au singulier ou accordé : on cherche le début
  // de chaque mot de 4 lettres ou plus (« droit » pour « Droits de l'homme ») au début d'un mot de l'indice.
  const racines = (terme) => terme.toLowerCase().split(/[\s'’-]+/).filter((m) => m.length >= 4)
    .map((m) => (m.length > 5 ? m.slice(0, m.length - 2) : m))
  const indice = (f) => {
    const d = S.indices?.[f.cle] ?? f.definition
    const trouve = racines(f.terme).find((r) => new RegExp(`(^|[^a-zà-ÿœ])${r}`, "i").test(d))
    if (trouve)
      throw new Error(`l'indice de « ${f.terme} » contient un mot qui commence par « ${trouve} » : écrire "indices": {"${f.cle}": "…"} dans semaine.json`)
    return d
  }
  fiches.forEach((f, i) => {
    for (const [format, sous] of [["post", "4x5"], ["statut", "9x16"]]) {
      const p = `${sous}/j${i + 1}-${f.cle}`
      page(`${p}-1-question`, format, { sombre: true,
        corps: `<p class="surtitre">${T.fiche} ${T.numero} ${i + 1} · ${T.saisDefinir}</p><h1>${question(f)}</h1><p class="preuve">${auExamen(f)}</p>` +
          `<p class="appel">${format === "post" ? T.appelDefPost : T.appelDefStatut} ${T.ficheCeSoir}</p>` })
      page(`${p}-2-reponse-soir`, format, { corps: `<p class="surtitre">${T.laDefinition}</p>${definition(f)}${INVITATION}` })
    }
    videos.push({ nom: `j${i + 1}-${f.cle}`, scenes: [
      { id: "question", sombre: true, duree: lecture(f.terme, 3.5, 5),
        html: `<p class="surtitre">${T.fiche} ${T.numero} ${i + 1} · ${T.saisDefinir}</p><h1>${question(f)}</h1><p class="preuve">${auExamen(f)}</p>` },
      { id: "a-toi", duree: 1.5 + COMPTE, compte: COMPTE,
        html: `<h2>${question(f)}</h2><p>${T.videoDef}</p><div class="compte"></div>` },
      { id: "definition", duree: lecture(f.definition, 4, 13), html: `<p class="surtitre">${T.laDefinition}</p>${definition(f)}` },
      finVideo(i),
    ] })
  })
  const ordre = (S.ordre_devine ?? [3, 0, 4, 2, 1].map((k) => fiches[k].cle)).map((c) => {
    const f = fiches.find((x) => x.cle === c)
    if (!f) throw new Error(`ordre_devine : clé inconnue « ${c} »`)
    return f
  })
  const liste = (ligne) => `<ol class="defi">${ordre.map((f) => `<li>${ligne(f)}</li>`).join("")}</ol>`
  for (const [format, sous] of [["post", "4x5"], ["statut", "9x16"]]) {
    page(`${sous}/j6-devine-1-questions`, format, { corps: `<h2>${T.devineQ}</h2>${liste((f) => enLigne(indice(f)))}` })
    page(`${sous}/j6-devine-2-reponses-soir`, format, { corps: `<h2>${T.devineR}</h2>${liste((f) => `<b>${question(f)}</b>`)}${INVITATION}` })
  }
  page("4x5/j7-recap-0-couverture", "post", { sombre: true, pied: T.toucheDefinitions,
    corps: `<p class="surtitre">${T.semaineEn(echapper(S.matiere_nom))}</p><h1>${T.recapTitre}</h1><p class="preuve">${T.recapPreuve}</p>` })
  fiches.forEach((f, i) => page(`4x5/j7-recap-${i + 1}-${f.cle}`, "post", { pied: `${i + 1} / 5`,
    corps: definition(f) + (i === fiches.length - 1 ? INVITATION : "") }))
}

const css = `
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Work Sans",sans-serif;background:#888}
.page{width:1080px;display:flex;flex-direction:column;overflow:hidden;background:hsl(40 30% 98%);color:hsl(150 15% 10%);margin-bottom:20px}
.post{height:1350px;padding:72px 80px 56px}
.statut{height:1920px;padding:230px 80px 240px}
.sombre{background:hsl(158 83% 13%);color:hsl(40 30% 98%)}
.bandeau{display:inline-block;font-weight:600;font-size:30px;padding:12px 28px;border-radius:99px;background:hsl(158 45% 92%);color:hsl(158 83% 16%)}
main{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;padding:28px 0}
.contenu{font-size:44px;line-height:1.45}
.contenu>*+*{margin-top:.6em}
h1{font-family:Fraunces,serif;font-size:2em;line-height:1.15;font-weight:600}
h2{font-family:Fraunces,serif;font-size:1.25em;line-height:1.22;font-weight:600;color:hsl(158 83% 22%)}
p+p{margin-top:.35em}
ol,ul{padding-left:1.3em}li{margin-top:.35em}
.surtitre{text-transform:uppercase;letter-spacing:.09em;font-size:.75em;font-weight:600;opacity:.75}
.preuve{font-size:1.02em;border-top:3px solid hsl(38 92% 55%);padding-top:.8em;margin-top:1.4em}
.preuve b{color:hsl(38 95% 62%)}
.piege{background:hsl(38 95% 92%);border-left:12px solid hsl(30 90% 48%);border-radius:18px;padding:.9em 1em;font-size:1.12em}
.piege h2{color:hsl(24 85% 33%);margin-bottom:.4em}
.reponse{background:hsl(158 45% 92%);border-radius:18px;padding:.9em 1em;font-size:1.12em}
.invitation{border:3px solid hsl(158 83% 22%);border-radius:18px;padding:.7em .9em;font-size:.82em;margin-top:1.4em!important}
.invitation b{color:hsl(158 83% 22%)}.invitation .detail{font-size:.82em;opacity:.75}
code{font-family:Consolas,monospace;font-size:.95em;background:hsl(150 12% 91%);border-radius:8px;padding:.05em .3em}
.sombre .appel{color:hsl(38 95% 62%)}
.origine{font-size:.78em;opacity:.7}
.appel{font-weight:600;color:hsl(158 83% 22%);margin-top:1.4em!important}
.defi li{margin-top:.7em;font-size:.95em}
.katex{font-size:1.08em;white-space:nowrap}.katex-display{margin:.35em 0}
.ns{white-space:nowrap}.formule-longue .katex{white-space:normal}
.contenu p:has(.mfrac) .katex .base,.contenu li:has(.mfrac) .katex .base{margin:.14em 0}
.contenu p:has(.mfrac)+p,.contenu p+p:has(.mfrac){margin-top:.6em}
footer{display:flex;justify-content:space-between;align-items:center;font-size:28px;font-weight:500}
footer img{height:58px}
`
const feuilles = [
  "node_modules/katex/dist/katex.min.css",
  "node_modules/@fontsource/work-sans/400.css", "node_modules/@fontsource/work-sans/500.css",
  "node_modules/@fontsource/work-sans/600.css", "node_modules/@fontsource/fraunces/600.css",
].map((p) => `<link rel="stylesheet" href="${url(p)}">`).join("")
writeFileSync(resolve(sources, "pages.html"),
  `<!doctype html><html lang="${T.lang}"><meta charset="utf-8">${feuilles}<style>${css}</style><body>${pages.join("\n")}</body></html>`)

// ---------------------------------------------------------------- la page des vidéos TikTok (filmée par filmer.py)
// Écran 1080 × 1920. TikTok couvre le haut (onglets), la droite (boutons) et le bas (légende, son) : le texte reste dans
// une zone de 72 à 930 px en largeur et de 300 à 1500 px en hauteur.
const cssVideo = `
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Work Sans",sans-serif;width:1080px;height:1920px;overflow:hidden;background:hsl(40 30% 98%)}
.scene{position:absolute;inset:0;background:hsl(40 30% 98%);color:hsl(150 15% 10%);opacity:0}
.scene.sombre{background:hsl(158 83% 13%);color:hsl(40 30% 98%)}
.scene header{position:absolute;top:200px;left:72px}
.bandeau{display:inline-block;font-weight:600;font-size:32px;padding:12px 28px;border-radius:99px;background:hsl(158 45% 92%);color:hsl(158 83% 16%)}
.zone{position:absolute;top:300px;left:72px;right:150px;bottom:530px;display:flex;flex-direction:column;justify-content:center}
.scene footer{position:absolute;left:72px;right:150px;bottom:430px;display:flex;align-items:center;justify-content:space-between;
  font-size:36px;font-weight:600;border-top:3px solid hsl(158 45% 85%);padding-top:22px}
.scene.sombre footer{border-top-color:hsl(158 50% 30%)}
.scene footer img{height:62px}
.contenu{font-size:50px;line-height:1.42}
.contenu>*+*{margin-top:.55em}
h1{font-family:Fraunces,serif;font-size:1.9em;line-height:1.13;font-weight:600}
h2{font-family:Fraunces,serif;font-size:1.3em;line-height:1.2;font-weight:600;color:hsl(158 83% 22%)}
.sombre h2{color:hsl(38 95% 62%)}
p+p{margin-top:.35em}
ol,ul{padding-left:1.3em}li{margin-top:.3em}
.surtitre{text-transform:uppercase;letter-spacing:.09em;font-size:.72em;font-weight:600;opacity:.75}
.rappel{font-size:.75em;font-weight:600;opacity:.7}
.preuve{font-size:1em;border-top:3px solid hsl(38 92% 55%);padding-top:.8em;margin-top:1.3em!important}
.preuve b{color:hsl(38 95% 62%)}
.piege{background:hsl(38 95% 92%);color:hsl(150 15% 10%);border-left:14px solid hsl(30 90% 48%);border-radius:20px;padding:.9em 1em;font-size:1.08em}
.piege h2{color:hsl(24 85% 33%);margin-bottom:.35em}
.reponse{background:hsl(158 45% 92%);color:hsl(150 15% 10%);border-radius:20px;padding:.9em 1em;font-size:1.08em}
.reponse h2{color:hsl(158 83% 22%)}
.origine{font-size:.75em;opacity:.7}
.appel{font-weight:600;color:hsl(158 83% 22%);margin-top:1em!important}
.sombre .appel{color:hsl(38 95% 62%)}
.detail{font-size:.8em;opacity:.8}
.logo-fin{height:110px;margin-bottom:.6em}
.compte{width:220px;height:220px;border-radius:50%;border:14px solid hsl(38 92% 55%);display:flex;align-items:center;justify-content:center;
  font-family:Fraunces,serif;font-size:130px;font-weight:600;color:hsl(24 85% 33%);margin:.5em auto 0!important}
code{font-family:Consolas,monospace;font-size:.95em;background:hsl(150 12% 91%);border-radius:8px;padding:.05em .3em}
.katex{font-size:1.06em;white-space:nowrap}.katex-display{margin:.3em 0}
.ns{white-space:nowrap}.formule-longue .katex{white-space:normal}
.contenu p:has(.mfrac) .katex .base,.contenu li:has(.mfrac) .katex .base{margin:.14em 0}
.contenu p:has(.mfrac)+p,.contenu p+p:has(.mfrac){margin-top:.6em}
`
// render(t) dessine l'instant t et renvoie une clé : tant qu'elle ne change pas, filmer.py réutilise l'image précédente.
const jsVideo = `
const D = window.DATA
let V = null, debuts = []
const lisse = (x) => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x)
window.choisir = async (i) => {
  V = D.videos[i]
  document.body.innerHTML = V.scenes.map((s) =>
    '<section class="scene' + (s.sombre ? ' sombre' : '') + '"><header><span class="bandeau">' + D.bandeau + '</span></header>' +
    '<div class="zone"><div class="contenu">' + s.html + '</div></div>' +
    // Le nom de domaine sur chaque scène (sauf la dernière, qui l'affiche en grand), avec le logo, au-dessus de la
    // zone que TikTok recouvre en bas (légende, son).
    (s.id === "fin" ? "" : '<footer><img src="' + (s.sombre ? D.logoSombre : D.logo) + '" alt="EduKora"><span>edukora.africa</span></footer>') +
    '</section>').join("")
  // On ne mesure qu'une fois les polices (Fraunces, Work Sans, KaTeX) et le logo chargés.
  document.querySelectorAll(".scene").forEach((e) => { e.style.opacity = 1 })
  await document.fonts.ready
  await Promise.all([...document.images].map((im) => im.decode().catch(() => {})))
  // Le texte d'une scène rétrécit jusqu'à tenir dans la zone (de 50 à 30 px).
  const scenes = [...document.querySelectorAll(".scene")]
  scenes.forEach((el) => {
    el.style.opacity = 1
    const zone = el.querySelector(".zone"), c = el.querySelector(".contenu")
    // Déborde : trop haut, ou un bout de texte (formule, ponctuation qui la suit) qui dépasse la zone ou son encadré.
    // Le texte visible seulement : la copie MathML des formules (pour les lecteurs d'écran) est hors champ.
    const depasse = (boite, limite) => {
      const w = document.createTreeWalker(boite, NodeFilter.SHOW_TEXT), r = document.createRange()
      for (let n = w.nextNode(); n; n = w.nextNode()) {
        if (!n.textContent.trim() || n.parentElement.closest(".katex-mathml")) continue
        r.selectNodeContents(n)
        for (const x of r.getClientRects()) if (x.width > 0 && x.right > limite + 2) return true
      }
      return false
    }
    const interieur = (b) => b.getBoundingClientRect().right - parseFloat(getComputedStyle(b).paddingRight)
    const deborde = () => c.scrollHeight > zone.clientHeight || depasse(c, zone.getBoundingClientRect().right) ||
      [...c.querySelectorAll(".reponse, .piege")].some((b) => depasse(b, interieur(b)))
    let t = 50
    // Un texte court grandit (jusqu'à 64 px), un texte long rétrécit (jusqu'à 30 px).
    while (t < 64 && !deborde() && c.scrollHeight < zone.clientHeight * 0.6) c.style.fontSize = (++t) + "px"
    while (t > 30 && deborde()) c.style.fontSize = (--t) + "px"
    el.dataset.taille = t
    el.dataset.deborde = deborde() ? "1" : ""
    el.style.opacity = 0
  })
  debuts = []
  let t = 0
  for (const s of V.scenes) { debuts.push(t); t += s.duree }
  V.total = t
  return { total: t, tailles: scenes.map((e, k) => ({ scene: V.scenes[k].id, taille: +e.dataset.taille, deborde: !!e.dataset.deborde })) }
}
window.render = (t) => {
  const scenes = document.querySelectorAll(".scene")
  const cle = []
  V.scenes.forEach((s, k) => {
    const el = scenes[k], l = t - debuts[k]
    // Entrée en 0,4 s, sortie en fondu sur 0,35 s (sauf la dernière scène).
    const entree = lisse(l / 0.4), sortie = k === V.scenes.length - 1 ? 1 : 1 - lisse((l - (s.duree - 0.35)) / 0.35)
    const op = l < 0 || l > s.duree ? 0 : Math.min(entree, sortie)
    el.style.opacity = op
    if (op <= 0) return
    // Les lignes du contenu arrivent l'une après l'autre.
    const enfants = [...el.querySelector(".contenu").children]
    const etats = enfants.map((e, j) => {
      const p = lisse((l - 0.15 - j * 0.28) / 0.35)
      e.style.opacity = p
      e.style.transform = "translateY(" + ((1 - p) * 36).toFixed(1) + "px)"
      return p.toFixed(2)
    })
    let n = ""
    if (s.compte) {
      const debutCompte = s.duree - s.compte - 0.35
      n = Math.max(1, Math.min(s.compte, Math.ceil(s.compte - (l - debutCompte))))
      el.querySelector(".compte").textContent = n
    }
    cle.push(k, op.toFixed(2), etats.join(","), n)
  })
  return cle.join("|")
}
window.pret = document.fonts.ready.then(() => true)
`
writeFileSync(resolve(sources, "videos.html"),
  `<!doctype html><html lang="${T.lang}"><meta charset="utf-8">${feuilles}<style>${cssVideo}</style>` +
  `<script>window.DATA = ${JSON.stringify({ bandeau: BANDEAU, videos, logo: url("public/brand/logo-horizontal-minimal.svg"),
    logoSombre: url("public/brand/logo-horizontal-minimal-dark.svg") }).replace(/</g, "\\u003c")}</script>` +
  `<script>${jsVideo}</script><body></body></html>`)

// ---------------------------------------------------------------- brouillon des légendes (jamais écrasé)
// Les lignes publiées des légendes suivent la langue de la semaine ; les titres de travail (« Jour 1 », « Publication »,
// « Le soir ») restent en français pour l'utilisateur, et les passages ⟦…⟧ disent quoi écrire.
const LIEN = EN
  ? `${SITE}/en/edukora-sheets?cursus=${S.lien_cursus ?? S.cursus[0]}&matiere=${S.matiere}`
  : `${SITE}/fiches-edukora?cursus=${S.lien_cursus ?? S.cursus[0]}&matiere=${S.matiere}`
const SITE_LANGUE = EN ? `${SITE}/en` : SITE
const C = EN ? {
  fin: ["#Cameroon", "#Revision", "#EduKora", "#EduKoraSheets"], tiktok: "#LearnOnTikTok",
  entete: (n) => `📘 EduKora sheets, ${S.bandeau}${n ? `: sheet no. ${n}` : ""}`,
  entrainer: `Practise more: ${SITE_LANGUE}`,
  quiz: avecQuiz ? `Keep going with a quiz, no account needed: ${SITE_LANGUE}`
    : `Want more practice? A free quiz in another subject, no account needed: ${SITE_LANGUE}`,
  autres: `More EduKora sheets for ${S.examen} ${S.matiere_nom} (some free, the rest with a subscription): ${LIEN}`,
  sessions: (f) => (f.annees.length <= 3 ? `in the ${S.examen} in ${listeFr(f.annees)}`
    : `in ${f.annees.length} sessions of the ${S.examen}, from ${f.annees[0]} to ${f.annees.at(-1)}`),
  statut: "Reply to this status, answer tonight.", soir: "The answer: ",
  theme: "#Topic", pieges: "#Traps", defi: "#Challenge", definitions: "#Definitions", recapTag: "#Recap",
  j6: ["The 5 traps of the week. Which one have you fallen into? Reply with its number.",
    `Send this post to a friend preparing for the ${S.examen}.`],
  j7: (mot) => `Sunday challenge: 5 ${mot}, without looking at the sheets. Note your score out of 5 when you see the answers tonight.`,
  j7soir: "The answers to the challenge. How many out of 5? The sheet you missed is the one to review this week.",
  defQuestion: (f) => `Can you define "${f.terme}"? Asked ${C.sessions(f)}.`,
  defAppel: "Write your definition in the comments. The sheet comes tonight.",
  defStatut: (f) => `Define "${f.terme}" in your own words. Reply to this status, the sheet tonight.`,
  defCompare: "Compare with your answer: what did you miss?",
  devine: "5 definitions from this week, without the words. How many can you find? Reply 1 to 5 in the comments.",
  devineSoir: (liste) => `The answers: ${liste}. How many out of 5?`,
  recap: `This week's 5 definitions together. Save this post for your revision and send it to a friend preparing for the ${S.examen}.`,
  tiktokMethode: "Answer in the comments before the reveal. The full sheet on edukora.africa.",
  tiktokDef: "Say it in your own words in the comments, before the answer. The full sheet on edukora.africa.",
  langue: " (en anglais)",
} : {
  fin: ["#Cameroun", "#Révisions", "#EduKora", "#FichesEduKora"], tiktok: "#ApprendreSurTikTok",
  entete: (n) => `📘 Fiches EduKora, ${S.bandeau}${n ? ` : fiche n° ${n}` : ""}`,
  entrainer: "Pour t'entraîner davantage : https://edukora.africa",
  quiz: avecQuiz ? "Continue avec un quiz, sans compte : https://edukora.africa"
    : "Envie de t'entraîner encore ? Un quiz gratuit dans une autre matière, sans compte : https://edukora.africa",
  autres: `D'autres Fiches EduKora ${deLa(S.matiere_nom)} ${S.examen} (certaines gratuites, les autres avec l'abonnement) : ${LIEN}`,
  // La légende annonce les mêmes sessions que l'image.
  sessions: (f) => (f.annees.length <= 3 ? `au ${S.examen} en ${listeFr(f.annees)}`
    : `à ${f.annees.length} sessions du ${S.examen}, de ${f.annees[0]} à ${f.annees.at(-1)}`),
  statut: "Réponds à ce statut, correction ce soir.", soir: "La réponse : ",
  theme: "#Thème", pieges: "#Pièges", defi: "#Défi", definitions: "#Définitions", recapTag: "#Récap",
  j6: ["Les 5 pièges de la semaine. Lequel as-tu déjà fait ? Réponds avec son numéro.",
    `Envoie ce post à un camarade qui prépare le ${S.examen}.`],
  j7: (mot) => `Le défi du dimanche : 5 ${mot}, sans regarder les fiches. Note ton score sur 5 quand tu auras vu les réponses, ce soir.`,
  j7soir: "Les réponses du défi. Combien sur 5 ? La fiche que tu as ratée est celle à revoir cette semaine.",
  defQuestion: (f) => `Sais-tu définir « ${f.terme} » ? Notion demandée ${C.sessions(f)}.`,
  defAppel: "Écris ta définition en commentaire. La fiche arrive ce soir.",
  defStatut: (f) => `Définis « ${f.terme} » avec tes mots. Réponds à ce statut, la fiche ce soir.`,
  defCompare: "Compare avec ta réponse : qu'avais-tu oublié ?",
  devine: "5 définitions de la semaine, sans les mots. Lesquels retrouves-tu ? Réponds de 1 à 5 en commentaire.",
  devineSoir: (liste) => `Les réponses : ${liste}. Combien sur 5 ?`,
  recap: `Les 5 définitions de la semaine réunies. Enregistre cette publication pour tes révisions et envoie-la à un camarade qui prépare le ${S.examen}.`,
  tiktokMethode: "Réponds en commentaire avant la correction. La fiche complète sur edukora.africa.",
  tiktokDef: "Dis-le avec tes mots en commentaire, avant la réponse. La fiche complète sur edukora.africa.",
  langue: "",
}
const DIESES = (...propres) => [...S.hashtags, ...propres, ...C.fin].join(" ")
const sansBalises = (t) => t.replace(/<[^>]+>/g, "")

const legendes = resolve(dossier, "legendes.md")
if (!existsSync(legendes)) {
  const L = [`# Légendes de la semaine ${S.matiere_nom} ${S.examen}`, "",
    "Chaque jour a une légende du matin, une version courte pour le statut WhatsApp et un texte du soir.",
    `Les passages entre crochets doubles sont à écrire${C.langue} ; le reste est calculé depuis les fiches en ligne.`, ""]
  if (S.format === "methode") {
    for (const f of fiches) L.push(
      `## Jour ${f.rang} : ${f.court ?? f.terme}`, "", "**Publication**",
      C.entete(f.rang),
      `⟦Accroche${C.langue} : la difficulté de « ${f.terme} » en une phrase, posée à l'élève.⟧`,
      `⟦Ce que montrent les images, et ce qu'on attend en commentaire${C.langue}. Finir par « ${EN ? "answer tonight" : "correction ce soir"} ».⟧`,
      `${sansBalises(preuveDe(f))}.`,
      C.entrainer,
      DIESES(`⟦${C.theme}⟧`), "",
      `**Statut WhatsApp** : ⟦La question de l'exercice en une ligne${C.langue}.⟧ ${C.statut}`, "",
      `**Le soir** : ${C.soir}⟦la réponse (fiche : « ${brut(f.reponse)} »), puis le pourquoi en une phrase${C.langue}.⟧`,
      C.quiz, C.autres, "")
    L.push("## Jour 6 : les 5 pièges", "", "**Publication**", C.entete(), ...C.j6, C.entrainer, DIESES(C.pieges), "",
      "## Jour 7 : le défi", "", "**Publication**", C.entete(), C.j7(S.defi ?? T.defiMot), C.entrainer, DIESES(C.defi), "",
      `**Le soir** : ${C.j7soir}`, C.quiz, C.autres, "")
  } else {
    const ordre = (S.ordre_devine ?? [3, 0, 4, 2, 1].map((k) => fiches[k].cle)).map((c) => fiches.find((x) => x.cle === c))
    L.splice(4, 0, "Le soir, la définition est reprise ici telle qu'elle est sur l'image.")
    for (const f of fiches) L.push(
      `## Jour ${f.rang} : ${f.terme}`, "", "**Publication**",
      C.entete(f.rang), C.defQuestion(f),
      `⟦Une question qui oriente l'élève sans donner la réponse${C.langue}.⟧`,
      C.defAppel, C.entrainer, DIESES(C.definitions), "",
      `**Statut WhatsApp** : ${C.defStatut(f)}`, "",
      `**Le soir** : ${f.terme}. ${brut(f.definition)}`, C.defCompare, C.quiz, C.autres, "")
    L.push("## Jour 6 : quel est le mot ?", "", "**Publication**", C.entete(), C.devine, C.entrainer, DIESES(C.defi), "",
      `**Le soir** : ${C.devineSoir(ordre.map((f, i) => `${i + 1}. ${f.terme}`).join(", "))}`, C.quiz, C.autres, "",
      "## Jour 7 : les 5 définitions à garder", "", "**Publication**", C.entete(), C.recap, C.entrainer, DIESES(C.recapTag), "")
  }
  writeFileSync(legendes, L.join("\n"))
  console.log("legendes.md : brouillon écrit, passages ⟦…⟧ à compléter")
} else console.log("legendes.md existe déjà : non touché")

// ---------------------------------------------------------------- légendes TikTok, tirées des légendes du matin
// TikTok : une vidéo par jour, du lundi au vendredi. L'accroche et les hashtags du jour viennent de legendes.md, une fois
// celui-ci écrit ; un lien n'est pas cliquable dans une légende TikTok, edukora.africa s'écrit en clair.
const legendesTiktok = resolve(dossier, "legendes-tiktok.md")
if (!existsSync(legendesTiktok)) {
  const texte = existsSync(legendes) ? readFileSync(legendes, "utf8") : ""
  if (!texte || texte.includes("⟦")) console.log("legendes-tiktok.md : à tirer de legendes.md une fois celui-ci écrit (relancer construire.mjs)")
  else {
    const jours = Object.fromEntries([...texte.matchAll(/^## Jour (\d) [^\n]*\n([\s\S]*?)(?=^## |$(?![\s\S]))/gm)].map((m) => [+m[1], m[2]]))
    const TT = [`# Légendes TikTok de la semaine ${S.matiere_nom} ${S.examen}`, "",
      "Une vidéo par jour, du lundi au vendredi (`videos/`). Choisir le son dans TikTok au moment de publier.",
      "Les liens ne sont pas cliquables dans une légende TikTok : edukora.africa s'écrit en clair.", ""]
    for (const f of fiches) {
      const bloc = jours[f.rang] ?? ""
      const lignes_ = bloc.split("\n")
      const iEntete = lignes_.findIndex((l) => l.startsWith("📘"))
      const accroche = iEntete >= 0 ? lignes_[iEntete + 1]?.trim() : ""
      const dieses = lignes_.find((l) => l.startsWith("#")) ?? DIESES()
      TT.push(`## Jour ${f.rang} : ${f.court ?? f.terme}`, "",
        C.entete(f.rang),
        accroche || `⟦Accroche en une phrase pour « ${f.terme} »${C.langue}.⟧`,
        S.format === "methode" ? C.tiktokMethode : C.tiktokDef,
        (dieses.includes(C.tiktok) ? dieses : `${dieses} ${C.tiktok}`).replace(/\s+/g, " ").trim(), "")
    }
    writeFileSync(legendesTiktok, TT.join("\n"))
    console.log("legendes-tiktok.md : écrit à partir de legendes.md")
  }
} else console.log("legendes-tiktok.md existe déjà : non touché")

// ---------------------------------------------------------------- lignes du planning (une fois par semaine)
const planning = resolve(publications, "planning.csv")
const ENTETE = ["Date", "Jour", "Heure", "Plateforme", "Semaine", "Examen", "Matière", "Images", "Légende (legendes.md)",
  "Statut", "Publié le", "Lien", "Réactions"]
const q = (v) => `"${String(v).replace(/"/g, '""')}"`
const lundi = new Date(`${S.lundi}T12:00:00Z`)
if (lundi.getUTCDay() !== 1) throw new Error(`lundi : ${S.lundi} n'est pas un lundi`)
const JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
const jour = (k) => {
  const d = new Date(lundi.getTime() + k * 86400000)
  return [`${String(d.getUTCDate()).padStart(2, "0")}/${String(d.getUTCMonth() + 1).padStart(2, "0")}/${d.getUTCFullYear()}`, JOURS[k]]
}
const lignes = []
const ligne = (k, heure, plateforme, images, legende) =>
  lignes.push([...jour(k), heure, plateforme, nomSemaine, S.examen, S.matiere_nom, images, legende, "À relire", "", "", ""])
fiches.forEach((f, k) => {
  const p = `j${k + 1}-${f.cle}`
  if (S.format === "methode") {
    ligne(k, "17:30", "Facebook / Instagram", `images/4x5/${p}-1 à 5`, `Jour ${k + 1} : publication`)
    ligne(k, "17:45", "WhatsApp", `images/9x16/${p}-1-a-toi puis -2-piege`, `Jour ${k + 1} : statut`)
    ligne(k, "20:30", "Toutes", `images/4x5/${p}-6-reponse-soir ; 9x16/${p}-3-reponse-soir`, `Jour ${k + 1} : le soir`)
  } else {
    ligne(k, "17:30", "Facebook / Instagram", `images/4x5/${p}-1-question`, `Jour ${k + 1} : publication`)
    ligne(k, "17:45", "WhatsApp", `images/9x16/${p}-1-question`, `Jour ${k + 1} : statut`)
    ligne(k, "20:30", "Toutes", `images/4x5/${p}-2-reponse-soir ; 9x16/${p}-2-reponse-soir`, `Jour ${k + 1} : le soir`)
  }
})
if (S.format === "methode") {
  ligne(5, "11:00", "Facebook / Instagram", "images/4x5/j6-pieges-0 à 5", "Jour 6 : publication")
  ligne(6, "11:00", "Toutes", "images/4x5/j7-defi-1-questions ; 9x16/j7-defi-1-questions", "Jour 7 : publication")
  ligne(6, "19:00", "Toutes", "images/4x5/j7-defi-2-reponses-soir ; 9x16/j7-defi-2-reponses-soir", "Jour 7 : le soir")
} else {
  ligne(5, "11:00", "Toutes", "images/4x5/j6-devine-1-questions ; 9x16/j6-devine-1-questions", "Jour 6 : publication")
  ligne(5, "19:00", "Toutes", "images/4x5/j6-devine-2-reponses-soir ; 9x16/j6-devine-2-reponses-soir", "Jour 6 : le soir")
  ligne(6, "11:00", "Facebook / Instagram", "images/4x5/j7-recap-0 à 5", "Jour 7 : publication")
}
// TikTok : la vidéo du jour, du lundi au vendredi, en soirée.
fiches.forEach((f, k) => ligne(k, "19:00", "TikTok", `videos/j${k + 1}-${f.cle}.mp4`, `Jour ${k + 1} (legendes-tiktok.md)`))

// Une ligne n'est ajoutée que si la semaine n'a pas déjà une ligne pour les mêmes images : une date ou une heure
// changée à la main dans le planning reste telle quelle, et une plateforme ajoutée au moteur s'ajoute aux semaines faites.
const existant = existsSync(planning) ? readFileSync(planning, "utf8").replace(/^﻿/, "") : ""
const champs = (l) => [...l.matchAll(/"((?:[^"]|"")*)"/g)].map((m) => m[1].replace(/""/g, '"'))
const corps = existant.trim() ? existant.trimEnd().split(/\r?\n/) : [ENTETE.map(q).join(";")]
const dejaLa = new Set(corps.slice(1).map((l) => { const c = champs(l); return `${c[4]}|${c[7]}` }))
const nouvelles = lignes.filter((l) => !dejaLa.has(`${l[4]}|${l[7]}`))
// --sans-planning : plusieurs semaines préparées en même temps ne doivent pas écrire le planning ensemble.
if (SANS_PLANNING) console.log(`planning.csv : non touché (--sans-planning) ; ${nouvelles.length} ligne(s) à ajouter plus tard`)
else if (!nouvelles.length) console.log("planning.csv : la semaine y est déjà en entier, non touché")
else {
  // Les lignes restent triées par date, puis par heure.
  const cle = (l) => { const [d, , h] = champs(l); const [jj, mm, aa] = d.split("/"); return `${aa}${mm}${jj}${h}` }
  const toutes = [...corps.slice(1), ...nouvelles.map((l) => l.map(q).join(";"))].sort((a, b) => cle(a).localeCompare(cle(b)))
  writeFileSync(planning, "﻿" + [corps[0], ...toutes].join("\r\n") + "\r\n")
  console.log(`planning.csv : ${nouvelles.length} ligne(s) ajoutée(s) (statut « À relire »)`)
}

console.log(`${pages.length} vues dans sources/pages.html ; quiz sans compte dans la matière : ${avecQuiz ? "oui" : "non"}`)
for (const f of fiches) console.log(`  ${f.rang}. ${f.cle} : ${f.annees.length} session(s) officielle(s) (${f.annees.join(", ")})`)
