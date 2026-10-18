import { tn, useI18n } from "@/lib/i18n"

/**
 * Titre d'une section d'une longue épreuve (voir sectionsDEpreuve), posé avant sa première question :
 * l'intitulé complet de la section et son nombre de questions. Partagé par la fiche (« Le sujet ») et la
 * page de lecture, qui présentent les mêmes sections.
 */
export function EnTeteSection({ section }: { section: { intitule: string; items: unknown[] } }) {
  useI18n()
  return (
    <p className="-mb-2 mt-4 flex items-baseline gap-2 border-b border-border pb-2 font-display text-sm font-semibold uppercase tracking-wide text-muted-foreground first:mt-0">
      <span className="min-w-0 flex-1 leading-snug sm:truncate" title={section.intitule}>
        {section.intitule}
      </span>
      <span className="shrink-0 text-xs font-normal normal-case tabular-nums">
        {tn("ed.section_questions", section.items.length)}
      </span>
    </p>
  )
}
