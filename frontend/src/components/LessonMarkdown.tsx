import { Children, type ReactNode } from "react"
import { Link } from "react-router-dom"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import remarkGfm from "remark-gfm"
import remarkBreaks from "remark-breaks"
import { ArrowRight } from "lucide-react"

import { Callout } from "@/components/Callout"
import { SolutionToggle } from "@/components/SolutionToggle"
import { extractCallouts, extractSolutionToggles, flattenReactText, italicizeQuotes, normalizeMathBlocks, type CalloutVariant } from "@/lib/markdown"
import { API_BASE_URL } from "@/api/client"

const CALLOUT_SENTINEL = /^\[CALLOUT:(piege|conseil|rappel)\]$/
const SOLUTION_TOGGLE_SENTINEL = /^\[SOLUTION_TOGGLE\]$/
const COURS_LINK_SENTINEL = /^\[COURS_LINK:(\d+)\]$/
const COURS_REF_HREF = /^COURS_REF:(\d+)$/

/** Sépare les enfants "[COURS_LINK:id]" (un par cours associé) du reste du contenu. */
function extractCoursLinks(items: ReactNode[]): { coursIds: number[]; rest: ReactNode[] } {
  const coursIds: number[] = []
  const rest = items.filter((item) => {
    const match = flattenReactText(item).trim().match(COURS_LINK_SENTINEL)
    if (match) {
      coursIds.push(Number(match[1]))
      return false
    }
    return true
  })
  return { coursIds, rest }
}

interface LessonMarkdownProps {
  markdown: string
  /**
   * true en lecture complète authentifiée : un Cours généré depuis cette leçon
   * hérite toujours du même cursus (ou est "toutes séries", encore plus permissif),
   * donc l'abonnement qui donne accès à la leçon donne nécessairement accès au
   * cours - le lien peut pointer directement vers la lecture, sans détour par la
   * fiche. false dans l'aperçu public (non-abonné) : l'accès n'est pas garanti.
   */
  directCoursLinks?: boolean
}

/** Rendu Markdown partagé entre la lecture en ligne complète et l'aperçu public d'une leçon. */
export function LessonMarkdown({ markdown, directCoursLinks = false }: LessonMarkdownProps) {
  const coursHref = (coursId: number) => (directCoursLinks ? `/cours/${coursId}/lire` : `/cours/${coursId}`)

  function MarkdownBlockquote({ children }: { children?: ReactNode }) {
    // react-markdown insère des noeuds texte "\n" entre les <p> enfants : on les
    // ignore pour trouver le vrai premier paragraphe (celui qui porte le marqueur).
    const items = Children.toArray(children).filter((item) => typeof item !== "string" || item.trim() !== "")
    const firstText = flattenReactText(items[0]).trim()

    const calloutMarker = firstText.match(CALLOUT_SENTINEL)
    if (calloutMarker) {
      const { coursIds, rest } = extractCoursLinks(items.slice(1))
      return (
        <Callout variant={calloutMarker[1] as CalloutVariant} coursHrefs={coursIds.map(coursHref)}>
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
   * Marqueur "[COURS_LINK:id]" isolé (pas dans un Rappel de méthode) : filet de
   * sécurité quand le rappel source a été reformulé et ne matche aucun bloc précis
   * (voir Lesson._annotate_cours_links côté backend) - le lien reste visible.
   */
  function MarkdownParagraph({ children }: { children?: ReactNode }) {
    const match = flattenReactText(children).trim().match(COURS_LINK_SENTINEL)
    if (match) {
      return (
        <p className="not-prose my-3">
          <Link
            to={coursHref(Number(match[1]))}
            className="flex w-fit items-center gap-1 rounded-md border border-dashed border-border px-3 py-1.5 text-sm font-medium text-primary hover:underline"
          >
            Voir le cours complet
            <ArrowRight className="size-3.5" />
          </Link>
        </p>
      )
    }
    return <p>{children}</p>
  }

  /**
   * Lien "[label](COURS_REF:id)" - prérequis d'un Cours résolu vers un autre Cours
   * existant (voir Cours._render_section côté backend). Pointe toujours vers la
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
   * Figure d'exercice (voir catalog.models.Figure côté backend) : l'ingestion stocke
   * une URL relative ("/media/figures/...") dans le Markdown, portable entre les
   * environnements - on la résout ici contre l'API plutôt qu'à l'ingestion, pour ne
   * jamais figer un domaine dans le contenu stocké en base.
   */
  function MarkdownImage({ src, alt }: { src?: string; alt?: string }) {
    const resolvedSrc = src?.startsWith("/") ? `${API_BASE_URL}${src}` : src
    return <img src={resolvedSrc} alt={alt ?? ""} loading="lazy" className="rounded-md border border-border" />
  }

  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath, remarkGfm, remarkBreaks]}
      rehypePlugins={[rehypeKatex]}
      components={{ blockquote: MarkdownBlockquote, p: MarkdownParagraph, a: MarkdownAnchor, img: MarkdownImage }}
    >
      {italicizeQuotes(normalizeMathBlocks(extractSolutionToggles(extractCallouts(markdown))))}
    </ReactMarkdown>
  )
}
