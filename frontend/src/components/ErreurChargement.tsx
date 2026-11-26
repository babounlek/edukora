import { RefreshCw } from "lucide-react"

import { ApiError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

interface ErreurChargementProps {
  /** Ce qui n'a pas pu être chargé, ex. « tes accès » - sert à la phrase par défaut. */
  objet?: string
  /** Remplace la phrase par défaut. */
  message?: string
  onRetry?: () => void
  /** Variante compacte, pour un bloc au milieu d'une page plutôt qu'une page entière. */
  compact?: boolean
  className?: string
}

/**
 * Le message du serveur, seulement quand il est écrit pour l'élève : une réponse métier (400, 409...). Jamais un 404
 * de Django en anglais (« No QuizSession matches the given query. »), un refus d'accès générique, ni « Erreur API
 * (502) » : la phrase par défaut d'ErreurChargement dit mieux qu'il faut réessayer.
 */
export function messagePourEleve(erreur: unknown): string | undefined {
  if (!(erreur instanceof ApiError)) return undefined
  if (erreur.status < 400 || erreur.status >= 500 || [401, 403, 404].includes(erreur.status)) return undefined
  return erreur.message
}

/** Introuvable (404) : réessayer ne changera rien, on ne le propose pas. */
export function estIntrouvable(erreur: unknown): boolean {
  return erreur instanceof ApiError && erreur.status === 404
}

/**
 * Une panne n'est pas « aucun résultat » : sans ce bloc, une coupure réseau se lit comme un
 * catalogue, un carnet ou une liste d'accès vide, et l'élève cherche l'erreur ailleurs.
 */
export function ErreurChargement({ objet, message, onRetry, compact = false, className }: ErreurChargementProps) {
  useI18n()
  return (
    <div
      role="alert"
      className={cn(
        "flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-card/60 text-center",
        compact ? "px-4 py-8" : "px-6 py-14",
        className,
      )}
    >
      <span className="flex size-12 items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
        <RefreshCw className="size-6" aria-hidden="true" />
      </span>
      <p className="font-display text-lg font-semibold">
        {objet ? t("erreur.charger_objet", { objet }) : t("erreur.charger_page")}
      </p>
      <p className="max-w-sm text-sm text-muted-foreground">
        {message ?? t("erreur.message")}
      </p>
      {onRetry && (
        <Button onClick={onRetry} className="min-h-11 rounded-full">
          <RefreshCw />
          {t("erreur.reessayer")}
        </Button>
      )}
    </div>
  )
}
