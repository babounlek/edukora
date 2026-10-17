// Renomme des thèmes de questions dans les JSON d'exercices GCE Advanced Level (collisions de Tag avec le contenu français
// ou avec une autre matière - voir README.md, « Tag.name est unique et partagé »).
//
//   node scripts/gce/renommer_themes_al.js <dossier_racine> [--appliquer]
//
// Parcourt `<dossier_racine>/gce-al-*/*.json` (jamais l'O Level) et applique RENOMMAGES. Simulation par défaut.
// Les nouveaux noms ne sont PAS des variantes d'accent, de tiret ou de pluriel d'un tag français : `_resolve_or_create_tag`
// fusionnerait sinon le nouveau nom avec l'ancien (ex. « phenols » reviendrait à « Phénols »).
const fs = require("fs");
const path = require("path");

// Les clés incluent l'écriture du JSON (« phenols », « test cross ») ET le tag français auquel l'ingestion l'a déjà fusionné
// (« Phénols », « Test-cross ») : find_tag_variant ramène un nom à sa variante d'accent/de tiret.
const RENOMMAGES = {
  phenols: "phenol compounds",
  "Phénols": "phenol compounds",
  "test cross": "genetic test cross",
  "Test-cross": "genetic test cross",
  solutions: "chemical solutions",
  vectors: "gene vectors",
  asymptotes: "curve asymptotes",
  "climate change": "greenhouse effect and climate",
  "solar energy": "solar energy conversion",
  ethylene: "ethylene plant hormone",
  osmoregulation: "osmoregulation in animals",
};

const racine = process.argv[2];
const appliquer = process.argv.includes("--appliquer");
if (!racine) {
  console.error("usage: node renommer_themes_al.js <dossier_racine> [--appliquer]");
  process.exit(2);
}

let fichiers = 0;
let modifs = 0;
for (const dossier of fs.readdirSync(racine).filter((d) => d.startsWith("gce-al-"))) {
  const chemin = path.join(racine, dossier);
  if (!fs.statSync(chemin).isDirectory()) continue;
  for (const nom of fs.readdirSync(chemin).filter((n) => n.endsWith(".json"))) {
    const fichier = path.join(chemin, nom);
    const data = JSON.parse(fs.readFileSync(fichier, "utf8"));
    let touche = false;
    for (const question of data.questions || []) {
      question.themes = (question.themes || []).map((theme) => {
        if (Object.prototype.hasOwnProperty.call(RENOMMAGES, theme)) {
          touche = true;
          modifs += 1;
          console.log(`${dossier}/${nom} q${question.numero}: ${theme} -> ${RENOMMAGES[theme]}`);
          return RENOMMAGES[theme];
        }
        return theme;
      });
    }
    if (touche) {
      fichiers += 1;
      if (appliquer) fs.writeFileSync(fichier, JSON.stringify(data, null, 2), "utf8");
    }
  }
}
console.log(`${modifs} thème(s) à renommer dans ${fichiers} fichier(s)${appliquer ? " (écrit)" : " (simulation)"}`);
