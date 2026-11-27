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

// ---------------------------------------------------------------- l'instantané du site
async function lire(chemin) {
  const r = await fetch(SITE + chemin)
  if (!r.ok) throw new Error(`${SITE}${chemin} : ${r.status}`)
  return r.json()
}
const fusionner = (a, b) =>
  [...new Map([...a, ...b].map((s) => [`${s.annee}|${s.origine}`, s])).values()].sort((x, y) => x.annee - y.annee)

async function prendreInstantane() {
  const parId = new Map()
  for (const c of S.cursus) {
    const { fiches } = await lire(`/memos/fiches/?cursus=${c}&matiere=${S.matiere}`)
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
    for (const f of JSON.parse(readFileSync(autre, "utf8")).fiches ?? []) dejaPrises.set(f.id, d.name)
  }

// "fiches": [] : on liste les gratuites en ligne pour les choisir, sans rien construire.
if (!S.fiches.length) {
  console.log(`Gratuites en ligne (instantané du ${enLigne_.pris_le}) ; quiz sans compte dans la matière : ` +
    `${S.cursus.every((c) => enLigne_.essais.some((e) => e.cursus === c)) ? "oui" : "non"}`)
  for (const f of enLigne_.fiches) {
    const off = [...new Set(f.sessions.filter((s) => s.origine === "OFFICIEL").map((s) => s.annee))]
    const manque = ["exemple", "piege", "exercice", "reponse"].filter((c) => !f[c])
    console.log(`  id ${f.id} | ${f.terme} | ${f.rubrique || "-"} | ${off.length} session(s) officielle(s) ${off.join(",")}` +
      ` | séries ${f.cursus.join(",")}${manque.length ? ` | sans ${manque.join(", ")} (format definition)` : ""}` +
      (dejaPrises.has(f.id) ? ` | DÉJÀ DANS ${dejaPrises.get(f.id)} : à écarter` : ""))
  }
  console.log("Les textes complets sont dans sources/fiches-en-ligne.json. Remplir \"fiches\" dans semaine.json, puis relancer.")
  process.exit(0)
}

const fiches = S.fiches.map((choix, i) => {
  const f = enLigne_.fiches.find((n) => n.id === choix.id)
  if (!f) throw new Error(`la fiche ${choix.id} (${choix.cle}) n'est pas parmi les gratuites en ligne : voir sources/fiches-en-ligne.json`)
  if (!/^[a-z0-9-]+$/.test(choix.cle)) throw new Error(`clé « ${choix.cle} » : minuscules, chiffres et tirets seulement`)
  if (dejaPrises.has(choix.id) && !S.reprise)
    throw new Error(`la fiche ${choix.id} « ${f.terme} » est déjà dans ${dejaPrises.get(choix.id)} : en choisir une autre ` +
      `(ou "reprise": true dans semaine.json pour une semaine reprise exprès)`)
  const annees = [...new Set(f.sessions.filter((s) => s.origine === "OFFICIEL").map((s) => s.annee))].sort((a, b) => a - b)
  return { ...f, ...choix, rang: i + 1, annees }
})
const ecartees = enLigne_.fiches.filter((f) => !S.fiches.some((c) => c.id === f.id))
if (ecartees.length) console.log("Gratuites en ligne non retenues :", ecartees.map((f) => `${f.id} « ${f.terme} »`).join(", "))
const avecQuiz = S.cursus.every((c) => enLigne_.essais.some((e) => e.cursus === c))

// ---------------------------------------------------------------- texte et formules
const echapper = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
const maths = (tex, bloc) => katex.renderToString(tex.trim(), { displayMode: bloc, throwOnError: true })
const UNITES = "g\\/mol|g\\/L|mol\\/L|mol|mL|cm³|cm²|cm|km|kg|mm|g|L|m|min|h|s|V|A|W|J|N|Hz|Ω|°C|%"
// Espaces insécables : ponctuation double, unités, « = » et « / » du texte courant.
const insecables = (t) =>
  t.replace(/« /g, "« ").replace(/ ([?!:;»])/g, " $1")
    .replace(new RegExp(`(\\d) (${UNITES})(?![A-Za-zà-ÿ])`, "g"), "$1 $2")
    .replace(/ ([=\/]) /g, " $1 ")
const majuscule = (t) => t.charAt(0).toUpperCase() + t.slice(1)
const enLigne = (s) =>
  s.split(/(\$\$[\s\S]+?\$\$|\$[^$]+?\$|`[^`]+`)/).map((m) => {
    if (m.startsWith("`")) return `<code>${echapper(m.slice(1, -1))}</code>`
    if (m.startsWith("$$")) return maths(m.slice(2, -2), true)
    if (m.startsWith("$")) return maths(m.slice(1, -1), false)
    return insecables(echapper(m)).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
  }).join("")
