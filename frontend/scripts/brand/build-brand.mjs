/**
 * Génère l'identité visuelle d'EduKora : logos SVG, favicons et icônes d'application.
 *
 * Source unique : le symbole (livre ouvert + mortier + page qui monte) et les couleurs sont définis ICI ;
 * tous les fichiers de public/ et public/brand/ en dérivent. Ne retoucher aucun SVG à la main : modifier
 * ce fichier, puis relancer.
 *
 *   BRAND_TOOLS=<dossier contenant node_modules/sharp et node_modules/opentype.js> node scripts/brand/build-brand.mjs
 *
 * `sharp` et `opentype.js` ne sont volontairement PAS des dépendances du projet : l'identité se
 * régénère rarement, et les fichiers produits sont versionnés. Pour les installer à part :
 *   mkdir /tmp/brand-tools && cd /tmp/brand-tools && npm init -y && npm i sharp opentype.js
 *
 * Le nom et le slogan sont convertis en tracés (polices Fraunces 700 et Work Sans 600, déjà dans le
 * projet) : un SVG chargé via <img> n'a pas accès aux polices de la page, le texte retomberait sinon
 * sur une police système différente selon l'appareil.
 */
import { createRequire } from "node:module"
import { pathToFileURL } from "node:url"
import fs from "node:fs"
import path from "node:path"

const racine = path.resolve(import.meta.dirname, "..", "..")
const outils = process.env.BRAND_TOOLS
if (!outils) throw new Error("BRAND_TOOLS : dossier contenant node_modules/sharp et node_modules/opentype.js")
const depuisOutils = createRequire(path.join(path.resolve(outils), "x.js"))
const importer = async (nom) => (await import(pathToFileURL(depuisOutils.resolve(nom)).href)).default
const sharp = await importer("sharp")
const opentype = await importer("opentype.js")

const police = (paquet, fichier) => {
  const b = fs.readFileSync(path.join(racine, "node_modules", "@fontsource", paquet, "files", fichier))
  return opentype.parse(b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength))
}
const FRAUNCES = police("fraunces", "fraunces-latin-700-normal.woff")
const WORK_SANS = police("work-sans", "work-sans-latin-600-normal.woff")

const PUBLIC = path.join(racine, "public")
const BRAND = path.join(PUBLIC, "brand")
fs.mkdirSync(BRAND, { recursive: true })

const n = (v) => Number(v.toFixed(2))

// ---------------------------------------------------------------------------------------------
// Couleurs. Vert institutionnel #006837, vert profond #0B6623, vert clair #39B54A (charte).
// ---------------------------------------------------------------------------------------------
const PALETTES = {
  // fond clair : mortier + page gauche + nom en vert institutionnel, pages de droite en vert clair
  light: { a: "#006837", b: "#39B54A", c: "#0B6623", nom: "#006837", slogan: "#0B6623", filet: "#39B54A" },
  // fond sombre : les masses passent en blanc cassé, le vert clair reste (contraste > 4.5:1 sur #0d1a13)
  dark: { a: "#F2F8F3", b: "#39B54A", c: "#D5EBD9", nom: "#F2F8F3", slogan: "#BFE5C6", filet: "#39B54A" },
  mono: { a: "#000000", b: "#000000", c: "#000000", nom: "#000000", slogan: "#000000", filet: "#000000" },
  // pastille d'icône d'application : fond #006837, symbole clair
  pastille: { a: "#FFFFFF", b: "#8FDB9B", c: "#E3F4E6", nom: "#FFFFFF", slogan: "#FFFFFF", filet: "#8FDB9B" },
}
const FOND_PASTILLE = "#006837"

// ---------------------------------------------------------------------------------------------
// Symbole. Coordonnées de conception : boîte englobante (8,6)-(120,112), soit 112 x 106.
// Le livre domine ; le mortier est posé au-dessus sans le toucher ; la page de droite se lit en
// deux feuillets qui montent (idée de progression).
// ---------------------------------------------------------------------------------------------
const SYM = { x0: 8, y0: 6, w: 112, h: 106 }

