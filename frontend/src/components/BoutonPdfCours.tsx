import { useState } from "react"
import { toast } from "sonner"
import { FileDown, Loader2 } from "lucide-react"

import { Button } from "@/components/ui/button"
import { NetworkError } from "@/api/client"
import { telechargerCoursPdf } from "@/lib/coursPdf"
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
      toast.error(err instanceof NetworkError ? err.message : t("co.pdf_erreur"))
    } finally {
      setEnCours(false)
    }
  }

  return (
    <Button variant="outline" size="sm" className="rounded-full" disabled={enCours} onClick={telecharger}>
      {enCours ? <Loader2 className="animate-spin" /> : <FileDown />}
      {enCours ? t("co.pdf_preparation") : t("co.pdf")}
    </Button>
  )
}
