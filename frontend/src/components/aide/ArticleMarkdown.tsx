import { Link } from "react-router-dom"
import ReactMarkdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"

import { remplirGabarits } from "@/lib/aide/texte"

/**
 * Le rendu d'un article d'aide : du Markdown simple (titres, listes, gras, liens, tableaux), rien de plus.
 * Volontairement SANS le moteur des épreuves (formules KaTeX, encadrés, solutions) : il pèse plus de 600 Ko et l'aide
 * doit rester légère pour les connexions lentes. Les liens qui commencent par « / » restent dans l'application.
 */
const COMPOSANTS: Components = {
  h2: ({ children }) => <h2 className="mt-8 font-display text-xl font-semibold tracking-tight first:mt-0">{children}</h2>,
  h3: ({ children }) => <h3 className="mt-6 font-display text-lg font-semibold">{children}</h3>,
  p: ({ children }) => <p className="mt-3 leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="mt-3 list-disc space-y-1.5 pl-5 leading-relaxed marker:text-gold">{children}</ul>,
  ol: ({ children }) => <ol className="mt-3 list-decimal space-y-1.5 pl-5 leading-relaxed marker:font-semibold marker:text-gold">{children}</ol>,
  li: ({ children }) => <li className="pl-1">{children}</li>,
  strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
  code: ({ children }) => <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.9em]">{children}</code>,
  hr: () => <hr className="my-6 border-border" />,
  table: ({ children }) => (
    <div className="mt-4 overflow-x-auto">
      <table className="w-full border-collapse text-sm">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border-b border-border px-3 py-2 text-left font-semibold">{children}</th>,
  td: ({ children }) => <td className="border-b border-border px-3 py-2 align-top">{children}</td>,
  a: ({ href = "", children }) => {
    const classe = "font-medium text-primary underline underline-offset-2 hover:text-primary/80"
    if (href.startsWith("/")) return <Link to={href} className={classe}>{children}</Link>
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className={classe}>
        {children}
      </a>
    )
  },
}

export function ArticleMarkdown({ corps }: { corps: string }) {
  return (
    <div className="text-base text-foreground/90">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={COMPOSANTS}>
        {remplirGabarits(corps)}
      </ReactMarkdown>
    </div>
  )
}
