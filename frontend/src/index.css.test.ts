/// <reference types="node" />
// Seul fichier de src/ qui tourne réellement sous Node (lit index.css depuis le
// disque, voir plus bas) plutôt que dans un navigateur - tsconfig.app.json exclut
// délibérément les types Node du reste de l'app (jamais besoin d'y accéder aux API
// disque/process), donc la référence ci-dessus reste locale à ce seul fichier au lieu
// d'élargir "types" pour tout le projet.
import { readFileSync } from "fs"
import { resolve } from "path"
import { describe, expect, it } from "vitest"

/**
 * Vérifie le contraste WCAG AA (4.5:1, texte normal) de chaque paire fond/texte de
 * badge (voir components/ui/badge.tsx) - checklist de la reco 6.1 de l'audit UX,
 * rendue permanente plutôt qu'un audit ponctuel qui se démode au premier ajustement
 * de palette. Un badge affiche du texte en text-xs (~12px) : jamais assez grand pour
 * bénéficier du seuil allégé (3:1) réservé au "texte large" par WCAG.
 */

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  s /= 100
  l /= 100
  const k = (n: number) => (n + h / 30) % 12
  const a = s * Math.min(l, 1 - l)
  const f = (n: number) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)))
  return [f(0), f(8), f(4)]
}

function relativeLuminance([r, g, b]: [number, number, number]): number {
  const channel = (c: number) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
  const [rl, gl, bl] = [r, g, b].map(channel)
  return 0.2126 * rl + 0.7152 * gl + 0.0722 * bl
}

function contrastRatio(a: [number, number, number], b: [number, number, number]): number {
  const la = relativeLuminance(hslToRgb(...a))
  const lb = relativeLuminance(hslToRgb(...b))
  const lighter = Math.max(la, lb)
  const darker = Math.min(la, lb)
  return (lighter + 0.05) / (darker + 0.05)
}

const css = readFileSync(resolve(__dirname, "index.css"), "utf-8")

function extractHsl(block: "root" | "dark", varName: string): [number, number, number] {
  const blockMatch = css.match(block === "root" ? /:root\s*{([^}]*)}/ : /\.dark\s*{([^}]*)}/)
  if (!blockMatch) throw new Error(`Bloc "${block}" introuvable dans index.css`)
  const varMatch = blockMatch[1].match(new RegExp(`--${varName}:\\s*hsl\\(([\\d.]+)\\s+([\\d.]+)%\\s+([\\d.]+)%\\)`))
  if (!varMatch) throw new Error(`Variable --${varName} introuvable dans le bloc "${block}"`)
  return [Number(varMatch[1]), Number(varMatch[2]), Number(varMatch[3])]
}

// Chaque variante de badge.tsx qui pose du texte directement sur un fond de couleur -
// pas "outline" (texte sur transparent, hérite du contraste texte/page normal).
const BADGE_PAIRS: [string, string][] = [
  ["primary", "primary-foreground"],
  ["secondary", "secondary-foreground"],
  ["success", "success-foreground"],
  ["warning", "warning-foreground"],
  ["gold", "gold-foreground"],
  ["destructive", "destructive-foreground"],
]

describe.each(["root", "dark"] as const)("Contraste des badges - thème %s", (block) => {
  it.each(BADGE_PAIRS)("%s / %s atteint au moins 4.5:1", (bg, fg) => {
    const ratio = contrastRatio(extractHsl(block, bg), extractHsl(block, fg))
    expect(ratio).toBeGreaterThanOrEqual(4.5)
  })
})
