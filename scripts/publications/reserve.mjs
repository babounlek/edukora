// La réserve des fiches gratuites en ligne : pour chacune, la semaine qui l'utilise déjà (semaines/*/semaine.json).
// Écrit <publications>/reserve.csv et affiche les semaines encore possibles.
//
//   node reserve.mjs <dossier publications>
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs"
import { resolve } from "node:path"

const SITE = "https://edukora.africa"
const publications = resolve(process.argv[2] ?? ".")
if (!existsSync(resolve(publications, "semaines"))) {
  console.error("Usage : node reserve.mjs <dossier publications> (celui qui contient semaines/)")
  process.exit(1)
}
const lire = async (u) => { const r = await fetch(SITE + u); if (!r.ok) throw new Error(`${u} : ${r.status}`); return r.json() }

// Les semaines déjà préparées : fiche id -> semaine.
// Un semaine.json en cours d'écriture (autre préparation en parallèle) est ignoré, avec un message.
const lireSemaine = (nom) => {
  try { return { nom, ...JSON.parse(readFileSync(resolve(publications, "semaines", nom, "semaine.json"), "utf8")) } }
  catch { console.log(`(${nom}/semaine.json illisible pour l'instant : ignoré)`); return null }
}
const semaines = readdirSync(resolve(publications, "semaines"), { withFileTypes: true })
  .filter((d) => d.isDirectory() && existsSync(resolve(publications, "semaines", d.name, "semaine.json")))
  .map((d) => lireSemaine(d.name)).filter((s) => s && s.lundi && Array.isArray(s.fiches))
  .sort((a, b) => a.lundi.localeCompare(b.lundi))
const utilisee = new Map()
const termesUtilises = new Map()
// Une semaine lue sur le serveur local ("source", fiches GCE en brouillon) a des ids locaux : elle ne marque rien ici.
for (const s of semaines) if (!s.source) for (const f of s.fiches) utilisee.set(f.id, s.nom)
const locales = semaines.filter((s) => s.source)

// Tous les examens, francophones et anglophones (GCE) : une semaine GCE se publie en anglais.
const NOMS = { GCE_OL: "GCE O Level", GCE_AL: "GCE A Level" }
const cursus = (await lire("/catalog/cursus/?pays=cm")).map((c) => ({ ...c, examen: NOMS[c.examen] ?? c.examen }))
const essais = await lire("/quiz/essais/")
const lignes = new Map() // examen|matiere|id
for (const c of cursus) {
  const { matieres } = await lire(`/memos/matieres/?cursus=${c.id}`)
  for (const m of matieres.filter((m) => m.gratuites)) {
    const { fiches } = await lire(`/memos/fiches/?cursus=${c.id}&matiere=${m.matiere_id}`)
    for (const f of fiches.filter((f) => f.gratuit)) {
      const cle = `${c.examen}|${m.matiere_id}|${f.id}`
      const l = lignes.get(cle) ?? { examen: c.examen, series: [], matiere: m.matiere, matiere_id: m.matiere_id, cursus: [],
        id: f.id, terme: f.terme, officielles: new Set() }
      if (c.series?.code) l.series.push(c.series.code)
      l.cursus.push(c.id)
      f.sessions.filter((s) => s.origine === "OFFICIEL").forEach((s) => l.officielles.add(s.annee))
      lignes.set(cle, l)
      if (utilisee.has(f.id)) termesUtilises.set(f.terme.toLowerCase(), utilisee.get(f.id))
    }
  }
}

// Une même notion peut être gratuite à deux examens, avec deux fiches différentes (ex. « Tontine » au BEPC et au
// Probatoire) : sur la même page, ce serait la publier deux fois.
const toutes = [...lignes.values()]
const examenDe = new Map(semaines.map((s) => [s.nom, s.cursus]))
for (const l of toutes) {
  l.semaine = utilisee.get(l.id) ?? ""
  const ailleurs = termesUtilises.get(l.terme.toLowerCase())
  if (!l.semaine && ailleurs) l.remarque = `même notion déjà dans ${ailleurs} : ne pas la reprendre`
  // La même fiche, gratuite à deux examens : prise par la semaine de l'autre examen.
  else if (l.semaine && !(examenDe.get(l.semaine) ?? []).some((c) => l.cursus.includes(c)))
    l.remarque = `fiche aussi gratuite à un autre examen, déjà publiée dans ${l.semaine}`
  else l.remarque = ""
}
const q = (v) => `"${String(v).replace(/"/g, '""')}"`
const ordreExamen = { BEPC: 0, PROBATOIRE: 1, BAC: 2, "GCE O Level": 3, "GCE A Level": 4 }
toutes.sort((a, b) => (ordreExamen[a.examen] - ordreExamen[b.examen]) || a.matiere.localeCompare(b.matiere, "fr") ||
  b.officielles.size - a.officielles.size)
