import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Layers, ListRestart, NotebookPen, RotateCcw, type LucideIcon } from "lucide-react"

import { getErreurs, listRevisionsDues } from "@/api/endpoints"
import { useCartesDues } from "@/components/CartesDeRevision"
import { useNotesDues } from "@/components/RangeeNotes"
import { cleErreurs } from "@/lib/erreurs"
import { capitaliserTheme, cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

interface File {
  cle: string
  icone: LucideIcon
  titre: string
  detail: string
  vers: string
  geste: string
}

/**
 * « À revoir aujourd'hui » : les quatre files au même endroit. Thèmes dus, cartes, notes et erreurs vivaient chacune sur
 * son écran, sous des mots proches (audit du 2026-11-25, P9). Une ligne par file qui a quelque chose à faire, chacune
 * avec son nombre et son geste ; le bloc se tait quand tout est à jour. Les files elles-mêmes ne changent pas.
 */
export function ARevoirAujourdhui({ cursusId, className }: { cursusId: number; className?: string }) {
  useI18n()
  const { data: revisions } = useQuery({
    queryKey: ["revisions-dues"],
    queryFn: ({ signal }) => listRevisionsDues(signal),
    retry: false,
  })
  const { data: erreurs } = useQuery({
    queryKey: cleErreurs(cursusId),
    queryFn: ({ signal }) => getErreurs(cursusId, signal),
    retry: false,
  })
  const cartes = useCartesDues()?.total ?? 0
  const notes = useNotesDues()?.total ?? 0

  const themes = (Array.isArray(revisions) ? revisions : []).filter((r) => r.cursus === cursusId)
  const files: File[] = []
  if (themes.length > 0) {
    files.push({
      // Sans nombre : la file compte des étiquettes de thème, le compteur « En révision » juste au-dessus des thèmes regroupés
      // (43 contre 37 sur le même compte). Deux nombres pour ce qui se lit comme la même chose vaudraient moins qu'aucun.
      cle: "themes", icone: RotateCcw, titre: t("ar.themes"),
      detail: t("ar.themes_detail", { theme: capitaliserTheme(themes[0].theme), matiere: themes[0].subject_label }),
      vers: `/quiz?cursus=${cursusId}&theme=${themes[0].theme_id}`, geste: t("continuer.reviser"),
    })
  }
  if (cartes > 0) {
    files.push({ cle: "cartes", icone: Layers, titre: tn("cartes.dues", cartes), detail: t("ar.cartes_detail"), vers: "/cartes", geste: t("continuer.reviser") })
  }
  if (notes > 0) {
    files.push({ cle: "notes", icone: NotebookPen, titre: tn("ca.notes_dues", notes), detail: t("ar.notes_detail"), vers: "/carnet?reviser=1", geste: t("ca.reviser_matiere") })
  }
  if (erreurs && erreurs.total > 0) {
    files.push({ cle: "erreurs", icone: ListRestart, titre: tn("erreurs.total", erreurs.total), detail: t("ar.erreurs_detail"), vers: "/erreurs", geste: t("erreurs.voir") })
  }
  if (files.length === 0) return null

  return (
    <section aria-label={t("ar.titre")} className={cn("overflow-hidden rounded-3xl border border-border bg-card shadow-sm", className)}>
      <h2 className="px-5 pt-5 text-xs font-semibold uppercase tracking-[0.18em] text-primary">{t("ar.titre")}</h2>
      <ul className="mt-2 divide-y divide-border">
        {files.map((file) => (
          <li key={file.cle}>
            <Link to={file.vers} className="group flex items-center gap-3 px-5 py-3.5 transition-colors hover:bg-muted/40">
              <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <file.icone className="size-4" aria-hidden="true" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold">{file.titre}</span>
                <span className="line-clamp-2 text-xs text-muted-foreground">{file.detail}</span>
              </span>
              <span className="hidden shrink-0 text-sm font-medium text-primary sm:inline">{file.geste}</span>
              <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
