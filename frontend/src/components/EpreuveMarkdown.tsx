import {
  Children,
  createContext,
  memo,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from "react"
import { Link } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import remarkGfm from "remark-gfm"
import remarkBreaks from "remark-breaks"

import { t } from "@/lib/i18n"

import { Callout } from "@/components/Callout"
import { LienCours } from "@/components/LienCours"
import { SolutionToggle } from "@/components/SolutionToggle"
import { extractCallouts, extractSolutionToggles, flattenReactText, groupBareCoursLinks, italicizeQuotes, normalizeMathBlocks, type CalloutVariant } from "@/lib/markdown"
import { API_BASE_URL } from "@/api/client"

const CALLOUT_SENTINEL = /^\[CALLOUT:(piege|conseil|rappel)\]$/
const SOLUTION_TOGGLE_SENTINEL = /^\[SOLUTION_TOGGLE\]$/
// Le marqueur porte le slug du Cours depuis son introduction ; un id numérique reste
// possible sur du contenu compilé avant cette bascule (voir VisibleQuerySet.par_slug_ou_id
// côté backend, qui accepte encore les deux en lecture).
const COURS_LINK_SENTINEL = /^\[COURS_LINK:([a-zA-Z0-9_-]+)\]$/
// Voir groupBareCoursLinks (lib/markdown) : plusieurs marqueurs orphelins consécutifs
// regroupés en un seul, pour un encadré compact plutôt qu'une pile de boutons identiques.
const COURS_LINK_GROUP_SENTINEL = /^\[COURS_LINK_GROUP:([a-zA-Z0-9_,-]+)\]$/
const COURS_REF_HREF = /^COURS_REF:([a-zA-Z0-9_-]+)$/

/** Sépare les enfants "[COURS_LINK:slug]" (un par cours associé) du reste du contenu. */
function extractCoursLinks(items: ReactNode[]): { coursSlugs: string[]; rest: ReactNode[] } {
  const coursSlugs: string[] = []
  const rest = items.filter((item) => {
    const match = flattenReactText(item).trim().match(COURS_LINK_SENTINEL)
    if (match) {
      coursSlugs.push(match[1])
      return false
    }
    return true
  })
  return { coursSlugs, rest }
}

interface EpreuveMarkdownProps {
  markdown: string
  /**
   * true en lecture complète authentifiée : un Cours généré depuis cette épreuve
   * hérite toujours du même cursus (ou est "toutes séries", encore plus permissif),
   * donc l'abonnement qui donne accès à l'épreuve donne nécessairement accès au
   * cours - le lien peut pointer directement vers la lecture, sans détour par la
   * fiche. false dans l'aperçu public (non-abonné) : l'accès n'est pas garanti.
   */
  directCoursLinks?: boolean
}

// Voir DirectCoursLinksContext : lu par les rendus ci-dessous, qui vivent au niveau du module.
const DirectCoursLinksContext = createContext(false)

function useCoursHref() {
  const direct = useContext(DirectCoursLinksContext)
  return (coursSlug: string) => (direct ? `/cours/${coursSlug}/lire` : `/cours/${coursSlug}`)
}

// Les rendus ci-dessous sont définis ICI, au niveau du module, et non dans le corps de
// EpreuveMarkdown : redéfinis à chaque rendu, React les voyait comme de nouveaux types de
// composant et remontait tout l'arbre à chaque « Compris » ou signet - le Markdown et le KaTeX
// étaient reparsés, les corrigés (SolutionToggle) ouverts se refermaient et les figures
// clignotaient. `directCoursLinks` leur parvient par le contexte plutôt que par fermeture.

function MarkdownBlockquote({ children }: { children?: ReactNode }) {
  const coursHref = useCoursHref()
  // react-markdown insère des noeuds texte "\n" entre les <p> enfants : on les
  // ignore pour trouver le vrai premier paragraphe (celui qui porte le marqueur).
  const items = Children.toArray(children).filter((item) => typeof item !== "string" || item.trim() !== "")
  const firstText = flattenReactText(items[0]).trim()

  const calloutMarker = firstText.match(CALLOUT_SENTINEL)
  if (calloutMarker) {
    const { coursSlugs, rest } = extractCoursLinks(items.slice(1))
    return (
      <Callout variant={calloutMarker[1] as CalloutVariant} coursHrefs={coursSlugs.map(coursHref)} coursSlugs={coursSlugs}>
        {rest}
      </Callout>
    )
  }

  if (SOLUTION_TOGGLE_SENTINEL.test(firstText)) {
    return <SolutionToggle>{items.slice(1)}</SolutionToggle>
  }

  return <blockquote>{children}</blockquote>
}

/**
 * Marqueur "[COURS_LINK:slug]" isolé (pas dans un Rappel de méthode) : filet de
 * sécurité quand le rappel source a été reformulé et ne matche aucun bloc précis
 * (voir _annotate_cours_links côté backend) - le lien reste visible.
 *
 * "[COURS_LINK_GROUP:slug1,slug2,...]" : plusieurs marqueurs de ce type consécutifs
 * (voir groupBareCoursLinks, lib/markdown) - un exercice avec beaucoup de rappels non
 * appariés en accumule plusieurs à la suite, rendus dans un seul encadré plutôt
 * qu'empilés en boutons identiques.
 */
function MarkdownParagraph({ children }: { children?: ReactNode }) {
  const coursHref = useCoursHref()
  const text = flattenReactText(children).trim()

  const groupMatch = text.match(COURS_LINK_GROUP_SENTINEL)
  if (groupMatch) {
    const slugs = groupMatch[1].split(",")
    return (
      <div className="not-prose my-3 flex flex-col items-start gap-1.5 rounded-md border border-dashed border-border p-3">
        <p className="text-sm font-medium text-muted-foreground">{t("ed.cours_lies")}</p>
        {slugs.map((slug) => (
          <LienCours
            key={slug}
            slug={slug}
            to={coursHref(slug)}
            label={t("ed.voir_cours")}
            titreSeul
            className="flex items-center gap-1 text-sm font-medium text-primary hover:underline"
          />
        ))}
      </div>
    )
  }

  const match = text.match(COURS_LINK_SENTINEL)
  if (match) {
    return (
      <p className="not-prose my-3">
        <LienCours
          slug={match[1]}
          to={coursHref(match[1])}
          label={t("ed.voir_cours")}
          className="flex w-fit items-center gap-1 rounded-md border border-dashed border-border px-3 py-1.5 text-sm font-medium text-primary hover:underline"
        />
      </p>
    )
  }
  return <p>{children}</p>
}

/**
 * Lien "[label](COURS_REF:slug)" - prérequis d'un Cours résolu vers un autre Cours
 * existant (voir _render_cours_section côté backend). Pointe toujours vers la
 * fiche du cours, jamais directement vers la lecture : contrairement au cours
 * généré depuis l'épreuve qu'on est en train de lire, l'accès à un cours
 * référencé en prérequis n'est pas garanti par le même abonnement.
 */
function MarkdownAnchor({ href, children }: { href?: string; children?: ReactNode }) {
  const match = href?.match(COURS_REF_HREF)
  if (match) {
    return (
      <Link to={`/cours/${match[1]}`} className="font-medium text-primary hover:underline">
        {children}
      </Link>
    )
  }
  return (
    <a href={href} target="_blank" rel="noreferrer">
      {children}
    </a>
  )
}

/**
 * Tableau Markdown (remark-gfm). Entièrement auto-suffisant - grille complète,
 * padding et fond d'en-tête posés ici, jamais délégués à `prose` : ce composant est
 * rendu sous des contextes typographiques très différents (article `prose` d'un
 * corrigé, encadrés de Cours, cartes compactes en `prose-sm`), et son propre
 * `not-prose` neutralise `.prose table/th/td` dans tous ces cas - le tableau a donc
 * exactement la même grille partout. Bordures sur chaque cellule (border-collapse) :
 * même grille que les PDF (voir sujet_pdf_template.html).
 *
 * Ce `not-prose`-ci est légitime parce que rien sous cet élément n'attend la
 * typographie de prose. Un `not-prose` posé sur un conteneur qui, lui, contient un
 * `prose` est en revanche un piège : les sélecteurs du plugin se terminent tous par
 * `:not(:where([class~="not-prose"], [class~="not-prose"] *))`, donc un `prose`
 * imbriqué ne réactive jamais rien (voir CoursRegleBox).
 */
function MarkdownTable({ children }: { children?: ReactNode }) {
  const defilant = useRef<HTMLDivElement>(null)
  const [suiteADroite, setSuiteADroite] = useState(false)
  const mesurer = useCallback(() => {
    const el = defilant.current
    if (el) setSuiteADroite(el.scrollWidth - el.clientWidth - el.scrollLeft > 1)
  }, [])
  useEffect(() => {
    const el = defilant.current
    if (!el) return
    mesurer()
    if (typeof ResizeObserver === "undefined") return
    const observateur = new ResizeObserver(mesurer)
    observateur.observe(el)
    if (el.firstElementChild) observateur.observe(el.firstElementChild)
    return () => observateur.disconnect()
  }, [mesurer])

  // Un tableau plus large que l'écran (tableau de variations sur mobile) défile dans son cadre, mais rien
  // ne le disait : la dernière colonne (+∞) semblait simplement absente. Une ombre sur le bord droit signale
  // qu'il y a une suite, et disparaît une fois le bout atteint.
  return (
    <div className="not-prose relative my-4">
      <div ref={defilant} onScroll={mesurer} className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">{children}</table>
      </div>
      {suiteADroite && (
        <span
          aria-hidden="true"
          data-indice-defilement="droite"
          className="pointer-events-none absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-foreground/20 to-transparent"
        />
      )}
    </div>
  )
}

// `style` porte l'alignement de colonne du Markdown GFM (:---:) : on le laisse
// primer sur le text-left par défaut, plus lisible que le centrage pour des
// cellules rédigées.
function MarkdownTableHeaderCell({ children, style }: { children?: ReactNode; style?: CSSProperties }) {
  return (
    <th style={style} className="border border-border bg-muted/60 px-3 py-2 text-left font-semibold">
      {children}
    </th>
  )
}

function MarkdownTableCell({ children, style }: { children?: ReactNode; style?: CSSProperties }) {
  return (
    <td style={style} className="border border-border px-3 py-2 text-left align-top">
      {children}
    </td>
  )
}

/**
 * Figure d'exercice (voir catalog.models.Figure côté backend) : l'ingestion stocke
 * une URL relative ("/media/figures/...") dans le Markdown, portable entre les
 * environnements - on la résout ici contre l'API plutôt qu'à l'ingestion, pour ne
 * jamais figer un domaine dans le contenu stocké en base.
 */
function MarkdownImage({ src, alt }: { src?: string; alt?: string }) {
  const resolvedSrc = src?.startsWith("/") ? `${API_BASE_URL}${src}` : src
  return <img src={resolvedSrc} alt={alt?.trim() ? alt : t("ed.figure")} loading="lazy" className="rounded-md border border-border" />
}

const MARKDOWN_COMPONENTS = {
  blockquote: MarkdownBlockquote,
  p: MarkdownParagraph,
  a: MarkdownAnchor,
  img: MarkdownImage,
  table: MarkdownTable,
  th: MarkdownTableHeaderCell,
  td: MarkdownTableCell,
}

const REMARK_PLUGINS = [remarkMath, remarkGfm, remarkBreaks]
const REHYPE_PLUGINS = [rehypeRaw, rehypeKatex]

/** Rendu Markdown partagé entre la lecture en ligne complète et l'aperçu public d'une épreuve. */
function EpreuveMarkdownBase({ markdown, directCoursLinks = false }: EpreuveMarkdownProps) {
  // Le prétraitement est coûteux sur un long corrigé : refait seulement si le texte change.
  const source = useMemo(
    () => italicizeQuotes(normalizeMathBlocks(extractSolutionToggles(groupBareCoursLinks(extractCallouts(markdown))))),
    [markdown],
  )

  return (
    <DirectCoursLinksContext.Provider value={directCoursLinks}>
      <ReactMarkdown remarkPlugins={REMARK_PLUGINS} rehypePlugins={REHYPE_PLUGINS} components={MARKDOWN_COMPONENTS}>
        {source}
      </ReactMarkdown>
    </DirectCoursLinksContext.Provider>
  )
}

export const EpreuveMarkdown = memo(EpreuveMarkdownBase)