const csv = [["Examen", "Séries", "Matière", "Fiche", "Id", "Sessions officielles", "Semaine", "Lien des fiches", "Remarque"].map(q).join(";")]
for (const l of toutes) csv.push([l.examen, l.series.join(", ") || "-", l.matiere, l.terme, l.id, l.officielles.size, l.semaine,
  `${SITE}/fiches-edukora?cursus=${l.cursus[0]}&matiere=${l.matiere_id}`, l.remarque].map(q).join(";"))
writeFileSync(resolve(publications, "reserve.csv"), "﻿" + csv.join("\r\n") + "\r\n")

// Les groupes examen × matière : combien de gratuites restent libres.
const groupes = new Map()
for (const l of toutes) {
  const g = groupes.get(`${l.examen}|${l.matiere_id}`) ?? { examen: l.examen, matiere: l.matiere, matiere_id: l.matiere_id,
    series: new Set(), cursus: new Set(), libres: [], prises: 0 }
  l.series.forEach((s) => g.series.add(s)); l.cursus.forEach((c) => g.cursus.add(c))
  if (l.semaine) g.prises++
  else if (!l.remarque) g.libres.push(l)
  if (l.remarque) (g.ecartees ??= []).push(l)
  groupes.set(`${l.examen}|${l.matiere_id}`, g)
}
const quiz = (g) => [...g.cursus].every((c) => essais.some((e) => e.cursus === c && e.subject === g.matiere_id))
console.log(`reserve.csv : ${toutes.length} fiches gratuites, ${toutes.filter((l) => l.semaine).length} déjà dans une semaine\n`)
console.log("Semaines encore possibles (5 gratuites libres ou plus) :")
for (const g of [...groupes.values()].filter((g) => g.libres.length >= 5))
  console.log(`  ${g.examen.padEnd(10)} ${[...g.series].join(", ").padEnd(14)} ${g.matiere.padEnd(30)} ` +
    `cursus ${[...g.cursus].join(",")} matière ${g.matiere_id} : ${g.libres.length} libres` + (quiz(g) ? "" : " (pas de quiz sans compte dans la matière)") +
    (g.ecartees?.length ? ` ; à écarter : ${g.ecartees.map((l) => `« ${l.terme} » (${l.remarque})`).join(", ")}` : ""))
const courts = [...groupes.values()].filter((g) => g.libres.length && g.libres.length < 5)
if (courts.length) console.log("Moins de 5 libres :", courts.map((g) => `${g.examen} ${g.matiere} (${g.libres.length})`).join(", "))
// Les examens sans aucune fiche gratuite (le GCE au 27/11/2026) : ce qui existe d'autre de gratuit, les quiz sans compte.
for (const c of cursus.filter((c) => !toutes.some((l) => l.cursus.includes(c.id)))) {
  const siens = essais.filter((e) => e.cursus === c.id)
  if (c.langue !== "fr" || siens.length)
    console.log(`${c.examen}${c.series?.code ? " " + c.series.code : ""} (cursus ${c.id}, ${c.langue}) : aucune fiche gratuite en ligne ; ` +
      `${siens.length} quiz gratuit(s) sans compte${c.langue === "fr" ? "" : " (en anglais)"}`)
}
const doublons = toutes.filter((l) => l.remarque)
if (doublons.length) console.log("Notions déjà publiées sous un autre examen :", doublons.map((l) => `${l.terme} (${l.examen})`).join(", "))
console.log("\nSemaines préparées :", semaines.map((s) => `${s.nom}`).join(", ") || "aucune")
if (locales.length)
  console.log("Préparées sur des fiches en brouillon (serveur local, pas encore en ligne) :", locales.map((s) => s.nom).join(", "))
