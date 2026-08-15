import { useEffect, useState } from "react"
import { Quote, Star } from "lucide-react"

import { listTemoignages } from "@/api/endpoints"
import type { Temoignage } from "@/api/types"

/**
 * Preuve sociale publique (page d'accueil catalogue) - voir l'audit UX, reco 8.3.
 * Disparaît silencieusement tant qu'aucun témoignage n'est publié depuis l'admin
 * (jamais générés ni fabriqués - voir catalog.models.Temoignage).
 */
export function SocialProofSection() {
  const [temoignages, setTemoignages] = useState<Temoignage[]>([])

  useEffect(() => {
    listTemoignages().then(setTemoignages).catch(() => {})
  }, [])

  const hasTemoignages = temoignages.length > 0

  if (!hasTemoignages) return null

  return (
    <section className="mx-auto max-w-5xl animate-fade-up px-4 py-10 sm:px-6">
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
                <div className="flex shrink-0 items-center gap-0.5">
                  {Array.from({ length: temoignage.note }).map((_, index) => (
                    <Star key={index} className="size-3.5 fill-gold text-gold" />
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
