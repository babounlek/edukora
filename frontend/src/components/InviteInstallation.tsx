import { useState } from "react"
import { Smartphone } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { ecarterInstallation, proposerInstallation, useInstallationPossible } from "@/lib/installation"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Installe EduKora sur ton téléphone », proposé après un quiz : l'icône sur l'écran d'accueil est le rappel le moins cher
 * qui soit, et l'élève vient de voir à quoi sert le site. Une seule fois par appareil : « Plus tard » ou l'installation
 * la font disparaître pour de bon. Rien à l'écran quand le navigateur ne sait pas installer (voir lib/installation).
 */
export function InviteInstallation({ className }: { className?: string }) {
  useI18n()
  const possible = useInstallationPossible()
  const [enCours, setEnCours] = useState(false)
  if (!possible) return null

  async function installer() {
    setEnCours(true)
    try {
      if ((await proposerInstallation()) === "accepted") toast.success(t("install.fait"))
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-3 rounded-2xl border border-border bg-card p-4 sm:flex-row sm:items-center", className)}>
      <Smartphone className="size-6 shrink-0 text-gold-text" aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <p className="font-semibold">{t("install.titre")}</p>
        <p className="text-sm text-muted-foreground">{t("install.texte")}</p>
      </div>
      <div className="flex shrink-0 flex-wrap gap-2">
        <Button type="button" className="min-h-11 rounded-full" disabled={enCours} onClick={installer}>
          {t("install.installer")}
        </Button>
        <Button type="button" variant="ghost" className="min-h-11 rounded-full" disabled={enCours} onClick={ecarterInstallation}>
          {t("install.plus_tard")}
        </Button>
      </div>
    </div>
  )
}
