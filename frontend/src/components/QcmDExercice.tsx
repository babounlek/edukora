import { useState } from "react"
import ReactMarkdown from "react-markdown"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import remarkMath from "remark-math"
import { Check, ListChecks, X } from "lucide-react"

import type { QcmEpreuve } from "@/api/types"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/** Le texte d'un choix, en ligne (il peut porter du LaTeX). */
function Choix({ texte }: { texte: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeRaw, rehypeKatex]}
      components={{ p: ({ children }) => <>{children}</> }}
    >
      {texte}
    </ReactMarkdown>
  )
}

/**
 * « Réponds en cliquant » (audit produit 2026-11-13, R19/D3) : les QCM d'une annale, cliquables avant de lire le corrigé. Jusqu'ici
 * la bonne lettre n'était qu'un texte sous la question. Un choix fait ne se change plus (on se corrige en lisant le corrigé) ; le
 * score ne sert qu'à l'élève : rien n'est enregistré, ni points ni maîtrise, comme la lecture seule de l'épreuve.
 */
export function QcmDExercice({ qcm, defaultOpen = false }: { qcm: QcmEpreuve[]; defaultOpen?: boolean }) {
  useI18n()
  const [ouvert, setOuvert] = useState(defaultOpen)
  const [choisis, setChoisis] = useState<Record<number, string>>({})
  if (qcm.length === 0) return null

  const repondus = Object.keys(choisis).length
  const justes = qcm.filter((q) => choisis[q.id] === q.reponse_correcte).length

  if (!ouvert) {
    return (
      <Button
        type="button"
        variant="outline"
        className="mt-5 min-h-11 rounded-full border-primary/30 bg-primary/5 text-primary hover:bg-primary/10"
        onClick={() => setOuvert(true)}
      >
        <ListChecks className="size-4" aria-hidden="true" />
        {tn("qcm.repondre", qcm.length)}
      </Button>
    )
  }

  return (
    <section className="mt-5 rounded-2xl border border-primary/25 bg-primary/5 p-4 sm:p-5" aria-label={t("qcm.titre")}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
          <ListChecks className="size-3.5" aria-hidden="true" />
          {t("qcm.titre")}
        </p>
        <p className="text-xs tabular-nums text-muted-foreground" aria-live="polite">
          {t("qcm.score", { justes, repondus })}
        </p>
      </div>
      <ol className="mt-4 flex flex-col gap-6">
        {qcm.map((q) => {
          const choix = choisis[q.id]
          const repondu = choix !== undefined
          return (
            <li key={q.id}>
              <div className="prose prose-neutral max-w-none text-sm dark:prose-invert">
                <EpreuveMarkdown markdown={q.enonce_markdown} />
              </div>
              <ul className="mt-2 flex flex-col gap-1.5">
                {q.choix.map((c) => {
                  const lettre = c.lettre.toLowerCase()
                  const estBonne = lettre === q.reponse_correcte
                  const estChoisi = choix === lettre
                  return (
                    <li key={lettre}>
                      <button
                        type="button"
                        disabled={repondu}
                        aria-pressed={estChoisi}
                        onClick={() => setChoisis((prec) => ({ ...prec, [q.id]: lettre }))}
                        className={cn(
                          "flex min-h-11 w-full items-start gap-3 rounded-xl border px-3 py-2 text-left text-sm transition-colors",
                          !repondu && "border-border bg-card hover:border-primary/50",
                          repondu && estBonne && "border-success/60 bg-success/10",
                          repondu && estChoisi && !estBonne && "border-destructive/60 bg-destructive/10",
                          repondu && !estBonne && !estChoisi && "border-border bg-card opacity-70",
                        )}
                      >
                        <span className="mt-0.5 font-semibold uppercase tabular-nums">{lettre}</span>
                        <span className="min-w-0 flex-1">
                          <Choix texte={c.texte} />
                        </span>
                        {repondu && estBonne && <Check className="mt-0.5 size-4 shrink-0 text-success" aria-label={t("qcm.bonne_reponse")} />}
                        {repondu && estChoisi && !estBonne && <X className="mt-0.5 size-4 shrink-0 text-destructive" aria-label={t("qcm.mauvaise_reponse")} />}
                      </button>
                    </li>
                  )
                })}
              </ul>
            </li>
          )
        })}
      </ol>
      {repondus === qcm.length && (
        <p className="mt-4 text-sm font-medium">{t("qcm.fini", { justes, total: qcm.length })}</p>
      )}
    </section>
  )
}
