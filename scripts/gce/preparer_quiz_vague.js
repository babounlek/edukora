#!/usr/bin/env node
/**
 * Prépare une vague de quiz GCE pour les matières qui n'en ont pas encore : à partir des sélections brutes
 * `backend/ingest/_quiz/_sel_<CODE>.json` (voir selectionner_quiz_nouvelles_matieres.sh), garde les 25 compétences les
 * mieux classées PAR NIVEAU (O Level / A Level) et PAR MATIÈRE, puis les découpe en tranches de 5 pour les agents.
 *
 *   node scripts/gce/preparer_quiz_vague.js [--par-niveau 25]
 *
 * Règles :
 *  - une compétence exclusive d'un niveau reste à ce niveau ;
 *  - une compétence partagée par les deux niveaux (même Tag) est attribuée à UN seul niveau - celui dont il manque le plus
 *    de compétences - et sa requête est réécrite avec ce seul `cursus` : un même thème n'est jamais généré deux fois ;
 *  - l'ordre de la sélection (écart de couverture décroissant, voir quiz.ingestion.select_quiz_batch) est conservé.
 *
 * Écrit `backend/ingest/_quiz/_batch_cm_gce_<niveau>_<matiere>_NN.json` (une tranche) et
 * `backend/ingest/_quiz/_vague_nouvelles_matieres.json` (l'index que lit l'orchestration : une entrée par tranche, avec son
 * dossier de sortie `gce-<niveau>-<matiere>-NN`).
 */
const fs = require("fs");
const path = require("path");

const RACINE = path.resolve(__dirname, "..", "..");
const QUIZ = path.join(RACINE, "backend", "ingest", "_quiz");
const PAR_NIVEAU = Number((process.argv.indexOf("--par-niveau") > -1 && process.argv[process.argv.indexOf("--par-niveau") + 1]) || 25);
const TAILLE_TRANCHE = 5;

const SLUGS = {
  GCE_ADD_MATHS: "add-maths", GCE_BIOLOGY: "biology", GCE_CITIZENSHIP: "citizenship", GCE_COMMERCE: "commerce",
  GCE_COMPUTER_SCI: "computer-sci", GCE_ECONOMICS: "economics", GCE_ENGLISH: "english", GCE_FOOD_NUTRITION: "food-nutrition",
  GCE_FRENCH: "french", GCE_GEOGRAPHY: "geography", GCE_HISTORY: "history", GCE_HUMAN_BIOLOGY: "human-biology",
  GCE_GEOLOGY: "geology", GCE_ICT: "ict", GCE_PHILOSOPHY: "philosophy", GCE_PM_MECHANICS: "pm-mechanics",
  GCE_PM_STATISTICS: "pm-statistics", GCE_RELIGION: "religion", GCE_SBE_FRENCH: "sbe-french",
};

const examens = (r) => r.cursus.map((c) => c.examen);
const index = [];
const noms = new Map();
const bilan = [];

for (const [code, slug] of Object.entries(SLUGS)) {
  const fichier = path.join(QUIZ, `_sel_${code}.json`);
  if (!fs.existsSync(fichier)) { console.error(`MANQUE ${fichier}`); continue; }
  const sel = JSON.parse(fs.readFileSync(fichier, "utf8"));
  const niveaux = ["ol", "al"].filter((l) => sel.some((r) => examens(r).includes(`gce_${l}`)));
  const choisis = { ol: [], al: [] };

  for (const r of sel) {
    const ex = examens(r);
    if (ex.length === 1) {
      const l = ex[0] === "gce_ol" ? "ol" : "al";
      if (choisis[l].length < PAR_NIVEAU) choisis[l].push(r);
    }
  }
  for (const r of sel) {
    const ex = examens(r);
    if (ex.length < 2) continue;
    const candidats = niveaux.filter((l) => choisis[l].length < PAR_NIVEAU);
    if (!candidats.length) break;
    candidats.sort((a, b) => choisis[a].length - choisis[b].length);
    const l = candidats[0];
    choisis[l].push({ ...r, cursus: [{ examen: `gce_${l}`, serie: "" }] });
  }

  for (const l of niveaux) {
    const reqs = choisis[l];
    for (let i = 0; i < reqs.length; i += TAILLE_TRANCHE) {
      const num = String(i / TAILLE_TRANCHE + 1).padStart(2, "0");
      const tranche = reqs.slice(i, i + TAILLE_TRANCHE);
      const batch = `_batch_cm_gce_${l}_${slug}_${num}.json`;
      fs.writeFileSync(path.join(QUIZ, batch), JSON.stringify(tranche, null, 1));
      index.push({
        id: `${l}-${slug}-${num}`, dossier: `gce-${l}-${slug}-${num}`, batch, matiere: tranche[0].matiere,
        niveau: l === "ol" ? "gce_ol" : "gce_al", competences: tranche.map((r) => r.competence),
      });
      for (const r of tranche) noms.set(r.competence, [...(noms.get(r.competence) || []), `${l}-${slug}`]);
    }
    bilan.push(`${code.padEnd(20)} ${l.toUpperCase()}  ${String(reqs.length).padStart(2)} compétences`);
  }
}

fs.writeFileSync(path.join(QUIZ, "_vague_nouvelles_matieres.json"), JSON.stringify(index, null, 1));
console.log(bilan.join("\n"));
console.log(`\n${index.length} tranches, ${index.reduce((n, t) => n + t.competences.length, 0)} compétences.`);
const doublons = [...noms].filter(([, v]) => v.length > 1);
if (doublons.length) {
  console.log(`\nATTENTION - ${doublons.length} nom(s) de compétence présent(s) dans plusieurs matières/niveaux (external_id à renuméroter) :`);
  for (const [n, v] of doublons) console.log(`  ${n} : ${v.join(", ")}`);
}
