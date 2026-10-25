import { useState, type ReactNode } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { Check } from "lucide-react"
import { toast } from "sonner"

import { definirObjectifXp } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { EtatXp } from "@/api/types"
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { trackEvent } from "@/lib/analytics"
import { cn } from "@/lib/utils"
import { libelleRythme } from "@/lib/rythme"
import { t, useI18n } from "@/lib/i18n"

/**
 * Change le rythme du jour (le même réglage que « Ton rythme de chaque jour » du compte, voir ChoixRythme) depuis
 * l'endroit où l'objectif s'affiche : accueil, fin de quiz. Il était réglable seulement dans « Mon compte », menu à trois
 * entrées que l'élève n'ouvre pas (test élève Guyguy). `children` est le déclencheur : ce que l'élève clique.
 */
export function RythmeRapide({
  etat, onChange, children, className,
}: {
  etat: EtatXp
  /** Appelé avec l'état renvoyé par le serveur, pour qu'un écran déjà affiché se mette à jour. */
  onChange?: (nouvel: EtatXp) => void
  children: ReactNode
  className?: string
}) {
  useI18n()
  const queryClient = useQueryClient()
  const [enCours, setEnCours] = useState(false)

  async function choisir(valeur: number) {
    if (enCours || valeur === etat.objectif) return
    setEnCours(true)
    try {
      const nouvel = await definirObjectifXp(valeur)
      queryClient.setQueryData(["objectif-xp"], nouvel)
      queryClient.invalidateQueries({ queryKey: ["plan-du-jour"] })
      trackEvent("objectif_xp_choisi", { objectif: valeur })
      onChange?.(nouvel)
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : t("rythme.erreur"))
    } finally {
      setEnCours(false)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          disabled={enCours}
          aria-label={t("rythme.changer_aria", { rythme: libelleRythme(etat.objectif) })}
          className={cn(
            "rounded-lg text-left transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50 disabled:opacity-60",
            className,
          )}
        >
          {children}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="min-w-56">
        <DropdownMenuLabel>{t("rythme.titre")}</DropdownMenuLabel>
        {etat.objectifs_possibles.map((valeur) => (
          <DropdownMenuItem key={valeur} onSelect={() => void choisir(valeur)} className="flex items-center justify-between gap-3">
            <span>{libelleRythme(valeur)}</span>
            {valeur === etat.objectif && <Check className="size-4 text-success" aria-hidden="true" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
