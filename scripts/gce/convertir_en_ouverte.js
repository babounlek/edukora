// Convertit des QCM d'un JSON d'exercice GCE en questions OUVERTES (clé imprimée ou options discutables).
//
//   node scripts/gce/convertir_en_ouverte.js <fichier.json> <numero> [<numero> ...] [--note "texte"]
//
// Règle du mode GCE (voir README.md, « Clé de QCM fautive ») : on ne choisit jamais une lettre au hasard. La question passe
// en `ouverte` (choix vides, pas de reponse_correcte), les options sont recopiées dans l'énoncé (« Options as printed »),
// la réponse visée reste dans le corrigé, et l'écart est consigné dans `incertitudes` (champ en français).
// Idempotent : une question déjà ouverte est ignorée.
const fs = require("fs");

const args = process.argv.slice(2);
const noteIdx = args.indexOf("--note");
const note = noteIdx >= 0 ? args.splice(noteIdx, 2)[1] : "";
const [fichier, ...numeros] = args;
if (!fichier || numeros.length === 0) {
  console.error("usage: node convertir_en_ouverte.js <fichier.json> <numero> [<numero> ...] [--note \"texte\"]");
  process.exit(2);
}

const data = JSON.parse(fs.readFileSync(fichier, "utf8"));
const converties = [];
for (const numero of numeros) {
  const q = data.questions.find((x) => String(x.numero) === String(numero));
  if (!q) throw new Error(`question ${numero} introuvable dans ${fichier}`);
  if (q.type_reponse === "ouverte") continue;
  const options = q.choix.map((c) => `${c.lettre.toUpperCase()}) ${c.texte}`).join("   ");
  const cle = q.choix.find((c) => c.lettre === q.reponse_correcte);
  q.enonce_markdown = `${q.enonce_markdown}\n\n*Options as printed:* ${options}`;
  const sansReponse = q.corrige_markdown.replace(/\s*\*\*Answer:\s*[A-Da-d]\.?\*\*/g, "").trimEnd();
  const visee = cle ? `**Intended answer: ${cle.lettre.toUpperCase()} (${String(cle.texte).replace(/\.$/, "")}).**` : "";
  q.corrige_markdown =
    `${sansReponse}\n\n${visee}\n\nThe printed question is not reliable enough to be marked automatically so it is left open for self-assessment instead of being auto-marked.`;
  q.type_reponse = "ouverte";
  q.choix = [];
  q.reponse_correcte = "";
  converties.push(q.numero);
}
if (converties.length) {
  const texte = `Converties en questions ouvertes par le relecteur (clé ou options discutables) : ${converties.join(", ")}.${note ? " " + note : ""}`;
  data.incertitudes = [...(data.incertitudes || []), texte];
}
fs.writeFileSync(fichier, JSON.stringify(data, null, 2), "utf8");
console.log(`converties : ${converties.join(", ") || "aucune"} ; ouvertes au total : ${data.questions.filter((x) => x.type_reponse === "ouverte").length}`);
