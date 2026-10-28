// Poids des modules par chunk (taille « rendue » avant minification fine) : sert à repérer ce qui
// alourdit le chunk d'entrée. Usage : cd frontend && node ../scripts/perf/analyse-bundle.mjs [outDir]
// Construit dans un dossier temporaire (jamais dans dist/), sans toucher à la configuration du projet.
import path from "node:path"
import os from "node:os"
import fs from "node:fs"
import { createRequire } from "node:module"
import { pathToFileURL } from "node:url"

// Le script vit hors de frontend/ : on résout Vite depuis le dossier courant (frontend/).
const requireDepuisFrontend = createRequire(path.join(process.cwd(), "package.json"))
const { build } = await import(pathToFileURL(requireDepuisFrontend.resolve("vite")).href)

const outDir = process.argv[2] ?? fs.mkdtempSync(path.join(os.tmpdir(), "edukora-bundle-"))
const rapport = []
const sonde = {
  name: "sonde-chunks",
  generateBundle(_, bundle) {
    for (const [nom, c] of Object.entries(bundle)) {
      if (c.type !== "chunk") continue
      const modules = Object.entries(c.modules).map(([id, m]) => [id, m.renderedLength]).sort((a, b) => b[1] - a[1])
      rapport.push({ nom, taille: c.code.length, entree: c.isEntry, imports: c.imports, modules: modules.slice(0, 14), nbModules: modules.length })
    }
  },
}
process.env.VITE_DISABLE_PWA = "1"
await build({ logLevel: "error", build: { outDir, emptyOutDir: true }, plugins: [sonde] })
rapport.sort((a, b) => b.taille - a.taille)
for (const c of rapport.slice(0, Number(process.env.TOP ?? 6))) {
  console.log(`\n${c.nom}  ${(c.taille / 1024).toFixed(0)} Ko  ${c.entree ? "[ENTRÉE]" : ""}  (${c.nbModules} modules)`)
  for (const [id, n] of c.modules) console.log("   ", String(n).padStart(8), id.split(path.sep).join("/").replace(/.*node_modules\//, "nm:").replace(/.*\/src\//, "src/"))
}
console.log("\ndossier:", outDir)