function symbole(p) {
  return [
    // mortier : plateau, bandeau, gland
    `<path fill="${p.a}" d="M64 6 108 22 64 38 20 22Z"/>`,
    `<path fill="${p.c}" d="M36 32 64 42.2 92 32V46C92 51 78 54 64 54S36 51 36 46Z"/>`,
    `<path fill="${p.b}" d="M100.5 25.5h3V42h-3zM99 42h6l1.5 8h-9z"/>`,
    // livre : page gauche, puis deux feuillets à droite
    `<path fill="${p.a}" d="M61 69C52 60 32 56 8 60V100C32 96 52 100 61 112Z"/>`,
    `<path fill="${p.b}" d="M67 69C76 60 96 56 120 60V72C98 68 78 72 67 81Z"/>`,
    `<path fill="${p.b}" d="M67 87C78 78 98 74 120 78V100C96 96 76 100 67 112Z"/>`,
  ].join("")
}

/** Version simplifiée pour 16 à 48 px : pas de gland, plateau plus épais, une seule page à droite. */
const PETIT = { x0: 7, y0: 8, w: 50, h: 50 }
function symbolePetit(p) {
  return [
    `<path fill="${p.a}" d="M32 8 56 17 32 26 8 17Z"/>`,
    `<path fill="${p.c}" d="M17 23.5 32 29 47 23.5V29C47 32 40 34 32 34S17 32 17 29Z"/>`,
    `<path fill="${p.a}" d="M30 41C25 36.5 16 35 7 36.5V54C16 52.5 25 53.5 30 58.5Z"/>`,
    `<path fill="${p.b}" d="M34 41C39 36.5 48 35 57 36.5V54C48 52.5 39 53.5 34 58.5Z"/>`,
  ].join("")
}

// ---------------------------------------------------------------------------------------------
// Texte en tracés.
// ---------------------------------------------------------------------------------------------
/** Sérialisation maison : toPathData d'opentype.js 2.0 écrit « NaN » sur certains segments du K de Fraunces. */
function donneesChemin(chemin) {
  return chemin.commands
    .map((c) => {
      switch (c.type) {
        case "M": case "L": return `${c.type}${n(c.x)} ${n(c.y)}`
        case "Q": return `Q${n(c.x1)} ${n(c.y1)} ${n(c.x)} ${n(c.y)}`
        case "C": return `C${n(c.x1)} ${n(c.y1)} ${n(c.x2)} ${n(c.y2)} ${n(c.x)} ${n(c.y)}`
        case "Z": return "Z"
        default: throw new Error(`commande de chemin inattendue : ${c.type}`)
      }
    })
    .join("")
}

function texte(font, chaine, taille, { interlettre = 0 } = {}) {
  const echelle = taille / font.unitsPerEm
  const glyphes = font.stringToGlyphs(chaine)
  let x = 0
  const morceaux = []
  const b = { x1: Infinity, y1: Infinity, x2: -Infinity, y2: -Infinity }
  glyphes.forEach((g, i) => {
    if (i > 0) x += font.getKerningValue(glyphes[i - 1], g) * echelle
    const chemin = g.getPath(x, 0, taille)
    const gb = chemin.getBoundingBox()
    // les glyphes sans contour (espace) ont une boîte vide : on ne les compte pas
    if (chemin.commands.length > 0) {
      b.x1 = Math.min(b.x1, gb.x1)
      b.y1 = Math.min(b.y1, gb.y1)
      b.x2 = Math.max(b.x2, gb.x2)
      b.y2 = Math.max(b.y2, gb.y2)
      morceaux.push(donneesChemin(chemin))
    }
    x += g.advanceWidth * echelle + (i < glyphes.length - 1 ? interlettre : 0)
  })
  return { d: morceaux.join(""), x1: b.x1, x2: b.x2, y1: b.y1, y2: b.y2, w: b.x2 - b.x1 }
}

const SLOGANS = { fr: "RÉUSSIS TON EXAMEN", en: "PASS YOUR EXAM" }
const NOM = "EduKora"

