import { Link } from "react-router-dom"
import { ChevronRight } from "lucide-react"

import { t, useI18n } from "@/lib/i18n"

export interface MaillonFilAriane {
  libelle: string
  /** Absent pour le dernier maillon : la page courante. */
  to?: string
}

/**
 * Le fil d'Ariane d'une page publique (Accueil > examen > épreuve). Le même fil est balisé BreadcrumbList dans le
 * HTML servi aux moteurs (catalog/prerendu.py) : un balisage doit refléter ce que le visiteur lit à l'écran.
 */
export function FilAriane({ maillons }: { maillons: MaillonFilAriane[] }) {
  useI18n()
  return (
    <nav aria-label={t("ex.fil_ariane")} className="mb-4 flex flex-wrap items-center gap-1 text-sm text-muted-foreground">
      {maillons.map((m, i) => (
        <span key={`${i}-${m.libelle}`} className="flex min-w-0 items-center gap-1">
          {i > 0 && <ChevronRight className="size-3.5 shrink-0" aria-hidden="true" />}
          {m.to ? (
            <Link to={m.to} className="hover:text-primary">
              {m.libelle}
            </Link>
          ) : (
            <span aria-current="page" className="truncate text-foreground">
              {m.libelle}
            </span>
          )}
        </span>
      ))}
    </nav>
  )
}
