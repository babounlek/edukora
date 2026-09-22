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
  // Le corps s'arrête à la PREMIÈRE ligne vide après le titre - SKILL.md l'impose sans
  // exception ("Le bloc `### Rappel de méthode` reste UN SEUL paragraphe, sans aucune
  // ligne blanche à l'intérieur" ; même règle pour Piège/Conseil) : le principe général
  // (2-4 lignes) est le SEUL contenu de l'encadré coloré, la résolution chiffrée qui
  // suit (point 2 du template, "Corrigé détaillé étape par étape") n'a jamais sa place
  // dedans - même repère que _RAPPEL_BLOCK_RE côté backend, qui ne retient lui aussi que
  // le premier paragraphe pour décider où injecter [COURS_LINK:...].
  //
  // Historique : entre le 2026-08-31 et le 2026-09-02, cette frontière avait été
  // repoussée à la prochaine "vraie" rupture (titre/---/nouvelle sous-question) pour
  // absorber les rappels à plusieurs paragraphes déjà présents en base (~39% du corpus
  // à l'époque, jusqu'à toucher la quasi-totalité des exercices ensuite) plutôt que de
  // les tronquer visuellement. Effet de bord non anticipé : l'encadré "Rappel de
  // méthode" finissait par engloutir la résolution ENTIÈRE (démonstration chiffrée,
  // formules $$...$$, réponse finale en gras), rendant rappel et correction
  // indiscernables l'un de l'autre - signalé en prod (mathematiques-probatoire-c-et-e-
  // 2008, mathematiques-probatoire-a-2023-blanc). Revenu à la règle d'origine du skill :
  // un rappel qui déborde sur un second paragraphe n'est plus mis en valeur au-delà du
  // premier, celui-ci redevenant un texte de corrigé normal, visuellement distinct de
  // l'encadré - exactement la séparation attendue, sans toucher au contenu déjà en base.
  //
  // Un marqueur "[COURS_LINK:...]" NE compte PAS comme fin de bloc (voir
  // _annotate_cours_links côté backend, qui l'injecte comme paragraphe séparé juste
  // après le premier paragraphe d'un Rappel de méthode) : il doit rester dans le même
  // blockquote, sans quoi il atterrit hors du Callout en texte brut non stylé. Plusieurs
  // marqueurs consécutifs sont possibles (un même bloc peut correspondre à plusieurs
  // rappels fusionnés, voir sa docstring) : chacun repousse la frontière d'autant.
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

const BARE_COURS_LINK_LINE_RE = /^\[COURS_LINK:([a-zA-Z0-9_-]+)\]$/gm

/**
 * Regroupe une pile de marqueurs `[COURS_LINK:slug]` orphelins consécutifs (2 ou plus)
 * en un seul marqueur `[COURS_LINK_GROUP:slug1,slug2,...]`, à appeler après
 * extractCallouts - un marqueur encore présent à ce stade, hors blockquote, est
 * forcément orphelin (voir `append_unmatched` côté backend,
 * catalog.rendering.annotate_cours_links) : le rappel de méthode source n'a pas pu être
 * apparié à un bloc précis dans le corrigé, et son lien est ajouté tel quel en fin
 * d'exercice plutôt que d'être perdu. Un exercice qui compte beaucoup de rappels non
 * appariés (un "Problème" à plusieurs parties, notamment) en accumule plusieurs à la
 * suite - chacun rendu isolément comme son propre bouton "Voir le cours complet" pleine
 * largeur, ils s'empilaient verticalement, strictement identiques à l'oeil (même texte,
 * même icône, seule la cible du lien diffère) : à l'affichage, on n'y voit qu'un même
 * lien répété plusieurs fois de suite plutôt que plusieurs cours réellement distincts
 * (signalé en prod sur mathematiques-probatoire-c-2004, scan corpus du 2026-09-02 : 29
 * exercices touchés, toutes matières confondues). Un seul marqueur orphelin reste
 * inchangé (voir COURS_LINK_SENTINEL côté EpreuveMarkdown.tsx) : rien à regrouper, et un
 * encadré à un seul lien resterait identique aux deux rendus.
 */
export function groupBareCoursLinks(markdown: string): string {
  // Le dernier marqueur d'une pile n'est pas forcément suivi d'un saut de ligne (fin de
  // chaîne, voir annotate_cours_links côté backend qui n'ajoute rien après le dernier
  // slug) : capturé à part, sans "\n+" obligatoire après lui, contrairement aux
  // marqueurs précédents de la même pile.
  return markdown.replace(
    /(?:^\[COURS_LINK:[a-zA-Z0-9_-]+\]\n+){1,}^\[COURS_LINK:[a-zA-Z0-9_-]+\]/gm,
    (block) => {
      const slugs = Array.from(block.matchAll(BARE_COURS_LINK_LINE_RE), (m) => m[1])
      return `[COURS_LINK_GROUP:${slugs.join(",")}]`
    },
  )
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
