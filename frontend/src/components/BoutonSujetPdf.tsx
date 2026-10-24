import { useState } from "react"
import { toast } from "sonner"
import { FileDown, Loader2 } from "lucide-react"

import { ouvrirSujetClassique } from "@/api/endpoints"
import { NetworkError } from "@/api/client"
import { Button } from "@/components/ui/button"
import { QuotaPdfInfo } from "@/components/QuotaPdfInfo"
import { t, useI18n } from "@/lib/i18n"
import { cn } from "@/lib/utils"

/**
 * « Télécharger le sujet » d'une épreuve classique. Le sujet est public mais il est servi par l'API, qui compte le
 * téléchargement dans le quota quotidien : on ne pointe donc plus vers le fichier (un lien direct n'enverrait ni
 * jeton ni cookie, et passerait à côté du compteur). Le nombre de téléchargements restants est affiché dessous.
 */
export function BoutonSujetPdf({ epreuveId, url, grand = false }: { epreuveId: number; url: string; grand?: boolean }) {
  useI18n()
  const [enCours, setEnCours] = useState(false)

  async function telecharger() {
    if (enCours) return
    setEnCours(true)
    try {
      await ouvrirSujetClassique(url)
    } catch (err) {
      toast.error(err instanceof NetworkError ? err.message : t("gl.pdf_sujet"))
    } finally {
      setEnCours(false)
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <Button
        variant="outline"
        size={grand ? "lg" : "sm"}
        className={cn("rounded-full", grand && "h-12")}
        disabled={enCours}
        onClick={telecharger}
      >
        {enCours ? <Loader2 className="animate-spin" /> : <FileDown />}
        {t("ed.telecharger")}
      </Button>
      <QuotaPdfInfo doc={`lesson:${epreuveId}`} className="text-xs" />
    </div>
  )
}
