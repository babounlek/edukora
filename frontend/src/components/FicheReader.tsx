import { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import { ArrowLeft, ArrowRight, Eye, RotateCcw } from "lucide-react"

import type { EpreuveHeader } from "@/api/types"
import { parseFicheCards } from "@/lib/ficheCards"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { CountryBadge } from "@/components/CountryBadge"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"

interface FicheReaderProps {
  title: string
  header: EpreuveHeader
  markdown: string
}

/**
 * Rendu inline (pas de <p> bloc) pour le titre d'une carte, qui peut contenir du
 * LaTeX ("## Dérivée de $x^n$ ?") - même pattern que ChoixText dans
 * QuizSessionPage.tsx pour le texte d'un choix QCM, même besoin.
 */
function CardQuestion({ texte }: { texte: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
      components={{ p: ({ children }) => <>{children}</> }}
    >
      {texte}
    </ReactMarkdown>
  )
}

/**
 * Lecture d'une fiche (Lesson.lesson_type=FICHE) en format court - une carte
 * recto/verso à la fois plutôt que l'article long-format des corrigés (voir
 * EpreuveReaderPage), pensée pour une révision de 5 minutes entre deux cours. Aucun
 * nouveau modèle de données : les cartes sont dérivées du même content_markdown en
 * découpant par titre de niveau 2 (voir lib/ficheCards.ts).
 */
export function FicheReader({ title, header, markdown }: FicheReaderProps) {
  const [cards] = useState(() => parseFicheCards(markdown))
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)

  if (cards.length === 0) {
    return <p className="text-sm text-muted-foreground">Cette fiche est vide pour le moment.</p>
  }

  const card = cards[index]
  const isFirst = index === 0
  const isLast = index === cards.length - 1

  function goTo(next: number) {
    setIndex(next)
    setRevealed(false)
  }

  return (
    <div>
      <h1 className="font-display text-2xl font-semibold">{title}</h1>
      <div className="mt-3 flex flex-wrap gap-1.5">
        <CountryBadge code={header.pays.code} label={header.pays.label} />
        <Badge variant="secondary">{header.matiere}</Badge>
        {header.serie && <Badge variant="outline">Série {header.serie}</Badge>}
      </div>

      <div className="mt-6 mb-3 flex items-center justify-between">
        <p className="text-sm font-medium text-muted-foreground">
          Carte {index + 1} / {cards.length}
        </p>
        <div className="h-1.5 w-32 overflow-hidden rounded-full bg-secondary">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${((index + 1) / cards.length) * 100}%` }}
          />
        </div>
      </div>

      <Card className="min-h-[220px] animate-fade-up" key={index}>
        <CardContent className="flex flex-col gap-4 pt-6">
          <p className="font-display text-xl font-medium leading-snug">
            <CardQuestion texte={card.question} />
          </p>

          {revealed ? (
            <article className="prose prose-neutral max-w-none border-t border-border pt-4 text-justify dark:prose-invert">
              <EpreuveMarkdown markdown={card.reponse} />
            </article>
          ) : (
            <Button variant="outline" onClick={() => setRevealed(true)} className="w-fit">
              <Eye />
              Voir la réponse
            </Button>
          )}
        </CardContent>
      </Card>

      <div className="mt-5 flex items-center justify-between gap-2">
        <Button variant="ghost" disabled={isFirst} onClick={() => goTo(index - 1)}>
          <ArrowLeft />
          Précédente
        </Button>
        {isLast ? (
          <Button variant="outline" onClick={() => goTo(0)}>
            <RotateCcw />
            Recommencer
          </Button>
        ) : (
          <Button onClick={() => goTo(index + 1)}>
            Suivante
            <ArrowRight />
          </Button>
        )}
      </div>
    </div>
  )
}
