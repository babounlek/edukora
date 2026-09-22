// @vitest-environment node
//
// Ce fichier tourne en environnement Node pur, jamais jsdom (le défaut du projet,
// voir vitest.config.ts) : katex.renderToString a un chemin de détection de
// fonctionnalités qui se comporte différemment sous un DOM simulé - constaté ici en
// pratique, une même entrée invalide ($\foobarbaz{x}$) ne produit AUCUNE erreur sous
// jsdom alors qu'elle produit bien un noeud "katex-error" sous Node pur, faussant tout
// l'audit par de faux négatifs silencieux. Un test de contenu textuel n'a de toute
// façon aucun besoin d'un DOM.
import { existsSync, readFileSync } from "node:fs"

import { describe, expect, it } from "vitest"
import { unified } from "unified"
import remarkParse from "remark-parse"
import remarkMath from "remark-math"
import remarkGfm from "remark-gfm"
import remarkBreaks from "remark-breaks"
import remarkRehype from "remark-rehype"
import rehypeRaw from "rehype-raw"
import rehypeKatex from "rehype-katex"

import {
  extractCallouts,
  extractSolutionToggles,
  italicizeQuotes,
  normalizeMathBlocks,
} from "./markdown"

/**
 * Audit corpus-entier du rendu KaTeX/Markdown - compétence `audit-qualite-rendu`,
 * étape 2 (voir sa SKILL.md). Prend en entrée le JSON produit par la commande Django
 * `dump_rendering_corpus` (un enregistrement par champ markdown réellement affiché à
 * l'élève) et fait tourner le VRAI moteur de rendu (remark-math/remark-gfm/
 * remark-breaks/rehype-raw/rehype-katex, même chaîne que EpreuveMarkdown.tsx) sur
 * chacun -
 * jamais une vérification par regex seule, qui a déjà historiquement manqué de vrais
 * bugs (voir la note "how to apply" de project_epreuve_reader_latex_rendering_fixes
 * dans la mémoire du projet).
 *
 * Ignoré (un seul test factice, toujours vert) si AUDIT_RENDU_DUMP n'est pas défini -
 * pour que `npm test` reste propre par défaut ; ce fichier n'est un vrai audit que
 * lancé explicitement avec un dump frais.
 */

interface CorpusRecord {
  model: string
  pk: number
  ref: string
  field: string
  pipeline: "full" | "bare"
  markdown: string
}

interface HastNode {
  type?: string
  properties?: {
    className?: unknown
    title?: unknown
    style?: unknown
    mathcolor?: unknown
  }
  children?: HastNode[]
}

/**
 * "#cc0000" est la couleur d'erreur canonique de KaTeX - le seul signal fiable, pas la
 * classe "katex-error" seule. Vérifié empiriquement : une exception de parsing réelle
 * (ex. `\dfrac{1}` - argument manquant) produit bien un span.katex-error, MAIS une
 * commande totalement inconnue (ex. `\hlinex`, un contrôle indéfini) ne lève RIEN et ne
 * porte AUCUNE classe "katex-error" - KaTeX la rend silencieusement en `mstyle
 * mathcolor="#cc0000"` / `style="color:#cc0000"`, sans jamais passer par le mécanisme
 * try/catch de rehype-katex. Ignorer ce second cas aurait fait passer sous silence
 * exactement la classe de bug déjà documentée dans la mémoire du projet (repérée à
 * l'origine par lecture humaine du rendu, jamais par un check automatisé).
 */
const KATEX_ERROR_COLOR = "#cc0000"

/** Même ordre que le rendu réel (EpreuveMarkdown.tsx) - le seul consommateur du pipeline "full". */
function preprocessFull(markdown: string): string {
  return italicizeQuotes(
    normalizeMathBlocks(
      extractSolutionToggles(
        extractCallouts(markdown),
      ),
    ),
  )
}

function findKatexErrors(node: HastNode, out: string[] = []): string[] {
  const { className, title, style, mathcolor } = node.properties ?? {}

  const isThrownError =
    Array.isArray(className) && className.includes("katex-error")

  const isLenientErrorColor =
    (typeof style === "string" && style.includes(KATEX_ERROR_COLOR)) ||
    mathcolor === KATEX_ERROR_COLOR

  if (isThrownError) {
    out.push(String(title ?? "erreur KaTeX (titre indisponible)"))
  } else if (isLenientErrorColor) {
    out.push(
      `KaTeX a rendu ce noeud en rouge d'erreur (${KATEX_ERROR_COLOR}) sans lever d'exception - commande probablement inconnue/mal formée`,
    )
  }

  for (const child of node.children ?? []) {
    findKatexErrors(child, out)
  }

  return out
}

