import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Award } from "lucide-react"

import { getReussites } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { nouveauxJalons } from "@/lib/jalonsVus"
import { jouerRetour } from "@/lib/retours"
import { cn } from "@/lib/utils"
import { t, useI18n, type CleI18n } from "@/lib/i18n"

/**
 * Les jalons que ce quiz vient de faire franchir, fêtés tout de suite sur l'écran de résultat : jusqu'ici un jalon ne se
 * voyait qu'en dépliant « Tous mes jalons » dans « Ma progression ». Relit « Mes réussites » après le quiz et compare à
 * ce que l'appareil a déjà montré (voir lib/jalonsVus) ; rien à l'écran quand rien de neuf.
 */
export function JalonsAtteints({ className }: { className?: string }) {
  useI18n()
  const { user } = useAuth()
  const profilId = user?.profil_actif?.id
  const { data, isFetchedAfterMount } = useQuery({
    queryKey: ["reussites"],
    queryFn: ({ signal }) => getReussites(signal),
    enabled: profilId != null,
    // Le quiz vient de changer les faits : la réponse gardée d'une visite précédente ne dit rien de ce qu'il a ouvert.
    staleTime: 0,
    refetchOnMount: "always",
  })
  const [nouveaux, setNouveaux] = useState<string[]>([])

  useEffect(() => {
    if (!data || !isFetchedAfterMount || profilId == null) return
    const codes = nouveauxJalons(profilId, data.jalons.filter((j) => j.obtenu).map((j) => j.code))
    if (codes.length === 0) return
    setNouveaux(codes)
    jouerRetour("palier")
  }, [data, isFetchedAfterMount, profilId])

  if (nouveaux.length === 0) return null
  return (
    <ul className={cn("flex flex-col gap-2", className)} role="status">
      {nouveaux.map((code) => (
        <li key={code} className="animate-quiz-bravo flex items-center gap-3 rounded-2xl border border-gold/50 bg-gold/15 px-4 py-3">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-gold/30 text-gold-text" aria-hidden="true">
            <Award className="size-5" />
          </span>
          <span className="min-w-0 flex-1">
            <span className="block text-xs font-semibold uppercase tracking-wide text-gold-text">{t("jalon.atteint")}</span>
            <span className="block font-display text-base font-semibold">{t(`jalon.${code}` as CleI18n)}</span>
          </span>
          <Link to="/parcours" className="shrink-0 text-xs font-medium text-primary underline-offset-2 hover:underline">
            {t("reussites.tous_jalons")}
          </Link>
        </li>
      ))}
    </ul>
  )
}
