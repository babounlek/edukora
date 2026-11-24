import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import remarkBreaks from "remark-breaks"
import rehypeKatex from "rehype-katex"

import { cn } from "@/lib/utils"

/**
 * Le texte d'une note, avec ses formules : « $a^2+b^2=c^2$ » s'affiche en formule, comme dans les cours. Ni HTML brut ni
 * liens : c'est un texte écrit par l'élève, rien d'autre que du texte et des maths ne doit s'y rendre.
 */
export function NoteTexte({ texte, className }: { texte: string; className?: string }) {
  return (
    <div className={cn("text-sm leading-relaxed [&_p]:my-0 [&_.katex-display]:my-2 [&_.katex-display]:overflow-x-auto [&_ul]:my-1 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:my-1 [&_ol]:list-decimal [&_ol]:pl-5 [&_strong]:font-semibold", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkMath, remarkBreaks]}
        rehypePlugins={[rehypeKatex]}
        disallowedElements={["a", "img"]}
        unwrapDisallowed
      >
        {texte}
      </ReactMarkdown>
    </div>
  )
}