function markdown(texte, { titres = false } = {}) {
  const sortie = []
  let liste = null, premiere = true
  const fermer = () => { if (liste) sortie.push(`</${liste}>`); liste = null }
  // Un bloc $$ sur plusieurs lignes devient une seule ligne.
  for (const ligne of texte.replace(/\$\$\s*([\s\S]+?)\s*\$\$/g, (_, t) => `$$${t.replace(/\n/g, " ")}$$`).split("\n")) {
    const m = ligne.match(/^(\d+\.|-)\s+(.*)$/)
    if (m) {
      const type = m[1] === "-" ? "ul" : "ol"
      // Une liste numérotée coupée par une formule centrée reprend à son numéro (« 5. »), pas à 1.
      const debut = type === "ol" && parseInt(m[1], 10) > 1 ? ` start="${parseInt(m[1], 10)}"` : ""
      if (liste !== type) { fermer(); sortie.push(`<${type}${debut}>`); liste = type }
      sortie.push(`<li>${enLigne(m[2])}</li>`)
      premiere = false
      continue
    }
    fermer()
    if (!ligne.trim()) continue
    // Dans une définition, une ligne toute en gras devient un titre (« **La méthode** »). La première ligne aussi
    // quand elle commence par une étiquette en gras (« **Quand ?** … », « **À retenir** : … », « **L'idée** : … »).
    const t = titres && (ligne.match(/^\*\*([^*]+)\*\*\s*:?\s*$/) || (premiere && ligne.match(/^\*\*([^*]+)\*\*\s*[:,]?\s*(.+)$/)))
    premiere = false
    if (t) {
      const titre = t[1].trim() === "Quand ?" ? "Quand l'utiliser ?" : t[1].trim()
      sortie.push(`<h2>${enLigne(titre)}</h2>`)
      if (t[2]) sortie.push(`<p>${enLigne(majuscule(t[2]))}</p>`)
    } else sortie.push(`<p>${enLigne(ligne)}</p>`)
  }
  fermer()
  return sortie.join("")
}
const listeFr = (a) => (a.length < 2 ? `${a[0] ?? ""}` : `${a.slice(0, -1).join(", ")} et ${a.at(-1)}`)
const deLa = (nom) => (/^[aeiouyéèêàâîôûh]/i.test(nom) ? `d'${nom}` : `de ${nom}`)

// ---------------------------------------------------------------- les vues
const pages = []
function page(nom, format, { sombre = false, corps, pied = "" }) {
  const logo = url(`public/brand/logo-horizontal-minimal${sombre ? "-dark" : ""}.svg`)
  pages.push(`<section class="page ${format}${sombre ? " sombre" : ""}" data-nom="${nom}">
<header><span class="bandeau">${BANDEAU}</span></header>
<main><div class="contenu">${corps}</div></main>
<footer><img src="${logo}" alt="EduKora"><span>${/\d \/ 5$/.test(pied) ? `edukora.africa · ${pied}` : pied || "edukora.africa"}</span></footer></section>`)
}
const BANDEAU = `<b>Fiches EduKora</b> · ${echapper(S.bandeau)}`
// L'invitation, après l'effort. Pas de total de fiches : il change (« certaines gratuites, les autres avec l'abonnement »).
const INVITATION = `<div class="invitation"><p><b>Envie de t'entraîner encore ?</b> Essaie un quiz ${avecQuiz ? "" : "gratuit dans une autre matière "}sur edukora.africa, sans compte.</p>
<p class="detail">D'autres Fiches EduKora t'y attendent : certaines gratuites, les autres avec l'abonnement.</p></div>`
// sans_coupure s'écrit avec des espaces ordinaires : on le transforme comme le titre avant de le chercher.
const question = (f) =>
  (S.sans_coupure ?? []).reduce((t, bout) => {
    const cible = insecables(echapper(bout))
    if (!t.includes(cible)) return t
    return t.replace(cible, `<span style="white-space:nowrap">${cible}</span>`)
  }, insecables(echapper(f.terme)))