/** Place un texte : son coin haut-gauche visuel en (x, yHaut). */
function poser(t, fill, x, yHaut) {
  return `<path fill="${fill}" transform="translate(${n(x - t.x1)} ${n(yHaut - t.y1)})" d="${t.d}"/>`
}
/** Idem, mais la ligne de base est en (x, yBase). */
function poserBase(t, fill, x, yBase) {
  return `<path fill="${fill}" transform="translate(${n(x - t.x1)} ${n(yBase)})" d="${t.d}"/>`
}
function placerSymbole(p, x, y, echelle, petit = false) {
  const s = petit ? PETIT : SYM
  const tx = n(x - s.x0 * echelle)
  const ty = n(y - s.y0 * echelle)
  return `<g transform="translate(${tx} ${ty}) scale(${echelle})">${(petit ? symbolePetit : symbole)(p)}</g>`
}
const filet = (p, x, y, l, ep) => `<rect fill="${p.filet}" x="${n(x)}" y="${n(y)}" width="${n(l)}" height="${n(ep)}" rx="${n(ep / 2)}"/>`

function svg(largeur, hauteur, corps, libelle) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${n(largeur)} ${n(hauteur)}" width="${n(largeur)}" height="${n(hauteur)}" role="img" aria-label="${libelle}">${corps}</svg>\n`
}

// ---------------------------------------------------------------------------------------------
// Mises en page. Marge = 4 unités autour de la boîte englobante : jamais de rognage.
// ---------------------------------------------------------------------------------------------
const M = 4
const TAILLE_NOM = 78
const nomGrand = texte(FRAUNCES, NOM, TAILLE_NOM)
const hNom = nomGrand.y2 - nomGrand.y1

function ligneSlogan(langue, taille) {
  return texte(WORK_SANS, SLOGANS[langue], taille, { interlettre: taille * 0.2 })
}

/** Slogan centré entre deux filets, sur une largeur donnée. Retourne le SVG partiel et la hauteur. */
function sloganFiletes(p, langue, xGauche, yHaut, largeur) {
  const taille = 20
  const s = ligneSlogan(langue, taille)
  const hS = s.y2 - s.y1
  const ecart = 12
  const lFilet = Math.max(0, (largeur - s.w) / 2 - ecart)
  const yMilieu = yHaut + hS / 2
  let out = poser(s, p.slogan, xGauche + (largeur - s.w) / 2, yHaut)
  if (lFilet >= 10) {
    out += filet(p, xGauche, yMilieu - 1.5, lFilet, 3)
    out += filet(p, xGauche + largeur - lFilet, yMilieu - 1.5, lFilet, 3)
  }
  return { corps: out, h: hS }
}

