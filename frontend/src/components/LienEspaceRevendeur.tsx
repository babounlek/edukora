import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Store } from "lucide-react"

import { ApiError } from "@/api/client"
import { getEspaceRevendeur } from "@/api/endpoints"
import { t, useI18n } from "@/lib/i18n"

/**
 * Raccourci vers l'espace revendeur, visible seulement d'un compte rattaché à une fiche revendeur : le serveur
 * répond 404 aux autres, et la carte n'apparaît alors pas. Même clé de requête que la page elle-même, donc le
 * tableau de bord s'ouvre sur des chiffres déjà chargés.
 */
export function LienEspaceRevendeur() {
  useI18n()
  const espace = useQuery({
    queryKey: ["revendeur", "moi"],
    queryFn: ({ signal }) => getEspaceRevendeur(signal),
    retry: (nombre, err) => !(err instanceof ApiError && err.status < 500) && nombre < 2,
  })
  if (!espace.data) return null

  return (
    <Link
      to="/espace-revendeur"
      className="flex items-center gap-3 rounded-2xl border border-border bg-card p-4 transition-colors hover:bg-muted/40"
    >
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
        <Store className="size-4.5" aria-hidden="true" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-sm font-semibold">{t("rev.lien_compte")}</span>
        <span className="block text-xs text-muted-foreground">{t("rev.lien_compte_aide")}</span>
      </span>
      <ArrowRight className="size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
    </Link>
  )
}