for (const bout of S.sans_coupure ?? [])
  if (!fiches.some((f) => f.terme.includes(bout)))
    console.log(`sans_coupure : « ${bout} » ne figure dans aucun titre de la semaine`)
// Sur les images, « Probatoire D » ne se coupe pas en fin de ligne.
const EXAMEN = S.examen.replace(/ /g, " ")

function preuveDe(f) {
  const n = f.annees.length
  if (!n) throw new Error(`« ${f.terme} » n'a aucune session officielle : la carte ne peut rien annoncer`)
  if (n === 1) return `Demandée au ${EXAMEN} en <b>${f.annees[0]}</b>`
  const modele = (S.preuve ?? `Demandée dans <b>{n} sujets</b> du ${S.examen} entre {debut} et {fin}`).replace(S.examen, EXAMEN)
  return modele.replace("{n}", n).replace("{debut}", f.annees[0]).replace("{fin}", f.annees.at(-1))
}

if (S.format === "methode") {
  const aRetenir = (f) => /^\*\*À retenir\*\*/.test(f.definition)
  const blocExemple = (f) => {
    const [titre, ...reste] = f.exemple.split("\n")
    const m = titre.match(/^\*\*(.+?)\*\*\s*[:,]?\s*(.*)$/)
    return m ? { titre: m[1], corps: [majuscule(m[2]), ...reste].join("\n") } : { titre: "Exemple", corps: f.exemple }
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
    page(`${p}-1-question`, "post", { sombre: true, pied: `Touche l'image pour voir ${aRetenir(f) ? "la fiche" : "la méthode"} →`,
      corps: `<p class="surtitre">${aRetenir(f) ? "Fiche à retenir" : "Fiche de méthode"} n° ${i + 1}</p><h1>${question(f)}</h1><p class="preuve">${preuveDe(f)}</p>` })
    page(`${p}-2-methode`, "post", { pied: suite(2), corps: markdown(f.definition, { titres: true }) })
    page(`${p}-3-exemple`, "post", { pied: suite(3), corps: `<h2>${enLigne(ex.titre)}</h2>${markdown(ex.corps)}` })
    page(`${p}-4-piege`, "post", { pied: suite(4), corps: `<div class="piege"><h2>Le piège</h2>${markdown(f.piege)}</div>` })
    page(`${p}-5-a-toi`, "post", { pied: suite(5),
      corps: `<h2>À toi</h2>${at.origine}${markdown(at.enonce)}<p class="appel">Écris ta réponse en commentaire. Correction ce soir.</p>` })
    page(`${p}-6-reponse-soir`, "post", {
      corps: `<p class="surtitre">La réponse</p>${markdown(at.enonce)}<div class="reponse">${markdown(f.reponse)}</div>${INVITATION}` })

    const s = `9x16/j${i + 1}-${f.cle}`
    page(`${s}-1-a-toi`, "statut", {
      corps: `<p class="surtitre">À toi</p><h2>${question(f)}</h2>${at.origine}${markdown(at.enonce)}<p class="appel">Réponds à ce statut. Correction ce soir.</p>` })
    page(`${s}-2-piege`, "statut", { corps: `<h2>${question(f)}</h2><div class="piege"><h2>Le piège</h2>${markdown(f.piege)}</div>` })
    page(`${s}-3-reponse-soir`, "statut", {
      corps: `<p class="surtitre">La réponse</p>${markdown(at.enonce)}<div class="reponse">${markdown(f.reponse)}</div>${INVITATION}` })
  })

  // Samedi : les 5 pièges (couverture + les pièges titrés).
  page("4x5/j6-pieges-0-couverture", "post", { sombre: true, pied: "Touche l'image pour voir les pièges →",
    corps: `<p class="surtitre">La semaine en ${echapper(S.matiere_nom)}</p><h1>5 pièges à éviter au ${EXAMEN}</h1><p class="preuve">Lequel as-tu déjà fait ?</p>` })
  fiches.forEach((f, i) => page(`4x5/j6-pieges-${i + 1}-${f.cle}`, "post", { pied: `Piège ${i + 1} / 5`,
    corps: `<h2>${question(f)}</h2><div class="piege">${markdown(f.piege)}</div>${i === fiches.length - 1 ? INVITATION : ""}` }))

  // Dimanche : les 5 exercices sans la méthode, puis les 5 réponses. Un intitulé court situe chaque question.
  const liste = (champ) => `<ol class="defi">${fiches.map((f) =>
    `<li>${f.court ? `<p class="origine">${echapper(f.court)}</p>` : ""}${markdown(champ === "exercice" ? sujetDe(f).enonce : f.reponse)}</li>`).join("")}</ol>`
  for (const [format, sous] of [["post", "4x5"], ["statut", "9x16"]]) {
    page(`${sous}/j7-defi-1-questions`, format, {
      corps: `<h2>Le défi du dimanche : 5 ${S.defi ?? "questions"}, sans regarder les fiches</h2>${liste("exercice")}` })
    page(`${sous}/j7-defi-2-reponses-soir`, format, { corps: `<h2>Le défi du dimanche : les réponses</h2>${liste("reponse")}${INVITATION}` })
  }
} else {
  // Définitions seules : le mot le matin, la fiche le soir ; samedi retrouver le mot ; dimanche le récapitulatif.
  const auExamen = (f) => (f.annees.length <= 3
    ? `Au ${EXAMEN} en <b>${listeFr(f.annees)}</b>`
    : `Au ${EXAMEN} : <b>${f.annees.length} sessions</b> entre ${f.annees[0]} et ${f.annees.at(-1)}`)
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
        corps: `<p class="surtitre">Fiche n° ${i + 1} · Sais-tu définir ?</p><h1>${question(f)}</h1><p class="preuve">${auExamen(f)}</p>` +
          `<p class="appel">${format === "post" ? "Écris ta définition en commentaire." : "Réponds à ce statut."} La fiche ce soir.</p>` })
      page(`${p}-2-reponse-soir`, format, { corps: `<p class="surtitre">La définition</p>${definition(f)}${INVITATION}` })
    }
  })
  const ordre = (S.ordre_devine ?? [3, 0, 4, 2, 1].map((k) => fiches[k].cle)).map((c) => {
    const f = fiches.find((x) => x.cle === c)
    if (!f) throw new Error(`ordre_devine : clé inconnue « ${c} »`)
    return f
  })
  const liste = (ligne) => `<ol class="defi">${ordre.map((f) => `<li>${ligne(f)}</li>`).join("")}</ol>`
  for (const [format, sous] of [["post", "4x5"], ["statut", "9x16"]]) {
    page(`${sous}/j6-devine-1-questions`, format, { corps: `<h2>Quel est le mot ? 5 définitions de la semaine</h2>${liste((f) => enLigne(indice(f)))}` })
    page(`${sous}/j6-devine-2-reponses-soir`, format, { corps: `<h2>Quel est le mot ? Les réponses</h2>${liste((f) => `<b>${question(f)}</b>`)}${INVITATION}` })
  }
  page("4x5/j7-recap-0-couverture", "post", { sombre: true, pied: "Touche l'image pour voir les définitions →",
    corps: `<p class="surtitre">La semaine en ${echapper(S.matiere_nom)}</p><h1>5 définitions à garder</h1><p class="preuve">Enregistre-les pour tes révisions.</p>` })
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
footer{display:flex;justify-content:space-between;align-items:center;font-size:28px;font-weight:500}
footer img{height:58px}
`
const feuilles = [
  "node_modules/katex/dist/katex.min.css",
  "node_modules/@fontsource/work-sans/400.css", "node_modules/@fontsource/work-sans/500.css",
  "node_modules/@fontsource/work-sans/600.css", "node_modules/@fontsource/fraunces/600.css",
].map((p) => `<link rel="stylesheet" href="${url(p)}">`).join("")
writeFileSync(resolve(sources, "pages.html"),
  `<!doctype html><html lang="fr"><meta charset="utf-8">${feuilles}<style>${css}</style><body>${pages.join("\n")}</body></html>`)

// ---------------------------------------------------------------- brouillon des légendes (jamais écrasé)
const LIEN = `${SITE}/fiches-edukora?cursus=${S.lien_cursus ?? S.cursus[0]}&matiere=${S.matiere}`
const DIESES = (...propres) => [...S.hashtags, ...propres, "#Cameroun", "#Révisions", "#EduKora", "#FichesEduKora"].join(" ")
const QUIZ = avecQuiz
  ? "Continue avec un quiz, sans compte : https://edukora.africa"
  : "Envie de t'entraîner encore ? Un quiz gratuit dans une autre matière, sans compte : https://edukora.africa"
const AUTRES = `D'autres Fiches EduKora ${deLa(S.matiere_nom)} ${S.examen} (certaines gratuites, les autres avec l'abonnement) : ${LIEN}`
// Une formule en texte simple, comme on l'écrit dans une légende Facebook (pas de LaTeX : il ne s'y affiche pas).
const EXPOSANTS = { 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹", "-": "⁻", "+": "⁺" }
const SYMBOLES = { times: "×", approx: "≈", le: "≤", leq: "≤", ge: "≥", geq: "≥", neq: "≠", pm: "±", infty: "∞", to: "→",
  cdot: "·", pi: "π", Delta: "Δ", alpha: "α", beta: "β", lambda: "λ", mu: "µ", Omega: "Ω", circ: "°", in: "∈", cap: "∩", cup: "∪",
  Rightarrow: "⇒", Leftrightarrow: "⇔", mathbb: "", ldots: "…", dots: "…" }
function texteBrut(t) {
  const exposant = (e) => ([...e].every((c) => c in EXPOSANTS) ? [...e].map((c) => EXPOSANTS[c]).join("") : `^(${e})`)
  // Un numérateur ou un dénominateur composé prend des parenthèses, sauf s'il en a déjà.
  const terme = (a) => (/^[\w,.²³]+$/.test(a) || /^\([^()]*\)[²³]?$/.test(a) ? a : `(${a})`)
  const formule = (f) => {
    let x = f.replace(/\\left|\\right/g, "").replace(/\{,\}/g, ",")
      .replace(/\^\{([^{}]*)\}/g, (_, e) => exposant(e)).replace(/\^([0-9])/g, (_, e) => EXPOSANTS[e])
      .replace(/\\[dt]?frac(\d)(\d)/g, "$1/$2")
    for (let i = 0; i < 5; i++)
      x = x.replace(/\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}/g, (_, a, b) => `${terme(a)}/${terme(b)}`)
        .replace(/\\sqrt\{([^{}]*)\}/g, "√($1)").replace(/\\(?:text|mathrm|operatorname)\{([^{}]*)\}/g, "$1")
    return x.replace(/\\[,;!]|~/g, " ").replace(/\\%/g, "%")
      .replace(/\\([A-Za-z]+)/g, (m, n) => SYMBOLES[n] ?? n).replace(/[{}]/g, "").replace(/\s+/g, " ").trim()
  }
  return t.replace(/\$\$([\s\S]+?)\$\$/g, (_, f) => formule(f)).replace(/\$([^$]+)\$/g, (_, f) => formule(f))
    .replace(/\*\*/g, "").replace(/\s*\n\s*/g, " ").trim()
}
const brut = texteBrut
const sansBalises = (t) => t.replace(/<[^>]+>/g, "")
// La légende annonce les mêmes sessions que l'image.
const sessionsTexte = (f) => (f.annees.length <= 3 ? `au ${S.examen} en ${listeFr(f.annees)}`
  : `à ${f.annees.length} sessions du ${S.examen}, de ${f.annees[0]} à ${f.annees.at(-1)}`)

const legendes = resolve(dossier, "legendes.md")
if (!existsSync(legendes)) {
  const L = [`# Légendes de la semaine ${S.matiere_nom} ${S.examen}`, "",
    "Chaque jour a une légende du matin, une version courte pour le statut WhatsApp et un texte du soir.",
    "Les passages entre crochets doubles sont à écrire ; le reste est calculé depuis les fiches en ligne.", ""]
  if (S.format === "methode") {
    for (const f of fiches) L.push(
      `## Jour ${f.rang} : ${f.court ?? f.terme}`, "", "**Publication**",
      `📘 Fiches EduKora, ${S.bandeau} : fiche n° ${f.rang}`,
      `⟦Accroche : la difficulté de « ${f.terme} » en une phrase, posée à l'élève.⟧`,
      "⟦Ce que montrent les images, et ce qu'on attend en commentaire. Finir par « correction ce soir ».⟧",
      `${sansBalises(preuveDe(f))}.`,
      "Pour t'entraîner davantage : https://edukora.africa",
      DIESES("⟦#Thème⟧"), "",
      `**Statut WhatsApp** : ⟦La question de l'exercice en une ligne.⟧ Réponds à ce statut, correction ce soir.`, "",
      `**Le soir** : La réponse : ⟦la réponse (fiche : « ${brut(f.reponse)} »), puis le pourquoi en une phrase.⟧`,
      QUIZ, AUTRES, "")
    L.push("## Jour 6 : les 5 pièges", "", "**Publication**", `📘 Fiches EduKora, ${S.bandeau}`,
      "Les 5 pièges de la semaine. Lequel as-tu déjà fait ? Réponds avec son numéro.",
      `Envoie ce post à un camarade qui prépare le ${S.examen}.`,
      "Pour t'entraîner davantage : https://edukora.africa", DIESES("#Pièges"), "",
      "## Jour 7 : le défi", "", "**Publication**", `📘 Fiches EduKora, ${S.bandeau}`,
      `Le défi du dimanche : 5 ${S.defi ?? "questions"}, sans regarder les fiches. Note ton score sur 5 quand tu auras vu les réponses, ce soir.`,
      "Pour t'entraîner davantage : https://edukora.africa", DIESES("#Défi"), "",
      "**Le soir** : Les réponses du défi. Combien sur 5 ? La fiche que tu as ratée est celle à revoir cette semaine.",
      QUIZ, AUTRES, "")
  } else {
    const ordre = (S.ordre_devine ?? [3, 0, 4, 2, 1].map((k) => fiches[k].cle)).map((c) => fiches.find((x) => x.cle === c))
    L.splice(4, 0, "Le soir, la définition est reprise ici telle qu'elle est sur l'image.")
    for (const f of fiches) L.push(
      `## Jour ${f.rang} : ${f.terme}`, "", "**Publication**",
      `📘 Fiches EduKora, ${S.bandeau} : fiche n° ${f.rang}`,
      `Sais-tu définir « ${f.terme} » ? Notion demandée ${sessionsTexte(f)}.`,
      "⟦Une question qui oriente l'élève sans donner la réponse.⟧",
      "Écris ta définition en commentaire. La fiche arrive ce soir.",
      "Pour t'entraîner davantage : https://edukora.africa", DIESES("#Définitions"), "",
      `**Statut WhatsApp** : Définis « ${f.terme} » avec tes mots. Réponds à ce statut, la fiche ce soir.`, "",
      `**Le soir** : ${f.terme}. ${brut(f.definition)}`, "Compare avec ta réponse : qu'avais-tu oublié ?", QUIZ, AUTRES, "")
    L.push("## Jour 6 : quel est le mot ?", "", "**Publication**", `📘 Fiches EduKora, ${S.bandeau}`,
      "5 définitions de la semaine, sans les mots. Lesquels retrouves-tu ? Réponds de 1 à 5 en commentaire.",
      "Pour t'entraîner davantage : https://edukora.africa", DIESES("#Défi"), "",
      `**Le soir** : Les réponses : ${ordre.map((f, i) => `${i + 1}. ${f.terme}`).join(", ")}. Combien sur 5 ?`, QUIZ, AUTRES, "",
      "## Jour 7 : les 5 définitions à garder", "", "**Publication**", `📘 Fiches EduKora, ${S.bandeau}`,
      `Les 5 définitions de la semaine réunies. Enregistre cette publication pour tes révisions et envoie-la à un camarade qui prépare le ${S.examen}.`,
      "Pour t'entraîner davantage : https://edukora.africa", DIESES("#Récap"), "")
  }
  writeFileSync(legendes, L.join("\n"))
  console.log("legendes.md : brouillon écrit, passages ⟦…⟧ à compléter")
} else console.log("legendes.md existe déjà : non touché")

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
const existant = existsSync(planning) ? readFileSync(planning, "utf8").replace(/^﻿/, "") : ""
if (existant.includes(`"${nomSemaine}"`)) console.log("planning.csv : la semaine y est déjà, non touché")
else {
  const corps = existant.trim() ? existant.trimEnd().split(/\r?\n/) : [ENTETE.map(q).join(";")]
  // Les lignes restent triées par date, puis par heure.
  const cle = (l) => { const [d, , h] = l.split(";").map((c) => c.replace(/"/g, "")); const [jj, mm, aa] = d.split("/"); return `${aa}${mm}${jj}${h}` }
  const toutes = [...corps.slice(1), ...lignes.map((l) => l.map(q).join(";"))].sort((a, b) => cle(a).localeCompare(cle(b)))
  writeFileSync(planning, "﻿" + [corps[0], ...toutes].join("\r\n") + "\r\n")
  console.log(`planning.csv : ${lignes.length} lignes ajoutées (statut « À relire »)`)
}

console.log(`${pages.length} vues dans sources/pages.html ; quiz sans compte dans la matière : ${avecQuiz ? "oui" : "non"}`)
for (const f of fiches) console.log(`  ${f.rang}. ${f.cle} : ${f.annees.length} session(s) officielle(s) (${f.annees.join(", ")})`)