const MISES_EN_PAGE = {
  /** Icône à gauche, nom à droite, slogan entre filets dessous. */
  horizontal(p, langue) {
    const ecart = 30
    const gap = 14
    const sl = sloganFiletes(p, langue, 0, 0, nomGrand.w)
    const bloc = hNom + gap + sl.h
    const xNom = M + SYM.w + ecart
    const yBloc = M + (SYM.h - bloc) / 2
    const corps =
      placerSymbole(p, M, M, 1) +
      poser(nomGrand, p.nom, xNom, yBloc) +
      `<g transform="translate(${n(xNom)} ${n(yBloc + hNom + gap)})">${sl.corps}</g>`
    return { w: xNom + nomGrand.w + M, h: SYM.h + 2 * M, corps }
  },
  /** Icône au-dessus, nom et slogan centrés. */
  vertical(p, langue) {
    const gap1 = 24
    const gap2 = 14
    const W = nomGrand.w
    const sl = sloganFiletes(p, langue, 0, 0, W)
    const xSym = M + (W - SYM.w) / 2
    const yNom = M + SYM.h + gap1
    const corps =
      placerSymbole(p, xSym, M, 1) +
      poser(nomGrand, p.nom, M, yNom) +
      `<g transform="translate(${M} ${n(yNom + hNom + gap2)})">${sl.corps}</g>`
    return { w: W + 2 * M, h: yNom + hNom + gap2 + sl.h + M, corps }
  },
  /** Une seule ligne « EduKora — SLOGAN », icône à gauche. */
  horizontalCompact(p, langue) {
    const l = ligneCompacte(p, langue)
    const sym = 0.7
    const hSym = SYM.h * sym
    const ecart = 22
    const yBase = M + hSym / 2 + l.hCap / 2
    const corps =
      placerSymbole(p, M, M, sym) +
      `<g transform="translate(${n(M + SYM.w * sym + ecart)} ${n(yBase)})">${l.corps}</g>`
    return { w: M + SYM.w * sym + ecart + l.w + M, h: hSym + 2 * M, corps }
  },
  /** Icône au-dessus, une seule ligne « EduKora — SLOGAN » dessous. */
  verticalCompact(p, langue) {
    const l = ligneCompacte(p, langue)
    const sym = 0.9
    const W = Math.max(l.w, SYM.w * sym)
    const gap = 20
    const yBase = M + SYM.h * sym + gap + l.hCap
    const corps =
      placerSymbole(p, M + (W - SYM.w * sym) / 2, M, sym) +
      `<g transform="translate(${n(M + (W - l.w) / 2)} ${n(yBase)})">${l.corps}</g>`
    return { w: W + 2 * M, h: yBase + M, corps }
  },
  horizontalMinimal(p) {
    const ecart = 30
    const xNom = M + SYM.w + ecart
    // le centre optique du nom se cale un peu sous le centre du symbole (le poids du livre est en bas)
    const yNom = M + SYM.h / 2 - hNom / 2 + 8
    const corps = placerSymbole(p, M, M, 1) + poser(nomGrand, p.nom, xNom, yNom)
    return { w: xNom + nomGrand.w + M, h: SYM.h + 2 * M, corps }
  },
  verticalMinimal(p) {
    const gap = 24
    const W = nomGrand.w
    const corps =
      placerSymbole(p, M + (W - SYM.w) / 2, M, 1) + poser(nomGrand, p.nom, M, M + SYM.h + gap)
    return { w: W + 2 * M, h: M + SYM.h + gap + hNom + M, corps }
  },
  icone(p) {
    return { w: SYM.w + 2 * M, h: SYM.h + 2 * M, corps: placerSymbole(p, M, M, 1) }
  },
  typographie(p) {
    return { w: nomGrand.w + 2 * M, h: hNom + 2 * M, corps: poser(nomGrand, p.nom, M, M) }
  },
}

/** « EduKora — SLOGAN » ; origine = ligne de base à gauche. hCap = hauteur du nom (jusqu'à l'ascendante). */
function ligneCompacte(p, langue) {
  const nom = texte(FRAUNCES, NOM, 56)
  const s = texte(WORK_SANS, SLOGANS[langue], 15, { interlettre: 3 })
  const ecart = 14
  const tiret = 16
  const x2 = nom.w + ecart
  const x3 = x2 + tiret + ecart
  // le slogan repose sur la même ligne de base que le nom
  const corps =
    poserBase(nom, p.nom, 0, 0) +
    filet(p, x2, -(s.y2 - s.y1) / 2 - 1.5, tiret, 3) +
    poserBase(s, p.slogan, x3, 0)
  return { corps, w: x3 + s.w, hCap: nom.y2 - nom.y1 }
}

// ---------------------------------------------------------------------------------------------
// Fichiers.
// ---------------------------------------------------------------------------------------------
const ecrire = (chemin, contenu) => {
  fs.mkdirSync(path.dirname(chemin), { recursive: true })
  fs.writeFileSync(chemin, contenu)
}

const produits = [] // { fichier, svg, w, h } : pour la rastérisation

function ajouter(fichier, miseEnPage, palette, langue) {
  const m = MISES_EN_PAGE[miseEnPage](PALETTES[palette], langue)
  const libelle = langue ? `${NOM} — ${SLOGANS[langue]}` : NOM
  const contenu = svg(m.w, m.h, m.corps, libelle)
  ecrire(path.join(BRAND, fichier + ".svg"), contenu)
  produits.push({ fichier, svg: contenu, w: m.w, h: m.h })
}

