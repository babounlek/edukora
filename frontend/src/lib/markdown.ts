/**
 * remark-math n'identifie un bloc `$$...$$` multi-lignes comme maths "display" que
 * s'il est isolé par des lignes vides ET que les délimiteurs `$$` sont seuls sur leur
 * ligne, comme un fence de code (```). Le Markdown produit par correction-experte ne
 * garantit ni l'un ni l'autre : `$$\begin{array}{...}` sur la même ligne, ou
 * `\end{array}$$ --- ### Question suivante` collé en fin de bloc. Dans les deux cas
 * remark-math perd la ligne d'ouverture ou de fermeture, et KaTeX échoue ensuite avec
 * des erreurs du type "\hline valid only within array environment" (le `\begin{array}`
 * ayant été amputé). Vérifié empiriquement avec le vrai moteur KaTeX.
 *
 * On reformate donc chaque bloc `$$...$$` multi-lignes en fence propre : `$$` seul sur
 * sa ligne, contenu, `$$` seul sur sa ligne, le tout isolé par des lignes vides.
 * Les formules sur une seule ligne (`$$x=1$$`) sont déjà gérées correctement et ne
 * sont pas modifiées.
 */
export function normalizeMathBlocks(markdown: string): string {
  return mapOutsideCode(markdown, (text) =>
    text.replace(/(^[ \t]*(?:>[ \t]?)+)?\$\$([\s\S]*?)\$\$/gm, (match, quotePrefix: string | undefined, inner: string) => {
      if (!match.includes("\n")) return match

      if (quotePrefix) {
        // Bloc display DANS une citation (solution masquée, encadré) : chaque ligne
        // regénérée garde son préfixe ">" - sinon le bloc sortait de la citation et les
        // ">" restants finissaient dans la formule (KaTeX : "\hline valid only within array").
        const prefix = quotePrefix.trimEnd()
        const body = inner
          .split("\n")
          .map((line) => line.replace(/^[ \t]*(?:>[ \t]?)+/, ""))
          .join("\n")
          .trim()
          .split("\n")
          .map((line) => (line ? `${prefix} ${line}` : prefix))
        return [prefix, `${prefix} $$`, ...body, `${prefix} $$`, `${prefix} `].join("\n")
      }

      return `\n\n$$\n${inner.trim()}\n$$\n\n`
    }),
  )
    .replace(/\n{3,}/g, "\n\n")
    .trim()
}

const CODE_SEGMENT_RE = /(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]+`)/g

/**
 * Applique `transform` uniquement au texte HORS code (bloc fencé ou span inline). Sans ça,
 * du code PHP comme `$c=$$a;` ou `echo " ";` était pris pour une formule display `$$...$$`
 * ou un guillemet à mettre en italique : le code affiché s'en trouvait corrompu, voire
 * le rendu en erreur KaTeX.
 */
function mapOutsideCode(markdown: string, transform: (text: string) => string): string {
  return markdown
    .split(CODE_SEGMENT_RE)
    .map((segment, index) => (index % 2 === 1 ? segment : transform(segment)))
    .join("")
}

const MATH_SPAN_RE = /\$\$[\s\S]+?\$\$|\$[^$\n]+?\$/g
const GUILLEMET_RE = /«([^»\n*$]+)»/g
const STRAIGHT_QUOTE_RE = /"([^"\n*$]+)"/g

/**
 * Met en italique tout texte entre guillemets (« » ou "..."), guillemets compris -
 * convention typographique demandée pour les citations dans les corrigés/cours.
 * Découpe d'abord le texte en alternant segments hors-maths / maths (même motif que
 * $...$ utilisé par remark-math) pour ne jamais toucher un guillemet qui tomberait
 * dans une formule LaTeX ; seuls les segments hors-maths sont transformés.
 */
export function italicizeQuotes(markdown: string): string {
  return mapOutsideCode(markdown, (text) =>
    text
      .split(new RegExp(`(${MATH_SPAN_RE.source})`, "g"))
      .map((chunk, index) => {
        if (index % 2 === 1) return chunk
        return chunk
          .replace(GUILLEMET_RE, (_match, inner: string) => `*«${inner}»*`)
          .replace(STRAIGHT_QUOTE_RE, (_match, inner: string) => `*"${inner}"*`)
      })
      .join(""),
  )
}

/** Aplati un arbre de nœuds React (tel que reçu par un composant react-markdown) en texte brut. */
export function flattenReactText(node: unknown): string {
  if (typeof node === "string" || typeof node === "number") return String(node)
  if (Array.isArray(node)) return node.map(flattenReactText).join("")
  if (node && typeof node === "object" && "props" in node) {
    return flattenReactText((node as { props: { children?: unknown } }).props.children)
  }
  return ""
}

export type CalloutVariant = "piege" | "conseil" | "rappel"

// "Rappel de m[eé]thode" plutôt que "Rappel de méthode" littéral : SKILL.md exige
// l'accent (et avertit noir sur blanc qu'un titre différent perd la mise en valeur
// silencieusement), mais correction-experte génère très régulièrement "methode" sans
// accent en pratique - sur tout le corpus déjà ingéré vérifié, systématiquement. Sans
// cette tolérance, le bloc reste un `### ...` brut au lieu de l'encadré coloré prévu,
// exactement l'avertissement du skill mais côté génération plutôt que plateforme.
// Chaque motif reste ancré (^...$) pour ne matcher que l'intitulé entier, pas une
// sous-chaîne.
const CALLOUT_TITLE_PATTERNS: [pattern: string, variant: CalloutVariant][] = [
  ["Piège à éviter", "piege"],
  ["Conseil", "conseil"],
  ["Rappel de m[eé]thode", "rappel"],
]

