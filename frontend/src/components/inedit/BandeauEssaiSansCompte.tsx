import { Link, useLocation } from "react-router-dom"
import { UserPlus } from "lucide-react"

import { t, useI18n } from "@/lib/i18n"
import { useEssaiSansCompte } from "@/lib/useEssaiSansCompte"

/**
 * Rappel discret pour qui essaie une inédite gratuite SANS compte (voir lib/invite.ts) : sa copie n'est gardée que sur
 * cet appareil. Un lien pour créer le compte, qui la reprend ; l'élève revient ici ensuite. Rien pour un connecté.
 */
export function BandeauEssaiSansCompte({ className }: { className?: string }) {
  useI18n()
  const location = useLocation()
  const essai = useEssaiSansCompte()
  if (!essai) return null
  return (
    <p className={`flex flex-wrap items-center gap-x-2 gap-y-1 rounded-lg border border-border bg-muted/50 px-3 py-2 text-sm text-muted-foreground ${className ?? ""}`}>
      <UserPlus className="size-4 shrink-0" aria-hidden="true" />
      <span>{t("ine.invite_bandeau")}</span>
      <Link
        to="/connexion"
        state={{ from: `${location.pathname}${location.search}`, intent: t("ine.invite_intent") }}
        className="font-medium text-primary underline-offset-2 hover:underline"
      >
        {t("ine.invite_creer")}
      </Link>
    </p>
  )
}