const COULEURS = [["", "light"], ["-dark", "dark"]]
for (const [suffixe, pal] of COULEURS) {
  for (const langue of ["fr", "en"]) {
    ajouter(`logo-horizontal-${langue}${suffixe}`, "horizontal", pal, langue)
    ajouter(`logo-vertical-${langue}${suffixe}`, "vertical", pal, langue)
    ajouter(`logo-horizontal-compact-${langue}${suffixe}`, "horizontalCompact", pal, langue)
    ajouter(`logo-vertical-compact-${langue}${suffixe}`, "verticalCompact", pal, langue)
  }
  ajouter(`logo-horizontal-minimal${suffixe}`, "horizontalMinimal", pal)
  ajouter(`logo-vertical-minimal${suffixe}`, "verticalMinimal", pal)
  ajouter(`icon${suffixe}`, "icone", pal)
  ajouter(`wordmark${suffixe}`, "typographie", pal)
}
for (const langue of ["fr", "en"]) {
  ajouter(`logo-horizontal-${langue}-mono`, "horizontal", "mono", langue)
  ajouter(`logo-vertical-${langue}-mono`, "vertical", "mono", langue)
}
ajouter("logo-horizontal-minimal-mono", "horizontalMinimal", "mono")
ajouter("icon-mono", "icone", "mono")
ajouter("wordmark-mono", "typographie", "mono")

// --- Pastilles d'icône d'application ----------------------------------------------------------
/** Pastille carrée de côté 64 ; symbole centré, occupant `part` du côté. `rayon` : arrondi (0 = plein cadre). */
function pastille({ detail, part, rayon }) {
  const p = PALETTES.pastille
  const s = detail ? SYM : PETIT
  const echelle = (64 * part) / Math.max(s.w, s.h)
  const x = (64 - s.w * echelle) / 2
  const y = (64 - s.h * echelle) / 2 + (detail ? 0 : 0)
  const fond = `<rect width="64" height="64"${rayon ? ` rx="${rayon}"` : ""} fill="${FOND_PASTILLE}"/>`
  return fond + placerSymbole(p, x, y, echelle, !detail)
}
const svgPastille = (opts) => svg(64, 64, pastille(opts), NOM)

// favicon.svg : symbole simplifié, lisible dès 16 px, fond propre (visible sur onglet clair ou sombre)
const faviconSvg = svgPastille({ detail: false, part: 0.84, rayon: 14 })
ecrire(path.join(PUBLIC, "favicon.svg"), faviconSvg)
// icône d'application « any » : symbole complet, coins arrondis
const iconeApp = svgPastille({ detail: true, part: 0.72, rayon: 14 })
ecrire(path.join(BRAND, "app-icon.svg"), iconeApp)
// icône « maskable » : plein cadre, symbole dans la zone de sécurité (cercle de 40 % du côté)
const iconeMasquable = svgPastille({ detail: true, part: 0.54, rayon: 0 })
// Apple : plein cadre (iOS applique son propre arrondi), symbole un peu plus grand que le maskable
const iconeApple = svgPastille({ detail: true, part: 0.68, rayon: 0 })

// ---------------------------------------------------------------------------------------------
// Rastérisation.
// ---------------------------------------------------------------------------------------------
async function png(contenuSvg, largeur, fichier, { fond } = {}) {
  const m = contenuSvg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/)
  const vbW = Number(m[1])
  const vbH = Number(m[2])
  const hauteur = Math.round((largeur * vbH) / vbW)
  let img = sharp(Buffer.from(contenuSvg), { density: Math.ceil((72 * largeur) / vbW) })
    .resize(largeur, hauteur)
  if (fond) img = img.flatten({ background: fond })
  const tampon = await img.png({ compressionLevel: 9, palette: false }).toBuffer()
  ecrire(fichier, tampon)
  return tampon
}

// Logos principaux : PNG transparent (par palette) et sur fond plein, 1600 px de large (2x et plus sur un en-tête d'e-mail)
const FOND_CLAIR = "#FFFFFF"
const FOND_SOMBRE = "#0D1A13"
for (const p of produits) {
  const base = p.fichier
  if (/^logo-(horizontal|vertical)-(fr|en)(-dark)?$/.test(base)) {
    const sombre = base.endsWith("-dark")
    const largeur = base.startsWith("logo-vertical") ? 900 : 1600
    await png(p.svg, largeur, path.join(BRAND, "png", base + ".png"))
    await png(p.svg, largeur, path.join(BRAND, "png", base.replace(/-dark$/, "") + (sombre ? "-on-dark" : "-on-light") + ".png"), {
      fond: sombre ? FOND_SOMBRE : FOND_CLAIR,
    })
  }
}
await png(produits.find((p) => p.fichier === "icon").svg, 512, path.join(BRAND, "png", "icon.png"))
await png(produits.find((p) => p.fichier === "icon-dark").svg, 512, path.join(BRAND, "png", "icon-dark.png"))