const TITLES_ALTERNATION = CALLOUT_TITLE_PATTERNS.map(([pattern]) => pattern).join("|")

function resolveCalloutVariant(title: string): CalloutVariant | undefined {
  return CALLOUT_TITLE_PATTERNS.find(([pattern]) => new RegExp(`^${pattern}$`).test(title))?.[1]
}

/**
 * correction-experte doit désormais utiliser un titre `### Piège à éviter` / `### Conseil` /
 * `### Rappel de méthode` (voir SKILL.md), mais du contenu déjà en base utilise encore
 * l'ancien format `**Titre.** texte...`. On convertit les deux formes en citation Markdown
 * avec un marqueur `[CALLOUT:variant]` sur sa propre ligne, que <Callout> sait reconnaître -
 * ainsi le corps reste du Markdown normalement interprété (gras, maths, etc.), contrairement
 * à un bloc de code qui afficherait tout en texte brut.
 */
export function extractCallouts(markdown: string): string {
  // Le corps s'arrête normalement à la première ligne vide (un "### Piège à éviter"/
  // "Conseil"/"Rappel de méthode" n'est en pratique jamais qu'un seul paragraphe) -
  // sauf quand cette ligne vide est immédiatement suivie d'un marqueur
  // "[COURS_LINK:...]" (voir _annotate_cours_links côté backend, qui l'injecte comme
  // paragraphe séparé juste après un Rappel de méthode) : il faut alors continuer pour
  // l'inclure dans le même blockquote, sans quoi il atterrit hors du Callout, en texte
  // brut non stylé (constaté en prod). Sans le `(?!\[COURS_LINK:)`, un corps
  // multi-paragraphe engloutirait aussi tout texte qui suit sans son propre titre
  // "###" - notamment l'énoncé de la question suivante, qui n'est séparé du corrigé
  // précédent que par une ligne vide (voir _render_question_corrige) : régression
  // vérifiée et exclue explicitement ici.
  const headingRe = new RegExp(
    `^###[ \\t]*(${TITLES_ALTERNATION})[ \\t]*\\n+([\\s\\S]*?)(?=\\n{2,}(?!\\[COURS_LINK:)|\\n#{1,6}[ \\t]|\\n---|\\n*(?![\\s\\S]))`,
    "gm",
  )
  markdown = markdown.replace(headingRe, (_match, title: string, body: string) => {
    const variant = resolveCalloutVariant(title)
    const quoted = body.trim().split("\n").map((line) => (line ? `> ${line}` : ">")).join("\n")
    return `> [CALLOUT:${variant}]\n>\n${quoted}\n\n`
  })

  const paragraphRe = new RegExp(`^\\*\\*(${TITLES_ALTERNATION})\\.?\\*\\*[ \\t]*(.*)$`, "gm")
  markdown = markdown.replace(paragraphRe, (_match, title: string, rest: string) => {
    const variant = resolveCalloutVariant(title)
    return `> [CALLOUT:${variant}]\n>\n> ${rest}`
  })

  return markdown
}

// `(?![\s\S])` = fin du texte : avec le flag `m`, un `$` s'arrêtait à la fin de la PREMIÈRE
// ligne du corps, laissant le reste d'une solution multi-ligne (fence de code, calcul)
// visible en clair, hors du bouton, et cassant le fence.
const SOLUTION_HEADING_RE = /^###[ \t]*Solution[ \t]*\n+([\s\S]*?)(?=\n#{1,6}[ \t]|\n---|\n*(?![\s\S]))/gm

/**
 * Un exercice d'auto-évaluation d'un Cours ("### Solution", voir Cours._render_section)
 * doit rester masqué tant que l'élève n'a pas cherché par lui-même. Converti en citation
 * Markdown avec un marqueur `[SOLUTION_TOGGLE]`, sur le même principe que les callouts,
 * pour que <SolutionToggle> puisse l'afficher derrière un bouton "Voir la solution".
 */
export function extractSolutionToggles(markdown: string): string {
  return markdown.replace(SOLUTION_HEADING_RE, (_match, body: string) => {
    const quoted = body.trim().split("\n").map((line) => (line ? `> ${line}` : ">")).join("\n")
    return `> [SOLUTION_TOGGLE]\n>\n${quoted}\n\n`
  })
}
