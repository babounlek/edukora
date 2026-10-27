import { t, useI18n } from "@/lib/i18n"

const SECTIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] as const

/**
 * Texte de la charte du revendeur (docs-revendeurs/CHARTE-REVENDEUR.md), en dix rubriques. Sa version
 * (CHARTE_VERSION côté serveur) est celle que le candidat accepte : la changer demande de relire ce texte.
 */
export function CharteRevendeur({ version }: { version: string }) {
  useI18n()
  return (
    <div className="rounded-xl border border-border bg-muted/30 p-4 text-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {t("cand.charte_version", { version })}
      </p>
      <div className="mt-3 flex max-h-72 flex-col gap-3 overflow-y-auto pr-1">
        {SECTIONS.map((n) => (
          <section key={n}>
            <h3 className="font-semibold">{t(`charte.${n}_titre`)}</h3>
            <p className="mt-0.5 text-muted-foreground">{t(`charte.${n}_texte`)}</p>
          </section>
        ))}
      </div>
    </div>
  )
}
