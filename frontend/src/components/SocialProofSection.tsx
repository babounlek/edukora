import { useEffect, useState } from "react"
import { Quote, Star } from "lucide-react"

import { listTemoignages } from "@/api/endpoints"
import type { Temoignage } from "@/api/types"
import { t, useI18n } from "@/lib/i18n"

/** En dessous, la section ne s'affiche pas : un avis seul sur la page fait plus douter qu'aucun. */
export const SEUIL_AVIS_AFFICHES = 3

/**
 * Preuve sociale publique (page d'accueil catalogue, /tarifs) - voir l'audit UX, reco 8.3.
 * Disparaît silencieusement tant que SEUIL_AVIS_AFFICHES avis ne sont pas publiés depuis l'admin
 * (jamais générés ni fabriqués - voir catalog.models.Temoignage et catalog.avis).
 */
export function SocialProofSection({ fournis }: {
  /** Les témoignages déjà reçus par la page (l'accueil les a avec ses chiffres, voir getAccueilVitrine) : la section ne les
   * redemande pas. `null` tant que la page les attend. Sans cette prop, la section les charge elle-même (/tarifs). */
  fournis?: Temoignage[] | null
} = {}) {
  const { langue } = useI18n()
  const [charges, setCharges] = useState<Temoignage[]>([])
  const autonome = fournis === undefined

  useEffect(() => {
    if (!autonome) return
    listTemoignages(langue).then(setCharges).catch(() => {})
  }, [autonome, langue])

  const temoignages = autonome ? charges : (fournis ?? [])

  if (temoignages.length < SEUIL_AVIS_AFFICHES) return null

  return (
    <section aria-labelledby="avis-publies-titre" className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
      <h2 id="avis-publies-titre" className="mb-4 font-display text-xl font-semibold">
        {t("avis.section_titre")}
      </h2>
      <div className="grid gap-4 sm:grid-cols-3">
        {temoignages.slice(0, 3).map((temoignage) => (
          <div key={temoignage.id} className="rounded-xl border border-border p-5">
            <Quote className="mb-2 size-5 text-primary/60" />
            <p className="text-sm text-foreground">{temoignage.contenu}</p>
            <div className="mt-3 flex items-center justify-between gap-2">
              <p className="text-sm font-medium">
                {temoignage.auteur_nom}
                {temoignage.auteur_description && (
                  <span className="font-normal text-muted-foreground"> · {temoignage.auteur_description}</span>
                )}
              </p>
              {temoignage.note !== null && (
                <div className="flex shrink-0 items-center gap-0.5" role="img" aria-label={t("temoignage.note", { n: temoignage.note })}>
                  {Array.from({ length: temoignage.note }).map((_, index) => (
                    <Star key={index} aria-hidden="true" className="size-3.5 fill-gold text-gold-text" />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