/**
 * Scanner de parité des délimiteurs $ / $$ (voir le "Eleventh check" de
 * feedback_correction_experte_consistency dans la mémoire du projet) : n'attrape rien
 * que le vrai moteur n'attraperait pas déjà (un déséquilibre corrompt aussi le rendu
 * KaTeX en aval), mais localise en une passe LE caractère fautif au lieu de laisser
 * deviner lequel, parmi N erreurs KaTeX en cascade sans rapport apparent, est la vraie
 * cause racine.
 */
function findDelimiterImbalance(markdown: string): string | null {
  const stack: string[] = []
  let i = 0

  while (i < markdown.length) {
    const char = markdown[i]

    if (char === "\\") {
      i += 2
      continue
    }

    // Un span de code (`` `...` ``, fence de longueur quelconque) est tokenisé comme
    // du code avant que remark-math ne considère le moindre "$" : tout "$" à
    // l'intérieur - ex. `` `$B$10` `` ou `` `$` `` pour documenter un symbole en
    // toutes lettres - est donc invisible au vrai moteur et ne doit pas compter ici
    // non plus (faux positif constaté sur Cours#5017/5009 "bureautique" : "$" isolé
    // dans `` `$` `` faisait déborder la pile alors que le rendu réel est correct).
    // Suit la règle CommonMark : la fin d'un span est la PROCHAINE suite de backticks
    // de la MÊME longueur ; sans fermeture, les backticks sont du texte littéral.
    if (char === "`") {
      let fenceLen = 0
      while (markdown[i + fenceLen] === "`") fenceLen += 1
      const fence = "`".repeat(fenceLen)
      const closeIdx = markdown.indexOf(fence, i + fenceLen)
      i = closeIdx === -1 ? i + fenceLen : closeIdx + fenceLen
      continue
    }

    if (char === "$") {
      const token = markdown[i + 1] === "$" ? "$$" : "$"

      if (stack.length > 0 && stack[stack.length - 1] === token) {
        stack.pop()
      } else {
        stack.push(token)
      }

      i += token.length
      continue
    }

    i += 1
  }

  if (stack.length === 0) return null

  return `délimiteur(s) non refermé(s) : ${stack.join(", ")} (position finale de la pile)`
}

function buildProcessor(pipeline: CorpusRecord["pipeline"]) {
  const processor = unified()
    .use(remarkParse)
    .use(remarkMath)

  if (pipeline === "full") {
    processor.use(remarkGfm).use(remarkBreaks)
  }

  return processor
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeKatex)
}

function auditRecord(
  record: CorpusRecord,
  processor: ReturnType<typeof buildProcessor>,
): string[] {
  const issues: string[] = []

  const delimiterIssue = findDelimiterImbalance(record.markdown)

  if (delimiterIssue) {
    issues.push(delimiterIssue)
  }

  const source =
    record.pipeline === "full"
      ? preprocessFull(record.markdown)
      : record.markdown

  try {
    const tree = processor.runSync(
      processor.parse(source),
    ) as unknown as HastNode

    issues.push(...findKatexErrors(tree))
  } catch (error) {
    // Un throw (plutôt qu'un noeud katex-error) planterait la VRAIE page côté élève,
    // pas seulement une formule cassée - à distinguer clairement dans le rapport.
    issues.push(
      `le pipeline a levé une exception (page réelle probablement en écran blanc) : ${(error as Error).message}`,
    )
  }

  return issues
}

const dumpPath = process.env.AUDIT_RENDU_DUMP

describe("audit qualité de rendu", () => {
  if (!dumpPath) {
    it(
      "ignoré - définir AUDIT_RENDU_DUMP=<chemin vers le dump JSON> pour lancer un audit réel",
      () => {
        expect(true).toBe(true)
      },
    )

    return
  }

  if (!existsSync(dumpPath)) {
    throw new Error(
      `AUDIT_RENDU_DUMP=${dumpPath} introuvable - lancer d'abord la commande Django dump_rendering_corpus.`,
    )
  }

  const records: CorpusRecord[] = JSON.parse(
    readFileSync(dumpPath, "utf-8"),
  )

  const processors = {
    full: buildProcessor("full"),
    bare: buildProcessor("bare"),
  }

  for (const record of records) {
    if (!record.markdown.trim()) continue

    it(
      `${record.model}#${record.pk} ${record.ref} [${record.field}/${record.pipeline}]`,
      () => {
        const issues = auditRecord(
          record,
          processors[record.pipeline],
        )

        expect(issues).toEqual([])
      },
    )
  }
})