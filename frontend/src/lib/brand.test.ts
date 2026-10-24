import { existsSync, readFileSync, readdirSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"

import { DIMENSIONS_LOGO } from "@/lib/brandAssets"

/**
 * L'identité visuelle est générée (scripts/brand/build-brand.mjs) puis référencée à la main dans index.html,
 * vite.config.ts et components/Logo.tsx : ces tests attrapent un fichier manquant ou un chemin qui a dérivé.
 */
const racine = resolve(__dirname, "../..")
const publicDir = resolve(racine, "public")
const lire = (chemin: string) => readFileSync(resolve(racine, chemin), "utf-8")

describe("SVG de marque", () => {
  const fichiers = readdirSync(resolve(publicDir, "brand")).filter((f) => f.endsWith(".svg"))

  it("chaque entrée de la table de dimensions a son fichier, et inversement (sauf l'icône d'application)", () => {
    const attendus = Object.keys(DIMENSIONS_LOGO).map((nom) => `${nom}.svg`).sort()
    expect(fichiers.filter((f) => f !== "app-icon.svg").sort()).toEqual(attendus)
  })

  it.each(fichiers)("%s : viewBox cohérent avec la table, sans script ni ressource distante", (fichier) => {
    const svg = readFileSync(resolve(publicDir, "brand", fichier), "utf-8")
    const m = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/)
    expect(m).not.toBeNull()
    const dims = DIMENSIONS_LOGO[fichier.replace(/\.svg$/, "")]
    if (dims) expect([Number(m![1]), Number(m![2])]).toEqual(dims)
    expect(svg).not.toMatch(/<script|<image|<foreignObject|xlink:href|url\(|@import/i)
    // le seul « http » toléré est l'espace de noms XML
    expect(svg.replace('xmlns="http://www.w3.org/2000/svg"', "")).not.toMatch(/https?:/)
    // chemins sans valeur invalide (régression : toPathData d'opentype.js écrivait NaN)
    expect(svg).not.toMatch(/NaN|undefined|Infinity/)
  })

  it("le nom de la marque est exact dans les libellés, les slogans officiels dans les logos complets", () => {
    for (const fichier of fichiers) {
      const svg = readFileSync(resolve(publicDir, "brand", fichier), "utf-8")
      expect(svg).not.toMatch(/Edukora|EduKamer|Edukamer/)
    }
    expect(readFileSync(resolve(publicDir, "brand/logo-horizontal-fr.svg"), "utf-8")).toContain("EduKora — RÉUSSIS TON EXAMEN")
    expect(readFileSync(resolve(publicDir, "brand/logo-horizontal-en.svg"), "utf-8")).toContain("EduKora — PASS YOUR EXAM")
  })
})

describe("favicons et icônes d'application", () => {
  const html = lire("index.html")
  const liens = [...html.matchAll(/<link rel="(?:icon|apple-touch-icon)"[^>]*href="([^"]+)"/g)].map((m) => m[1])

  it("index.html référence tous les formats attendus", () => {
    expect(liens).toEqual(expect.arrayContaining([
      "/favicon.ico", "/favicon-32x32.png", "/favicon-16x16.png", "/favicon.svg", "/apple-touch-icon.png",
    ]))
  })

  it.each(liens)("%s existe dans public/", (href) => {
    expect(existsSync(resolve(publicDir, href.slice(1)))).toBe(true)
  })

  it("le manifeste (vite.config.ts) et le service worker pointent vers des fichiers réels", () => {
    const sources = lire("vite.config.ts") + lire("public/push-sw.js")
    const icones = [...sources.matchAll(/["'](\/pwa-[\w-]+\.png)["']/g)].map((m) => m[1])
    expect(icones.length).toBeGreaterThanOrEqual(3)
    for (const icone of new Set(icones)) expect(existsSync(resolve(publicDir, icone.slice(1)))).toBe(true)
  })

  it("favicon.ico contient les tailles 16, 32 et 48", () => {
    const ico = readFileSync(resolve(publicDir, "favicon.ico"))
    expect(ico.readUInt16LE(2)).toBe(1)
    const n = ico.readUInt16LE(4)
    const tailles = Array.from({ length: n }, (_, i) => ico.readUInt8(6 + 16 * i))
    expect(tailles).toEqual([16, 32, 48])
  })
})
