import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { History } from "lucide-react"

import { getCoursEpreuves } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { epreuveDetailPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * « Où cette notion est tombée » : les épreuves officielles qui portent un thème du cours. Le cours n'avait aucun chemin
 * vers les sujets, alors que c'est ce qui distingue une révision d'une lecture (audit du 2026-11-25). Sans épreuve, rien
 * n'est affiché.
 */
export function OuTombe({ slug, pays, cursusId, className }: { slug: string; pays: string; cursusId?: number; className?: string }) {
  useI18n()
  const { user } = useAuth()
  // L'examen que l'élève prépare, quand le cours le concerne : sinon les épreuves des examens du cours.
  const cursus = cursusId ?? user?.cursus_prepare?.id
  const { data } = useQuery({
    queryKey: ["cours-ou-tombe", slug, cursus ?? null],
    queryFn: ({ signal }) => getCoursEpreuves(slug, cursus, signal),
  })
  if (!data || data.total === 0) return null
  return (
    <section aria-label={t("ot.titre")} className={cn("rounded-2xl border border-gold/40 bg-gold/[0.07] p-5", className)}>
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-gold-text">
        <History className="size-3.5" aria-hidden="true" />
        {t("ot.titre")}
      </p>
      <p className="mt-1 text-sm">{tn("ot.nombre", data.total)}</p>
      <ul className="mt-3 flex flex-col gap-1.5">
        {data.epreuves.map((epreuve) => (
          <li key={epreuve.slug}>
            <Link to={epreuveDetailPath(pays, epreuve.slug)} className="text-sm font-medium text-primary underline-offset-4 hover:underline">
              {epreuve.title}
            </Link>
          </li>
        ))}
      </ul>
      {data.total > data.epreuves.length && (
        <p className="mt-2 text-xs text-muted-foreground">{tn("ot.autres", data.total - data.epreuves.length)}</p>
      )}
    </section>
  )
}