// Cartes d'aperçu de lien (Pillow, backend/catalog/apercu_partage.py) : logos sur fond sombre et polices de la marque.
// Pillow ne sait pas lire le SVG : on lui fournit des PNG transparents.
const MARQUE_BACKEND = path.resolve(racine, "..", "backend", "catalog", "static", "catalog", "marque")
await png(produits.find((p) => p.fichier === "logo-horizontal-minimal-dark").svg, 1000, path.join(MARQUE_BACKEND, "logo-minimal.png"))
for (const langue of ["fr", "en"]) {
  await png(produits.find((p) => p.fichier === `logo-horizontal-${langue}-dark`).svg, 1400, path.join(MARQUE_BACKEND, `logo-${langue}.png`))
}
for (const [paquet, fichier] of [
  ["fraunces", "fraunces-latin-700-normal.woff"],
  ["work-sans", "work-sans-latin-500-normal.woff"],
  ["work-sans", "work-sans-latin-600-normal.woff"],
]) {
  fs.copyFileSync(path.join(racine, "node_modules", "@fontsource", paquet, "files", fichier), path.join(MARQUE_BACKEND, fichier))
}

// Favicons et icônes d'application
const p16 = await png(faviconSvg, 16, path.join(PUBLIC, "favicon-16x16.png"))
const p32 = await png(faviconSvg, 32, path.join(PUBLIC, "favicon-32x32.png"))
const p48 = await png(faviconSvg, 48, path.join(BRAND, "png", "favicon-48x48.png"))
await png(iconeApple, 180, path.join(PUBLIC, "apple-touch-icon.png"))
await png(iconeApp, 192, path.join(PUBLIC, "pwa-192.png"))
await png(iconeApp, 512, path.join(PUBLIC, "pwa-512.png"))
await png(iconeMasquable, 512, path.join(PUBLIC, "pwa-maskable-512.png"))

// favicon.ico : trois images PNG (16, 32, 48) dans un conteneur ICO
function ico(images) {
  const entete = Buffer.alloc(6)
  entete.writeUInt16LE(1, 2)
  entete.writeUInt16LE(images.length, 4)
  const entrees = []
  let decalage = 6 + 16 * images.length
  for (const { taille, tampon } of images) {
    const e = Buffer.alloc(16)
    e.writeUInt8(taille, 0)
    e.writeUInt8(taille, 1)
    e.writeUInt16LE(1, 4)
    e.writeUInt16LE(32, 6)
    e.writeUInt32LE(tampon.length, 8)
    e.writeUInt32LE(decalage, 12)
    decalage += tampon.length
    entrees.push(e)
  }
  return Buffer.concat([entete, ...entrees, ...images.map((i) => i.tampon)])
}
ecrire(path.join(PUBLIC, "favicon.ico"), ico([
  { taille: 16, tampon: p16 },
  { taille: 32, tampon: p32 },
  { taille: 48, tampon: p48 },
]))

// Dimensions des SVG de marque, lues par components/Logo.tsx (width/height : pas de décalage de mise en page)
const dimensions = Object.fromEntries(produits.map((p) => [p.fichier, [n(p.w), n(p.h)]]))
ecrire(path.join(racine, "src", "lib", "brandAssets.ts"),
  `// Fichier généré par scripts/brand/build-brand.mjs : ne pas modifier à la main.
/** Largeur et hauteur intrinsèques (unités du viewBox) de chaque SVG de public/brand/. */
export const DIMENSIONS_LOGO: Record<string, [number, number]> = {
${Object.entries(dimensions).map(([k, v]) => `  "${k}": [${v[0]}, ${v[1]}],`).join("\n")}
}
`)

console.log(`${produits.length} SVG de marque, favicons et icônes d'application générés.`)
