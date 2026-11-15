import { useQuery } from "@tanstack/react-query"
import { GraduationCap } from "lucide-react"

import { getNoteEstimee } from "@/api/endpoints"
import type { MatiereNoteEstimee } from "@/api/types"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

function Ligne({ m }: { m: MatiereNoteEstimee }) {
  return (
    <li className="rounded-xl border border-border bg-card px-4 py-3">
      <div className="flex flex-wrap items-baseline justify-between gap-x-3">
        <p className="text-sm font-semibold">{m.subject_label}</p>
        {m.statut === "estimee" && (
          <p className="font-display text-lg font-semibold tabular-nums">{t("bulletin.fourchette", { bas: m.bas ?? 0, haut: m.haut ?? 0 })}</p>
        )}
      </div>
      {m.statut === "estimee" && (
        <>
          {!m.calibre && <p className="text-xs text-muted-foreground">{t("bulletin.a_confirmer")}</p>}
          {m.themes_rentables && m.themes_rentables.length > 0 && (
            <p className="mt-2 text-xs text-muted-foreground">
              <span className="font-medium text-foreground">{t("bulletin.rentables")}</span>{" "}
              {m.themes_rentables.map((x) => `${x.theme} (+${String(x.points).replace(".", ",")})`).join(" · ")}
            </p>
          )}
        </>
      )}
      {m.statut === "pas_assez" && (
        <p className="text-xs text-muted-foreground">
          {(m.couverture_pct ?? 0) < (m.couverture_min_pct ?? 0)
            ? t("bulletin.plus_de_themes")
            : tn("bulletin.encore_reponses", Math.max(1, (m.reponses_min ?? 0) - (m.reponses ?? 0)))}
        </p>
      )}
      {m.statut === "sans_donnees" && <p className="text-xs text-muted-foreground">{t("bulletin.sans_donnees")}</p>}
    </li>
  )
}

/**
 * Bulletin prévisionnel (audit produit 2026-11-13, R15) : une fourchette de note par matière, jamais un chiffre exact. Rien ne
 * s'affiche tant que le serveur ne l'active pas : la méthode attend la relecture d'un enseignant, et seul le personnel la voit
 * d'ici là (avec un bandeau qui le dit).
 */
export function BulletinPrevisionnel({ className }: { className?: string }) {
  useI18n()
  const { data } = useQuery({ queryKey: ["note-estimee"], queryFn: ({ signal }) => getNoteEstimee(signal), retry: false })
  if (!data || !data.actif) return null
  const matieres = data.matieres ?? []
  if (matieres.length === 0) return null

  return (
    <section className={cn("rounded-2xl border border-border bg-card/60 p-5", className)} aria-label={t("bulletin.titre")}>
      {data.relecture && (
        <p className="mb-3 rounded-lg bg-gold/15 px-3 py-2 text-xs font-medium text-gold-text">{t("bulletin.relecture")}</p>
      )}
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        <GraduationCap className="size-3.5" aria-hidden="true" />
        {t("bulletin.titre")}
      </p>
      {data.moyenne && (
        <p className="mt-2 font-display text-2xl font-semibold tabular-nums">
          {t("bulletin.moyenne", { bas: data.moyenne.bas, haut: data.moyenne.haut })}
          <span className="ml-2 text-sm font-normal text-muted-foreground">
            {t("bulletin.sur_matieres", { n: data.moyenne.matieres, total: data.moyenne.total })}
          </span>
        </p>
      )}
      <p className="mt-1 text-xs text-muted-foreground">{t("bulletin.avertissement")}</p>
      <ul className="mt-4 flex flex-col gap-2">
        {matieres.map((m) => (
          <Ligne key={m.subject_id} m={m} />
        ))}
      </ul>
    </section>
  )
}
