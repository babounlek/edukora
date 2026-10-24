import { useState } from "react"
import { toast } from "sonner"
import { FileDown, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { ApiError, NetworkError } from "@/api/client"
import type { QuotaPdf } from "@/api/types"
import { QuotaPdfInfo } from "@/components/QuotaPdfInfo"
import { telechargerCoursPdf } from "@/lib/coursPdf"
import { messageLimiteAtteinte, signalerChangementQuota } from "@/lib/quotaPdf"
import { useEnLigne } from "@/lib/pwa"
import { t, useI18n } from "@/lib/i18n"

/**
 * « Télécharger en PDF » : le cours à garder sur le téléphone ou à imprimer. Pour tout le monde ; le serveur décide de
 * la version (avec les exercices d'application pour un abonné, sans eux sinon). Rien à proposer hors connexion : le
 * PDF se prépare côté serveur.
 */
export function BoutonPdfCours({ slug }: { slug: string }) {
  useI18n()
  const enLigne = useEnLigne()
  const [enCours, setEnCours] = useState(false)

  if (!enLigne) return null

  async function telecharger() {
    setEnCours(true)
    try {
      await telechargerCoursPdf(slug)
    } catch (err) {
      if (err instanceof ApiError && err.status === 429 && err.body && typeof err.body === "object" && "restant" in err.body) {
        // Quota quotidien atteint : le serveur l'a refusé avant de préparer quoi que ce soit.
        toast.error(messageLimiteAtteinte(err.body as QuotaPdf))
        signalerChangementQuota()
      } else {
        toast.error(err instanceof NetworkError ? err.message : t("co.pdf_erreur"))
      }
    } finally {
      setEnCours(false)
    }
  }

  return (
    <span className="flex flex-col items-start gap-1">
      <Button variant="outline" size="sm" className="rounded-full" disabled={enCours} onClick={telecharger}>
        {enCours ? <Loader2 className="animate-spin" /> : <FileDown />}
        {enCours ? t("co.pdf_preparation") : t("co.pdf")}
      </Button>
      <QuotaPdfInfo doc={`cours:${slug}`} className="text-xs" />
    </span>
  )
}
